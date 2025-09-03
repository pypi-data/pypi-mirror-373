from qolab.file_utils import save_table_with_header, infer_compression
import datetime
import numpy as np
import yaml
import pandas
import os


def headerFromDictionary(d, prefix=""):
    """Converts dictionary to YAML format with optional prefix for every line."""
    header = []
    tail = yaml.dump(d, default_flow_style=False, sort_keys=False)
    tail = tail.split("\n")
    header.extend(tail)
    prefixed_header = [prefix + line for line in header]
    return prefixed_header


def from_timestamps_to_dates(timestamps):
    """Formats timestamps to datetime format"""
    dates = [datetime.datetime.fromtimestamp(float(ts)) for ts in timestamps]
    return dates


def loadTraceRawHeaderAndData(fname, tryCompressedIfMissing=True):
    """Load trace file and return header and data.

    Parameters
    ----------
    fname: str or Path
        file name path

    tryCompressedIfMissing: False or True (default)
        - False : use file name as is
        - True : if the provided filename is missing
            attempts to load a compressed version of filename.
            e.g. look for 'data.dat.gz', 'data.dat.bz', etc
    """
    headerstr = []
    data = None
    if (not os.path.exists(fname)) and tryCompressedIfMissing:
        # attempt to locate compressed file for the missing base file
        for ext in ["gz", "bz", "bz2"]:
            if os.path.exists(fname + "." + ext):
                fname += "." + ext
                break
    # we will try to guess if the file compressed
    _open = open
    compression = infer_compression(fname)
    if compression == "gzip":
        # TODO improve detection by reading magic bytes:
        # gzip files have first 2 bytes set to b'\x1f\x8b'
        import gzip

        _open = gzip.open
    elif compression == "bzip":
        # TODO improve detection by reading magic bytes:
        # bzip files have first 2 bytes set to b'BZ'
        import bz2

        _open = bz2.open
    with _open(fname, mode="rb") as tracefile:
        # Reading yaml header prefixed by '% '
        # It sits at the top and below is just data in TSV format
        while True:
            ln = tracefile.readline()
            if ln[0:2] == b"% ":
                headerstr.append(ln[2:].decode("utf-8"))
            else:
                break
        header = yaml.load(str.join("\n", headerstr), Loader=yaml.BaseLoader)
        # now we load the data itself
        tracefile.seek(0)  # rewind file to the beginning
        # Note: pandas reads csv faster by factor of 8 then numpy.genfromtxt
        df = pandas.read_csv(tracefile, comment="%", delimiter="\t", header=None)
        data = df.to_numpy()
    return (header, data)


def loadTrace(fname, tryCompressedIfMissing=True):
    """Load trace file."""
    (header, data) = loadTraceRawHeaderAndData(
        fname, tryCompressedIfMissing=tryCompressedIfMissing
    )
    return traceFromHeaderAndData(header, data)


def traceFromHeaderAndData(header, data=None):
    """Generate trace class from it description (header) and data."""
    label = None
    model = None
    tr = None
    if "config" not in header:
        print("Error: trace has now config")
        return None
    else:
        if "label" in header["config"]:
            label = header["config"]["label"]
        if "model" not in header["config"]:
            print("Error: unknown trace model")
            return None
        else:
            model = header["config"]["model"]
            if model == "Trace":
                tr = Trace(label)
                if data is not None:
                    tr.values = data
            elif model == "TraceXY":
                tx = traceFromHeaderAndData(header["TraceX"])
                ty = traceFromHeaderAndData(header["TraceY"])
                if data is not None:
                    tx.values = data[:, 0]
                    ty.values = data[:, 1]
                tr = TraceXY(label)
                tr.x = tx
                tr.y = ty
            elif model == "TraceSetSameX":
                tx = traceFromHeaderAndData(header["TraceX"])
                tx.values = data[:, 0]
                tr = TraceSetSameX(label)
                tr.addTraceX(tx)
                ytrs_header = header["TraceY"]
                cnt = 0
                for name, h in ytrs_header.items():
                    ty = traceFromHeaderAndData(h)
                    cnt += 1
                    ty.values = data[:, cnt]
                    trxy = TraceXY(name)
                    trxy.x = tx
                    trxy.y = ty
                    tr.addTrace(trxy)

            else:
                print(f"Error: unknown trace model: {model}")
                return None
        tr.config = header["config"]

    return tr


class Trace:
    """Base Trace class, which holds only one variable"""

    def __init__(self, label):
        self.config = {}
        self.config["label"] = label
        self.config["model"] = "Trace"
        self.config["version"] = "0.1"
        # 'type' is useful to indicate way of representation,
        # it makes sense on y_vs_x traces.
        # If set to none we have normal y vs x.
        # If set to 'timestamp' x will be converted to datetime dates
        self.config["type"] = None
        self.config["item_format"] = ".15e"
        self.config["tags"] = {}
        self.last_saved_pos = 0
        self._trace_specific_init()
        self.clear_data()

    def _trace_specific_init(self):
        self.config["unit"] = None
        self.values = np.empty(0)
        self.last_saved_pos = 0

    def clear_last_saved_pos(self):
        self.last_saved_pos = 0

    def clear_data(self):
        self.clear_last_saved_pos()
        if self.values is not None:
            self.values = np.empty(0, dtype=self.values.dtype)

    def __repr__(self):
        lbl = self.config["label"]
        cls_name = f"{self.__class__.__name__}('{lbl}'"
        return "".join([cls_name, f", N={self.values.size}", ")"])

    def plot(self):
        import matplotlib.pyplot as plt

        x = self.values
        if self.config["type"] is not None:
            if self.config["type"] == "timestamp":
                x = from_timestamps_to_dates(self.values)
        plt.plot(x, label=self.config["label"])
        plt.xlabel("index")
        plt.ylabel(f"{self.config['unit']}")
        plt.legend()
        plt.grid(True)

    def getConfig(self):
        d = {}
        d["config"] = self.config.copy()
        return d

    def getData(self):
        return self.values

    def getHeader(self, prefix=""):
        d = self.getConfig()
        return headerFromDictionary(d, prefix="")

    def save(
        self, fname, last_saved_pos=None, skip_headers_if_file_exist=False, **kwargs
    ):
        """Save trace to file and returns its filename."""
        if last_saved_pos is None:
            last_saved_pos = self.last_saved_pos
        data = self.getData()
        if last_saved_pos > 0:
            skip_headers_if_file_exist = True
        fname = save_table_with_header(
            fname,
            data[last_saved_pos:, :],
            self.getHeader(),
            item_format=self.config["item_format"],
            skip_headers_if_file_exist=skip_headers_if_file_exist,
            **kwargs,
        )
        self.last_saved_pos = data.shape[0]
        return fname

    def addPoint(self, val):
        self.values = np.append(self.values, val)


class TraceXY(Trace):
    """Data structure to handle two linked variables X and Y.

    It is handy for Y vs X data arrangements.
    """

    def __init__(self, label):
        super().__init__(label)
        self.config["model"] = "TraceXY"

    def _trace_specific_init(self):
        self.x = None
        self.y = None

    def clear_data(self):
        self.clear_last_saved_pos()
        if self.x is not None:
            self.x.clear_data()
        if self.y is not None:
            self.y.clear_data()

    def __repr__(self):
        lbl = self.config["label"]
        cls_name = f"{self.__class__.__name__}('{lbl}'"
        # xlabel = f"{self.x.config['label']}"
        xparam = f", {self.x}"
        yparam = f", {self.y}"
        return "".join([cls_name, xparam, yparam, ")"])

    def plot(self):
        import matplotlib.pyplot as plt

        x = self.x.values
        if self.x.config["type"] is not None:
            if self.x.config["type"] == "timestamp":
                x = from_timestamps_to_dates(x)
        plt.plot(x, self.y.values, label=self.config["label"])
        plt.xlabel(f"{self.x.config['label']} ({self.x.config['unit']})")
        plt.ylabel(f"{self.y.config['label']} ({self.y.config['unit']})")
        plt.legend()
        plt.grid(True)

    def getConfig(self):
        config = {}
        config["config"] = self.config.copy()
        config["TraceX"] = {}
        config["TraceX"] = self.x.getConfig()
        config["TraceY"] = {}
        config["TraceY"] = self.y.getConfig()
        return config

    def getData(self):
        data = self.x.values
        if data.ndim == 1:
            data = data[:, np.newaxis]
        vals = self.y.values
        if vals.ndim == 1:
            vals = vals[:, np.newaxis]
        data = np.concatenate((data, vals), 1)
        return data

    def addPoint(self, valX, valY):
        self.x.values = np.append(self.x.values, valX)
        self.y.values = np.append(self.y.values, valY)


class TraceSetSameX(Trace):
    """Data structure to handle multiple Ys vs X dependencies.
    It is handy for scope traces."""

    def __init__(self, label):
        super().__init__(label)
        self.config["model"] = "TraceSetSameX"

    def _trace_specific_init(self):
        self.x = None
        self.traces = {}

    def clear_data(self):
        self.clear_last_saved_pos()
        if self.x is not None:
            self.x.clear_data()
        for k, tr in self.traces.items():
            tr.clear_data()

    def __repr__(self):
        lbl = self.config["label"]
        cls_name = f"{self.__class__.__name__}('{lbl}'"
        xparam = f", x: {self.x}"
        yparam = f", traces: {list(self.traces.keys())}"
        return "".join([cls_name, xparam, yparam, ")"])

    def addTraceX(self, tr):
        self.x = tr

    def addTrace(self, tr):
        if tr.config["model"] == "TraceXY":
            if self.x is None:
                self.x = tr.x
            trY = tr.y
            self.traces[tr.config["label"]] = trY
        elif tr.config["model"] == "Trace":
            if self.x is None:
                self.x = tr
            else:
                self.traces[tr.config["label"]] = tr

    def plot(self):
        import matplotlib.pyplot as plt

        nplots = len(self.traces.keys())
        fig = plt.gcf()
        fig, axs = plt.subplots(nplots, 1, sharex=True, num=fig.number)
        cnt = 0
        x = self.x.values
        if self.x.config["type"] is not None:
            if self.x.config["type"] == "timestamp":
                x = from_timestamps_to_dates(x)
        for k, tr in self.traces.items():
            axs[cnt].plot(x, tr.values, label=k)
            axs[cnt].set_ylabel(f"{tr.config['label']} ({tr.config['unit']})")
            axs[cnt].legend()
            axs[cnt].grid(True)
            cnt += 1
        plt.xlabel(f"{self.x.config['label']} ({self.x.config['unit']})")

    def items(self):
        return self.traces.items()

    def keys(self):
        return self.traces.keys()

    def getTrace(self, label):
        tr = TraceXY(label)
        tr.x = self.x
        tr.y = self.traces[label]
        return tr

    def getConfig(self):
        config = {}
        config["config"] = self.config.copy()
        config["TraceX"] = {}
        config["TraceX"] = self.x.getConfig()
        config["TraceY"] = {}
        for k, v in self.traces.items():
            config["TraceY"][k] = v.getConfig()
        return config

    def getData(self):
        data = self.x.values
        if data.ndim == 1:
            data = data[:, np.newaxis]
        for k, v in self.traces.items():
            vals = v.values
            if vals.ndim == 1:
                vals = vals[:, np.newaxis]
            data = np.concatenate((data, vals), 1)
        return data

    def addPointToTrace(self, val, name=None):
        if name is None:
            self.x.values = np.append(self.x.values, val)
        else:
            a = self.traces[name].values
            a = np.append(a, val)
            self.traces[name].values = a


if __name__ == "__main__":
    print("Testing trace")
    x = Trace("x trace")
    x.values = np.random.normal(2, 2, (4, 1))
    x.values = np.array(x.values, int)
    x.config["unit"] = "s"
    x.config["tags"]["tag1"] = "xxxx"
    x.config["tags"]["tag2"] = "xxxx"
    x.save("xtrace.dat", skip_headers_if_file_exist=True)
    # print(x.getHeader())
    y = Trace("y trace")
    y.values = np.random.normal(2, 2, (4, 1))
    y.config["unit"] = "V"
    y.config["tags"]["ytag2"] = "yyyy"
    xy = TraceXY("xy trace")
    xy.config["tags"]["xy tag"] = "I am xy tag"
    xy.x = x
    xy.y = y
    xy.save("xytrace.dat")
    # print(xy.getHeader())
    xyn = TraceSetSameX("many ys trace")
    xyn.config["tags"]["descr"] = "I am many ys trace"
    xy.config["label"] = "y1"
    xyn.addTrace(xy)
    xy.config["label"] = "y2"
    xyn.addTrace(xy)
    xy.config["label"] = "y3"
    xyn.addTrace(xy)
    xyn.save("xyntrace.dat")
    # print(xyn.getHeader())
