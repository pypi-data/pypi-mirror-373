import os

from qolab.file_utils import infer_compression, save_table_with_header


def test_infer_compression():
    assert infer_compression("data.dat") is None
    assert infer_compression("data.unknown_ext") is None
    assert infer_compression("data.dat.gz") == "gzip"
    assert infer_compression("data.dat.bz") == "bzip"
    assert infer_compression("data.dat.bz2") == "bzip"


def test_save_table_with_header_match_filename_to_compression():
    import tempfile

    data = [[1, 3], [2, 5]]
    headerstr = ["header 1", "header 2"]
    with tempfile.TemporaryDirectory(prefix="qolab_test") as d:
        fname = os.path.join(d, "t.dat")
        assert save_table_with_header(
            fname,
            data,
            header=headerstr,
            compressionmethod=None,
            match_filename_to_compression=True,
        ) == (fname)
        assert save_table_with_header(
            fname,
            data,
            header=headerstr,
            compressionmethod="gzip",
            match_filename_to_compression=True,
        ) == (fname + ".gz")
        assert save_table_with_header(
            fname,
            data,
            header=headerstr,
            compressionmethod="bzip",
            match_filename_to_compression=True,
        ) == (fname + ".bz")

        # now cases when requested extension does not match the compression
        assert save_table_with_header(
            fname + ".gz",
            data,
            header=headerstr,
            compressionmethod=None,
            match_filename_to_compression=True,
        ) == (fname + ".gz")
        assert save_table_with_header(
            fname + ".bz",
            data,
            header=headerstr,
            compressionmethod="gzip",
            match_filename_to_compression=True,
        ) == (fname + ".bz.gz")
        assert save_table_with_header(
            fname + ".gz",
            data,
            header=headerstr,
            compressionmethod="bzip",
            match_filename_to_compression=True,
        ) == (fname + ".gz.bz")

        # do as I told cases, extension does not match compression
        assert save_table_with_header(
            fname + ".gz",
            data,
            header=headerstr,
            compressionmethod=None,
            match_filename_to_compression=False,
        ) == (fname + ".gz")
        assert save_table_with_header(
            fname,
            data,
            header=headerstr,
            compressionmethod="gzip",
            match_filename_to_compression=False,
        ) == (fname)
        assert save_table_with_header(
            fname,
            data,
            header=headerstr,
            compressionmethod="bzip",
            match_filename_to_compression=False,
        ) == (fname)
