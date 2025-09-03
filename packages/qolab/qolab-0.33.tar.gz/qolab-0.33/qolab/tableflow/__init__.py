"""
Provide basic method to process data describing tables.

Created by Eugeniy E. Mikhailov 2024/05/27

The basic idea that we will have an *input* table
with data description and we (re)generate *output* table
based on the input table with processed rows.

If output table already have processed rows with entries different from NA
such rows are skipped.

Super handy for bulk processing data files where only a few parameters changed.
"""

import pandas as pd
import numpy as np
import warnings


def loadInOutTables(inputFileName=None, outputFileName=None, comment=None):
    """Load the input and the output tables from files.

    The output table loaded only if the corresponding file exists.
    Otherwise it is a clone of the input table.

    Parameters
    ==========
    inputFileName : path or string
        Path to the input table filename. If this file does not exists,
        return None for both tables.
    outputFileName : path or string or None
        Path to the output table filename. If such file does not exit,
        clone the input table to the output one.
    comment : string or None (default)
        String which indicates a comment in the input `csv` file.
        Usually it is either '#' or '%'. If set to None, internally changed to '#'.
    """
    if not inputFileName:
        return None, None

    if not comment:
        comment = "#"

    tIn = pd.read_csv(inputFileName, comment=comment)
    tIn.columns = tIn.columns.str.removeprefix(" ")
    # clean up leading white space in columns names

    try:
        tOut = pd.read_csv(outputFileName, comment=comment)
    except Exception:
        tOut = tIn.copy(deep=True)

    return tIn, tOut


def ilocRowOrAdd(tbl, row):
    """Find a row in a table (`tbl`) similar to a provided `row`.

    NA in both sets treated as a match.
    If similar 'row' not found in the table, insert it.

    `tbl` can have more columns than `row` but all columns of `row`
    must be present in `tbl`.

    i.e. we looking for the following match
    # (tSub == row) | (tSub.isna() & row.isna())
    """
    # pandas is extremely slow to work with selections/views
    # so we transform everything to numpy
    t = tbl.to_numpy()
    cols = tbl.columns.to_numpy()
    r = row.to_numpy()
    colsRow = row.keys()
    res = np.zeros(t.shape, dtype=bool)  # array filled with False

    # columns not in row are not part of comparison so we set them to True
    for idx, c in enumerate(cols):
        if c not in colsRow:
            res[:, idx] = True

    for idx, c in enumerate(colsRow):
        if c not in cols:
            warnings.warn(f"input table is missing column '{c}'")
            continue
        if pd.isna(r[idx]):
            res[:, cols == c] = pd.isna(t[:, cols == c])
            continue
        res[:, cols == c] = t[:, cols == c] == r[idx]
    match = res.all(axis=1)
    if np.any(match):
        return np.where(match)[0][0]
    # we need to create new row since tbl does not has it
    i = len(tbl)
    updateTblRowAt(tbl, i, row)
    return i


def updateTblRowAt(tbl, i, row):
    """Update row  with position 'i' in the table ('tbl') with values from 'row'."""
    for k in row.keys():
        tbl.at[i, k] = row[k]
    return


def isRedoNeeded(row, cols2check):
    """Check is Redo required in a given row.

    Redo is required if *all* required entries in 'cols2check' are NA
    or we are missing columns in cols2check list

    Parameters
    ==========
    row: pandas row
        row to perform check on
    cols2check: list of strings
        List of strings with column names which considered as generated outputs.
    """
    for c in cols2check:
        if c not in row.keys():
            return True
    if row[cols2check].isna().all():
        return True
    return False


def reflowTable(
    tIn,
    tOut,
    process_row_func=None,
    postProcessedColums=None,
    extraInfo=None,
    redo=False,
):
    """Reflow/update table tOut in place based on the inputs specified in table tIn.

    Effectively maps unprocessed rows to ``process_row_func``.

    Parameters
    ==========
    postProcessedColums : list of strings
        List of column names which need to be generated
    extraInfo : dictionary (optional)
        Dictionary of additional parameter supplied to ``process_row_func``
    process_row_func : function
        Function which will take a row from the input table and generate
        row with post processed entries (columns).
        Expected to have signature like:
        ``rowOut = process_row_func(rowIn, extraInfo=userInfo)``
    redo : True or False (default)
        Flag indicating if reflow is needed unconditionally
        (i.e. True forces reflow of all entries).
    """
    if not process_row_func:
        warnings.warn("process_row_func is not provided, exiting reflowTable")
        return
    if not postProcessedColums:
        warnings.warn("postProcessedColums are not provided, exiting reflowTable")
        return

    for index, rowIn in tIn.iterrows():
        iOut = ilocRowOrAdd(tOut, rowIn)
        rowOutBefore = tOut.iloc[iOut]

        if not (redo or isRedoNeeded(rowOutBefore, postProcessedColums)):
            continue

        # processing data describing row
        rowOut = process_row_func(rowOutBefore, extraInfo=extraInfo)
        updateTblRowAt(tOut, iOut, rowOut)
