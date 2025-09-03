"""
Created by Eugeniy E. Mikhailov 2024/07/18
"""

from qolab.hardware.basic import BasicInstrument
from qolab.hardware.scpi import SCPI_PROPERTY
from ._basic import ScopeSCPI, calcSparsingAndNumPoints
from qolab.data.trace import Trace
import numpy as np
import scipy.signal
from pyvisa.errors import VisaIOError
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)8s %(name)s: %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RigolDS1054z(ScopeSCPI):
    """Rigol 1054 scope"""

    vertDivOnScreen = 8
    horizDivOnScreen = 12

    def __init__(self, resource, *args, **kwds):
        super().__init__(resource, *args, **kwds)
        self.config["Device model"] = "Rigol DS1054z"
        self.deviceProperties.update({"MemoryDepth"})
        self.resource.read_termination = "\n"
        self.numberOfChannels = 4
        self.maxRequiredPoints = 1200
        self.resource.timeout = 1000  # timeout in ms
        # desired number of points per channel, can return twice more

    TimePerDiv = SCPI_PROPERTY(
        scpi_prfx=":TIMEBASE:MAIN:SCALE",
        ptype=float,
        doc="Scope Time per Division",
    )

    def getTimePerDiv(self):
        return self.TimePerDiv

    def setTimePerDiv(self, value):
        self.TimePerDiv = value

    TrigDelay = SCPI_PROPERTY(
        scpi_prfx=":TIMEBASE:MAIN:OFFSET",
        ptype=float,
        doc="Scope Time Offset or Trigger Delay",
    )

    @BasicInstrument.tsdb_append
    def getTrigDelay(self):
        return self.TrigDelay

    @BasicInstrument.tsdb_append
    def setTrigDelay(self, value):
        self.TrigDelay = value

    @BasicInstrument.tsdb_append
    def getChanVoltageOffset(self, chNum):
        qstr = f":CHANnel{chNum}:OFFSet?"
        rstr = self.query(qstr)
        return float(rstr)

    @BasicInstrument.tsdb_append
    def setChanVoltageOffset(self, chNum, val):
        cstr = f":CHANnel{chNum}:OFFSet {val}"
        self.write(cstr)

    @BasicInstrument.tsdb_append
    def getChanVoltsPerDiv(self, chNum):
        qstr = f":CHANnel{chNum}:SCALe?"
        rstr = self.query(qstr)
        return float(rstr)

    @BasicInstrument.tsdb_append
    def setChanVoltsPerDiv(self, chNum, vPerDiv):
        cstr = f":CHANnel{chNum}:SCALe {vPerDiv}"
        self.write(cstr)

    @BasicInstrument.tsdb_append
    def getTriggerStatus(self):
        """Get Trigger Status.

        We expect TD, WAIT, RUN, AUTO, or STOP.
        """
        res = self.query(":TRIGger:STATus?")
        return res

    @BasicInstrument.tsdb_append
    def getRun(self):
        """Is acquisition running or stopped."""

        if self.getTriggerStatus() != "STOP":
            return True
        return False

    @BasicInstrument.tsdb_append
    def setRun(self, isRun):
        """Either enable run or stop the acquisition."""

        if isRun:
            self.run()
            return
        self.stop()

    @BasicInstrument.tsdb_append
    def getTimeBaseMode(self):
        """Get he mode of the horizontal timebase.

        We expect {MAIN|XY|ROLL}.
        MAIN stands for normal voltage vs time mode.
        XY stands X vs Y mode.
        ROLL stands for rolling mode.
        """
        res = self.query(":TIMebase:MODE?")
        return res

    @BasicInstrument.tsdb_append
    def setTimeBaseMode(self, val):
        """Set trigger mode.

        Takes {MAIN|XY|ROLL}.
        """
        self.write(f":TIMebase:MODE? {val}")

    @BasicInstrument.tsdb_append
    def getRoll(self):
        """Is Roll mode enabled."""
        if self.getTimeBaseMode() == "Roll":
            return True
        return False

    @BasicInstrument.tsdb_append
    def getTriggerMode(self):
        """Get trigger mode.

        We expect AUTO, NORM, or SING (for Single)
        """
        res = self.query(":TRIGger:SWEep?")
        return res

    @BasicInstrument.tsdb_append
    def setTriggerMode(self, val):
        """Set trigger mode.

        Takes AUTO, NORMal, or SINGle
        """
        self.write(f":TRIGger:SWEep {val}")

    @BasicInstrument.tsdb_append
    def getMemoryDepth(self):
        """Memory depth per channel.

        Returns
        -------
        Number corresponding to memory depth or AUTO
        """

        res = self.query(":ACQuire:MDEPth?")
        return res

    @BasicInstrument.tsdb_append
    def setMemoryDepth(self, val):
        """Set memory depth per channel.

        For 1 channel regime valid settings are
        {AUTO|12000|120000|1200000|12000000|24000000}
        Wherein, 24000000 (pts) is an optional memory depth.

        For 2 channel regime divide numbers by 2, i.e.
        {AUTO|6000|60000|600000|6000000|12000000}

        For 4 channel regime divide numbers by 4, i.e.
        {AUTO|3000|30000|300000|3000000|6000000}

        For 8 channel regime valid settings are
        {AUTO|12000|120000|1200000|12000000|24000000}.
        Wherein, 24000000 (pts) is an optional memory depth.

        For 16 channel regime valid settings are
        {AUTO|6000|60000| 600000|6000000|12000000}.
        Wherein, 12000000 (pts) is an optional memory depth.
        """

        # memory depth can be changed only when scope is not in STOP state
        running = self.getRun()
        if not running:
            self.setRun(True)
        self.write(f":ACQuire:MDEPth {val}")
        if not running:  # restore STOP/RUN state
            self.setRun(False)

    @BasicInstrument.tsdb_append
    def getSampleRate(self):
        """Get sample rate.

        Returns
        -------
        Sample rate in units of Samples/Second
        """

        res = self.query(":ACQuire:SRATe?")
        return float(res)

    def stop(self):
        self.write(":STOP")

    def run(self):
        self.write(":RUN")

    def restorePriorToFastGrab(self, chNum, old_config):
        """Restore relevant channel/scope settings prior to fast grab tune up."""
        self.setMemoryDepth(old_config["DeviceConfig"]["MemoryDepth"])

    def switchToFastGrab(self, chNum):
        """Switch scope to the fastest mode for trace delivery.

        To be fast, it should aim to decrease data transfer time,
        i.e. reduce number of transferred point.
        It also need to be interface dependent. GPIB and USB are known
        to be quite slow when compared to network connection.

        FIXME try to be smart about connection interface.

        Return
        ------
        old_config : dictionary
            old config with settings necessary to restore initial state
        """

        old_config = self.getConfig()
        self.setMemoryDepth(3000)

        return old_config

    def getRawWaveform(
        self, chNum, availableNpnts=None, maxRequiredPoints=None, decimate=True
    ):
        """
        Get raw channel waveform in binary format.

        The idea is to have minimal processing from internal representation
        to actual volts, since it might require less queering of the scope
        or/and faster data transfer.

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

        # if RAW is used the scope should be in STOP state
        self.write(f":WAVeform:SOURce CHAN{chNum}")
        self.write(
            ":WAVeform:MODE RAW"
        )  # {NORMal|MAXimum|RAW} RAW gives maximum number of points
        self.write(
            ":WAVeform:FORMat BYTE"
        )  # {WORD|BYTE|ASCii}, scope is 8 bit, BYTE is enough
        preamble = self.query(":WAVeform:PREamble?").split(",")
        """
        Format is
        <format>,<type>,<points>,<count>,<xincrement>,<xorigin>,<xreference>,<yincrement>,<yorigin>,<yreference>
        Wherein,
        <format>: 0 (BYTE), 1 (WORD) or 2 (ASC).
        <type>: 0 (NORMal), 1 (MAXimum) or 2 (RAW).
        <points>: an integer between 1 and 12000000. After the memory depth option is
                  installed, <points> is an integer between 1 and 24000000.
        <count>: the number of averages in the average sample mode
                 and 1 in other modes.
        <xincrement>: the time difference between two neighboring points
                      in the X direction.
        <xorigin>: the start time of the waveform data in the X direction.
        <xreference>: the reference time of the data point in the X direction.
        <yincrement>: the waveform increment in the Y direction.
        <yorigin>: the vertical offset relative
                   to the "Vertical Reference Position" in the Y direction.
        <yreference>: the vertical reference position in the Y direction.
        """
        rawChanCfg = {
            "format": int(preamble[0]),
            "type": int(preamble[1]),
            "availableNpnts": int(preamble[2]),
            "Navrg": int(preamble[3]),
            "xincrement": float(preamble[4]),
            "xorigin": float(preamble[5]),
            "xreference": int(preamble[6]),
            "yincrement": float(preamble[7]),
            "yorigin": int(preamble[8]),
            "yreference": int(preamble[9]),
        }
        logger.debug(f"rawChanCfg: {rawChanCfg}")
        availableNpnts = rawChanCfg["availableNpnts"]
        wfRaw = np.zeros(availableNpnts, dtype=np.uint8)
        maxreadable = 250_000  # the maximum number of bytes readable in one go
        chunk_size = 70_000  # unfortunately large chunk size prone to read errors
        errCnt = 0
        strt = 1
        stp = min(chunk_size, availableNpnts)
        errorFreeChunkSize = []
        errorProneChunkSize = []
        while strt <= availableNpnts:
            stp = strt - 1 + chunk_size
            stp = min(stp, availableNpnts)
            chunk_size = stp - strt + 1
            # reading requested number of points in chunks
            self.write(f":WAVeform:STARt {strt}")
            self.write(f":WAVeform:STOP {stp}")
            qstr = ":WAVeform:DATA?"
            try:
                wfRawChunk = self.query_binary_values(
                    qstr,
                    datatype="b",
                    header_fmt="ieee",
                    container=np.array,
                    chunk_size=(chunk_size + 100),
                )
                if len(wfRawChunk) == 0:
                    logger.info("Got empty chunk. Redoing.")
                    continue  # we need to repeat chunk read
                if len(wfRawChunk) != chunk_size:
                    logger.info(
                        "Expected chunk with length"
                        + f" {chunk_size} but got {len(wfRawChunk)}"
                    )
                    logger.info(
                        f"Current pointers are {strt=} {stp=} with {chunk_size=}"
                    )
                    logger.info("Redoing, chunk reading.")
                    continue  # we need to repeat chunk read
                wfRaw[strt - 1 : stp] = wfRawChunk  # noqa: E203 whitespace before ':'
                """
                All this craziness with tuning chunk_size
                and catching VisaIOError
                is because Rigol usbtmc connection is buggy.
                It present itself as high speed device over USB,
                but set incompatible packet size of 64
                while the USB standard dictates 512.
                In linux dmesg complains:
                'bulk endpoint 0x3 has invalid maxpacket 64'
                """
                strt += chunk_size
                errorFreeChunkSize.append(chunk_size)
                chunk_size = min(maxreadable, int(chunk_size * 1.1))
            except VisaIOError as err:
                logger.info(f"Detected recoverable {err}")
                errCnt += 1
                errorProneChunkSize.append(chunk_size)
                logger.debug(
                    f"Visa error count is {errCnt} while reading raw chunk the scope"
                )
                logger.debug(f"Current pointers are {strt=} {stp=} with {chunk_size=}")
                if len(errorFreeChunkSize) > 10:
                    chunk_size = int(np.mean(errorFreeChunkSize))
                else:
                    chunk_size = max(1, int(np.mean(errorProneChunkSize) * 0.8))
                logger.debug(f"New {chunk_size=}")
                logger.debug("Redoing, chunk reading.")
                pass  # we repeat this loop iteration again

        logger.debug(f"final {chunk_size=}")
        if maxRequiredPoints is None:
            maxRequiredPoints = self.maxRequiredPoints
        (
            sparsing,
            Npnts,
            availableNpnts,
            maxRequiredPoints,
        ) = calcSparsingAndNumPoints(
            availableNpnts=availableNpnts, maxRequiredPoints=maxRequiredPoints
        )
        rawChanCfg["Npnts"] = Npnts
        rawChanCfg["sparsing"] = sparsing
        if not decimate and sparsing > 1:
            wfRaw = wfRaw[::sparsing]

        trRaw = Trace(f"Ch{chNum}")
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

    def getTimeTrace(self, rawChanCfg):
        timePerDiv = self.getTimePerDiv()
        trigDelay = self.getTrigDelay()
        availableNpnts = rawChanCfg["availableNpnts"]
        sparsing = rawChanCfg["sparsing"]
        Npnts = rawChanCfg["Npnts"]
        ind = np.linspace(0, Npnts - 1, Npnts)
        dx = rawChanCfg["xincrement"]
        xorig = rawChanCfg["xorigin"]
        tval = (ind - rawChanCfg["xreference"]) * dx * sparsing + xorig
        t = Trace("time")
        t.values = tval.reshape(tval.size, 1)
        t.config["unit"] = "S"
        t.config["tags"]["TimePerDiv"] = timePerDiv
        t.config["tags"]["TrigDelay"] = trigDelay
        t.config["tags"]["SampleRate"] = int(1 / dx)
        t.config["tags"]["AvailableNPnts"] = availableNpnts
        t.config["tags"]["Npnts"] = Npnts
        t.config["tags"]["Sparsing"] = sparsing
        return t

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
        rawChanCfg = trRaw.config["tags"]["rawChanConfig"]
        VoltageOffset = self.getChanVoltageOffset(chNum)
        VoltsPerDiv = self.getChanVoltsPerDiv(chNum)
        tr = trRaw
        tr.values = (
            np.array(trRaw.values, dtype=int)
            - rawChanCfg["yreference"]
            - rawChanCfg["yorigin"]
        ) * rawChanCfg["yincrement"]

        tr.config["unit"] = "Volt"
        tr.config["tags"]["VoltageOffset"] = VoltageOffset
        tr.config["tags"]["VoltsPerDiv"] = VoltsPerDiv
        return tr


if __name__ == "__main__":
    import pyvisa

    print("testing")
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    # instr = rm.open_resource("TCPIP::192.168.0.62::INSTR")
    instr = rm.open_resource("USB0::0x1AB1::0x04CE::DS1ZA170502787::0::INSTR")
    scope = RigolDS1054z(instr)
    print(f"ID: {scope.idn}")
    print(f"TimePerDiv = {scope.TimePerDiv}")
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
