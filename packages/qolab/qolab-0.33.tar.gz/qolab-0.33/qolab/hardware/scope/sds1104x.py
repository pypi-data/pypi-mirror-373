"""
Created by Eugeniy E. Mikhailov 2021/11/29
"""

from qolab.hardware.basic import BasicInstrument
from ._basic import ScopeSCPI, calcSparsingAndNumPoints
from qolab.hardware.scpi import response2numStr
from qolab.data.trace import Trace
import numpy as np
import scipy.signal
from pyvisa.constants import InterfaceType
import platform


class SDS1104X(ScopeSCPI):
    """Siglent SDS1104x scope"""

    # SDS1104x has actually 8 divisions but its behave like it has 10,
    # the grabbed trace has more points outside what is visible on the screen
    vertDivOnScreen = 10
    horizDivOnScreen = 14

    def __init__(self, resource, *args, **kwds):
        super().__init__(resource, *args, **kwds)
        self.config["Device model"] = "SDS1104X"
        self.resource.read_termination = "\n"
        self.numberOfChannels = 4
        self.maxRequiredPoints = 1000
        # desired number of points per channel, can return twice more

    def mean(self, chNum):
        # get mean on a specific channel calculated by scope
        # PAVA stands for PArameter VAlue
        qstr = f"C{chNum}:PAVA? MEAN"
        rstr = self.query(qstr)
        # reply is in the form 'C1:PAVA MEAN,3.00E-02V'
        prefix, numberString, unit = response2numStr(rstr, firstSeparator=",", unit="V")
        return float(numberString)

    def getAvailableNumberOfPoints(self, chNum):
        if chNum != 1 and chNum != 3:
            # for whatever reason 'SAMPLE_NUM' fails for channel 2 and 4
            chNum = 1
        qstr = f"SAMPLE_NUM?  C{chNum}"
        rstr = self.query(qstr)
        # reply is in the form 'SANU 7.00E+01pts'
        prefix, numberString, unit = response2numStr(
            rstr, firstSeparator=" ", unit="pts"
        )
        return int(float(numberString))

    @BasicInstrument.tsdb_append
    def getSampleRate(self):
        rstr = self.query("SAMPLE_RATE?")
        # expected reply is like 'SARA 1.00E+09Sa/s'
        prefix, numberString, unit = response2numStr(
            rstr, firstSeparator=" ", unit="Sa/s"
        )
        return int(float(numberString))

    def setSampleRate(self, val):
        print("Cannot set SampleRate directly for SDS1104X")
        # it is not possible to do with this model directly
        pass

    def getRawWaveform(
        self, chNum, availableNpnts=None, maxRequiredPoints=None, decimate=True
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

        rawChanCfg = {}
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
            # Apparently sparsing has no effect with this command
            # and effectively uses SP=1 for any sparsing
            # but I want to make sure and force it
            cstr = "WAVEFORM_SETUP NP,0,FP,0,SP,1"
            # technically when we know Npnts and sparsing
            # we can use command from the follow up 'else' clause
        else:
            # we just ask every point with 'sparsing' interval
            # fast to grab but we could do better with more advance decimate
            # method, which allow better precision for the price
            # of longer acquisition time
            cstr = f"WAVEFORM_SETUP SP,{sparsing},NP,{Npnts},FP,0"
            # Note: it is not enough to provide sparsing (SP),
            # number of points (NP) needed to be calculated properly too!
            # From the manual
            # WAVEFORM_SETUP SP,<sparsing>,NP,<number>,FP,<point>
            # SP Sparse point. It defines the interval between data points.
            # For example:
            #   SP = 0 sends all data points.
            #   SP = 1 sends all data points.
            #   SP = 4 sends every 4th data point
            # NP — Number of points. It indicates how many points should be transmitted.
            # For example:
            #   NP = 0 sends all data points.
            #   NP = 50 sends a maximum of 50 data points.
            # FP — First point. It specifies the address of the first data point
            # to be sent.
            # For example:
            #   FP = 0 corresponds to the first data point.
            #   FP = 1 corresponds to the second data point
        self.write(cstr)

        trRaw = Trace(f"Ch{chNum}")

        qstr = f"C{chNum}:WAVEFORM? DAT2"
        # expected full reply: 'C1:WF DAT2,#9000000140.........'
        try:
            wfRaw = self.query_binary_values(
                qstr,
                datatype="b",
                header_fmt="ieee",
                container=np.array,
                chunk_size=(Npnts + 100),
            )
            if (platform.system() == 'Windows') and (self.resource.interface_type == InterfaceType.usb):
                # Somehow on windows (at least with USB interface)
                # there is a lingering empty string which we need to flush out
                r = self.read()
                if r != "":
                    print(f"WARNING: We expected an empty string but got {r=}")
            trRaw.values = wfRaw.reshape(wfRaw.size, 1)
            if decimate and sparsing != 1:
                numtaps = 3
                # not sure it is the best case
                trRaw.values = scipy.signal.decimate(
                    trRaw.values, sparsing, numtaps, axis=0
                )
        except ValueError as err:
            # most likely we get crazy number of points
            # self.read() # flushing the bogus output of previous command
            print(f"Error {err=}: getting waveform failed for {qstr=}")
            wfRaw = np.array([])
        trRaw.config["unit"] = "Count"
        trRaw.config["tags"]["Decimate"] = decimate
        trRaw.config["tags"]["rawChanConfig"] = rawChanCfg
        return trRaw

    def getChanVoltsPerDiv(self, chNum):
        qstr = f"C{chNum}:VDIV?"
        rstr = self.query(qstr)
        # expected reply to query: 'C1:VDIV 1.04E+00V'
        prefix, numberString, unit = response2numStr(rstr, firstSeparator=" ", unit="V")
        return float(numberString)

    def setChanVoltsPerDiv(self, chNum, vPerDiv):
        cstr = f"C{chNum}:VDIV {vPerDiv}"
        self.write(cstr)
        # if out of range, the VAB bit (bit 2) in the STB register to be set

    def getChanVoltageOffset(self, chNum):
        qstr = f"C{chNum}:OFST?"
        rstr = self.query(qstr)
        # expected reply to query: 'C1:OFST -1.27E+00V'
        prefix, numberString, unit = response2numStr(rstr, firstSeparator=" ", unit="V")
        return float(numberString)

    def setChanVoltageOffset(self, chNum, val):
        cstr = f"C{chNum}:OFST {val}"
        self.write(cstr)

    def getLED(self):
        """Returns binary mask of available LEDs"""
        qstr = "LED?"
        rstr = self.query(qstr)
        prefix, numberString, unit = response2numStr(rstr, firstSeparator=" ", unit="")
        return int(numberString, 16)  # convert from hex string to integer

    def toggleRun(self):
        # SY_FP is undocumented, reverse engineered from the web interface
        self.write("SY_FP 12,1")

    @BasicInstrument.tsdb_append
    def getRun(self):
        ledStatus = self.getLED()
        return bool(ledStatus & (1 << 17))

    @BasicInstrument.tsdb_append
    def setRun(self, val):
        state = self.getRun()
        if state != val:
            self.toggleRun()

    @BasicInstrument.tsdb_append
    def getRoll(self):
        ledStatus = self.getLED()
        return bool(ledStatus & (1 << 10))

    def toggleRoll(self):
        # SY_FP is undocumented, reverse engineered from the web interface
        self.write("SY_FP 49,1")

    @BasicInstrument.tsdb_append
    def setRoll(self, val):
        rollState = self.getRoll()
        if rollState != val:
            self.toggleRoll()

    @BasicInstrument.tsdb_append
    def getTimePerDiv(self):
        qstr = "TDIV?"
        rstr = self.query(qstr)
        # expected reply to query: 'TDIV 2.00E-08S'
        prefix, numberString, unit = response2numStr(rstr, firstSeparator=" ", unit="S")
        return float(numberString)

    @BasicInstrument.tsdb_append
    def setTimePerDiv(self, timePerDiv):
        cstr = f"TDIV {timePerDiv}"
        self.write(cstr)
        # if out of range, the VAB bit (bit 2) in the STB register to be set

    @BasicInstrument.tsdb_append
    def getTrigDelay(self):
        qstr = "TRIG_DELAY?"
        rstr = self.query(qstr)
        # expected reply to query: 'TRDL -0.00E+00S'
        prefix, numberString, unit = response2numStr(rstr, firstSeparator=" ", unit="S")
        return float(numberString)

    @BasicInstrument.tsdb_append
    def setTrigDelay(self, value):
        cstr = f"TRIG_DELAY {value}"
        self.write(cstr)

    def getWaveform(
        self, chNum, availableNpnts=None, maxRequiredPoints=None, decimate=True, **kwargs
    ):
        """
        For decimate use see ``getRawWaveform``.

        In short decimate=True is slower but more precise.
        """
        trRaw = self.getRawWaveform(
            chNum,
            availableNpnts=availableNpnts,
            maxRequiredPoints=maxRequiredPoints,
            decimate=decimate,
        )
        VoltageOffset = self.getChanVoltageOffset(chNum)
        VoltsPerDiv = self.getChanVoltsPerDiv(chNum)
        tr = trRaw
        tr.values = (
            trRaw.values * VoltsPerDiv * self.vertDivOnScreen / 250 - VoltageOffset
        )
        tr.config["unit"] = "Volt"
        tr.config["tags"]["VoltageOffset"] = VoltageOffset
        tr.config["tags"]["VoltsPerDiv"] = VoltsPerDiv
        return tr

    def getTimeTrace(self, rawChanCfg):
        availableNpnts = rawChanCfg["availableNpnts"]
        sparsing = rawChanCfg["sparsing"]
        Npnts = rawChanCfg["Npnts"]
        sampleRate = self.getSampleRate()
        timePerDiv = self.getTimePerDiv()
        trigDelay = self.getTrigDelay()
        if Npnts is None and sparsing is None:
            # using channel 1 as reference
            Npnts = self.getAvailableNumberOfPoints(1)
        tval = np.arange(Npnts) / sampleRate * sparsing
        tval = tval - timePerDiv * self.horizDivOnScreen / 2 - trigDelay
        t = Trace("Time")
        t.values = tval.reshape(tval.size, 1)
        t.config["unit"] = "s"
        t.config["tags"]["TimePerDiv"] = timePerDiv
        t.config["tags"]["TrigDelay"] = trigDelay
        t.config["tags"]["SampleRate"] = sampleRate
        t.config["tags"]["AvailableNPnts"] = availableNpnts
        t.config["tags"]["Npnts"] = availableNpnts
        t.config["tags"]["Sparsing"] = sparsing
        return t

    def getTriggerMode(self):
        # we expect NORM, AUTO, SINGLE, STOP
        res = self.query("TRIG_MODE?")
        # res is in the form 'TRMD AUTO'
        return res[5:]

    def setTriggerMode(self, val):
        # we expect NORM, AUTO, SINGLE, STOP
        self.write(f"TRIG_MODE {val}")


if __name__ == "__main__":
    import pyvisa

    print("testing")
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    instr = rm.open_resource("TCPIP::192.168.0.62::INSTR")
    scope = SDS1104X(instr)
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
    traces = scope.getAllTraces()
