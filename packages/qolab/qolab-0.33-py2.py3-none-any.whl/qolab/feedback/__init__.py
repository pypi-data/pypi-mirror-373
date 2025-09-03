import time
from qolab.hardware.basic import BasicInstrument


class PID(BasicInstrument):
    """Proportional–integral–derivative controller.

    Calculates feedback based on gains, time, and previous error signal measurements.
    """

    def __init__(self, Gp=0, Gi=0, Gd=0, sign=1, enable=True, *args, **kwds):
        super().__init__(*args, **kwds)
        self.config["Device model"] = "Generic Software PID loop"
        self.config["Device type"] = "PID loop"
        self.config["FnamePrefix"] = "pid"
        self.deviceProperties.update({"Gp", "Gi", "Gd", "Sign", "Enable"})
        self.setGp(Gp)
        self.setGi(Gi)
        self.setGd(Gd)
        self.setSign(sign)
        self.setEnable(enable)

        self.reset()

    def __repr__(self):
        s = ""
        s += f"{self.__class__.__name__}("
        s += f"Gp={self.Gp}"
        s += f", Gi={self.Gi}"
        s += f", Gd={self.Gd}"
        s += f", sign={self.enable}"
        if self.config["DeviceNickname"] is not None:
            s += ", device_nickname='"
            s += f"{self.config['DeviceNickname']}"
            s += "'"
        s += ")"
        return s

    @BasicInstrument.tsdb_append
    def getGp(self):
        return self.Gp

    @BasicInstrument.tsdb_append
    def setGp(self, val):
        self.Gp = val

    @BasicInstrument.tsdb_append
    def getGi(self):
        return self.Gi

    @BasicInstrument.tsdb_append
    def setGi(self, val):
        self.Gi = val

    @BasicInstrument.tsdb_append
    def getGd(self):
        return self.Gd

    @BasicInstrument.tsdb_append
    def setGd(self, val):
        self.Gd = val

    @BasicInstrument.tsdb_append
    def getSign(self):
        return self.sign

    @BasicInstrument.tsdb_append
    def setSign(self, val):
        self.sign = val

    @BasicInstrument.tsdb_append
    def getEnable(self):
        return self.enable

    @BasicInstrument.tsdb_append
    def setEnable(self, val):
        self.enable = val

    def reset(self):
        self.err_1dt_back = 0
        self.err_2dt_back = 0
        self.err_now = 0
        self.last_update = time.time()

    def feedback(self, err):
        # PID feedback
        # see https://en.wikipedia.org/wiki/PID_controller#Pseudocode
        self.err_2dt_back = self.err_1dt_back
        self.err_1dt_back = self.err_now
        self.err_now = err

        tnow = time.time()
        dt = tnow - self.last_update
        self.last_update = tnow
        A0 = self.Gp + self.Gi * dt + self.Gd / dt
        A1 = -self.Gp - 2 * self.Gd / dt
        A2 = self.Gd / dt

        u = A0 * self.err_now + A1 * self.err_1dt_back + A2 * self.err_2dt_back
        u *= self.sign
        if not self.enable:
            return 0
        return u
