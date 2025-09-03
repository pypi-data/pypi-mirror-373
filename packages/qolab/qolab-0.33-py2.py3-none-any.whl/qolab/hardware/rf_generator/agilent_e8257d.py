from qolab.hardware.basic import BasicInstrument
from ._basic import RFGeneratorSCPI


class AgilentE8257D(RFGeneratorSCPI):
    """Agilent E8257D RF generator.

    Note: Fixed frequency and Center frequency (of sweep)
    are different in this model.
    """

    def __init__(self, resource, *args, **kwds):
        super().__init__(resource, *args, **kwds)
        self.resource.read_termination = "\n"
        self.config["Device model"] = "Agilent E8257D"
        self.deviceProperties.update(
            {
                "RFPowerState",
                "RFAmplitude",
                "ModulationState",
                "FM1State",
                "FM1Source",
                "FM1ModulationDepth",
                "FM2State",
                "FM2Source",
                "FM2ModulationDepth",
                "FrequencyMode",  # sweep or continious
                "SweepCentralFreq",
                "SweepSpan",
            }
        )

    @BasicInstrument.tsdb_append
    def getFreqFixed(self):
        qstr = ":FREQuency:Fixed?"
        rstr = self.query(qstr)
        return float(rstr)

    @BasicInstrument.tsdb_append
    def setFreqFixed(self, freq):
        cstr = f":FREQuency:FIXED {freq}Hz"
        self.write(cstr)

    @BasicInstrument.tsdb_append
    def getSweepCentralFreq(self):
        qstr = ":FREQuency:CENTer?"
        rstr = self.query(qstr)
        return float(rstr)

    @BasicInstrument.tsdb_append
    def setSweepCentralFreq(self, cfreq):
        cstr = f":FREQuency:CENTer {cfreq}Hz"
        self.write(cstr)

    @BasicInstrument.tsdb_append
    def getSweepSpan(self):
        qstr = ":FREQuency:SPAN?"
        rstr = self.query(qstr)
        return float(rstr)

    @BasicInstrument.tsdb_append
    def setSweepSpan(self, span):
        cstr = f":FREQuency:SPAN {span}Hz"
        self.write(cstr)

    @BasicInstrument.tsdb_append
    def setSweep(self, cfreq=None, span=None):
        if cfreq is not None:
            self.setSweepCentralFreq(cfreq)
        if cfreq is not None:
            self.setSweepSpan(span)

    @BasicInstrument.tsdb_append
    def getModulationState(self):
        return int(self.query(":MODulation:STATe?"))

    @BasicInstrument.tsdb_append
    def setModulationState(self, val):
        self.write(f":MODulation:STATe {val}")

    @BasicInstrument.tsdb_append
    def getRFPowerState(self):
        return int(self.query(":OUTPut:STATe?"))

    @BasicInstrument.tsdb_append
    def setRFPowerState(self, val):
        self.write(f":OUTPut:STATe {val}")

    @BasicInstrument.tsdb_append
    def getRFAmplitude(self):
        return float(self.query(":POWer:AMPLitude?"))

    @BasicInstrument.tsdb_append
    def setRFAmplitude(self, val):
        self.write(f":POWer:AMPLitude {val}")

    @BasicInstrument.tsdb_append
    def getFM1ModulationDepth(self):
        return float(self.query(":FM1:Deviation?"))

    @BasicInstrument.tsdb_append
    def setFM1ModulationDepth(self, val):
        self.write(f":FM1:Deviation {val}")

    @BasicInstrument.tsdb_append
    def getFM2ModulationDepth(self):
        return float(self.query(":FM2:Deviation?"))

    @BasicInstrument.tsdb_append
    def setFM2ModulationDepth(self, val):
        self.write(f":FM2:Deviation {val}")

    @BasicInstrument.tsdb_append
    def getFM1Source(self):
        return str(self.query(":FM1:Source?"))

    @BasicInstrument.tsdb_append
    def setFM1Source(self, val):
        self.write(f":FM1:Source {val}")

    @BasicInstrument.tsdb_append
    def getFM2Source(self):
        return str(self.query(":FM2:Source?"))

    @BasicInstrument.tsdb_append
    def setFM2Source(self, val):
        self.write(f":FM2:Source {val}")

    @BasicInstrument.tsdb_append
    def getFM1State(self):
        return int(self.query(":FM1:State?"))

    @BasicInstrument.tsdb_append
    def setFM1State(self, val):
        self.write(f":FM1:State {val}")

    @BasicInstrument.tsdb_append
    def getFM2State(self):
        return int(self.query(":FM2:State?"))

    @BasicInstrument.tsdb_append
    def setFM2State(self, val):
        self.write(f":FM2:State {val}")

    @BasicInstrument.tsdb_append
    def getFrequencyMode(self):
        return str(self.query(":Frequency:Mode?"))

    @BasicInstrument.tsdb_append
    def setFrequencyMode(self, val):
        self.write(f":Frequency:Mode {val}")

    @BasicInstrument.tsdb_append
    def startFrequencySweep(self):
        self.setFrequencyMode("Sweep")

    def stopFrequencySweep(self):
        self.setFrequencyMode("FIXED")


if __name__ == "__main__":
    import pyvisa

    print("testing")
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    instr = rm.open_resource("TCPIP::192.168.0.114::INSTR")
    rfgen = AgilentE8257D(instr)
    print("------ Header start -------------")
    print(str.join("\n", rfgen.getHeader()))
    print("------ Header ends  -------------")
