from qolab.hardware.basic import BasicInstrument
from ._basic import MultimeterSCPI
from qolab.hardware.scpi import SCPI_PROPERTY
from pyvisa import constants as pyvisa_constants
import time


class HP_34401(MultimeterSCPI):
    r"""HP 34401 multimeter (same as Agilent 34401)

    Example
    -------

    >>> from qolab.hardware.multimeter.hp_34401 import HP_34401
    >>> rm = pyvisa.ResourceManager()
    >>> instr=rm.open_resource('ASRL/dev/ttyUSB0::INSTR')
    >>> multimeter = HP_34401(instr)
    >>> print("------ Header start -------------")
    >>> print(str.join("\n", multimeter.getHeader()))
    >>> print("------ Header ends  -------------")
    """

    def __init__(self, resource, *args, **kwds):
        super().__init__(resource, *args, **kwds)
        self.config["Device model"] = "HP 34401"
        self.resource.read_termination = "\r\n"
        self.resource.baud_rate = 9600
        self.resource.data_bits = 8
        self.resource.parity = pyvisa_constants.Parity.none
        self.resource.stop_bits = pyvisa_constants.StopBits.one
        self.resource.timeout = 5000
        self.switchTime = 0.5  # switch time in seconds for Function/Measurement change
        self.deviceProperties.update({"Function"})

    rawFunction = SCPI_PROPERTY(
        scpi_prfx="SENSe:FUNCtion",
        ptype=str,
        doc="""
        Current measurement function (Voltmeter DC/AC, Currentmeter DC/AC, etc.
        Important! When assigning, string should be quoted, i.e. use:
            Function=\'"VOLT:DC"\'

        Possible values:
            "VOLTage:DC", same as "VOLT"
            "VOLTage:DC:RATio"
            "VOLTage:AC"
            "CURRent:DC", same as "CURR"
            "CURRent:AC"
            "RESistance" (2-wire ohms)
            "FRESistance" (4-wire ohms)
            "FREQuency"
            "PERiod"
            "CONTinuity"
            "DIODe"
        """,
    )

    def getFunction(self):
        rfunc = self.rawFunction
        if rfunc == '"VOLT"':
            return "Vdc"
        elif rfunc == '"VOLT:AC"':
            return "Vac"
        elif rfunc == '"CURR"':
            return "Adc"
        elif rfunc == '"CURR:AC"':
            return "Aac"
        elif rfunc == '"RES"':
            return "Resistance"
        elif rfunc == '"FRES"':
            return "Resistance4Wires"
        elif rfunc == '"DIOD"':
            return "Diode"
        elif rfunc == '"FREQ"':
            return "Frequency"
        elif rfunc == '"PER"':
            return "Period"
        elif rfunc == '"CONT"':
            return "Continuity"
        else:
            return "Unknown"

    def toRemote(self):
        self.write("SYSTem:REMote")

    def toLocal(self):
        self.write("SYSTem:LOCal")

    def isSensing(self, test):
        return test == self.rawFunction

    Reading = SCPI_PROPERTY(
        scpi_prfx="SYSTem:REMote; :READ",
        ptype=float,
        doc="Report current measurement",
        no_setter=True,
    )

    # HP 34401 is tricky:
    # when reading over serial interface the value of measurement/function,
    # the device need to be switched to REMOTE mode.
    # But this leaves screen blank and unusable.
    # So we have to do the dance with toRemote and toLocal.
    def getReadingWithSettingFunction(
        self, desired_function_string, function_internal_name
    ):
        """
        Get the required reading.

        But first check if the multimeter is set to do specific function/measurement.
        If the instrument set to do different function, set to the desired one.
        Note: the function name should be in quotes, i.e. "Volt".
        """
        if not self.isSensing(function_internal_name):
            self.rawFunction = desired_function_string
            time.sleep(self.switchTime)
        # self.toRemote() # this is done inside of Reading
        ret = self.Reading
        self.toLocal()
        return ret

    @BasicInstrument.tsdb_append
    def getVdc(self):
        return self.getReadingWithSettingFunction('"VOLTage:DC"', '"VOLT"')

    @BasicInstrument.tsdb_append
    def getVac(self):
        return self.getReadingWithSettingFunction('"VOLTage:AC"', '"VOLT:AC"')

    @BasicInstrument.tsdb_append
    def getAdc(self):
        return self.getReadingWithSettingFunction('"CURRent:DC"', '"CURR"')

    @BasicInstrument.tsdb_append
    def getAac(self):
        return self.getReadingWithSettingFunction('"CURRent:AC"', '"CURR:AC"')

    @BasicInstrument.tsdb_append
    def getResistance(self):
        return self.getReadingWithSettingFunction('"RESistance"', '"RES"')

    @BasicInstrument.tsdb_append
    def getResistance4Wires(self):
        return self.getReadingWithSettingFunction('"FRESistance"', '"FRES"')

    @BasicInstrument.tsdb_append
    def getDiode(self):
        return self.getReadingWithSettingFunction('"DIODe"', '"DIOD"')

    @BasicInstrument.tsdb_append
    def getFreq(self):
        return self.getReadingWithSettingFunction('"FREQuency"', '"FREQ"')

    @BasicInstrument.tsdb_append
    def getPeriod(self):
        return self.getReadingWithSettingFunction('"PERiod"', '"PER"')


if __name__ == "__main__":
    import pyvisa

    print("testing")
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    instr = rm.open_resource("ASRL/dev/ttyUSB0::INSTR")
    multimeter = HP_34401(instr)
    print("------ Header start -------------")
    print(str.join("\n", multimeter.getHeader()))
    print("------ Header ends  -------------")
