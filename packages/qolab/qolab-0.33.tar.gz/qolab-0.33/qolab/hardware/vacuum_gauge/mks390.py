"""
Module: MKS Granville-Phillips 390 Micro-Ion Gauge Control
Description: This module provides a class to interface with the 
             MKS Granville-Phillips 390 Micro-Ion Gauge
             using pyvisa.

Author: Mykhailo Vorobiov
Email: mvorobiov@wm.edu
Date Created: 2024-10-22
Date Updated: 2024-11-05
"""

from qolab.hardware.scpi import SCPIinstr
import pyvisa
import numpy as np
import time


class MKS390(SCPIinstr):
    """
    A class for interfacing with the MKS Granville-Phillips 390 Micro-Ion Gauge
    for vacuum measurements between 1e-11 and 1e+3 Torr.
    """

    def __init__(self, resource, gauge_id="#02", *args, **kwds):
        """
        Initialize the vacuum gaguge class
        """
        super().__init__(resource, *args, **kwds)
        self.resource = resource

        # self.config["Device model"] = "MKS 390"
        self.resource.baud_rate = 19200
        self.resource.timeout = 5000
        self.resource.read_termination = "\r"
        self.resource.write_termination = "\r"

        self.write = self.resource.write
        self.read = self.resource.read
        self.read_raw = self.resource.read_raw

        self.ignition_status = False
        self.id = gauge_id

        # self._read_ignition_status()

    def enable_ignition(self, ig_status=False):
        self._read_ignition_status()
        if not (self.ignition_status == ig_status):
            try:
                # Sending a command
                command = self.id + "IG 0"
                self.write(command)
                self.ignition_status = ig_status
                print(
                    f"[INFO] Vacuum gauge ignition status changed to: {self.ignition_status}"
                )
            except pyvisa.VisaIOError as e:
                print(f"[ERROR!] Failed to change vacuum gauge ignition status.\n\t{e}")
        else:
            print(
                f"[WARNING] No change to vacuum gauge ignition status: {self.ignition_status}"
            )

    def get_ignition_status(self):
        self._read_ignition_status()
        return self.ignition_status

    def _read_ignition_status(self):
        try:
            # Sending a command
            command = self.id + "IGS"
            self.write(command)
            time.sleep(0.01)
            self.ignition_status = bool(self.read_raw(8).strip().split()[1])
            return self.ignition_status
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Failed to read vacuum gauge ignition status.\n\t{e}")

    # @BasicInstrument.tsdb_append # The function does not work with the decorator (need to work on it later)
    def get_pressure(self):
        try:
            # Sending a command
            command = self.id + "RD"
            self.write(command)
            # Waiting and reading the response
            time.sleep(0.01)
            response = float(self.read_raw(14).strip().split()[1])
            return response
        except pyvisa.VisaIOError as e:
            print(f"[ERROR!] Failed to get vacuum gauge reading.\n\t{e}")
            return np.nan()


'''    
    def close(self):
        """
        Close the connection to the vacuum gauge.
        """
        if self.gauge:
            try:
                self.gauge.close()
                self.logger.info("Connection to the vacuum gaguge closed.")
            except pyvisa.VisaIOError as e:
                self.logger.error(f"Error closing connection to the vacuum gauge: {e}")
'''
# Example usage
if __name__ == "__main__":
    import pyvisa

    rm = pyvisa.ResourceManager()

    gauge = MKS390(rm, "visa://192.168.194.15/ASRL13::INSTR", gauge_id="#02")
    pressure = gauge.get_reading()
    gauge.close()
    print(pressure)
