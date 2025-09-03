"""Basic multimeter classes to be included in hardware aware classes."""

from qolab.hardware.scpi import SCPIinstr
from qolab.hardware.basic import BasicInstrument


class Multimeter(BasicInstrument):
    """
    Multimeter basic class.

    Intended to be part of the hardware aware class.
    """

    def __init__(self, *args, **kwds):
        BasicInstrument.__init__(self, *args, **kwds)
        self.config["Device type"] = "Multimeter"
        self.config["Device model"] = (
            "Generic Multimeter generator Without Hardware interface"
        )
        self.config["FnamePrefix"] = "Multimeter"
        self.config["Device model"] = "Generic Multimeter Without Hardware interface"
        self.config["FnamePrefix"] = "multimeter"
        self.deviceProperties.update({})

    # Minimal set of methods to be implemented.
    def getVdc(self):
        """Report DC Voltage"""
        print("getVdc is not implemented")
        return None

    def getVac(self):
        """Report AC Voltage"""
        print("getVac is not implemented")
        return None

    def getAdc(self):
        """Report DC Current"""
        print("getAdc is not implemented")
        return None

    def getAac(self):
        """Report AC Current"""
        print("getAac is not implemented")
        return None

    def getResistance(self):
        """Report Resistance"""
        print("getResistance is not implemented")
        return None

    def getResistance4Wires(self):
        """Report Resistance with 4 wire method"""
        print("getResistance4Wires is not implemented")
        return None

    def getDiode(self):
        """Report Diode Voltage drop"""
        print("getDiode is not implemented")
        return None

    def getFreq(self):
        """Report Frequency"""
        print("getFreq is not implemented")
        return None


class MultimeterSCPI(SCPIinstr, Multimeter):
    """
    SCPI enabled basic multimeter.

    Intended to be part of the hardware aware class.

    Example
    -------
    >>> rm = pyvisa.ResourceManager()
    >>> MultimeterSCPI(rm.open_resource('TCPIP::192.168.0.2::INSTR'))
    """

    pass

    def __init__(self, resource, *args, **kwds):
        SCPIinstr.__init__(self, resource)
        Multimeter.__init__(self, *args, **kwds)
        self.config["DeviceId"] = str.strip(self.idn)
