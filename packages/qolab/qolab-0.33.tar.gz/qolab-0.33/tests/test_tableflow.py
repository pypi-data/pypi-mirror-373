import pytest
import qolab.tableflow as tblfl
import pandas as pd


def test_table_load_noinputs():
    assert tblfl.loadInOutTables() == (None, None)
    assert tblfl.loadInOutTables(
        inputFileName=None, outputFileName="non_existing_file"
    ) == (None, None)


def test_wrong_comment_in_table_file_to_load():
    with pytest.raises(Exception):
        # should raise ParserError
        tblfl.loadInOutTables(
            inputFileName="tests/tableflow_test_data/tableIn1.csv",
            outputFileName=None,
            comment="%",
        )


def test_right_comment_in_table_file_to_load():
    tIn, tOut = tblfl.loadInOutTables(
        inputFileName="tests/tableflow_test_data/tableIn1.csv",
        outputFileName=None,
        comment="#",
    )
    assert isinstance(tIn, pd.core.frame.DataFrame)


def test_table_equality_with_no_output_file_name():
    tIn, tOut = tblfl.loadInOutTables(
        inputFileName="tests/tableflow_test_data/tableIn1.csv",
        outputFileName=None,
        comment="#",
    )
    assert isinstance(tIn, pd.core.frame.DataFrame)
    assert isinstance(tOut, pd.core.frame.DataFrame)
    assert tIn.equals(tOut)
    col0 = tIn.keys()[0]
    vBefore = tIn.at[0, col0]
    tIn.at[0, col0] = vBefore + 1
    assert not tIn.equals(tOut)


def test_table_load_with_in_out_file_names():
    # different filenames, same content for ease of testing
    tIn, tOut = tblfl.loadInOutTables(
        inputFileName="tests/tableflow_test_data/tableIn1.csv",
        outputFileName="tests/tableflow_test_data/tableOut1nonProcessed.csv",
        comment="#",
    )
    assert isinstance(tIn, pd.core.frame.DataFrame)
    assert isinstance(tOut, pd.core.frame.DataFrame)
    assert tIn.equals(tOut)

    # different filenames, different content
    tIn, tOut = tblfl.loadInOutTables(
        inputFileName="tests/tableflow_test_data/tableIn1.csv",
        outputFileName="tests/tableflow_test_data/tableOut1pariallyProcessed.csv",
        comment="#",
    )
    assert isinstance(tIn, pd.core.frame.DataFrame)
    assert isinstance(tOut, pd.core.frame.DataFrame)
    assert not tIn.equals(tOut)
    assert "out1" in tOut.columns
    assert "out1" not in tIn.columns


def test_for_existing_row():
    tbl1 = pd.DataFrame({"a": [1, 2, 3], "b": [1, 4, 6]})
    r = pd.Series({"a": 2, "b": 4})
    assert tblfl.ilocRowOrAdd(tbl1, r) == 1


def test_for_existing_row_with_NA():
    # NA in both table and raw should return a hit
    tbl1 = pd.DataFrame({"a": [1, 2, 3], "b": [1, pd.NA, 6]})
    r = pd.Series({"a": 2, "b": pd.NA})
    assert tblfl.ilocRowOrAdd(tbl1, r) == 1

    # should insert new row
    tbl1 = pd.DataFrame({"a": [1, 2, 3], "b": [1, 4, 6]})
    r = pd.Series({"a": 2, "b": pd.NA})
    assert tblfl.ilocRowOrAdd(tbl1, r) == 3

    # should insert new row
    tbl1 = pd.DataFrame({"a": [1, 2, 3], "b": [1, 4, 6]})
    r = pd.Series({"a": 2, "b": pd.NA})
    assert tblfl.ilocRowOrAdd(tbl1, r) == 3


def test_for_nonexisting_row_and_its_insertion():
    tbl1 = pd.DataFrame({"a": [1, 2, 3], "b": [1, 4, 6]})
    r = pd.Series({"a": 2, "b": 10})
    assert len(tbl1) == 3
    assert tblfl.ilocRowOrAdd(tbl1, r) == 3
    assert len(tbl1) == 4


def test_isRedoNeeded():
    r = pd.Series({"a": 2, "b": 4, "c": pd.NA})
    assert not tblfl.isRedoNeeded(r, ["a", "b"])
    assert tblfl.isRedoNeeded(r, ["c"])
    assert tblfl.isRedoNeeded(r, ["non_existing"])
    assert not tblfl.isRedoNeeded(r, ["b", "c"])


def test_reflowTable():
    tIn, tOut = tblfl.loadInOutTables(
        inputFileName="tests/tableflow_test_data/tableIn1.csv",
        outputFileName="tests/tableflow_test_data/tableOut1pariallyProcessed.csv",
        comment="#",
    )
    # check for warnings
    with pytest.warns(UserWarning):
        tblfl.reflowTable(tIn, tOut)

    with pytest.warns(UserWarning):
        tblfl.reflowTable(tIn, tOut, postProcessedColums=["dummyName"])

    def frow(row):
        return row

    with pytest.warns(UserWarning):
        tblfl.reflowTable(tIn, tOut, process_row_func=frow)

    # now run reflow
    def frow(row, extraInfo=None):
        rowOut = row.copy()
        rowOut["out1"] = row["x"] * row["x"]
        return rowOut

    assert len(tIn) != len(tOut)
    tblfl.reflowTable(
        tIn, tOut, process_row_func=frow, postProcessedColums=["out1", "out2"]
    )
    assert len(tIn) == len(tOut)
    assert (tOut["out1"] == tOut["x"] * tOut["x"]).all()

    # check that reflow is done
    tOut.loc[tOut["x"] == 1, "out1"] = pd.NA
    tblfl.reflowTable(
        tIn, tOut, process_row_func=frow, postProcessedColums=["out1", "out2"]
    )
    assert (tOut["out1"] == tOut["x"] * tOut["x"]).all()

    # check that reflow is not reprocessed
    tOut.loc[tOut["x"] == 1, "out1"] = 12121  # crazy number
    tblfl.reflowTable(
        tIn, tOut, process_row_func=frow, postProcessedColums=["out1", "out2"]
    )
    assert (tOut.loc[tOut["x"] == 1, "out1"] == 12121).all()  # should not change

    # now we are forcing redo
    tOut.loc[tOut["x"] == 1, "out1"] = 12121  # crazy number
    tblfl.reflowTable(
        tIn,
        tOut,
        process_row_func=frow,
        postProcessedColums=["out1", "out2"],
        redo=True,
    )
    assert not (tOut.loc[tOut["x"] == 1, "out1"] == 12121).all()  # must not be the same
    assert (tOut["out1"] == tOut["x"] * tOut["x"]).all()
