import logging
import justpy as jp
import pyvisa
import numpy as np
import qolab.tsdb as tsdb
import asyncio
import time
import qolab.gui.web as gui
from qolab.hardware import BasicInstrument
from qolab.hardware.scope import SDS1104X
from qolab.hardware.rf_generator import AgilentE8257D
from qolab.hardware.lockin import SRS_SR865A
from qolab.feedback import PID
from qolab.data import TraceSetSameX, TraceXY, Trace
from qolab.hardware.i_server import I800

# this should be done before justpy is called or log formatter does not work
logging.basicConfig(
    format="%(asctime)s %(levelname)8s %(name)s: %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)


tmplog = logging.getLogger("qolab.gui.web")
tmplog.setLevel(logging.INFO)
tmplog = logging.getLogger("qolab.tsdb")
tmplog.setLevel(logging.INFO)
logger = logging.getLogger("Magnetometer")
logger.setLevel(logging.INFO)


def getConfig(apparatus):
    config = apparatus.config.copy()
    ai = apparatus.instruments
    for n, i in ai.items():
        config[n] = i.getConfig()
    return config


def initLog(extra_tags={}):
    errorTrace = Trace("error")
    errorTrace.config["unit"] = "V"
    timeTrace = Trace("time")
    timeTrace.config["unit"] = "S"
    timeTrace.config["type"] = "timestamp"
    errorLog = TraceXY("error")
    errorLog.x = timeTrace
    errorLog.y = errorTrace

    freqTrace = Trace("frequency")
    freqTrace.config["unit"] = "Hz"
    freqLog = TraceXY("frequency")
    freqLog.x = timeTrace
    freqLog.y = freqTrace

    feedbackTrace = Trace("feedback")
    feedbackTrace.config["unit"] = "Hz"
    feedbackLog = TraceXY("feedback")
    feedbackLog.x = timeTrace
    feedbackLog.y = feedbackTrace

    eitTrace = Trace("eit")
    eitTrace.config["unit"] = "V"
    eitLog = TraceXY("eit")
    eitLog.x = timeTrace
    eitLog.y = eitTrace

    rfPoutTrace = Trace("rfPout")
    rfPoutTrace.config["unit"] = "dBm"
    rfPoutLog = TraceXY("rfPout")
    rfPoutLog.x = timeTrace
    rfPoutLog.y = rfPoutTrace

    cellTemperatureLog = TraceXY("cellTemperature")
    cellTemperatureLog.x = timeTrace
    cellTemperatureLog.y = Trace("cellTemperature")
    cellTemperatureLog.y.config["unit"] = "C"

    log = TraceSetSameX("timelog")
    log.addTrace(errorLog)
    log.addTrace(freqLog)
    log.addTrace(feedbackLog)
    log.addTrace(eitLog)
    log.addTrace(rfPoutLog)
    log.addTrace(cellTemperatureLog)
    log.config["tags"]["apparatus"] = getConfig(apparatus)
    log.config["tags"].update(extra_tags)
    return log


async def feedbackLoop(apparatus, nsteps):
    # while True:
    for i in range(0, nsteps):
        adjustRFandLog(apparatus)
        await asyncio.sleep(0.1)
    apparatus.runStatus = False


def adjustRFandLog(apparatus):
    timenow = time.time()

    ai = apparatus.instruments
    pid = ai["pid"]
    log = apparatus.gui_log.traces

    err, eit = apparatus.getErrAndEit()
    fdbck = pid.feedback(err)

    freq0 = apparatus.getRFreq()
    apparatus.setFeefback(fdbck)

    rfPout = apparatus.getRFAmplitude()

    apparatus.getBCurrent()
    # this automatically logs value to TSDB

    tCell = ai["cellTemperatureController"].getTemperature()

    log.addPointToTrace(timenow)
    log.addPointToTrace(err, "error")
    log.addPointToTrace(freq0, "frequency")
    log.addPointToTrace(fdbck, "feedback")
    log.addPointToTrace(rfPout, "rfPout")
    log.addPointToTrace(eit, "eit")
    log.addPointToTrace(tCell, "cellTemperature")


async def initial_lock_to_eit(apparatus, extra_tags={}):
    rfPout = apparatus.getRFAmplitude()
    apparatus.state = f"Initial lock RF power {rfPout} dBm"
    logger.info(apparatus.state)
    update_webpage(apparatus=apparatus)

    ai = apparatus.instruments
    apparatus.gui_log.setTraces(initLog(extra_tags=extra_tags))
    ai["pid"].reset()
    ai["pid"].setEnable(True)
    apparatus.runStatus = True
    await asyncio.gather(feedbackLoop(apparatus, nsteps=50))


async def calibratingLockin(apparatus, extra_tags={}):
    ai = apparatus.instruments
    rfPout = apparatus.getRFAmplitude()
    apparatus.state = f"Calibrating lockin response at RF power {rfPout} dBm"
    logger.info(apparatus.state)
    update_webpage(apparatus=apparatus)
    ai["pid"].setEnable(False)
    ai["pid"].reset()
    apparatus.gui_log.setTraces(initLog(extra_tags=extra_tags))
    await asyncio.gather(feedbackLoop(apparatus, nsteps=20))

    fr0 = ai["rfgen"].getFreqFixed()
    df = 10
    ai["pid"].setEnable(False)
    ai["pid"].reset()
    apparatus.setRFreq(fr0 + df)
    await asyncio.gather(feedbackLoop(apparatus, nsteps=20))
    apparatus.setRFreq(fr0)

    log = apparatus.gui_log.traces
    trE = log.getTrace("error")

    e1 = np.mean(trE.y.values[0:20])
    e2 = np.mean(trE.y.values[20:])
    dE = e2 - e1
    slope = dE / df
    apparatus.setLockinSlope(slope)

    logger.info(f"dE = {dE}")
    logger.info(f"lockin error signal slope = {slope} V/Hz")
    ai["error_signal_response_to_eit_detuning"].conversion_factor = float(slope)

    return float(slope)


async def responseToChangeOfBfieldControlVoltage(apparatus, extra_tags={}):
    ai = apparatus.instruments
    rfPout = apparatus.getRFAmplitude()
    apparatus.state = (
        f"Calibrating lockin response to change of Bfield control voltage, {rfPout} dBm"
    )
    logger.info(apparatus.state)
    update_webpage(apparatus=apparatus)
    ai["pid"].setEnable(True)
    ai["pid"].reset()
    apparatus.gui_log.setTraces(initLog(extra_tags=extra_tags))
    dV = 0.01
    ai["lockin"].AuxOut1 = dV

    # initial lock
    ai["pid"].setEnable(True)
    ai["pid"].reset()
    await asyncio.gather(feedbackLoop(apparatus, nsteps=20))

    # this is for the money lock
    await asyncio.gather(feedbackLoop(apparatus, nsteps=30))

    fr0 = ai["rfgen"].getFreqFixed()

    # this is for the money lock
    ai["lockin"].AuxOut1 = 0
    ai["pid"].setEnable(True)
    ai["pid"].reset()
    await asyncio.gather(feedbackLoop(apparatus, nsteps=30))
    fr1 = ai["rfgen"].getFreqFixed()

    # log = apparatus.gui_log.traces
    # trE = log.getTrace("error")

    df = fr0 - fr1
    slope = df / dV

    logger.info(f"df = {df}")
    logger.info(f"response to magnetic control voltage = {slope} Hz/V")
    ai["B_control_voltage_to_eit_detuning"].conversion_factor = float(slope)

    # relock to default state
    ai["lockin"].AuxOut1 = 0
    ai["pid"].setEnable(True)
    ai["pid"].reset()
    await asyncio.gather(feedbackLoop(apparatus, nsteps=20))

    return float(slope)


async def record_magnetometer_noise(apparatus):
    ai = apparatus.instruments
    rfPout = apparatus.getRFAmplitude()
    ai["pid"].setEnable(False)

    apparatus.state = f"Record magnetometer noise,  RF power {rfPout} dBm"
    logger.info(apparatus.state)

    scope = ai["scope.monitor"]
    old_config = scope.getConfig()
    tperdiv = 1
    scope.setTimePerDiv(tperdiv)
    scope.setRoll(True)

    await asyncio.sleep(tperdiv * 14 + 1)
    errorTr = scope.getTrace(1, maxRequiredPoints=10000)
    errorTr.config["label"] = "error vs time"
    errorTr.y.config["label"] = "error"
    log = errorTr
    log.config["tags"]["apparatus"] = getConfig(apparatus)
    magNoise = BasicInstrument(device_nickname=".".join(["magnetometer", "noise"]))
    magNoise.config["FnamePrefix"] = "magnetometer_noise"
    magNoise.config["SavePath"] = apparatus.config["SavePath"]
    fname = magNoise.getNextDataFile()
    log.save(fname)
    logger.info(f"Magnetometer noise file: {fname}")

    apparatus.gui_log.setTraces(log)
    update_webpage(apparatus=apparatus)

    logger.info("Restoring scope settings")
    scope.setConfig(old_config)


async def longTermLock(apparatus, extra_tags={}):
    ai = apparatus.instruments
    rfPout = apparatus.getRFAmplitude()
    apparatus.state = f"Long term lock RF power {rfPout} dBm"
    logger.info(apparatus.state)

    ai = apparatus.instruments
    rfPout = apparatus.getRFAmplitude()
    apparatus.runStatus = True
    ai["pid"].setEnable(True)

    apparatus.gui_log.setTraces(initLog(extra_tags=extra_tags))
    update_webpage(apparatus=apparatus)

    res = await asyncio.gather(feedbackLoop(apparatus, nsteps=10000000))
    return res


async def sweepRFPower(apparatus, extra_tags={}, rfPowerList=[]):
    apparatus.gui_log.setTraces(initLog(extra_tags=extra_tags))
    ai = apparatus.instruments
    # for p in np.linspace(-10,10, 110):
    ai["pid"].setEnable(True)
    for p in rfPowerList:
        ai["rfgen"].setRFAmplitude(p)
        rfPout = ai["rfgen"].getRFAmplitude()
        apparatus.state = f"lock with RF power {rfPout} dBm"
        logger.info(apparatus.state)
        update_webpage(apparatus=apparatus)
        ai["pid"].reset()
        apparatus.runStatus = True
        res = await asyncio.gather(feedbackLoop(apparatus, nsteps=50))
    return res


freqZero = 6_834_686_400
# freqDeltaMp2 = 6_835_385_570; # T=83.7C
freqDeltaMp2 = 6_835_393_258
# T=60C
# freqDeltaMp2 = 6_835_396_000; # T=44.6C
dfB = freqDeltaMp2 - freqZero
freqDeltaMm2 = freqZero - dfB


async def main():
    app_nickname = apparatus.config["DeviceNickname"]

    task_wp_update_loop = asyncio.create_task(update_webpage_loop(update_interval=1))

    apparatus.gui_log = gui.QOLTimeLog(a=wp)
    apparatus.gui_log.save_controls.getNextDataFile = apparatus.getNextDataFile

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
    # print('------ Header start -------------')
    # print(str.join('\n', scope.getHeader()))
    # print(str.join('\n', rfgen.getHeader()))
    # print('------ Header ends  -------------')
    # ch1  = scope.getTrace(1)
    # traces = scope.getAllTraces()
    # pid = PID(100,400,0, sign=-1); # good for dm=-2 resonance
    pid = PID(
        5,
        20,
        0,
        sign=-1,
        device_nickname=".".join([app_nickname, "pid"]),
        tsdb_ingester=tsdb_ingester,
    )

    apparatus.instruments = {}
    ai = apparatus.instruments
    ai["rfgen"] = rfgen
    ai["lockin"] = lockin
    ai["pid"] = pid
    ai["cellTemperatureController"] = I800(
        device_nickname=".".join([app_nickname, "cellTemperatureController"]),
        tsdb_ingester=tsdb_ingester,
    )
    ai["scope.feedback"] = scope_fdbk
    scope_fdbk.setRoll(False)
    scope_fdbk.setRun(True)
    scope_fdbk.setTimePerDiv(0.0005)
    scope_fdbk.setChanVoltsPerDiv(1, 0.2)
    scope_fdbk.setChanVoltsPerDiv(3, 0.02)
    ai["scope.monitor"] = scope_mon
    scope_mon.setRoll(False)
    scope_mon.setRun(True)
    scope_mon.setTimePerDiv(0.0005)
    scope_mon.setChanVoltsPerDiv(1, 0.10)
    scope_mon.setChanVoltsPerDiv(2, 0.002)
    scope_mon.setChanVoltageOffset(2, -0.0726)
    apparatus.state = None
    apparatus.runStatus = False

    error_signal_response_to_eit_detuning = BasicInstrument(
        device_nickname=".".join(
            [app_nickname, "error_signal_response_to_eit_detuning"]
        ),
        tsdb_ingester=tsdb_ingester,
    )
    error_signal_response_to_eit_detuning.deviceProperties.update(
        {"conversion_factor", "unit"}
    )
    error_signal_response_to_eit_detuning.conversion_factor = None
    error_signal_response_to_eit_detuning.unit = "V_per_Hz"
    ai["error_signal_response_to_eit_detuning"] = error_signal_response_to_eit_detuning

    B_control_voltage_to_eit_detuning = BasicInstrument(
        device_nickname=".".join([app_nickname, "B_control_voltage_to_eit_detuning"]),
        tsdb_ingester=tsdb_ingester,
    )
    B_control_voltage_to_eit_detuning.deviceProperties.update(
        {"conversion_factor", "unit"}
    )
    B_control_voltage_to_eit_detuning.conversion_factor = None
    B_control_voltage_to_eit_detuning.unit = "Hz_per_V"
    ai["B_control_voltage_to_eit_detuning"] = B_control_voltage_to_eit_detuning

    # SweepSpan = 10000
    ai["rfgen"].stopFrequencySweep()
    # ai['rfgen'].setFreqFixed(freqDeltaMm2)
    # ai['rfgen'].setFreqFixed(freqZero)
    apparatus.setRFreq(freqDeltaMp2)
    # apparatus.setRFreq(freqZero)

    rfPstart = -10
    # rfPstop = 10
    # rfPowerList = np.linspace(rfPstart, rfPstop, 11)
    rfPower0 = rfPstart
    rfPower0 = 9
    apparatus.setRFAmplitude(rfPower0)

    d = getConfig(apparatus)
    instruments_config = gui.QOLDictionary(
        a=wp, name="Instruments configs", container=d
    )
    extra_tags = {}

    await initial_lock_to_eit(apparatus, extra_tags=extra_tags)

    await calibratingLockin(apparatus, extra_tags=extra_tags)
    instruments_config.container = getConfig(apparatus)
    instruments_config.display_container_dictionary()

    await responseToChangeOfBfieldControlVoltage(apparatus, extra_tags=extra_tags)
    instruments_config.container = getConfig(apparatus)
    instruments_config.display_container_dictionary()

    # await sweepRFPower(apparatus, extra_tags=extra_tags, rfPowerList=rfPowerList)

    await record_magnetometer_noise(apparatus)

    await longTermLock(apparatus, extra_tags=extra_tags)

    apparatus.state = "Done working with hardware"
    logger.info(apparatus.state)
    update_webpage(apparatus=apparatus)

    apparatus.gui_log.stop_tasks()
    task_wp_update_loop.cancel()
    logger.info("exiting main loop")
    update_webpage(apparatus=apparatus)
    return apparatus


def update_webpage(byWhom=None, apparatus=None):
    timestr = time.strftime("%a, %d %b %Y, %H:%M:%S", time.localtime())
    clock_upd.text = f"Last update at {timestr}"
    try:
        status_line.text = apparatus.state
    except Exception:
        pass
    jp.run_task(wp.update())


async def update_webpage_loop(update_interval=1):
    while True:
        update_webpage()
        await asyncio.sleep(update_interval)


async def getPage():
    return wp


async def jp_startup():
    jp.run_task(main())


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
    logger.info("========== Start up ===========")
    tsdb_client = tsdb.Client(
        "influx", "http://lumus.physics.wm.edu:8428", database="qolab"
    )
    tsdb_ingester = tsdb.Ingester(
        tsdb_client, batch=11, measurement_prefix="VAMPIRE.HighPower"
    )

    wp = jp.WebPage(delete_flag=False)
    apparatus = Apparatus(
        tsdb_ingester=tsdb_ingester,
        device_nickname="magnetometer",
    )
    apparatus.config["Device type"] = "QOL VAMPIRE HighPower magnetometer"
    apparatus.config["Device model"] = "v0.1"
    apparatus.config["FnamePrefix"] = "magnetometer"
    apparatus.config["SavePath"] = "/mnt/qol_grp_data/data.VAMPIRE.HighPower"
    # apparatus.config['SavePath'] = './data'

    d = jp.Div(
        text="Magnetometer log",
        a=wp,
        classes="text-white bg-blue-500 text-center text-xl",
    )

    div_status = jp.Div(
        classes="text-xl flex m0 p-1 space-x-4 bg-gray-300 font-mono", a=wp
    )
    clock_upd = jp.Div(
        text="Clock Loading...", classes="text-xl bg-gray-400", a=div_status
    )
    status_line = jp.Div(text="Status Loading...", classes="text-xl", a=div_status)

    # mpl.use("TkAgg")
    # apparatus = asyncio.run(main())
    jp.justpy(getPage, startup=jp_startup)
