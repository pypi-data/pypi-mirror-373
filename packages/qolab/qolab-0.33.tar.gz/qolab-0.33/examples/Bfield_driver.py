import logging
import pyvisa
import numpy as np
from qolab.hardware.power_supply.keysight_e3612a import KeysightE3612A
import qolab.tsdb as tsdb

# this should be done before justpy is called or log formatter does not work
logging.basicConfig(
    format="%(asctime)s %(levelname)8s %(name)s: %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)

tmplogger = logging.getLogger("qolab.tsdb")
tmplogger.setLevel(logging.INFO)
logger = logging.getLogger("BfieldDriver")
logger.setLevel(logging.INFO)


class BfieldDriver(KeysightE3612A):
    """need to set power supply"""

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.config["Device type"] = (
            "B field coil driver based on Keysight E3612A power supply"
        )
        self.config["Device model"] = "v0.1"
        self.deviceProperties = self.deviceProperties.union(
            {"B", "Bslope_TperA", "CoilAssignment"}
        )
        """"
        Rough magnetic field calibration of the 3 axes coils in large magnetic shield
        - Ch1: 70mA -> 650 kHz shift for delta m = 2
        - Ch2: 70mA -> 700 kHz shift for delta m = 2
        - Ch2: 70mA -> 659 kHz shift for delta m = 2
        A better calibration obtained on 20220601 see file
          20220601.magnetic_field_callibration/calibration_currentToB.dat
        """
        # B response to current in a given channel
        # Olivia's Calibration with flux gate magnetometer used from 2023/04/28
        #  +/-     0.0000007
        self._Bslope_TperA = {1: 0.00065859269, 2: 0.00070732580, 3: 0.00066754994}
        """
        # Irina's Calibration used prior 2023/04/27
        self._Bslope_TperA = {
                1: 0.0006571429,
                2: 0.0007085714,
                3: 0.0006675714
                }
        # Eugeniy's Calibration
        self._Bslope_TperA = {
                1: 0.0006574710928926532,
                2: 0.0007064314754023079,
                3: 0.0006635058865577695
                }
        """
        # assuming that Ch1 controls Bz, Ch2 -> Bx, Ch3 -> By
        self._coil_assignment = {"chX": 2, "chY": 3, "chZ": 1}

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
tsdb_client = tsdb.Client("influx", "http://qo.physics.wm.edu:8428", database="qolab")
tsdb_ingester = tsdb.Ingester(tsdb_client, batch=11, measurement_prefix="VAMPIRE.VCSEL")

logger.info("Accessing hardware")
rm = pyvisa.ResourceManager()
instr = rm.open_resource("USB0::10893::4354::MY61001869::0::INSTR")
app_nickname = "BfieldDriver"
Bfield = BfieldDriver(
    instr,
    device_nickname=".".join([app_nickname, "b_field_driver"]),
    tsdb_ingester=None,
)


print("Use me as : Bfield.setBinDegrees(theta=Angle, phi=Angle)")
