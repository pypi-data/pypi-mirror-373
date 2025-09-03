from qolab.hardware.basic import BasicInstrument
from ._basic import PowerSupplySCPI
import time


class KeysightE3612A(PowerSupplySCPI):
    """Keysight E3612A power supply"""

    def __init__(self, resource, *args, **kwds):
        super().__init__(resource, *args, **kwds)
        self.resource.read_termination = "\n"
        self.config["Device model"] = "Keysight E3612A"
        self.numberOfChannels = 3
        self.deviceProperties.update({"OpMode"})
        self.channelProperties = {
            "IsOn",
            "Regulation",
            "Vout",
            "Vlimit",
            "Iout",
            "Ilimit",
            "dV",
            "dI",
        }
        self.deffaultChannelR = 47
        # used if no empirical way to calculate it via Vout/Iout

    def getChandV(self, chNum):
        """Get voltage precision per channel.

        Obtained from data sheet.
        Alternative estimate is by assuming 14 bit precision from the maximum reading.
        """
        if chNum == 1:
            return 0.24e-3
        return 1.5e-3

    def getChandI(self, chNum):
        """Current precision per channel.

        Obtained from data sheet.
        Alternative estimate is by assuming 14 bit precision from the maximum reading.
        """
        if chNum == 1:
            return 0.2e-3
        return 0.160e-3  # see specification for high current > 20mA

    def getOpMode(self):
        """Queries power supply operation mode, returns OFF|PAR|SER|TRAC.

        OFF stands for independent channels
        """
        qstr = "OUTP:PAIR?"
        rstr = self.query(qstr)
        return rstr

    def setOpMode(self, val):
        """Sets power supply operation mode, returns OFF|PAR|SER|TRAC.

        OFF stands for independent channels.
        """
        cmnd = f"OUTP:PAIR {val}"
        self.write(cmnd)

    def setChanOn(self, chNum):
        """Power up channel output"""
        self.write(f"OUTP ON,(@{chNum})")

    def setChanOff(self, chNum):
        """Power down channel output"""
        self.write(f"OUTP OFF,(@{chNum})")

    @BasicInstrument.tsdb_append
    def getChanIsOn(self, chNum):
        """Queries channel output state"""
        qstr = f"OUTP? (@{chNum})"
        rstr = self.query(qstr)
        return bool(float(rstr))

    @BasicInstrument.tsdb_append
    def getChanRegulation(self, chNum):
        """Queries channel output regulation

        0 - The output is off and unregulated
        1 - The output is CC (constant current) operating mode
        2 - The output is CV (constant voltage) operating mode
        3 - The output has hardware failure
        """
        qstr = f"STAT:QUES:INST:ISUM{chNum}:COND?"
        rstr = self.query(qstr)
        return int(rstr)

    @BasicInstrument.tsdb_append
    def getChanVout(self, chNum):
        qstr = f"MEAS:VOLT? (@{chNum})"
        rstr = self.query(qstr)
        return float(rstr)

    @BasicInstrument.tsdb_append
    def getChanVlimit(self, chNum):
        qstr = f"SOUR:VOLT? (@{chNum})"
        rstr = self.query(qstr)
        return float(rstr)

    @BasicInstrument.tsdb_append
    def setChanVlimit(self, chNum, val):
        if val < 0:
            val = 0
        if chNum == 1 and val > 6.180:
            val = 6.180
        if (chNum == 2 or chNum == 3) and val > 25.750:
            val = 25.750
        cmnd = f"SOURCe:VOLT {val},(@{chNum})"
        self.write(cmnd)

    @BasicInstrument.tsdb_append
    def getChanIout(self, chNum):
        qstr = f"MEAS:CURR? (@{chNum})"
        rstr = self.query(qstr)
        return float(rstr)

    def setChanIout_mA(self, chNum, val, **kwds):
        """Set current in mA.

        Calls setChanIout with val converted from mA to A.
        """
        return self.setChanIout(chNum, val / 1000.0, **kwds)

    @BasicInstrument.tsdb_append
    def setChanIout(self, chNum, val, currentHeadRoom=1e-3, dwellTime=0.3):
        """Set current in the channel.

        We will tune Vout to achieve desired Iout.
        Generally setting current limit will maintain current near
        but not exact to desired value.
        Since Vlimit can be set with good precision,
        this function will try tune Vlimit until the Idesired is reached.
        """
        iDesired = val
        # self.setChanIlimit(chNum, val+currentHeadRoom)
        # Here, we assume that hook up is already made,
        # so we can estimate source resistance.
        # So the protocol is the following:
        #  find R -> calculate required Vout for the desired Idesired
        #  -> set Vlimit to reach desired Vout and Iout
        # In general, once we estimate resistance of the load + source,
        # we do not need to anything extra.
        # But there is a problem: for a given Vlimit setting, the actual Vout
        # is slightly off.
        # We will assume that Vlimit = R*Iout + Vo = Vout + Vo,
        # i.e. linear approximation
        for i in range(10):
            iOut = self.getChanIout(chNum)
            if abs(iOut - iDesired) <= self.getChandI(chNum):
                break
            vOut = self.getChanVout(chNum)
            if self.getChanRegulation(chNum) == 2:  # i.e. CV mode
                vLimit = self.getChanVlimit(chNum)
                Vo = vLimit - vOut
            else:
                Vo = 0
            if (iOut == 0) or (
                vOut <= 0.001
            ):  # when vOut set to 0 the numbers are misreported
                R = self.deffaultChannelR  # some default
            else:
                R = vOut / iOut
            vDesired = R * iDesired
            self.setChanVlimit(chNum, vDesired + Vo)
            time.sleep(dwellTime)

    @BasicInstrument.tsdb_append
    def getChanIlimit(self, chNum):
        qstr = f"SOURce:CURR? (@{chNum})"
        rstr = self.query(qstr)
        return float(rstr)

    @BasicInstrument.tsdb_append
    def setChanIlimit(self, chNum, val):
        """Set current limit, seems to be >=0.002 for Ch1 and >=0.001 for Ch2 and Ch3"""
        if chNum == 1 and val < 0.002:
            val = 0.002
        if chNum == 1 and val > 5.150:
            val = 5.150
        if (chNum == 2 or chNum == 3) and val < 0.001:
            val = 0.001
        if (chNum == 2 or chNum == 3) and val > 1.030:
            val = 1.030
        cmnd = f"SOURCe:CURR {val},(@{chNum})"
        self.write(cmnd)


if __name__ == "__main__":
    import pyvisa

    print("testing")
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    instr = rm.open_resource("USB0::10893::4354::MY61001869::0::INSTR")
    ps = KeysightE3612A(instr)
    print("------ Header start -------------")
    print(str.join("\n", ps.getHeader()))
    print("------ Header ends  -------------")
