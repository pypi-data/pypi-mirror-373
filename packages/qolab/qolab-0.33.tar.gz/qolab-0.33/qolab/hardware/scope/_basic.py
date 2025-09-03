"""
Provide basic class to build an operational scope

Created by Eugeniy E. Mikhailov 2021/11/29
"""

import numpy as np
from qolab.hardware.scpi import SCPIinstr
from qolab.hardware.basic import BasicInstrument
from qolab.data.trace import TraceSetSameX, TraceXY
import time
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)8s %(name)s: %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def calcSparsingAndNumPoints(availableNpnts=None, maxRequiredPoints=None):
    """Calculate sparcing and number of sparced points.

    Parameters
    ----------
    availableNpnts: int or None (throws error)
        Number of available points. If set to None exit with error
    maxRequiredPoints: int or None (throws error)
        number of requested points after decimation.
        If availableNpnts< maxRequiredPoints*2,
        decimation is impossible and we will get up to factor of 2 more
        than requested.

    Return
    ------
    (sparsing, Npnts, availableNpnts, maxRequiredPoints)
    """
    if availableNpnts is None:
        raise ValueError("Invalid availableNpnts value, must be int.")
    if maxRequiredPoints is None:
        raise ValueError("Invalid maxRequiredPoints value, must be int.")

    if availableNpnts <= maxRequiredPoints * 2:
        Npnts = availableNpnts
        sparsing = 1
    else:
        sparsing = int(np.floor(availableNpnts / maxRequiredPoints))
        Npnts = int(np.floor(availableNpnts / sparsing))
    return (sparsing, Npnts, availableNpnts, maxRequiredPoints)


class Scope(BasicInstrument):
    """Minimal class to implement a scope.

    Intended to be used as a parent for hardware aware scopes.

    Provide a minimal set of methods to be implemented by a scope.
    """

    vertDivOnScreen = 8  # should be adjusted in hardware aware class
    horizDivOnScreen = 8  # should be adjusted in hardware aware class
    minVoltsPerDiv = 0.001  # should be adjusted in hardware aware class

    def __init__(self, *args, **kwds):
        BasicInstrument.__init__(self, *args, **kwds)
        self.config["Device type"] = "Scope"
        self.config["Device model"] = "Generic Scope Without Hardware interface"
        self.config["FnamePrefix"] = "scope"
        self.numberOfChannels = 0
        # deviceProperties must have 'get' and preferably 'set' methods available,
        # i.e. 'SampleRate' needs getSampleRate() and love to have setSampleRate(value)
        # they will be used to obtain config and set device according to it
        self.deviceProperties.update(
            {"SampleRate", "TimePerDiv", "TrigDelay", "TriggerMode", "Roll", "Run"}
        )
        # same is applied to channelProperties
        # but we need setter/getter with channel number
        # i.e.  VoltsPerDiv must provide
        # getChanVoltsPerDiv(chNum) and setSampleRate(chNum, value)
        self.channelProperties = {
            "VoltsPerDiv",
            "VoltageOffset",
        }

    def getWaveform(
        self, chNum, availableNpnts=None, maxRequiredPoints=None, decimate=True
    ):
        """
        Get scope channel waveform where X axis is index and not time.

        Waveform MUST HAVE entry in config dictionary such as
        ``wafeform.config["tags"]["rawChanConfig"]``
        with items helping to calculate time trace
        (Usually ``SampleRate``, ``Npnts``, ``sparsing``).

        For decimate use see ``getRawWaveform``.

        In short decimate=True is slower but more precise.

        """
        raise NotImplementedError("getWaveform function is not implemented")

    def getTimeTrace(self, rawChanCfg):
        """Constructs time trace from properties in ``rawChanCfg`` dictionary."""
        raise NotImplementedError("getTimeTrace function is not implemented")

    def getTrace(
        self,
        chNum,
        availableNpnts=None,
        maxRequiredPoints=None,
        decimate=True,
        fmath=False,
    ):
        """Get scope trace with time axis set."""
        old_run_status = self.getRun()
        if old_run_status:  # avoid unnecessary status change
            self.setRun(False)  # stop if currently running
            self._waitUntillStop()
        # to get synchronous channels
        wfVoltage = self.getWaveform(
            chNum,
            availableNpnts=availableNpnts,
            maxRequiredPoints=maxRequiredPoints,
            decimate=decimate,
            fmath=fmath,
        )
        rawChanCfg = wfVoltage.config["tags"]["rawChanConfig"]
        t = self.getTimeTrace(rawChanCfg)
        if fmath:
            tr = TraceXY(f"ChF{chNum}")
        else:
            tr = TraceXY(f"Ch{chNum}")
        tr.x = t
        tr.y = wfVoltage
        # restore scope to the before acquisition mode
        if old_run_status:  # avoid unnecessary status change
            self.setRun(old_run_status)  # start running if it was old run state
        return tr

    def getTriggerMode(self):
        # we expect NORM, AUTO, SINGLE
        raise NotImplementedError("getTriggerMode function is not implemented")

    def setTriggerMode(self, mode):
        # we expect NORM, AUTO, SINGLE
        raise NotImplementedError("setTriggerMode function is not implemented")

    def getRun(self):
        """Is acquisition running or stopped."""
        raise NotImplementedError("getRun function is not implemented")

    def setRun(self, val):
        """Either enable run or stop the acquisition."""
        raise NotImplementedError("setRun function is not implemented")

    def _waitUntillStop(self, timeout=1):
        """Wait until scope in the stop state.

        Just because we ask for a scope to stop, does not mean
        that it is stopped. It can still wait for a trigger or untill
        the time span is filled.

        Parameter
        ---------
        timeout : float
            timeout in seconds, default is 1 second
        """
        starttime = time.time()
        deadline = starttime + timeout
        while time.time() < deadline:
            if self.getRun():
                time.sleep(0.010)
            else:
                logger.debug(f"Scope stopped within {time.time()-starttime} seconds.")
                return
        logger.warning(
            f"Scope did not reach STOP state within {timeout=} sec, try to increase it."
        )

    def getAllTraces(self, availableNpnts=None, maxRequiredPoints=None, decimate=True):
        allTraces = TraceSetSameX("scope traces")
        allTraces.config["tags"]["DAQ"] = self.getConfig()
        old_run_status = self.getRun()
        if old_run_status:  # avoid unnecessary status change
            self.setRun(False)  # stop if currently running
            self._waitUntillStop()
        # to get synchronous channels
        for chNum in range(1, self.numberOfChannels + 1):
            allTraces.addTrace(
                self.getTrace(
                    chNum,
                    availableNpnts=availableNpnts,
                    maxRequiredPoints=maxRequiredPoints,
                    decimate=decimate,
                )
            )
        # restore scope to the before acquisition mode
        if old_run_status:  # avoid unnecessary status change
            self.setRun(old_run_status)  # start running if it was old run state
        return allTraces

    def restorePriorToFastGrab(self, chNum, old_config):
        """Restore relevant channel/scope settings prior to fast grab tune up."""
        logger.info("method restorePriorToFastGrab is not implemented")

    def switchToFastGrab(self, chNum):
        """Switch scope to the fastest mode for trace delivery.

        Intended to be used in chanAutoScale methods where speed
        transfer is more important than fidelity. It is good
        idea to implement function ``restorePriorToFastGrab(chan, old_config)``
        to be used in conjunction with ``switchToFastGrab``.

        To be fast, it should aim to decrease data transfer time,
        i.e. reduce number of transferred point.
        It also need to be interface dependent. GPIB and USB are known
        to be quite slow when compared to network connection.

        So try to be smart in hardware dependent classes.

        Return
        ------
        old_config : dictionary
            old config with settings necessary to restore initial state
        """

        logger.info("machinery for switchToFastGrab is not implemented")
        return self.getConfig()

    def chanAutoScale(self, chNum, margin=0.125, timeout=5):
        """Auto scale channel to fit signal on screen.

        Tunes Volts per division and Channel offset to fit signal
        on screen (vertically).

        Parameters
        ----------
        chNum : int
            Channel to auto scale
        margin: float
           How much extra space (margin) to have with respect to full screen.
           Default is 0.125 (i.e. 12.5%).
           Note that margin = 0.25 corresponds to 1 vertical division
           at top and bottom for 8 division scope.
        """

        old_config = self.switchToFastGrab(chNum)
        starttime = time.time()
        deadline = starttime + timeout
        timespan = self.getTimePerDiv() * self.horizDivOnScreen
        scaled_corectly = False
        self.setRun(True)

        while (not scaled_corectly) and (time.time() < deadline):
            time.sleep(
                timespan + 0.5
            )  # give enough time to acquire a trace and switch to Run
            tr = self.getTrace(chNum)
            vPerDiv = self.getChanVoltsPerDiv(chNum)
            offset = self.getChanVoltageOffset(chNum)
            v_range = vPerDiv * self.vertDivOnScreen
            v_max = v_range / 2 - offset
            v_min = -v_range / 2 - offset
            y = tr.y.values
            tr_max = y.max()
            tr_min = y.min()
            signal_range = tr_max - tr_min
            margin_t = (v_max - tr_max) / v_range
            margin_b = (tr_min - v_min) / v_range
            is_margin_t_good = (margin_t > margin * 0.5) and (margin_t < margin * 1.0)
            is_margin_b_good = (margin_b > margin * 0.5) and (margin_b < margin * 1.0)
            if (is_margin_b_good) and (is_margin_t_good):
                scaled_corectly = True
                break
            old_offset = offset
            old_vPerDiv = vPerDiv
            offset = -(tr_max + tr_min) / 2
            if min(margin_t, margin_b) < 0.01:  # too close to edge, zoom out
                vPerDiv *= 2
            elif (signal_range / v_range) < 0.2:  # signal is too small, zoom in
                vPerDiv /= 2
            else:
                vPerDiv = signal_range / (self.vertDivOnScreen * (1 - margin * 1.2))
            if vPerDiv < self.minVoltsPerDiv:
                vPerDiv = self.minVoltsPerDiv
            logger.debug(f"Auto Scaler Requesting {vPerDiv=} for {chNum=}.")
            self.setChanVoltsPerDiv(chNum, vPerDiv)
            logger.debug(f"Auto Scaler Requesting {offset=} for {chNum=}.")
            self.setChanVoltageOffset(chNum, offset)
            relOffsetChange = abs(old_offset - offset) / old_vPerDiv
            relVperDivChange = abs(old_vPerDiv - vPerDiv) / old_vPerDiv
            if (relOffsetChange < 0.5) and (relVperDivChange < 0.05):
                # we converge, there is no point to improve
                break
            scaled_corectly = False
        self.restorePriorToFastGrab(chNum, old_config)
        if time.time() > deadline:
            logger.warning(
                f"Scope did not make proper channel {chNum}"
                + f"scaling within {timeout=} sec."
            )

    def plot(self, **kwargs):
        allTraces = self.getAllTraces(**kwargs)
        allTraces.plot()

    def save(
        self,
        fname=None,
        item_format="e",
        availableNpnts=None,
        maxRequiredPoints=None,
        decimate=True,
        extension="dat",
    ):
        allTraces = self.getAllTraces(
            availableNpnts=availableNpnts,
            maxRequiredPoints=maxRequiredPoints,
            decimate=decimate,
        )
        allTraces.config["item_format"] = item_format
        if fname is None:
            fname = self.getNextDataFile(extension=extension)
        allTraces.save(fname)
        print(f"Data saved to: {fname}")
        return fname


class ScopeSCPI(SCPIinstr, Scope):
    """SCPI aware scope.

    Use as a parent for a hardware aware scope classes.

    Example
    -------

    >>> rm = pyvisa.ResourceManager()
    >>> ScopeSCPI(rm.open_resource('TCPIP::192.168.0.2::INSTR'))
    """

    def __init__(self, resource, *args, **kwds):
        SCPIinstr.__init__(self, resource)
        Scope.__init__(self, *args, **kwds)
        self.config["DeviceId"] = str.strip(self.idn)
