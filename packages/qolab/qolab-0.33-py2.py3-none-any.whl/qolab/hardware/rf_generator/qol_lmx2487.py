from qolab.hardware.basic import BasicInstrument
from ._basic import RFGenerator
import serial
import re
import time


class QOL_LMX2487(RFGenerator):
    """
    QOL lab made RF generator based on TI LMX2487 chip.

    The communication with RF generator is done via nodeMCU controlling esp2866 chip.
    """

    def __init__(
        self,
        *args,
        port="/dev/ttyUSB0",
        speed=115200,
        timeout=1,
        setToDefaults=False,
        **kwds,
    ):
        super().__init__(*args, **kwds)
        self.config["Device model"] = "QOL made RF generator based on TI LMX2487 chip"
        self.port = port
        self.speed = speed
        self.timeout = timeout
        self.connection = serial.Serial(self.port, self.speed, timeout=self.timeout)
        self.log = []
        self.logCapacity = 10
        self._FreqFixed = None
        self.hopeFree = True
        self.hopeFreeFreqJump = 100e3  # we break laser lock if Freq change is larger
        self.dwellTime = 0.1  # needed for hope free setling
        if setToDefaults:
            self.sendSerialCmd("set_lmx2487_board_to_default_state()")

    def add2log(self, text):
        self.log.append(text)
        while len(self.log) > self.logCapacity:
            self.log.pop(0)

    def log2str(self, interval=None):
        strOut = ""
        for e in self.log:
            strOut += e
        return strOut

    def sendSerialCmd(self, cmd):
        self.connection.write(bytes(cmd + "\r", "ascii"))
        if "3.4" == serial.__version__:
            # older version style
            resp = self.connection.read_until(terminator=b"> ")
        else:
            # new style after 20180616
            resp = self.connection.read_until(expected=b"> ")
        resp = resp.decode("utf-8")
        self.add2log(resp)
        return resp

    @BasicInstrument.tsdb_append
    def setFreqFixed(self, freq):
        """Set frequency of RF signal.

        Will do incremental hope free tuning to desired frequency,
        if self.hopeFree is True.
        RF generator itself is fine, but our laser looses lock without it.
        """

        finished = False
        while not finished:
            frNow = self.getFreqFixed()
            dF = freq - frNow
            if dF >= 0:
                dFSign = 1
            else:
                dFSign = -1
            dF = abs(dF)
            if dF <= self.hopeFreeFreqJump or not self.hopeFree:
                fr = freq
                finished = True
            else:
                fr = frNow + dFSign * self.hopeFreeFreqJump
            self._FreqFixed = fr
            cmd_str = f"setFreq({fr:.2f})"
            self.sendSerialCmd(cmd_str)
            if not finished:
                time.sleep(self.dwellTime)

    @BasicInstrument.tsdb_append
    def getFreqFixed(self):
        """Gets RF signal frequency.

        Talking to hardware is slow, so we use cached value if we can.
        """
        if self._FreqFixed is None:
            resp = self.sendSerialCmd("getFreq()")
            m = re.search("[0-9.]+", resp)
            if m is not None:
                self._FreqFixed = float(m.group())
        return self._FreqFixed


if __name__ == "__main__":
    import platform

    if platform.system() == "Linux":
        rfgen = QOL_LMX2487(port="/dev/ttyUSB0", speed=115200, timeout=1)
    else:
        rfgen = QOL_LMX2487(port="COM4", speed=115200, timeout=1)
    print("testing")
    print("------ Header start -------------")
    print(str.join("\n", rfgen.getHeader()))
    print("------ Header ends  -------------")
