from ._basic import LockinSCPI
from qolab.hardware.scpi import SCPI_PROPERTY


class SRS_SR865A(LockinSCPI):
    """SRS SR865A lockin"""

    def __init__(self, resource, *args, **kwds):
        super().__init__(resource, *args, **kwds)
        self.config["Device model"] = "SRS SR865A"
        self.resource.read_termination = "\n"
        self.deviceProperties.update(
            {"TimeBaseMode", "AuxOut1", "AuxOut2", "AuxOut3", "AuxOut4"}
        )

    FreqInt = SCPI_PROPERTY(
        scpi_prfx="FreqInt", ptype=float, doc="Internal LO frequency"
    )
    FreqExt = SCPI_PROPERTY(
        scpi_prfx="FreqExt", ptype=float, doc="External LO frequency", no_setter=True
    )
    Harm = SCPI_PROPERTY(scpi_prfx="Harm", ptype=float, doc="Harmonic of the LO")
    SinAmpl = SCPI_PROPERTY(scpi_prfx="SLVL", ptype=float, doc="Modulation amplitude")
    SinOffset = SCPI_PROPERTY(scpi_prfx="SOFF", ptype=float, doc="Modulation offset")
    EquivalentNoiseBW = SCPI_PROPERTY(
        scpi_prfx="ENBW",
        ptype=float,
        doc="Equivalent Noise BandWidth (it is not 3dB BW, see the manual)",
        no_setter=True,
    )
    TimeBaseMode = SCPI_PROPERTY(
        scpi_prfx="TBMODE",
        ptype=int,
        doc="10 MHz reference mode: 0 - Auto, 1 - Internal",
    )
    RefPhase = SCPI_PROPERTY(scpi_prfx="PHAS", ptype=float, doc="LO/reference phase")

    Sensitivity = SCPI_PROPERTY(
        scpi_prfx="SCAL",
        ptype=int,
        doc="""
    Sensitivity:
        0:   1  V (uA),  6:  10 mV (nA),  ... 27: 1 nV (fA)
        1: 500 mV (nA),  7:   5 mV (nA),
        2: 200 mV (nA),  8:   2 mV (nA),
        3: 100 mV (nA),  9:   1 mV (nA),
        4:  50 mV (nA), 10: 500 uV (pA),
        5:  20 mV (nA), 11: 200 uV (pA),
    """,
    )
    TimeConstan = SCPI_PROPERTY(
        scpi_prfx="OFLT",
        ptype=int,
        doc="""
    Time constant:
        0:   1 uS,    6:   1 mS, ..... , 21: 30 kS
        1:   3 uS,    7:   3 mS,
        2:  10 uS,    8:  10 mS,
        3:  30 uS,    9:  30 mS,
        4: 100 uS,   10: 100 mS,
        5: 300 uS,   11: 300 mS,
    """,
    )
    FilterSlope = SCPI_PROPERTY(
        scpi_prfx="OFSL",
        ptype=int,
        doc="""
    Output Filter slope:
        0:  6dB/Oct
        1: 12dB/Oct
        2: 18dB/Oct
        3: 24dB/Oct
    """,
    )

    AuxOut1 = SCPI_PROPERTY(
        scpi_prfx=["AUXV? 0", "AUXV 0,{}"],
        ptype=float,
        doc="Voltage at Auxilarly output 1",
    )
    AuxOut2 = SCPI_PROPERTY(
        scpi_prfx=["AUXV? 1", "AUXV 1,{}"],
        ptype=float,
        doc="Voltage at Auxilarly output 2",
    )
    AuxOut3 = SCPI_PROPERTY(
        scpi_prfx=["AUXV? 2", "AUXV 2,{}"],
        ptype=float,
        doc="Voltage at Auxilarly output 3",
    )
    AuxOut4 = SCPI_PROPERTY(
        scpi_prfx=["AUXV? 3", "AUXV 3,{}"],
        ptype=float,
        doc="Voltage at Auxilarly output 4",
    )

    AuxIn1 = SCPI_PROPERTY(
        scpi_prfx=["OAUX? 0", ""],
        ptype=float,
        doc="Voltage at Auxilarly input 1",
        no_setter=True,
    )
    AuxIn2 = SCPI_PROPERTY(
        scpi_prfx=["OAUX? 1", ""],
        ptype=float,
        doc="Voltage at Auxilarly input 2",
        no_setter=True,
    )
    AuxIn3 = SCPI_PROPERTY(
        scpi_prfx=["OAUX? 2", ""],
        ptype=float,
        doc="Voltage at Auxilarly input 3",
        no_setter=True,
    )
    AuxIn4 = SCPI_PROPERTY(
        scpi_prfx=["OAUX? 3", ""],
        ptype=float,
        doc="Voltage at Auxilarly input 4",
        no_setter=True,
    )


if __name__ == "__main__":
    import pyvisa

    print("testing")
    rm = pyvisa.ResourceManager()
    print(rm.list_resources())
    instr = rm.open_resource("TCPIP::192.168.0.51::INSTR")
    lockin = SRS_SR865A(instr)
    print("------ Header start -------------")
    print(str.join("\n", lockin.getHeader()))
    print("------ Header ends  -------------")
