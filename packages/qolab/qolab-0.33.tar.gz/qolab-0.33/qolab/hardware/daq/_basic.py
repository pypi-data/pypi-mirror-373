"""Basic DAQ to be included into hardware aware classes."""

from qolab.hardware.basic import BasicInstrument


class DAQ(BasicInstrument):
    # Minimal set of methods to be implemented by a RFGenerator
    def __init__(self, *args, **kwds):
        BasicInstrument.__init__(self, *args, **kwds)
        self.config["Device type"] = "DAQ"
        self.config["Device model"] = "Generic DAQ Without Hardware interface"
        self.config["FnamePrefix"] = "daq"
        self.deviceProperties.update({"AnalogInputsNum", "AnalogOutputsNum"})

        # this is device dependent
        self.AnalogInputsNum = 0
        self.AnalogOutputsNum = 0
