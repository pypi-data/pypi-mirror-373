"""
Module: HP 3457A Digital Multimeter Control
Description: This module provides a class to interface with a digital multimeter (DMM)
             using pyvisa for performing measurements such as voltage, current,
             and resistance.

Author: Mykhailo Vorobiov
Email: mvorobiov@wm.edu
Date: 2024-10-02
Updated: 2024-11-05
"""

from qolab.hardware.basic import BasicInstrument
from ._basic import Multimeter

import pyvisa
import numpy as np


class HP3457A(Multimeter):
    """
    A class to interface with HP 3457A Digital Multimeter (DMM) via pyvisa.

    This class allows you to measure DC voltage, AC voltage, DC current, AC current,
    and resistance from a DMM using pyvisa communication.
    """

    # List of data return formats
    FORMATS = ["ASCII", "SINT", "DINT", "SREAL", "DREAL"]

    BEEPER_STATUS = ["ON", "OFF", "ONCE"]

    # List of functions
    FUNCTIONS = [
        "DCV",
        "ACV",
        "ACDCV",  # (This is here for future work)
        "OHM",  # (This is here for future work)
        "OHMF",  # (This is here for future work)
        "DCI",
        "ACI",
        "ACDCI",  # (This is here for future work)
        "FREQ",  # (This is here for future work)
        "PER",  # (This is here for future work)
    ]

    # Allowed number of power line cycles (defines A/D integration time)
    NPLC = [0.0005, 0.005, 0.1, 1, 10, 100]

    # DC Volts Spec (This is here for future work)
    DCV_RES = {
        "30mv": {"6.5": 10e-9, "5.5": 100e-9, "4.5": 1e-6, "3.5": 10e-6},
        "300mv": {"6.5": 100e-9, "5.5": 1e-6, "4.5": 10e-6, "3.5": 100e-6},
        "3v": {"6.5": 1e-6, "5.5": 10e-6, "4.5": 100e-6, "3.5": 1e-3},
        "30v": {"6.5": 10e-6, "5.5": 100e-6, "4.5": 1e-3, "3.5": 10e-3},
        "300v": {"6.5": 100e-6, "5.5": 1e-3, "4.5": 10e-3, "3.5": 100e-3},
    }

    DCV_ACC = {
        "30mv": {
            "100": {"acc": 0.0045, "counts": 365},
            "10": {"acc": 0.0045, "counts": 385},
            "1": {"acc": 0.0045, "counts": 500},
            ".1": {"acc": 0.0045, "counts": 70},
            ".005": {"acc": 0.0045, "counts": 19},
            ".0005": {"acc": 0.0045, "counts": 6},
        },
        "300mv": {
            "100": {"acc": 0.0035, "counts": 39},
            "10": {"acc": 0.0035, "counts": 40},
            "1": {"acc": 0.0035, "counts": 50},
            ".1": {"acc": 0.0035, "counts": 9},
            ".005": {"acc": 0.0035, "counts": 4},
            ".0005": {"acc": 0.0035, "counts": 4},
        },
        "3v": {
            "100": {"acc": 0.0025, "counts": 6},
            "10": {"acc": 0.0025, "counts": 7},
            "1": {"acc": 0.0025, "counts": 7},
            ".1": {"acc": 0.0025, "counts": 4},
            ".005": {"acc": 0.0025, "counts": 4},
            ".0005": {"acc": 0.0025, "counts": 4},
        },
        "30v": {
            "100": {"acc": 0.0040, "counts": 19},
            "10": {"acc": 0.0040, "counts": 20},
            "1": {"acc": 0.0040, "counts": 30},
            ".1": {"acc": 0.0040, "counts": 7},
            ".005": {"acc": 0.0040, "counts": 4},
            ".0005": {"acc": 0.0040, "counts": 4},
        },
        "300v": {
            "100": {"acc": 0.0055, "counts": 6},
            "10": {"acc": 0.0055, "counts": 7},
            "1": {"acc": 0.0055, "counts": 7},
            ".1": {"acc": 0.0055, "counts": 4},
            ".005": {"acc": 0.0055, "counts": 4},
            ".0005": {"acc": 0.0055, "counts": 4},
        },
    }

    # DC Current Spec (This is here for future work)
    DCI_RES = {
        "300ua": {"6.5": 100e-12, "5.5": 1e-9, "4.5": 10e-9, "3.5": 100e-9},
        "3ma": {"6.5": 1e-9, "5.5": 10e-9, "4.5": 100e-9, "3.5": 1e-6},
        "30ma": {"6.5": 10e-9, "5.5": 100e-9, "4.5": 1e-6, "3.5": 10e-6},
        "300ma": {"6.5": 100e-9, "5.5": 1e-6, "4.5": 10e-6, "3.5": 100e-6},
        "1a": {"6.5": 1e-6, "5.5": 10e-6, "4.5": 100e-6, "3.5": 1e-3},
    }
    # (This is here for future work)
    DCI_ACC = {
        "300ua": {
            "100": {"acc": 0.04, "counts": 104},
            "10": {"acc": 0.04, "counts": 104},
            "1": {"acc": 0.04, "counts": 115},
            ".1": {"acc": 0.04, "counts": 14},
            ".005": {"acc": 0.04, "counts": 5},
            ".0005": {"acc": 0.04, "counts": 4},
        },
        "3ma": {
            "100": {"acc": 0.04, "counts": 104},
            "10": {"acc": 0.04, "counts": 104},
            "1": {"acc": 0.04, "counts": 115},
            ".1": {"acc": 0.04, "counts": 14},
            ".005": {"acc": 0.04, "counts": 5},
            ".0005": {"acc": 0.04, "counts": 4},
        },
        "30ma": {
            "100": {"acc": 0.04, "counts": 104},
            "10": {"acc": 0.04, "counts": 104},
            "1": {"acc": 0.04, "counts": 115},
            ".1": {"acc": 0.04, "counts": 14},
            ".005": {"acc": 0.04, "counts": 5},
            ".0005": {"acc": 0.04, "counts": 4},
        },
        "300ma": {
            "100": {"acc": 0.08, "counts": 204},
            "10": {"acc": 0.08, "counts": 204},
            "1": {"acc": 0.08, "counts": 215},
            ".1": {"acc": 0.08, "counts": 24},
            ".005": {"acc": 0.08, "counts": 6},
            ".0005": {"acc": 0.08, "counts": 4},
        },
        "1a": {
            "100": {"acc": 0.08, "counts": 604},
            "10": {"acc": 0.08, "counts": 604},
            "1": {"acc": 0.08, "counts": 615},
            ".1": {"acc": 0.08, "counts": 64},
            ".005": {"acc": 0.08, "counts": 10},
            ".0005": {"acc": 0.08, "counts": 5},
        },
    }

    def __init__(self, resource, *args, **kwds):
        """
        Initialize the Digital Multimeter class and establish a connection.

        :param resource_name: VISA resource name for the multimeter.
        :param alias: Alias for logging.
        :param log_level: Logging level (default: INFO).
        """
        super().__init__(*args, **kwds)
        self.resource = resource
        self.config["Device model"] = "HP 3457A"
        self.resource.timeout = 5000
        self.resource.read_termination = "\r\n"
        self.resource.write_termination = "\r\n"

        self.read = self.resource.read
        self.write = self.resource.write
        self.read_bytes = self.resource.read_bytes

        self.switchTime = 0.5  # switch time in seconds for Function/Measurement change
        self.deviceProperties.update({"Function"})
        self.set_function("DCV")

    def get_idn(self):
        """
        Query the identification of the digital multimeter: manufacturer, model, serial number, and firmware version.

        :return: Identifier string if query is successful, or None otherwise.
        """
        try:
            self.write("ID?")
            return self.read_bytes(9).decode().strip()
        except pyvisa.VisaIOError as e:
            print(
                f"[ERROR!] Error retrieving identification of the digital multimeter: {e}"
            )
            return None

    def _check_format(self, format):
        if format in self.FORMATS:
            return True
        else:
            return False

    def set_format(self, format="ASCII"):
        if self._check_format(format):
            try:
                self.write(f"OFORMAT {format}")
                print(f"[INFO] Format  has been set to {format}")
            except pyvisa.VisaIOError as e:
                print(f"[ERROR!] Couldn't set reading format to {format}: {e}")
        else:
            print(
                f"[WARNING] Entered format is not allowed. Allowed formats: {self.FORMATS}"
            )

    @BasicInstrument.tsdb_append
    def get_reading(self):
        try:
            self.write("TARM AUTO")
            return float(self.read_bytes(16).decode().strip())
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Error failed to get reading: {e}")
            return np.nan()

    def set_beeper_status(self, status="OFF"):
        if status in self.BEEPER_STATUS:
            try:
                self.write(f"BEEP {status}")
                print(f"[INFO] Beeper is set to {status}")
            except pyvisa.VisaIOError as e:
                print(f"[ERROR!] Error setting beeper status: {e}")
        else:
            print(
                f"[WARNING!] The passed beeper status is not allowed."
                f"Choose from {self.BEEPER_STATUS}"
            )

    def set_function(self, function="DCV"):
        """
        Set the measurement function of the multimeter.

        :param function: Measurement function .
        """
        if function in self.FUNCTIONS:
            try:
                self.write(f"FUNC {function}")
                print(f"[INFO] Measurement function set to {function}")
            except pyvisa.VisaIOError as e:
                print(f"[ERROR!] Error setting measurement function: {e}")
        else:
            print(
                f"[WARNING!] Invalid measurement function '{function}'. "
                f"Valid functions are: {', '.join(self.FUNCTIONS)}"
            )

    @BasicInstrument.tsdb_append
    def get_temperature(self):
        try:
            self.write("TEMP?")
            temp = float(self.read(16).decode().strip())
            print(f"[INFO] DMM's internal temperature is: {temp}")
            return temp
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Error retrieving DMM's internal temperature: {e}")

    def get_memory_count(self):
        """
        Returns the total number of stored readings.
        """
        try:
            self.write("MCOUNT?")
            return float(self.read_bytes(16).decode().strip())
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Error failed to get count of reading in memory: {e}")
            return np.nan()

    def enable_keyboard(self, status=True):
        if status:
            try:
                self.write("LOCK ON")
                print("[INFO] DMM's keyboard is unlocked.")
            except pyvisa.VisaIOError as e:
                print(f"[ERROR!] Error unlocking the DMM's keyboard: {e}")
        else:
            try:
                self.write("LOCK OFF")
                print("[INFO] DMM's keyboard is locked.")
            except pyvisa.VisaIOError as e:
                print(f"[ERROR!] Error locking the DMM's keyboard: {e}")

    def set_nplc(self, nplc=10):
        if nplc in self.NPLC:
            try:
                self.write(f"FUNC {nplc}")
                print(f"[INFO] NPLC is set to {nplc}")
            except pyvisa.VisaIOError as e:
                print(f"[ERROR!] Error setting number of power line cycles (NPLC): {e}")
        else:
            print(
                f"[WARNING!] Invalid NPLC '{nplc}'. "
                f"Valid NPLC values are: {', '.join(str(self.NPLC))}"
            )

    # -----------------------------------------------------------
    # Methods to comply with other DMM QOLab module drivers
    # -----------------------------------------------------------
    @BasicInstrument.tsdb_append
    def getVdc(self):
        self.set_function("DCV")
        return self.get_reading()

    @BasicInstrument.tsdb_append
    def getVac(self):
        self.set_function("ACV")
        return self.get_reading()

    @BasicInstrument.tsdb_append
    def getAdc(self):
        self.set_function("DCI")
        return self.get_reading()

    @BasicInstrument.tsdb_append
    def getAac(self):
        self.set_function("ACI")
        return self.get_reading()


# Example usage
if __name__ == "__main__":

    rm = pyvisa.ResourceManager()
    instrument = rm.open_resource("visa://192.168.194.15/GPIB1::22::INSTR")
    dmm = HP3457A(instrument)
    dmm.set_format("ASCII")
    dmm.set_beeper_status("ONCE")
    dmm.set_function("DCI")
    print(dmm.get_reading())
    dmm.close()
