import pytest
from qolab.data.trace import loadTrace
import numpy as np
import os


def isItExpectedTrace(tr):
    cfg = tr.getConfig()
    assert cfg["config"]["version"] == "0.1"
    assert cfg["config"]["model"] == "Trace"
    data = tr.getData()
    assert np.all((data - np.array([[1], [3], [2], [5]])) == 0)
    return True


def test_load_uncompressed_v0dot1_trace():
    tr = loadTrace("tests/trace_test_data/xtrace1.dat")
    assert isItExpectedTrace(tr) is True


def test_load_gzip_compressed_v0dot1_trace():
    tr = loadTrace("tests/trace_test_data/xtrace1.dat.gz")
    assert isItExpectedTrace(tr) is True


def test_load_bzip_compressed_v0dot1_trace():
    tr = loadTrace("tests/trace_test_data/xtrace1.dat.bz")
    assert isItExpectedTrace(tr) is True

    tr = loadTrace("tests/trace_test_data/xtrace1.dat.bz2")
    assert isItExpectedTrace(tr) is True


def test_tryCompressedIfMissing():
    fname = "tests/trace_test_data/only_compressed_file1.dat"
    # we check that the guess is working for gzip compressed file (.gz)
    tr = loadTrace(fname, tryCompressedIfMissing=True)
    assert isItExpectedTrace(tr) is True

    fname = "tests/trace_test_data/only_compressed_file2.dat"
    # we check that the guess is working for bzip compressed file (.bz)
    tr = loadTrace(fname, tryCompressedIfMissing=True)
    assert isItExpectedTrace(tr) is True

    fname = "tests/trace_test_data/only_compressed_file3.dat"
    # we check that the guess is working for bzip compressed file (.bz2)
    tr = loadTrace(fname, tryCompressedIfMissing=True)
    assert isItExpectedTrace(tr) is True

    # now we disable search for compressed version
    with pytest.raises(FileNotFoundError):
        tr = loadTrace(fname, tryCompressedIfMissing=False)

    tr = loadTrace("tests/trace_test_data/xtrace1.dat")
    assert isItExpectedTrace(tr) is True


def test_saving_raw():
    import tempfile

    with tempfile.NamedTemporaryFile(delete=True) as fp:
        fp.close()
        fname = fp.name
        assert not os.path.exists(fname)

        tr = loadTrace("tests/trace_test_data/xtrace1.dat")
        tr.save(fname, compressionmethod=None)
        trLoaded = loadTrace(fname)
        assert isItExpectedTrace(trLoaded)
        os.remove(fname)


def test_saving_gzip():
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False) as fp:
        fp.close()
        fname = fp.name + ".bz"
        assert not os.path.exists(fname)

        tr = loadTrace("tests/trace_test_data/xtrace1.dat")
        tr.save(fname, compressionmethod="bzip")
        trLoaded = loadTrace(fname)
        assert isItExpectedTrace(trLoaded)
        os.remove(fname)
