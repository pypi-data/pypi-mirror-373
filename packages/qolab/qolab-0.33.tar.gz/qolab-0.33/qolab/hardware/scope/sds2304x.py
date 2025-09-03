"""
by Rob Behary and Eugeniy Mikhailov 2024/06/17
"""

from .sds1104x import SDS1104X
from qolab.hardware.basic import BasicInstrument
from qolab.hardware.scpi import response2numStr


class SDS2304X(SDS1104X):
    """Siglent SDS2304x scope"""

    # unlike SDS1104X, number of divisions matches what is seen on the screen
    vertDivOnScreen = 8
    horizDivOnScreen = 10

    def __init__(self, resource, *args, **kwds):
        super().__init__(resource, *args, **kwds)
        self.config["Device model"] = "SDS2304X"
        self.resource.read_termination = "\n"
        self.numberOfChannels = 4
        self.maxRequiredPoints = 1000
        # desired number of points per channel, can return twice more

    @BasicInstrument.tsdb_append
    def getTimePerDiv(self):
        qstr = "TDIV?"
        rstr = self.query(qstr)
        # Siglent claims that this model should have same commands as SDS1104X
        # However response is different.
        # For example we got '2.00E-08S' instead 'TDIV 2.00E-08S'
        # expected reply to query: '2.00E-08S'
        prefix, numberString, unit = response2numStr(
            rstr, firstSeparator=None, unit="S"
        )
        return float(numberString)
