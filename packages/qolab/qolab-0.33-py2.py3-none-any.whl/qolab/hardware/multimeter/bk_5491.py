from qolab.hardware.basic import BasicInstrument
from ._basic import Multimeter
from pyvisa import constants as pyvisa_constants
import time


class BK_5491(Multimeter):
    r"""BK 5491 multimeter

    Make sure to switch off the ECHO at the multimeter communication setup.

    Example
    -------
    >>> rm = pyvisa.ResourceManager()
    >>> instr=rm.open_resource('ASRL/dev/ttyUSB0::INSTR')
    >>> multimeter = BK_5491(instr)
    >>> print("------ Header start -------------")
    >>> print(str.join("\n", multimeter.getHeader()))
    >>> print("------ Header ends  -------------")
    """

    def __init__(self, resource, *args, **kwds):
        super().__init__(*args, **kwds)
        self.resource = resource
        self.config["Device model"] = "BK 5491"
        self.resource.read_termination = "\r\n"
        self.resource.baud_rate = 9600
        self.resource.data_bits = 8
        self.resource.parity = pyvisa_constants.Parity.none
        self.resource.stop_bits = pyvisa_constants.StopBits.one
        self.resource.timeout = 5000

        self.read = self.resource.read
        # we need to work around the prompts which BK_5491 sends during
        # communication to mimic SCPI
        # if you need raw connection use self.resource.write or self.resource.query
        # self.write = self.resource.write
        # self.query = self.resource.query
        self.read_bytes = self.resource.read_bytes
        self.read_binary_values = self.resource.read_binary_values
        self.query_binary_values = self.resource.query_binary_values

        self.switchTime = 0.5  # switch time in seconds for Function/Measurement change
        self.deviceProperties.update({"Function"})

    def isPrompt(self, string):
        if string[1] == ">":
            return True
        return False

    def isPromptGood(self, prompt):
        if prompt[0:2] == "=>":
            return True
        print(f"Error detected {prompt=}")
        return False

    def write(self, cmd_string):
        """Write/send command to instrument"""
        return self._readwrite(cmd_string, expect_reply=False, Nattemts=1)

    def query(self, cmd_string):
        """Query instrument with command"""
        return self._readwrite(cmd_string, expect_reply=True, Nattemts=5)

    def _readwrite(self, cmd_string, expect_reply=True, Nattemts=5):
        """
        Send command to instrument or query it readings (which is also a command)

        BK_5491 is not a SCPI instrument,
        so we get some replies (prompts ``*>``, ``=>``, etc)
        even if we just send a command not a query. So we have to work around this.
        """
        self.resource.read_bytes(self.resource.bytes_in_buffer)  # clear read buffer
        # print(f"dbg: {cmd_string=}")
        self.resource.write(cmd_string)
        if expect_reply:
            reply = self.resource.read()  # this should be result
            # print(f"dbg: {reply=}")
            if self.isPrompt(reply):
                prompt = reply
                if prompt[0] == "@":
                    if Nattemts >= 2:
                        """
                        print(
                        "dbg: numeric reading is not available yet"
                        + ", attempt one more time"
                        )
                        """
                        time.sleep(self.switchTime)
                        return self._readwrite(
                            cmd_string, expect_reply=expect_reply, Nattemts=Nattemts - 1
                        )
                print(
                    f"Error: we ask {cmd_string=}"
                    + f' and got prompt "{reply}" instead of result'  # noqa: W503
                )
                return None
        else:
            reply = None
        prompt = self.resource.read()  # this should be prompt
        if not self.isPromptGood(prompt):
            print(f'Error: expected good prompt but got "{prompt=}"')
        return reply

    def getReading(self):
        """Report current measurement displayed on the first/main display"""
        ret_string = self.query("R1")
        # print(f'dbg: getReading received "{ret_string}"')
        return float(ret_string)

    """
    BK_5491 has two displays which could be set and read separately,
    here we use only setting of the 1st display (prefix S1 below)
    to set the measurement and read it later.
    It is also possible to set range, but I prefer to leave in to
    the front panel user.
    If this is needed it would be followed by 3 symbols specifiers as
    outline in the manual.
    """

    @BasicInstrument.tsdb_append
    def getVdc(self):
        self.write("S10")
        return self.getReading()

    @BasicInstrument.tsdb_append
    def getVac(self):
        self.write("S11")
        return self.getReading()

    @BasicInstrument.tsdb_append
    def getAdc(self):
        self.write("S14")
        return self.getReading()

    @BasicInstrument.tsdb_append
    def getAac(self):
        self.write("S15")
        return self.getReading()

    @BasicInstrument.tsdb_append
    def getResistance(self):
        self.write("S12")
        return self.getReading()

    @BasicInstrument.tsdb_append
    def getResistance4Wires(self):
        self.write("S13")
        return self.getReading()

    @BasicInstrument.tsdb_append
    def getDiode(self):
        self.write("S16")
        return self.getReading()

    @BasicInstrument.tsdb_append
    def getFreq(self):
        self.write("S17")
        return self.getReading()

    """
    With BK_5491
    It is possible to send "key presses" like they are coming from the front panel
        K1 - Vdc
        K2 - Adc
        K3 - Vac
        K4 - Aac
        K5 - Resistance
        K6 - Diode
        K7 - Frequency (Hz)
        K8 - Auto
        K9 - Up key
        K10 - Down key
        K11 - MinMax key
        K12 - Hold key
        K13 - Local (manual does not specify, but it works this way)
        K14 - Rel key
        K15 - Shift key
        K16 - 2nd key
        K17 - Vdc and Vac keys simultaneously
        K18 - Adc and Aac keys simultaneously
        K19 - Shift then Up keys (increasing the intensity of the VFD display)
        K20 - Shift then Down keys (decreasing the intensity of the VFD display)
    """

    def toLocal(self):
        self.sendCmd("K13", expect_reply=False)

    def getFunction(self):
        reply = self.query("R0")
        """
        According to the manual:
        The reply is in 10 digits in the form <h1><h2><g1><g2><v><x><f1><r1><f2><r2>
        the <f1> and <f2> correspond to measurement/function of the 1st and 2nd display.
        Looks like it some sort of a lie, since in our BK_5491A with firmware v1.23,3
        we get back either 11 digits (if both displays are on) or 9 if only 1st display
        is on.
        We are concerned with 1st (primary) display
        """
        if len(reply) == 9:
            f1 = reply[7]
        elif len(reply) == 11:
            f1 = reply[7]
        else:
            return "Unknown"
        print(f1)
        if f1 == "0":
            return "Vdc"
        elif f1 == "1":
            return "Vac"
        elif f1 == "2":
            return "Resistance"
        elif f1 == "3":
            return "Resistance4Wires"
        elif f1 == "4":
            return "Adc"
        elif f1 == "5":
            return "Aac"
        elif f1 == "6":
            return "Diode"
        elif f1 == "7":
            return "Frequency"
        elif f1 == "8":
            return "V(ac+dc)"
        elif f1 == "9":
            return "A(ac+dc)"
        elif f1 == "A":
            return "Continuity"
        else:
            return "Unknown"


if __name__ == "__main__":
    import pyvisa

    print("testing")
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    instr = rm.open_resource("ASRL/dev/ttyUSB0::INSTR")
    multimeter = BK_5491(instr)
    print("------ Header start -------------")
    print(str.join("\n", multimeter.getHeader()))
    print("------ Header ends  -------------")
