"""Basic class to build hardware avare classes of power supplies."""

from qolab.hardware.scpi import SCPIinstr
from qolab.hardware.basic import BasicInstrument


class PowerSupply(BasicInstrument):
    """Base class for a Power Supply.

    Contains minimal set of methods to be implemented by a Power Supply.

    Intended to be used as a parent for hardware aware power supplies.
    """

    def __init__(self, *args, **kwds):
        BasicInstrument.__init__(self, *args, **kwds)
        self.config["Device type"] = "PowerSupply"
        self.config["Device model"] = (
            "Generic Power Supply generator Without Hardware interface"
        )
        self.config["FnamePrefix"] = "power_supply"
        self.deviceProperties.update({})


class PowerSupplySCPI(SCPIinstr, PowerSupply):
    """SCPI aware power supply.

    Intended to be used as a parent for hardware aware power supplies.

    Example
    -------

    >>> rm = pyvisa.ResourceManager()
    >>> PowerSupplySCPI(rm.open_resource('TCPIP::192.168.0.2::INSTR'))

    or

    >>> PowerSupplySCPI(rm.open_resource('USB0::10893::4354::MY61001869::0::INSTR'))
    """

    def __init__(self, resource, *args, **kwds):
        SCPIinstr.__init__(self, resource)
        PowerSupply.__init__(self, *args, **kwds)
        self.config["DeviceId"] = str.strip(self.idn)
