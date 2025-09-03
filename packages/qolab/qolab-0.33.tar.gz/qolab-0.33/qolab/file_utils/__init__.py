import platform
import re
import os
from datetime import date


def filename2os_fname(fname):
    r"""Translate Windows or Linux filename to OS dependent style.
    Takes in account the notion of 'Z:' drive on different systems.

    In particular replaces Z: <==> /mnt/qol_grp_data  and \\ <==> /

    Example
    -------
    >>> filename2os_fname("Z:\\dir1\\dir2\\file")  # when run on Linux
    '/mnt/qol_grp_data/dir1/dir2/file'
    """
    if platform.system() == "Windows":
        fname = re.sub("/mnt/qol_grp_data", "Z:", fname)
    else:
        fname = re.sub("Z:", "/mnt/qol_grp_data", fname)
        fname = re.sub(r"\\", "/", fname)

    fname = os.path.normpath(fname)
    return fname


def get_runnum(data_dir):
    r"""Reads, increments data counter and saves it back in the provided `data_dir`.
    If necessary creates counter file and full path to it.

    Examples
    --------
    >>> get_runnum('Z:\\Ramsi_EIT\\data\\')
    >>> get_runnum('/mnt/qol_grp_data/data')
    """
    data_dir = filename2os_fname(data_dir)
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    if not os.path.isdir(data_dir):
        print(f"ERROR: cannot create directory for data: {data_dir}")
        print("Will use current dir for storage")
        data_dir = "."

    runnumpath = os.path.join(data_dir, "autofile")
    # convert to OS dependent way
    runnumpath = filename2os_fname(runnumpath)

    if not os.path.exists(runnumpath):
        os.mkdir(runnumpath)
    runnum_file = os.path.join(runnumpath, "runnum.dat")
    runnum_file = filename2os_fname(runnum_file)

    run_number = 0
    if os.path.isfile(runnum_file):
        with open(runnum_file, "r") as f:
            content = f.readlines()
            run_number = int(content[0])
            f.close()

    # Increment it and fold if needed
    run_number = run_number + 1
    # Important: we are using five digit counters to synchronize
    # with qol_get_next_data_file.m
    if run_number > 99999:
        run_number = 0

    with open(runnum_file, "w") as f:
        f.write(f"{run_number}")
        f.close()
    return run_number


def get_next_data_file(
    prefix,
    savepath,
    run_number=None,
    datestr=None,
    date_format="%Y%m%d",
    extension="dat",
):
    """Generate a filename according to a standard naming scheme
    fname = os.path.join(savepath, f'{prefix}_{datestr}_{run_number:05d}.{extension}')
    if run_number is missing, acquires it with `get_runnum( savepath )`
    """
    if run_number is None:
        run_number = get_runnum(savepath)
    today = date.today()
    if datestr is None:
        datestr = today.strftime(date_format)
    fname = os.path.join(savepath, f"{prefix}_{datestr}_{run_number:05d}.{extension}")
    return fname


def infer_compression(fname):
    """Infers compression algorithm from filename extension"""
    compression = None  # usual suspect
    b, fext = os.path.splitext(fname)
    if fext == ".gz":
        compression = "gzip"
    elif (fext == ".bz") or (fext == ".bz2"):
        compression = "bzip"
    return compression


def save_table_with_header(
    fname,
    data,
    header="",
    comment_symbol="%",
    skip_headers_if_file_exist=False,
    item_format="e",
    item_separator="\t",
    compressionmethod=None,
    compresslevel=9,
    match_filename_to_compression=True,
):
    r"""Saves output to CSV or TSV file with specially formatted header.

    The file is appended if needed.
    It is possible to compress output file.

    Parameters
    ----------
    fname : string, full path of the saved file.
    data : array type (python or numpy).
    header : list or array of header strings to put at the beginning of the record
    comment_symbol : prefix for the header lines, default is '%'.
        Note that headers are actually prefixed with <comment_symbol> and <space>.
        Historically it is chosen as '%' to make files compatible with Matlab `load`.
        '#' symbmol is also good choice.
    skip_headers_if_file_exist : True or False (default).
        When True skip addition of headers in already existing file.
        Useful when appending to file with the same headers.
    item_format : output format like in formatted strings, examples are 'e', '.15e', 'f'
    item_separator : how to separate columns, '\t' is default.
        Natural choices are either ',' (comma) or '\t' (tab).
    compressionmethod :  compression method
        - None : no compression (default)
        - gzip : gzip method of compression
        - bzip : bzip2 method of compression
    compresslevel : 0 to 9 (default)
        Compression level as it is defined for gzip in Lib/gzip.py
        - 0 : no compression at all
        - 9 : the highest compression (default)
    match_filename_to_compression: True (default) or False
        If True changes the filename suffix in accordance with compression method,
        e.g. 'data.dat' -> 'data.dat.gz' if compression is set to 'gzip',
        otherwise assumes that users know what they do.
        However, there is one important distinction to make compression enabling back
        compatible with old code which does not have place to set compression, but
        still want to use it.
        If compressionmethod is None, but inferred from a filename compression is not None,
        than we do what filename prescribes.
    """
    fname = filename2os_fname(fname)
    compression_infered = infer_compression(fname)
    if (compression_infered != compressionmethod) and match_filename_to_compression:
        if (compressionmethod is None) and (compression_infered is not None):
            compressionmethod = compression_infered
        elif compressionmethod == "gzip":
            fname += ".gz"
        elif compressionmethod == "bzip":
            fname += ".bz"
    file_exist_flag = os.path.exists(fname)
    item_format = str.join("", ["{", f":{item_format}", "}"])
    _open = open  # standard file handler
    if compressionmethod == "gzip":
        import gzip

        _open = lambda fname, mode: gzip.open(  # noqa: E731
            fname, mode=mode, compresslevel=compresslevel
        )
    if compressionmethod == "bzip":
        import bz2

        _open = lambda fname, mode: bz2.open(  # noqa: E731
            fname, mode=mode, compresslevel=compresslevel
        )
    with _open(fname, mode="ab") as f:
        if not (file_exist_flag and skip_headers_if_file_exist):
            for line in header:
                f.write(f"{comment_symbol} {line}\n".encode("utf-8"))
        if data is not None:
            for r in data:
                line = item_separator.join(map(item_format.format, r))
                f.write(line.encode("utf-8"))
                f.write("\n".encode("utf-8"))
        f.close()
    return fname
