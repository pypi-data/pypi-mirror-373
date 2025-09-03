from ._basic import DAQ
import ue9  # not availabe via pip, download from LabJack website

# https://support.labjack.com/docs/software-driver


class LabJackUE9(DAQ):
    """
    DAQ LabJack UE9 class.

    This is custom modification of the stock ue9 class
    provided by LabJack.
    """

    def __init__(
        self, *args, debug=False, autoOpen=True, ethernet=False, ipAddress=None, **kargs
    ):
        """
        LabJack UE9 can be contacted via TCP, use
        LabJackUE9(ethernet=True, ipAddress="192.168.1.209")
        """
        super().__init__(*args, **kargs)
        self.config["Device model"] = "LabJack UE9"
        self.AnalogInputsNum = 4
        self.AnalogOutputsNum = 2

        self.daq = ue9.UE9(
            debug=debug, autoOpen=autoOpen, ethernet=ethernet, ipAddress=ipAddress
        )

        # For applying the proper calibration to readings.
        c = self.daq.getCalibrationData()

        # by evmik
        # fixing missing slope for gain '0'
        c["AINSlopes"]["0"] = 0.0000775030

    def getAIN(self, chNum):
        """get analog input (AIN) voltage"""
        BipGain = 8
        Resolution = 12
        SettlingTime = 0
        # BipGain = 8 -> bipolar range (-5V, +5V) gain 1
        # UE9 default BipGain = 0 -> signal range (0V, +5V) gain 1
        # other BipGain could be:
        #   0 = Unipolar Gain 1, 1 = Unipolar Gain 2,
        #   2 = Unipolar Gain 4, 3 = Unipolar Gain 8,
        #   8 = Bipolar Gain 1
        return self.daq.getAIN(
            chNum, BipGain=BipGain, Resolution=Resolution, SettlingTime=SettlingTime
        )

    def setDAC(self, chNum, volts):
        """set digital to analog (DAC) output voltage"""
        if (chNum is None) or (volts is None):
            print("setOutputCh needs chNum and volts to be set")
            return 0
        bits = self.daq.voltageToDACBits(volts, dacNumber=chNum)
        # results are completely bogus for DAC settings in UE9
        self.daq.singleIO(IOType=5, Channel=chNum, DAC=bits)
        return volts

    def close(self):
        self.daq.close()


if __name__ == "__main__":
    daq = LabJackUE9()
    print("testing")
    print("------ Header start -------------")
    print(str.join("\n", daq.getHeader()))
    print("------ Header ends  -------------")
