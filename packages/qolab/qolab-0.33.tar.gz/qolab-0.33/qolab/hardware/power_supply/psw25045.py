"""
Module: GW INSTEK GPP-250-4.5 power supply unit control
Description: This module provides a class to interface with the GW INSTEK GPP250-4.5 power
             supply unit (PSU) using pyvisa for setting current and voltage on the PSU

Author: Mykhailo Vorobiov
Email: mvorobiov@wm.edu
Date: 2024-10-02
Update: 2024-11-06
"""

from qolab.hardware.power_supply._basic import PowerSupplySCPI
from qolab.hardware.basic import BasicInstrument

import pyvisa
import numpy as np


class PSW25045(PowerSupplySCPI):
    """
    A class for interfacing with GW INSTEK GPP250-4.5
    signle channel power supply unit.
    """

    def __init__(self, resource, *args, **kwds):
        """
        Initialize the PSU class.
        """
        super().__init__(resource, *args, **kwds)
        self.resource = resource

        self.config["Device model"] = "GWInstek PSW 250-4.5"
        self.numberOfChannels = 2
        self.deviceProperties.update({"OpMode"})
        self.resource.read_termination = "\n"

        self.MAX_CURRENT = 4.5  # Amp
        self.MAX_VOLTAGE = 250.0  # Volt
        self.enable_output(False)

    @property
    def idn(self):
        return self.get_idn()

    def get_idn(self):
        """
        Query the identification of the instrument.

        :return: Identifier string if query is successful or None otherwise.
        """
        try:
            return self.query("*IDN?").strip()
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Error retrieving identification: {e}")
            return None

    @BasicInstrument.tsdb_append
    def get_out_current(self):
        """
        Query the current reading of the instrument.

        :return: Current reading in amps as float number and None if error occurs.
        """

        try:
            return float(self.query("MEAS:CURR?"))
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Error querying the current reading: {e}")
            return np.nan()

    @BasicInstrument.tsdb_append
    def get_out_voltage(self):
        """
        Query the voltage reading of the instrument.

        :return: Voltage reading in volts as float number and None if error occurs.
        """

        try:
            return float(self.query("MEAS:VOLT?"))
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Error querying the voltage reading: {e}")
            return np.nan()

    def get_out_power(self):
        """
        Query the power reading of the instrument.

        :return: Power reading in watts as float number and None if error occurs.
        """

        try:
            return float(self.query("MEAS:POWE?"))
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Error querying the power reading: {e}")
            return np.nan()

    def set_current(self, current):
        """
        Set the target current output of the instrument.
        """

        if current <= self.MAX_CURRENT and current >= 0.0:
            try:
                self.write(f"SOUR:CURR {current}")
                print(f"Current is set to {current} V")
            except pyvisa.VisaIOError as e:
                print(f"[ERROR!] Error setting the current target output: {e}")
        else:
            print(
                f"[WARNING] Target current must be between 0 and {self.MAX_CURRENT} Amps."
                f"\n\tThe traget current left unchanged."
            )

    def set_voltage(self, voltage):
        """
        Set the target voltage output of the instrument.
        """
        if voltage <= self.MAX_VOLTAGE and voltage >= 0.0:
            try:
                self.write(f"SOUR:VOLT {voltage}")
                print(f"[INFO] Voltage is set to {voltage} V")
            except pyvisa.VisaIOError as e:
                print(f"[ERROR!] Error setting the voltage target output: {e}")
        else:
            print(
                f"[WARNING] Target voltage must be between 0 and {self.MAX_VOLTAGE} Volts."
                f"\n\tThe traget voltage left unchanged."
            )

    def enable_output(self, output_state=False):
        """
        Set the output state of the instrument ON or OFF.

        :param output_state: Boolean flag. Sets the output ON if 'True' or OFF if 'False'.
        """
        self.output_state = (
            output_state  # This is here to define out state (need some work on it)
        )
        try:
            if self.output_state:
                self.write("OUTP:STAT 1")
                self.output_state = output_state
                print("[INFO] Output is ON")
            else:
                self.write("OUTP:STAT 0")
                self.output_state = not (output_state)
                print("[INFO] Output is OFF")
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Error toggle the output: {e}")
