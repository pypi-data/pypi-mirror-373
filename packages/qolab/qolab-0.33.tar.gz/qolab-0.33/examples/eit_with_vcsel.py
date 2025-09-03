import logging
import pyvisa
import numpy as np
import platform
import time
from tqdm import tqdm as pbar
import matplotlib.pyplot as plt
from qolab.hardware import BasicInstrument
from qolab.data import TraceSetSameX, Trace
from qolab.hardware.rf_generator import QOL_LMX2487
from qolab.hardware.daq import LabJackUE9
from qolab.hardware.power_supply.keysight_e3612a import KeysightE3612A
import qolab.tsdb as tsdb

# this should be done before justpy is called or log formatter does not work
logging.basicConfig(
    format="%(asctime)s %(levelname)8s %(name)s: %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)


tmplogger = logging.getLogger("qolab.tsdb")
tmplogger.setLevel(logging.INFO)
logger = logging.getLogger("Magnetometer")
logger.setLevel(logging.INFO)


def getConfig(apparatus):
    config = apparatus.config.copy()
    ai = apparatus.instruments
    for n, i in ai.items():
        config[n] = i.getConfig()
    return config


class Apparatus(BasicInstrument):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    def getConfig(self):
        config = self.config.copy()
        ai = self.instruments
        for n, i in ai.items():
            config[n] = i.getConfig()
        return config


class BfieldDriver(KeysightE3612A):
    """need to set power supply"""

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.config["Device type"] = (
            "B field coil driver based on Keysight E3612A power supply"
        )
        self.config["Device model"] = "v0.1"
        self.deviceProperties.update({"B", "Bslope_TperA", "CoilAssignment"})
        """"
        Rough magnetic field calibration of the 3 axes coils in large magnetic shield
        - Ch1: 70mA -> 650 kHz shift for delta m = 2
        - Ch2: 70mA -> 700 kHz shift for delta m = 2
        - Ch2: 70mA -> 659 kHz shift for delta m = 2
        A better calibration obtained on 20220601 see file
          20220601.magnetic_field_callibration/calibration_currentToB.dat
        """
        # B response to current in a given channel
        self._Bslope_TperA = {
            1: 0.0006574710928926532,
            2: 0.0007064314754023079,
            3: 0.0006635058865577695,
        }
        # assuming that Ch1 controls Bz, Ch2 -> By, Ch3 -> Bx
        self._coil_assignment = {"chX": 3, "chY": 2, "chZ": 1}

    def getBslope_TperA(self):
        return self._Bslope_TperA

    def getCoilAssignment(self):
        return self._coil_assignment

    def getB(self):
        Bslope_TperA = self.getBslope_TperA()
        coil_assignment = self.getCoilAssignment()
        chX = coil_assignment["chX"]
        chY = coil_assignment["chY"]
        chZ = coil_assignment["chZ"]

        Ix = self.getChanIout(chX)
        Iy = self.getChanIout(chY)
        Iz = self.getChanIout(chZ)
        Bx = Ix * Bslope_TperA[chX]
        By = Iy * Bslope_TperA[chY]
        Bz = Iz * Bslope_TperA[chZ]
        Bmag = float(np.sqrt(Bx * Bx + By * By + Bz * Bz))
        theta = float(np.arccos(Bz / Bmag))
        phi = float(np.arctan2(By, Bx))
        theta_degree = float(theta / np.pi * 180)
        phi_degree = float(phi / np.pi * 180)
        return {
            "Bmag": Bmag,
            "theta": theta,
            "phi": phi,
            "theta_degree": theta_degree,
            "phi_degree": phi_degree,
            "Bx": float(Bx),
            "By": float(By),
            "Bz": float(Bz),
        }

    def setB(self, Bmag=50e-6, theta=0, phi=0):
        """Sets B field currents based on B (in T) and angles theta, and phi"""
        self._Bmag = Bmag
        self._theta = theta
        self._phi = phi

        Bx = Bmag * np.sin(theta) * np.cos(phi)
        By = Bmag * np.sin(theta) * np.sin(phi)
        Bz = Bmag * np.cos(theta)

        Bslope_TperA = self.getBslope_TperA()
        coil_assignment = self.getCoilAssignment()
        chX = coil_assignment["chX"]
        chY = coil_assignment["chY"]
        chZ = coil_assignment["chZ"]

        Ix = Bx / Bslope_TperA[chX]
        Iy = By / Bslope_TperA[chY]
        Iz = Bz / Bslope_TperA[chZ]

        logger.info(f"Setting {Bmag=}, {theta=} {phi=} in radians")
        logger.info(f"Setting {chX=} to {Ix}")
        logger.info(f"Setting {chY=} to {Iy}")
        logger.info(f"Setting {chZ=} to {Iz}")
        self.setChanIout(chX, Ix)
        self.setChanIout(chY, Iy)
        self.setChanIout(chZ, Iz)
        return Ix, Iy, Iz

    def setBinDegrees(self, Bmag=50e-6, theta=0, phi=0):
        logger.info(f"Setting {Bmag=},  {theta=} {phi=} in degrees")
        return self.setB(Bmag=Bmag, theta=theta / 180 * np.pi, phi=phi / 180 * np.pi)


# TSDB logger setting
tsdb_client = tsdb.Client(
    "influx", "http://lumus.physics.wm.edu:8428", database="qolab"
)
tsdb_ingester = tsdb.Ingester(tsdb_client, batch=11, measurement_prefix="VAMPIRE.VCSEL")

# creating Apparatus with all instruments to be logged
app_nickname = "magnetometer"
apparatus = Apparatus(
    tsdb_ingester=tsdb_ingester,
    device_nickname=app_nickname,
)
apparatus.config["Device type"] = "QOL VAMPIRE VCSEL magnetometer"
apparatus.config["Device model"] = "v0.1"
apparatus.config["FnamePrefix"] = "magnetometer_eit"
# apparatus.config['SavePath'] = '/mnt/qol_grp_data/data.VAMPIRE.VCSEL'
apparatus.config["SavePath"] = "./data"


logger.info("Accessing hardware")
rm = pyvisa.ResourceManager()
instr = rm.open_resource("USB0::10893::4354::MY61001869::0::INSTR")
Bfield = BfieldDriver(
    instr,
    device_nickname=".".join([app_nickname, "b_field_driver"]),
    tsdb_ingester=tsdb_ingester,
)
ps = Bfield  # alias
# set safety current limit
ps.setChanIlimit(1, 0.1)  # max current in Amps
ps.setChanIlimit(2, 0.1)  # max current in Amps
ps.setChanIlimit(3, 0.1)  # max current in Amps

if platform.system() == "Linux":
    rfgen_port = "/dev/ttyUSB0"
else:
    rfgen_port = "COM4"
rfgen = QOL_LMX2487(
    port=rfgen_port,
    speed=115200,
    timeout=1,
    device_nickname=".".join([app_nickname, "rfgen"]),
    tsdb_ingester=tsdb_ingester,
)


daq = LabJackUE9(
    device_nickname=".".join([app_nickname, "daq"]), tsdb_ingester=tsdb_ingester
)

logger.info("Adding instruments to apparatus")
apparatus.instruments = {}
ai = apparatus.instruments
ai["rfgen"] = rfgen
ai["daq"] = daq
ai["b_field_driver"] = Bfield


logger.info("Setting magnetic field coils currents")
# ps.setChanIout_mA(1, 70)
# ps.setChanIout_mA(2, 0)
# ps.setChanIout_mA(3, 0)
logger.info("Done setting magnetic field coils currents")


def eitSweep(central_frequency, frequency_span, Np, Nsweeps=1):
    frList = np.linspace(
        central_frequency - frequency_span / 2,
        central_frequency + frequency_span / 2,
        Np,
    )
    trFreq = Trace("Frequency")
    trFreq.config["unit"] = "Hz"
    trTransmission = Trace("Transmission")
    trTransmission.config["unit"] = "Arb. Unit"
    trLockin = Trace("Lockin")
    trLockin.config["unit"] = "V"

    trEIT = TraceSetSameX("EIT")

    for sw in pbar(range(1, Nsweeps + 1), desc="Sweep"):
        for fr in pbar(frList, desc="Freq Scan"):
            rfgen.setFreqFixed(float(fr))
            time.sleep(dwellTime)
            transmission = daq.getAIN(0)
            lockin = daq.getAIN(1)

            trFreq.addPoint(fr)
            trTransmission.addPoint(transmission)
            trLockin.addPoint(lockin)

    # trFreq.values = trFreq.values - central_frequency
    trEIT.addTraceX(trFreq)
    trEIT.addTrace(trTransmission)
    trEIT.addTrace(trLockin)

    trEIT.config["tags"]["apparatus"] = apparatus.getConfig()

    return trEIT


def getCurrentCalibrationData(ch=1):
    curList = [20, 30, 40, 50, 60, 70, 80, 90, 100, 110]
    ps.setChanIout_mA(1, 0)
    ps.setChanIout_mA(2, 0)
    ps.setChanIout_mA(3, 0)
    for current in curList:
        logger.info(f"Preparing data for {current=} in {ch=} ready")
        ps.setChanIout_mA(ch, current)
        trEIT = eitSweep(central_frequency, frequency_span, Np, Nsweeps=Nsweeps)
        trEIT.plot()
        fn = apparatus.getNextDataFile()
        logger.info(f"Data ready for {current=} in {ch=}")
        logger.info(f"Data saved to {fn=}")
        trEIT.save(fn)


def calibrateCoilsCurrent():
    # Np = 1000
    # Nsweeps = 5
    getCurrentCalibrationData(ch=1)
    getCurrentCalibrationData(ch=2)
    getCurrentCalibrationData(ch=3)


def setBandTakeTrace(
    Bmag=50e-6,
    theta=0,
    phi=0,
    central_frequency=6.83468e9,
    frequency_span=2500e3,
    Np=100,
    Nsweeps=1,
):
    """theta and phi assumed to be in degrees"""
    Bfield.setBinDegrees(Bmag=Bmag, theta=theta, phi=phi)
    trEIT = eitSweep(central_frequency, frequency_span, Np, Nsweeps=Nsweeps)
    return trEIT


def rotateBandGetEITtrace():
    Np = 500
    Nsweeps = 5
    Bmag = 50e-6  # earth magnetic field in Tesla (0.5 G)
    phiStep = 10
    thetaStep = 10
    phiSet = range(0, 90 + phiStep, phiStep)
    thetaSet = range(0, 90 + thetaStep, thetaStep)
    for phi in phiSet:
        for theta in thetaSet:
            trEIT = setBandTakeTrace(
                Bmag=Bmag,
                theta=theta,
                phi=phi,
                central_frequency=central_frequency,
                frequency_span=frequency_span,
                Np=Np,
                Nsweeps=Nsweeps,
            )
            plt.clf()
            trEIT.plot()
            plt.draw()
            plt.pause(0.1)
            fn = apparatus.getNextDataFile()
            logger.info(f"Data ready for {Bmag=} in {theta=} {phi=}")
            logger.info(f"Data saved to {fn=}")
            trEIT.save(fn)


central_frequency = 6.83468e9
frequency_span = 2500e3

dwellTime = 0.1
Np = 100
Nsweeps = 1


tsdb_ingester.commit()
