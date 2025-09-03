"""Basic RF generator classes to implement hardware aware classes."""

from qolab.hardware.scpi import SCPIinstr
from qolab.hardware.basic import BasicInstrument


class RFGenerator(BasicInstrument):
    """Minimal set of methods to be implemented by a RF Generator.

    Intended to be used as a parent for hardware aware classes.
    """

    def __init__(self, *args, **kwds):
        BasicInstrument.__init__(self, *args, **kwds)
        self.config["Device type"] = "RFGenerator"
        self.config["Device model"] = "Generic RF generator Without Hardware interface"
        self.config["FnamePrefix"] = "rfgen"
        self.deviceProperties.update({"FreqFixed"})


class RFGeneratorSCPI(SCPIinstr, RFGenerator):
    """SCPI aware RF generator.

    Example
    -------

    >>> rm = pyvisa.ResourceManager()
    >>> RFGeneratorSCPI(rm.open_resource('TCPIP::192.168.0.2::INSTR'))
    """

    def __init__(self, resource, *args, **kwds):
        SCPIinstr.__init__(self, resource)
        RFGenerator.__init__(self, *args, **kwds)
        self.config["DeviceId"] = str.strip(self.idn)
