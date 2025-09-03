import logging
import universal_tsdb as utsdb
from universal_tsdb import Client, MaxErrorsException
import functools
import time

__all__ = ["Client", "Ingester", "MaxErrorsException"]

logging.basicConfig(
    format="%(asctime)s %(levelname)8s %(name)s: %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)
logger = logging.getLogger("qolab.tsdb")
logger.setLevel(logging.INFO)


class Ingester(utsdb.Ingester):
    """Same as universal_tsdb.Ingester but sets measurement_prefix.

    Handy with ``@tsdb_append_metric_for_class_setter_or_getter`` decorator
    to be used in hardware controlled classes

    Parameters
    ----------
    measurement_prefix: str (default is empty)
        standard ``utsdb`` measurement becomes measurement_prefix.measurement

    Example
    -------

    >>> from qolab.hardware.basic import BasicInstrument
    >>> from qolab.tsdb import Ingester
    >>> tsdb_client = Client("influx", "http://localhost:8428", database="qolab")
    >>> tsdb_ingester = Ingester(
    >>>     tsdb_client, batch=10, measurement_prefix="experiment.title"
    >>>  )
    >>>
    >>> class InstWithLog(BasicInstrument):
    >>>     def __init__(self, *args, **kwds):
    >>>        super().__init__(*args, **kwds)
    >>>        self.config["Device type"] = "TestTSDBLogger"
    >>>        self.config["Device model"] = "v01"
    >>>        self.config["FnamePrefix"] = "test_log"
    >>>        self.config["SavePath"] = "./data"
    >>>        self.deviceProperties.update({"D"})
    >>>        self.d = 13.45
    >>>
    >>>    @BasicInstrument.tsdb_append
    >>>    def setD(self, val):
    >>>        self.d = val
    >>>
    >>>    @BasicInstrument.tsdb_append
    >>>    def getD(self):
    >>>        return self.d
    >>>
    >>> dev = InstWithLog(tsdb_ingester=tsdb_ingester, device_nickname="tester")
    >>> dev.getD()
    >>> dev.setD(3)
    >>>
    >>> tsdb_ingester.commit()
    """

    def __init__(self, client, batch=0, measurement_prefix=""):
        super().__init__(client, batch=batch)
        self.measurement_prefix = measurement_prefix

    def append(self, timestamp=None, tags=None, measurement=None, **kwargs):
        if self.measurement_prefix is None or not isinstance(
            self.measurement_prefix, str
        ):
            raise ValueError("Invalid measurement_prefix, it should be string")
        if measurement is None or not isinstance(measurement, str):
            raise ValueError("Invalid measurement, it should be string")
        qolab_measurement = ".".join((self.measurement_prefix, measurement))
        # space is illegal for measurements fields
        qolab_measurement = qolab_measurement.replace(" ", "-")
        logger.debug(f"{qolab_measurement=} {tags=}, {kwargs=}")
        return super().append(
            timestamp=timestamp, tags=tags, measurement=qolab_measurement, **kwargs
        )


def tsdb_append_metric_for_class_setter_or_getter(tsdb_logger=None):
    """Send results of setters and getters to TSDB.

    Intended to be used as decorator for setters and getters,
    i.e. it expect the wrapped function to be something like getXXX or setXXX.
    """

    def wrap(f):
        @functools.wraps(f)
        def wrapper(*args, **kwds):
            if f.__name__[0:3] != "get" and f.__name__[0:3] != "set":
                logger.warning(
                    f"Do not know how to work with {f.__name__}"
                    + ", it is neither setXXX nor getXXX"  # noqa: W503
                )
                ret = f(*args, **kwds)
                return ret

            cls = args[0]
            action = f.__name__[0:3]
            var_name = f.__name__[3:]
            val = None
            if cls.config["DeviceNickname"] is not None:
                device_type = cls.config["DeviceNickname"]
            else:
                device_type = cls.config["Device type"]
            if action == "get":
                """getter"""
                val = f(*args, **kwds)
                ts = time.time()
                ret = val
            else:
                """setter"""
                val = args[1]
                ts = time.time()
                ret = f(*args, **kwds)

            logger.debug(f"function {f.__name__} {action} {var_name} = {val}")
            ts_ms = int(ts * 1000)
            fields = {var_name: val}
            try:
                if cls.tsdb_ingester is not None:
                    cls.tsdb_ingester.append(
                        ts_ms,
                        measurement=device_type,
                        tags={"action": action},
                        **fields,
                    )
            except ValueError as err:
                logger.error(f"{err=} in function {f.__name__}: {var_name} = {val}")
            return ret

        return wrapper

    return wrap


if __name__ == "__main__":
    from qolab.hardware.basic import BasicInstrument

    tsdb_client = Client("influx", "http://localhost:8428", database="qolab")
    tsdb_ingester = Ingester(
        tsdb_client, batch=10, measurement_prefix="experiment.title"
    )

    class InstWithLog(BasicInstrument):
        def __init__(self, *args, **kwds):
            super().__init__(*args, **kwds)
            self.config["Device type"] = "TestTSDBLogger"
            self.config["Device model"] = "v01"
            self.config["FnamePrefix"] = "test_log"
            self.config["SavePath"] = "./data"
            self.deviceProperties.update({"D"})
            self.d = 13.45

        @BasicInstrument.tsdb_append
        def setD(self, val):
            self.d = val

        @BasicInstrument.tsdb_append
        def getD(self):
            """get D variable"""
            return self.d

    dev = InstWithLog(tsdb_ingester=tsdb_ingester, device_nickname="tester")
    dev.getD()
    dev.setD(3)

    tsdb_ingester.commit()
