"""Basic lockin classes intended for expansion with hardware aware classes."""

from qolab.hardware.scpi import SCPIinstr
from qolab.hardware.basic import BasicInstrument


class Lockin(BasicInstrument):
    """Basic lockin class with.
    Intended to be expanded in hardware specific classes.
    """

    def __init__(self, *args, **kwds):
        BasicInstrument.__init__(self, *args, **kwds)
        self.config["Device type"] = "Lockin"
        self.config["FnamePrefix"] = "lockin"
        self.config["Device model"] = "Generic Lockin Without Hardware interface"
        self.config["FnamePrefix"] = "lockin"
        self.deviceProperties.update(
            {
                "FreqInt",
                "FreqExt",
                "Harm",
                "SinAmpl",
                "SinOffset",
                "RefPhase",
                "Sensitivity",
                "TimeConstan",
                "FilterSlope",
                "EquivalentNoiseBW",
            }
        )

    # Minimal set of methods to be implemented.
    pass


class LockinSCPI(SCPIinstr, Lockin):
    """Basic lockin class with SCPI interface.
    Intended to be expanded in hardware specific classes.

    Example
    -------
    >>> rm = pyvisa.ResourceManager()
    >>> LockinSCPI(rm.open_resource('TCPIP::192.168.0.2::INSTR'))
    """

    pass

    def __init__(self, resource, *args, **kwds):
        SCPIinstr.__init__(self, resource)
        Lockin.__init__(self, *args, **kwds)
        self.config["DeviceId"] = str.strip(self.idn)
