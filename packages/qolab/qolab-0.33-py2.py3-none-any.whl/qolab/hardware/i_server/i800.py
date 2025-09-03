"""
This unit talks to i-Series controllers sold by Omega and Newport.
They are often can be connected via iServer interface
Specifically, i853 units with LAN connection, but should be ok with many others.

Querying of this controller is slo-o-o-w at least 0.2 second and can be longer.
"""

from qolab.hardware.basic import BasicInstrument
from cachetools import cached, TTLCache
import socket
import logging

logger = logging.getLogger("qolab.hardware.i_server.i800")


class I800(BasicInstrument):
    """Newport i800 series controller, should work with similar Omega controllers

    Parameters
    ----------
    host : str
        hostname or IP of the controller unit
        the factory preset is '192.168.1.200' (default)
    port : int
        socket port (1000 i: default) which accept HTTP POST requests

    Example
    -------

    >>> tc = I800(host='192.168.1.200', port=1000)
    >>> print(tc.getConfig())
    """

    TTL_MEASURED = 30  # Time To Live for device measured things, i.e. Temperature
    TTL_SEATABLES = 600  # Time To Live for user seatables, i.e. SetPoints, Gains, etc

    def __init__(self, *args, host="192.168.1.200", port=1000, **kwds):
        BasicInstrument.__init__(self, *args, **kwds)
        self.host = host
        self.port = port
        self.modbus_address = "01"
        self.cmd_start_marker = "*"
        self.config["Device type"] = "TemperatureController"
        self.config["Device model"] = "i800"
        self.config["FnamePrefix"] = "temperature"
        self.deviceProperties.update({"Temperature", "SetPoint1", "SetPoint2"})

    def query(self, cmnd, trials=10):
        modbus_cmnd = f"{self.modbus_address}{cmnd}"
        qstr = f"POST / HTTP/1.1\r\n\r\n{self.cmd_start_marker}{modbus_cmnd}\r\n"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.send(qstr.encode("ascii"))
        reply = s.recv(100).decode("ascii")
        s.close()
        rlist = reply.split()
        # occasionally there is more than one reply, it also removes \r
        lreply = rlist[-1]
        # we will use the last one
        if lreply[0:5] != f"{modbus_cmnd}":
            # check the proper echo response
            logger.warning(
                f"Warning: expected {modbus_cmnd} but got {lreply[0:5]}"
                + f" in full set {reply}"  # noqa: W503
            )
            if trials > 0:
                return self.query(cmnd, trials - 1)
            return None
        return lreply[5:]

    @BasicInstrument.tsdb_append
    @cached(cache=TTLCache(maxsize=1, ttl=TTL_MEASURED))
    def getTemperature(self):
        command = "X01"
        # give decimal representation (X) of the temperature (01 address)
        reply = self.query(command)
        if reply is not None:
            return float(reply)
        else:
            return float("nan")

    def setPoinStr2value(self, spStr):
        raw = int(spStr, 16)
        if raw & (1 << 23):
            sign = -1
        else:
            sign = 1

        if raw & (0b1 << 20):
            scale = 1
        elif raw & (0b10 << 20):
            scale = 10
        elif raw & (0b11 << 20):
            scale = 100
        elif raw & (0b100 << 20):
            scale = 100
        else:
            logger.error(
                f"Error: unknown decimal point position in decoded {spStr} {bin(raw)}"
            )
            return float("nan")

        val = raw & 0xFFFFF
        return float(sign * val / scale)

    @BasicInstrument.tsdb_append
    @cached(cache=TTLCache(maxsize=1, ttl=TTL_SEATABLES))
    def getSetPoint1(self):
        command = "R01"
        reply = self.query(command)
        if reply is not None:
            return self.setPoinStr2value(reply)
        else:
            return float("nan")

    @BasicInstrument.tsdb_append
    @cached(cache=TTLCache(maxsize=1, ttl=TTL_SEATABLES))
    def getSetPoint2(self):
        command = "R02"
        reply = self.query(command)
        if reply is not None:
            return self.setPoinStr2value(reply)
        else:
            return float("nan")


if __name__ == "__main__":
    tc = I800()
    print(tc.getConfig())
