"""
Created by Eugeniy E. Mikhailov 2021/11/29
"""

from qolab.hardware.scope.sds1104x import SDS1104X
from qolab.hardware.scope._basic import calcSparsingAndNumPoints
from qolab.hardware.basic import BasicInstrument
from qolab.hardware.scpi import response2numStr
from qolab.data.trace import Trace
import numpy as np
import scipy.signal
from pyvisa.constants import InterfaceType
import platform

import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)8s %(name)s: %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SDS800XHD(SDS1104X):
    """Siglent SDS800XHD scope"""

    # SDS1104x has actually 8 divisions but its behave like it has 10,
    # the grabbed trace has more points outside what is visible on the screen
    vertDivOnScreen = 8
    horizDivOnScreen = 10

    def __init__(self, resource, *args, **kwds):
        super().__init__(resource, *args, **kwds)
        self.config["Device model"] = "SDS800XHD"
        self.resource.read_termination = "\n"
        self.resource.timeout = 1000
        self.numberOfChannels = 4
        self.maxRequiredPoints = 1000
        # desired number of points per channel, can return twice more
        self.deviceProperties.update({"MemoryDepth"})

    @BasicInstrument.tsdb_append
    def getTimePerDiv(self):
        qstr = "TDIV?"
        rstr = self.query(qstr)
        # Careful! TDIV? is undocumented for SDS800XHD scope,
        # the prescribe command is ":TIMebase:SCALe?".
        # But "TDIV?"  works identical to SDS2304, i.e.
        # Siglent claims that this model should have same commands as SDS1104X
        # However response is different.
        # For example we got '2.00E-08S' instead 'TDIV 2.00E-08S'
        # expected reply to query: '2.00E-08S'
        prefix, numberString, unit = response2numStr(
            rstr, firstSeparator=None, unit="S"
        )
        return float(numberString)

    def getRawWaveform(
        self,
        chNum,
        availableNpnts=None,
        maxRequiredPoints=None,
        decimate=True,
        fmath=False,
    ):
        """
        Get raw channel waveform in binary format.

        Parameters
        ----------
        chNum : int
            Scope channel to use: 1, 2, 3, or 4
        availableNpnts : int or None (default)
            Available number of points. Do not set it if you want it auto detected.
        maxRequiredPoints : int
            Maximum number of required points, if we ask less than available
            we well get sparse set which proportionally fills all available time range.
        decimate : False or True (default)
            Decimate should be read as apply the low pass filter or not, technically
            for both setting we get decimation (i.e. smaller than available
            at the scope number of points). The name came from
            ``scipy.signal.decimate`` filtering function.
            If ``decimate=True`` is used, we get all available points
            and then low-pass filter them to get ``maxRequiredPoints``
            The result is less noisy then, but transfer time from the instrument
            is longer.
            If ``decimate=False``, then it we are skipping points to get needed number
            but we might see aliasing, if there is a high frequency noise
            and sparing > 1. Unless you know what you doing, it is recommended
            to use ``decimate=True``.
        """

        if fmath and not decimate:
            print("WARNING: this scope cannot decimate function/math channel in hardware!:")
            print("WARNING: forcing decimate -> True")
            decimate = True
        rawChanCfg = {}
        # switching to binary data transfer
        self.write(":WAVeform:WIDTh WORD")  # two bytes per data point
        rawChanCfg["WaveformWidth"] = "WORD"
        self.write(":WAVeform:BYTeorder LSB")
        rawChanCfg["WaveformByteorder"] = "LSB"

        if availableNpnts is None:
            # using channel 1 to get availableNpnts
            availableNpnts = self.getAvailableNumberOfPoints(1)
            rawChanCfg["availableNpnts"] = availableNpnts

        if maxRequiredPoints is None:
            maxRequiredPoints = self.maxRequiredPoints
        (
            sparsing,
            Npnts,
            availableNpnts,
            maxRequiredPoints,
        ) = calcSparsingAndNumPoints(availableNpnts, maxRequiredPoints)
        rawChanCfg["Npnts"] = Npnts
        rawChanCfg["sparsing"] = sparsing
        if decimate:
            Npnts = availableNpnts  # get all of them and decimate later
        if (sparsing == 1 and Npnts == availableNpnts) or decimate:
            # We are getting all points of the trace
            self.write(":WAVeform:STARt 0")  # start point to read from the scope memory
            self.write(f":WAVeform:MAXPoint {availableNpnts}")  # last point to read
            self.write(":WAVeform:INTerval 1")  # sparsing of 1, i.e. read every point
            self.write(f":WAVeform:POINt {availableNpnts}")  # transfer all points
        else:
            # we just ask every point with 'sparsing' interval
            # fast to grab but we could do better with more advance decimate
            # method, which allow better precision for the price
            # of longer acquisition time
            self.write(":WAVeform:STARt 0")  # start point to read from the scope memory
            self.write(f":WAVeform:MAXPoint {availableNpnts}")  # last point to read
            self.write(f":WAVeform:INTerval {sparsing}")  #  interval between points
            # Note: it is not enough to provide sparsing
            # number of requested points needed to be asked too.
            # However this scope is smart enough to truncate the output to
            # physically available points, if you request more no harm is done.
            self.write(f":WAVeform:POINt {Npnts}")  # transfer all points

        trRaw = Trace(f"Ch{chNum}")
        if fmath:
            self.write(f":WAVeform:SOURce F{chNum}")
        else:
            self.write(f":WAVeform:SOURce C{chNum}")
        qstr = ":WAVeform:DATA?"
        if (self.resource.interface_type == InterfaceType.usb) and ("Windows" == (platform.system())):
            # Below seems to be Windows specific, I (Eugeniy) did not observe any problem on Linux
            # with larger chunk size.
            # Setting chunk size to 496 bytes, it seems that SDS sends data
            # in 512 bytes chunks via USB.
            # Which is 8 packets of 64 bytes, but each packet takes 2 bytes for a header.
            # Thus useful payload is 512-8*2 = 496
            # see https://patchwork.ozlabs.org/project/qemu-devel/patch/20200317095049.28486-4-kraxel@redhat.com/
            # Setting chunk_size for a large number has *catastrophic* results
            # on data transfer rate, since we wait for more data
            # which is not going to come until timeout expires
            # Setting it low is not as bad but still slows down the transfer.
            # NOTE: I am not sure if it is a Linux driver issue or more global.
            # The transfer rate is about
            #       5550 kB/S, for 10k points
            #       1400 kB/S, for 50k points
            #       1000 kB/S, for 100k points
            #       500  kB/S, for 500k points
            #       160  kB/S, for 1000k points
            #       55   kB/S, for 2.5M points
            # It is about factor of 2 slower (for 100k points),
            # if the scope is in the Run mode, i.e. not Stopped.
            # FIXME find why speed depends on number of points.
            wfRaw = self.query_binary_values(
                qstr,
                datatype="h",
                header_fmt="ieee",
                container=np.array,
                chunk_size=496,
            )
            if "Windows" == (platform.system()):
                # somehow on windows there is an extra '\n' at the end
                _ = self.read_bytes(1)
        else:
            wfRaw = self.query_binary_values(
                qstr, datatype="h", header_fmt="ieee", container=np.array, chunk_size = Npnts+100
            )
        trRaw.values = wfRaw.reshape(wfRaw.size, 1)
        if decimate and sparsing != 1:
            numtaps = 3
            # not sure it is the best case
            trRaw.values = scipy.signal.decimate(
                trRaw.values, sparsing, numtaps, axis=0
            )

        trRaw.config["unit"] = "Count"
        trRaw.config["tags"]["Decimate"] = decimate
        trRaw.config["tags"]["rawChanConfig"] = rawChanCfg
        return trRaw

    def getParsedPreamble(self):
        """
        Parse preamble generated by the scope.
        It has a lot of information, number of points, scale, bits resolution, etc.

        Note: preamble is channel specific! The prior code must set desired channel
        with self.write(":WAVeform:SOURce C{chNum}")
        """
        preamble = {}
        qstr = ":WAVeform:PREamble?"
        if self.resource.interface_type == InterfaceType.usb:
            # Setting chunk size to 496 bytes, it seems that SDS sends data
            # in 512 bytes chunks via USB.
            # Which is 8 packets of 64 bytes, but each packet takes 2 bytes for a header.
            # Thus useful payload is 512-8*2 = 496
            # see https://patchwork.ozlabs.org/project/qemu-devel/patch/20200317095049.28486-4-kraxel@redhat.com/
            # Setting chunk_size for a large number has *catastrophic* results
            # on data transfer rate, since we wait for more data
            # which is not going to come until timeout expires
            resp_bin = self.query_binary_values(
                qstr,
                datatype="c",
                header_fmt="ieee",
                container=np.array,
                chunk_size=496,
            )
        else:
            resp_bin = self.query_binary_values(
                qstr, datatype="c", header_fmt="ieee", container=np.array
            )
        preamble["Npoints"] = resp_bin[116:120].view(np.int32).item()
        preamble["firstPoint"] = resp_bin[132:136].view(np.int32).item()
        preamble["sparsing"] = resp_bin[136:140].view(np.int32).item()
        preamble["voltsPerDiv"] = resp_bin[156:160].view(np.float32).item()
        preamble["verticalOffset"] = resp_bin[160:164].view(np.float32).item()
        preamble["codePerDiv"] = resp_bin[164:168].view(np.float32).item()
        preamble["adcBit"] = resp_bin[172:174].view(np.int16).item()
        preamble["samplingTime"] = resp_bin[176:180].view(np.float32).item()
        preamble["trigDelay"] = (
            -resp_bin[180:188].view(np.float64).item()
        )  # manual is wrong, it claims that this int64

        return preamble

    def getWaveform(
        self,
        chNum,
        availableNpnts=None,
        maxRequiredPoints=None,
        decimate=True,
        fmath=False,
    ):
        """
        For decimate use see ``getRawWaveform``.

        In short decimate=True is slower but more precise.
        """
        if fmath and not decimate:
            print("WARNING: this scope cannot decimate function/math channel in hardware!:")
            print("WARNING: forcing decimate -> True")
            decimate = True
        trRaw = self.getRawWaveform(
            chNum,
            availableNpnts=availableNpnts,
            maxRequiredPoints=maxRequiredPoints,
            decimate=decimate,
            fmath=fmath,
        )
        preamble = self.getParsedPreamble()
        VoltageOffset = preamble["verticalOffset"]
        VoltsPerDiv = preamble["voltsPerDiv"]
        tr = trRaw
        tr.values = trRaw.values * VoltsPerDiv / preamble["codePerDiv"] - VoltageOffset
        tr.config["unit"] = "Volt"
        tr.config["tags"]["VoltageOffset"] = VoltageOffset
        tr.config["tags"]["VoltsPerDiv"] = VoltsPerDiv
        tr.config["tags"]["Preamble"] = preamble
        return tr

    @BasicInstrument.tsdb_append
    def setSampleRate(self, val):
        """
        Set scope sampling rate

        Note: Memory management should be set to fixed
        sampling rate otherwise this command has no effect,
        while reporting success.
        """
        self.write(
            ":ACQuire:MMANagement FSRate"
        )  # switch to fixed sampling rate setting
        cstr = f":ACQuire:SRATe {val}"
        self.write(cstr)

    @BasicInstrument.tsdb_append
    def getMemoryDepth(self):
        rstr = self.query(":ACQuire:MDEPth?")
        if rstr[-1] == "G":
            return int(rstr[:-1]) * 1_000_000_000
        if rstr[-1] == "M":
            return int(rstr[:-1]) * 1_000_000
        if rstr[-1] == "k":
            return int(rstr[:-1]) * 1_000
        return int(rstr)

    @BasicInstrument.tsdb_append
    def setMemoryDepth(self, val):
        """
        Set scope memory depth. Only predefined values are possible.

        Note: Memory management should be set to fixed
        memory depth otherwise this command has no effect,
        while reporting success.
        """
        self.write(
            ":ACQuire:MMANagement FMDepth"
        )  # switch to fixed memory depth setting
        # Note: 1k setting is not possible, but manual claims otherwise
        # if val <= 1e3:
        # depth = "1k"
        if val <= 10e3:
            depth = "10k"
        elif val <= 100e3:
            depth = "100k"
        elif val <= 1e6:
            depth = "1M"
        elif val <= 10e6:
            depth = "10M"
        else:
            logger.info(
                "Memory depth higher than 10M are possible for 2 or 1 channels acquisition modes."
            )
            logger.info("If you know what you doing set it manually.")
            logger.info("For now are setting to 10M memory depth.")
            depth = "10M"
            # Note: the manual states that 100M possible
            # but I do not see it in the front panel
            # here are the values for achievable settings
            # depth = "25M"   # possible for 2 channels
            # depth = "50M"   # possible for 1 channels

        cstr = f":ACQuire:MDEPth {depth}"
        self.write(cstr)


if __name__ == "__main__":
    import pyvisa

    print("testing")
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    # instr = rm.open_resource("TCPIP::192.168.0.62::INSTR")
    instr = rm.open_resource("USB0::62700::4119::SDS08A0X806445::0::INSTR")
    scope = SDS800XHD(instr)
    print(f"ID: {scope.idn}")
    # print(f'Ch1 mean: {scope.mean(1)}')
    print(f"Ch1 available points: {scope.getAvailableNumberOfPoints(1)}")
    print(f"Sample Rate: {scope.getSampleRate()}")
    print(f"Time per Div: {scope.getTimePerDiv()}")
    print(f"Ch1 Volts per Div: {scope.getChanVoltsPerDiv(1)}")
    print(f"Ch1 Voltage Offset: {scope.getChanVoltageOffset(1)}")
    print("------ Header start -------------")
    print(str.join("\n", scope.getHeader()))
    print("------ Header ends  -------------")
    ch1 = scope.getTrace(1)
    # traces = scope.getAllTraces()
