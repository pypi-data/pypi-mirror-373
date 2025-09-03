import logging
import pyvisa
import numpy as np
import qolab.tsdb as tsdb
import time
from qolab.hardware import BasicInstrument
from qolab.hardware.scope import SDS1104X
from qolab.hardware.rf_generator import AgilentE8257D
from qolab.hardware.lockin import SRS_SR865A
from qolab.hardware.i_server import I800

# this should be done before justpy is called or log formatter does not work
logging.basicConfig(
    format="%(asctime)s %(levelname)8s %(name)s: %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)

tmplogger = logging.getLogger("qolab.gui.web")
tmplogger.setLevel(logging.INFO)
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
        self.setLockinSlope(0)

    @BasicInstrument.tsdb_append
    def getBCurrent(self):
        scope = self.instruments["scope.monitor"]
        ch = scope.getTrace(2, decimate=False)
        bCurrent = np.mean(ch.y.values)
        # mV -> mA
        return bCurrent

    def getErrAndEit(self):
        scope = self.instruments["scope.feedback"]
        # we need to freeze scope since this two values are taken on the same scope
        trg_mode = scope.getTriggerMode()
        scope.setTriggerMode("STOP")
        err = self.getErr()
        eit = self.getEIT()
        scope.setTriggerMode(trg_mode)
        return (err, eit)

    @BasicInstrument.tsdb_append
    def getErr(self):
        scope = self.instruments["scope.feedback"]
        ch1 = scope.getTrace(1, decimate=False)
        err = np.mean(ch1.y.values)
        return err

    @BasicInstrument.tsdb_append
    def getEIT(self):
        scope = self.instruments["scope.feedback"]
        ch3 = scope.getTrace(3, decimate=False)
        eit = np.mean(ch3.y.values)
        return eit

    @BasicInstrument.tsdb_append
    def setFeefback(self, val):
        freq0 = self.getRFreq()
        self.setRFreq(freq0 + val)

    @BasicInstrument.tsdb_append
    def getRFreq(self):
        rfgen = self.instruments["rfgen"]
        return rfgen.getFreqFixed()

    @BasicInstrument.tsdb_append
    def setRFreq(self, val):
        rfgen = self.instruments["rfgen"]
        rfgen.setFreqFixed(val)

    @BasicInstrument.tsdb_append
    def getRFAmplitude(self):
        rfgen = self.instruments["rfgen"]
        return rfgen.getRFAmplitude()

    @BasicInstrument.tsdb_append
    def setRFAmplitude(self, val):
        rfgen = self.instruments["rfgen"]
        return rfgen.setRFAmplitude(val)

    @BasicInstrument.tsdb_append
    def setLockinSlope(self, val):
        self.lockin_slope = val


if __name__ == "__main__":
    # TSDB logger setting
    tsdb_client = tsdb.Client(
        "influx", "http://lumus.physics.wm.edu:8428", database="qolab"
    )
    tsdb_ingester = tsdb.Ingester(
        tsdb_client, batch=11, measurement_prefix="VAMPIRE.HighPower"
    )

    # creating Apparatus with all instruments to be logged
    apparatus = Apparatus(
        tsdb_ingester=tsdb_ingester,
        device_nickname="magnetometer",
    )
    apparatus.config["Device type"] = "QOL VAMPIRE HighPower magnetometer"
    apparatus.config["Device model"] = "v0.1"
    apparatus.config["FnamePrefix"] = "magnetometer_eit"
    apparatus.config["SavePath"] = "/mnt/qol_grp_data/data.VAMPIRE.HighPower"

    app_nickname = apparatus.config["DeviceNickname"]

    logger.info("Accessing hardware")
    rm = pyvisa.ResourceManager()
    instr_scope = rm.open_resource("TCPIP::192.168.0.61::INSTR")
    scope_fdbk = SDS1104X(
        instr_scope,
        device_nickname=".".join([app_nickname, "scope.feedback"]),
        tsdb_ingester=tsdb_ingester,
    )
    instr_scope = rm.open_resource("TCPIP::192.168.0.62::INSTR")
    scope_mon = SDS1104X(
        instr_scope,
        device_nickname=".".join([app_nickname, "scope.monitor"]),
        tsdb_ingester=tsdb_ingester,
    )
    instr_rfgen = rm.open_resource("TCPIP::192.168.0.114::INSTR")
    rfgen = AgilentE8257D(
        instr_rfgen,
        device_nickname=".".join([app_nickname, "rfgen"]),
        tsdb_ingester=tsdb_ingester,
    )
    instr_lockin = rm.open_resource("TCPIP::192.168.0.51::INSTR")
    lockin = SRS_SR865A(
        instr_lockin,
        device_nickname=".".join([app_nickname, "lockin"]),
        tsdb_ingester=tsdb_ingester,
    )

    # adding instruments to apparatus
    apparatus.instruments = {}
    ai = apparatus.instruments
    ai["rfgen"] = rfgen
    ai["lockin"] = lockin
    ai["cellTemperatureController"] = I800(
        device_nickname=".".join([app_nickname, "cellTemperatureController"]),
        tsdb_ingester=tsdb_ingester,
    )
    # Do not add scope.feedback to apparatus.instruments it will create recursive loop
    # in the saved data file
    # ai['scope.feedback'] = scope_fdbk
    scope_fdbk.config["SavePath"] = "/mnt/qol_grp_data/data.VAMPIRE.HighPower"
    scope_fdbk.config["FnamePrefix"] = "scope_eit"
    # scope_fdbk.setRoll(False)
    # scope_fdbk.setRun(True)
    # scope_fdbk.setTimePerDiv(0.0005)
    # scope_fdbk.setChanVoltsPerDiv(1, 0.02)
    # scope_fdbk.setChanVoltsPerDiv(3, 0.02)
    ai["scope.monitor"] = scope_mon
    # scope_mon.setRoll(False)
    # scope_mon.setRun(True)
    # scope_mon.setTimePerDiv(0.0005)
    # scope_mon.setChanVoltsPerDiv(2, 0.002)
    # scope_mon.setChanVoltageOffset(2, -0.0726)

    scope_fdbk.config["tags"] = {}

    cfFreq = [6_833_980_000, 6_834_686_000, 6_835_393_000]
    m = [-2, 0, 2]
    # rfgen.setSweepCentralFreq(6_833_980_000)
    rfgen.setSweepCentralFreq(6_834_686_000)
    # rfgen.setSweepCentralFreq(6_835_393_000)

    for fr, m in zip(cfFreq, m):
        rfgen.setSweepCentralFreq(fr)
        print(f"time to settle for {m=} with {fr=}")
        time.sleep(10)
        print("settling done")

        # if we want to save new set of traces repeat this two commands
        scope_fdbk.config["tags"]["apparatus"] = getConfig(apparatus)
        scope_fdbk.save(maxRequiredPoints=1000)

    tsdb_ingester.commit()
