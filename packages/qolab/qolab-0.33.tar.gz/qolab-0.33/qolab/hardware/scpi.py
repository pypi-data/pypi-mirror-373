"""
provide basic class to operate SCPI capable instruments
"""

import re
import logging
import time

logging.basicConfig(
    format="%(asctime)s %(levelname)8s %(name)s: %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)
logger = logging.getLogger("qolab.hardware.scpi")
logger.setLevel(logging.INFO)


def response2numStr(strIn, firstSeparator=None, unit=None):
    """Parses non standard SCPI reply.

    Often an instrument reply is in the form 'TDIV 2.00E-08S'
    (for example Siglent Scope).
    I.e. "<prefix><firstSeparator><numberString><unit> where
    prefix='TDIV', firstSeparator=' ', numberString='2.00E-08', unit='S'

    Parameters
    ----------
    prefix : str
        reply prefix, e.g. 'TDIV'
    firstSeparator : str
        separator between numerical part and prefix, e.g. ' '
    unit: str
        unit used in the reply, e.g. 'S'

    Returns
    -------
    (prefix, numberString, unit) tuple
    """
    prefix = None
    rstr = strIn
    if firstSeparator is not None and firstSeparator != "":
        spltStr = re.split(firstSeparator, strIn)
        prefix = spltStr[0]
        rstr = spltStr[1]
    if unit is not None and unit != "":
        spltStr = re.split(unit, rstr)
        if len(spltStr) == 1:
            unit = None
        numberString = spltStr[0]
    else:
        numberString = rstr
    return (prefix, numberString, unit)


class SCPI_PROPERTY(property):
    """Overrides 'property' class and makes it suitable for SCPI set and query notation.

    Adds ability to log into TSDB.
    Works within SCPIinstr class since it assumes that owner has query() and write().

    Parameters
    ----------
    scpi_prfx : str or None (default)
        SCPI command prefix to get/set property, for example 'FreqInt'
        is internally transformed to
        query 'FreqInt?' and setter 'FreqInt {val}'.
        It could be set as the explicit query and set format string list:
        ['AUXV? 1', 'AUXV 1,{}'] where {} is place holder for set value
    ptype :  type, str is default
        property type 'str', 'int', 'float', ...
    doc : str or None (default)
        short description of property, for example 'Internal lockin frequency'
    no_getter: True of False (default)
        does property has a getter, some properties has no getter,
        e.g. output voltage of a DAC
    no_setter : True of False (default)
        does property has a setter, some properties has no setter,
        e.g. measurement of external voltages for an ADC
    tsdb_logging : True (default) or False
        do we log get/set commands result/argument to TSDB

    Examples
    --------
    x = SCPI_PROPERTY(scpi_prfx='SETX', ptype=str, doc='property X', tsdb_logging=False)

    """

    def __init__(
        self,
        scpi_prfx=None,
        ptype=str,
        doc=None,
        no_getter=False,
        no_setter=False,
        tsdb_logging=True,
    ):
        self.no_getter = no_getter
        self.no_setter = no_setter
        self.tsdb_logging = tsdb_logging
        if no_getter:
            fget = None
        else:
            fget = self.get_scpi
        if no_setter:
            fset = None
        else:
            fset = self.set_scpi
        super().__init__(fget=fget, fset=fset)
        self.scpi_prfx = scpi_prfx
        self.ptype = ptype
        self.__doc__ = doc
        if isinstance(scpi_prfx, str):
            self.scpi_prfx_get = "".join([self.scpi_prfx, "?"])
            self.scpi_prfx_set = "".join([self.scpi_prfx, " {}"])
        elif isinstance(scpi_prfx, list):
            if len(scpi_prfx) != 2:
                raise ValueError(
                    f"{scpi_prfx=}, should be list with exactly two elements"
                )
            self.scpi_prfx_get = self.scpi_prfx[0]
            self.scpi_prfx_set = self.scpi_prfx[1]
        else:
            raise ValueError(f"{scpi_prfx=}, it should be either str or list type")

        if not isinstance(self.scpi_prfx_get, str):
            raise ValueError(f"{self.scpi_prfx_get=}, it should be str type")
        if not isinstance(self.scpi_prfx_set, str):
            raise ValueError(f"{self.scpi_prfx_set=}, it should be str type")

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = "_" + name

    def log_to_tsdb(self, owner, action=None, val=None):
        if owner.tsdb_ingester is None or not self.tsdb_logging:
            return
        if owner.config["DeviceNickname"] is not None:
            measurement = owner.config["DeviceNickname"]
        else:
            measurement = owner.config["Device type"]
        ts = time.time()
        ts_ms = int(ts * 1000)
        var_name = self.public_name
        tags = {"action": action}
        fields = {var_name: val}
        try:
            msg = f"{ts_ms=}, {measurement=}, {tags=}, {fields=}"
            logger.debug(msg)
            owner.tsdb_ingester.append(
                ts_ms, measurement=measurement, tags=tags, **fields
            )
        except ValueError as err:
            logger.error(f"{err=}: cannot log to TSDB {var_name} = {val}")

    def get_scpi(self, owner):
        val = self.ptype(owner.query(f"{self.scpi_prfx_get}"))
        self.log_to_tsdb(owner, action="get", val=val)
        return val

    def set_scpi(self, owner, val):
        cstr = self.scpi_prfx_set.format(val)
        owner.write(cstr)
        self.log_to_tsdb(owner, action="set", val=val)

    def __repr__(self):
        sargs = []
        sargs.append(f"scpi_prfx={self.scpi_prfx}")
        sargs.append(f"ptype={self.ptype}")
        sargs.append(f"doc={self.__doc__}")
        sargs.append(f"no_getter={self.no_getter}")
        sargs.append(f"no_setter={self.no_setter}")
        sargs.append(f"tsdb_logging={self.tsdb_logging}")
        sargs = ", ".join(sargs)
        s = "".join([f"{self.__class__.__name__}(", sargs, ")"])
        return s


class SCPIinstr:
    """Basic class which support SCPI commands.

    Intended to be a parent for more hardware aware classes.

    Example
    -------
    >>> rm = pyvisa.ResourceManager()
    >>> SCPIinstr(rm.open_resource('TCPIP::192.168.0.2::INSTR'))
    """

    def __init__(self, resource):
        self.resource = resource

        # convenience pyvisa functions
        self.read_bytes = self.resource.read_bytes
        self.read_binary_values = self.resource.read_binary_values
        self.query_binary_values = self.resource.query_binary_values

    def write(self, *args):
        logger.debug(f"write with args: {args}")
        return self.resource.write(*args)

    def read(self, *args):
        logger.debug(f"read with args: {args}")
        return self.resource.read(*args)

    def query(self, *args, **kwds):
        logger.debug(f"query with args: {args}")
        return self.resource.query(*args, **kwds)

    @property
    def idn(self):
        return self.query("*IDN?")

    def clear_status(self):
        self.write("*CLS")

    def set_event_status_enable(self):
        self.write("*ESE")

    def query_event_status_enable(self):
        return self.query("*ESE?")

    def query_event_status_register(self):
        return self.query("*ESR?")

    def set_wait_until_finished(self):
        self.write("*OPC")

    def wait_until_finished(self):
        return self.query("*OPC?")

    def reset(self):
        self.write("*RST")

    def set_service_request_enable(self):
        self.write("*SRE")

    def query_service_request_enable(self):
        return self.query("*SRE?")

    def query_status_byte(self):
        return self.query("*STB?")

    def self_test_result(self):
        return self.query("*TST?")

    def wait(self):
        self.write("*WAI")


if __name__ == "__main__":
    from qolab.hardware.basic import BasicInstrument

    class DummyInstrument(BasicInstrument):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        # in order to check SCPI_PROPERTY we need to implement write and query
        def write(self, str):
            print(f"write: {str=}")

        def query(self, str):
            print(f"query: {str=}")
            return "123"

        x = SCPI_PROPERTY(
            scpi_prfx="SETX", ptype=str, doc="property X", tsdb_logging=False
        )
        y = SCPI_PROPERTY(scpi_prfx="SETY", ptype=int, no_setter=True, doc="property Y")
        z = SCPI_PROPERTY(scpi_prfx="SETY", ptype=int, no_getter=True, doc="property Z")

    c1 = DummyInstrument()
    c1.deviceProperties.update({"x", "y"})
    c1.getConfig()
    c2 = DummyInstrument()
