"""
Module: GW INSTEK GPP-250-4.5 power supply unit control
Description: This module provides a class to interface with the GW INSTEK GPP250-4.5 power
             supply unit (PSU) using pyvisa for setting current and voltage on the PSU

Author: Mykhailo Vorobiov
Email: mvorobiov@wm.edu
Date: 2024-11-05
Update: 2024-11-05
"""

from qolab.hardware.power_supply._basic import PowerSupplySCPI
import pyvisa


class GPP3610H(PowerSupplySCPI):
    """
    A class for interfacing with GW INSTEK GPP-3610H
    signle channel power supply unit.
    """

    def __init__(self, resource, *args, **kwds):
        """
        Initialize the PSU class.
        """
        super().__init__(resource, *args, **kwds)
        self.resource = resource

        self.config["Device model"] = "GWInstek GPP-3610H"
        self.numberOfChannels = 2
        self.deviceProperties.update({"OpMode"})
        self.resource.read_termination = "\n"

        self.resource.timeout = 1000

        self.MAX_CURRENT = 10.0  # Amp
        self.MAX_VOLTAGE = 36.0  # Volt

    @property
    def idn(self):
        return self.get_idn()

    def get_idn(self):
        """
        Query the identification of the instrument.

        :return: Identifier string if query is successful or None otherwise.
        """
        try:
            self.write("*IDN?")
            response = self.read_bytes(count=39).decode().strip()
            return response
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Error retrieving identification: {e}")

    def get_out_current(self):
        """
        Query the current reading of the instrument.

        :return: Current reading in amps as float number and None if error occurs.
        """
        try:
            self.write("IOUT1?")
            response = float(self.read_bytes(count=8).decode()[:-2])
            return response
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Error querying the current reading: {e}")

    def get_out_voltage(self):
        """
        Query the voltage reading of the instrument.

        :return: Voltage reading in volts as float number and None if error occurs.
        """

        try:
            self.write("VOUT1?")
            response = float(self.read_bytes(count=8).decode()[:-2])
            return response
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Error querying the voltage reading: {e}")

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
