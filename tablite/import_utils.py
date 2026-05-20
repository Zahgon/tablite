
import numpy as np
import os
import math
import platform
import psutil
import csv
from pathlib import Path
import openpyxl
try:
    from pandas import read_excel, isna
except ModuleNotFoundError:
    pass
from tablite.utils import load_numpy, py_to_nim_encoding
import sys
import warnings
import logging

import struct
import pickle as pkl

from datetime import date, time, datetime

from mplite import TaskManager, Task

import tablite.nimlite as nimlite
from tablite.datatypes import DataTypes, list_to_np_array
from tablite.config import Config
from tablite.file_reader_utils import TextEscape, get_encoding, get_delimiter, ENCODING_GUESS_BYTES
from tablite.utils import type_check, unique_name, fixup_worksheet, strip_escape
from tablite.base import BaseTable, Page, Column

from tqdm import tqdm as _tqdm

logging.getLogger("lml").propagate = False
logging.getLogger("pyexcel_io").propagate = False
logging.getLogger("pyexcel").propagate = False


def from_pandas(T, df):
    """
    Creates Table using pd.to_dict('list')

    similar to:
    >>> import pandas as pd
    >>> df = pd.DataFrame({'a':[1,2,3], 'b':[4,5,6]})
    >>> df
        a  b
        0  1  4
        1  2  5
        2  3  6
    >>> df.to_dict('list')
    {'a': [1, 2, 3], 'b': [4, 5, 6]}

    >>> t = Table.from_dict(df.to_dict('list))
    >>> t.show()
        +===+===+===+
        | # | a | b |
        |row|int|int|
        +---+---+---+
        | 0 |  1|  4|
        | 1 |  2|  5|
        | 2 |  3|  6|
        +===+===+===+
    """
    pass


def from_hdf5(T, path, tqdm=_tqdm, pbar=None):
    """
    imports an exported hdf5 table.

    Note that some loss of type information is to be expected in columns of mixed type:
    >>> t.show(dtype=True)
    +===+===+=====+=====+====+=====+=====+===================+==========+========+===============+===+=========================+=====+===+
    | # | A |  B  |  C  | D  |  E  |  F  |         G         |    H     |   I    |       J       | K |            L            |  M  | O |
    |row|int|mixed|float|str |mixed| bool|      datetime     |   date   |  time  |   timedelta   |str|           int           |float|int|
    +---+---+-----+-----+----+-----+-----+-------------------+----------+--------+---------------+---+-------------------------+-----+---+
    | 0 | -1|None | -1.1|    |None |False|2023-06-09 09:12:06|2023-06-09|09:12:06| 1 day, 0:00:00|b  |-100000000000000000000000|  inf| 11|
    | 1 |  1|    1|  1.1|1000|1    | True|2023-06-09 09:12:06|2023-06-09|09:12:06|2 days, 0:06:40|嗨 | 100000000000000000000000| -inf|-11|
    +===+===+=====+=====+====+=====+=====+===================+==========+========+===============+===+=========================+=====+===+
    >>> t.to_hdf5(filename)
    >>> t2 = Table.from_hdf5(filename)
    >>> t2.show(dtype=True)
    +===+===+=====+=====+=====+=====+=====+===================+===================+========+===============+===+=========================+=====+===+
    | # | A |  B  |  C  |  D  |  E  |  F  |         G         |         H         |   I    |       J       | K |            L            |  M  | O |
    |row|int|mixed|float|mixed|mixed| bool|      datetime     |      datetime     |  time  |      str      |str|           int           |float|int|
    +---+---+-----+-----+-----+-----+-----+-------------------+-------------------+--------+---------------+---+-------------------------+-----+---+
    | 0 | -1|None | -1.1|None |None |False|2023-06-09 09:12:06|2023-06-09 00:00:00|09:12:06|1 day, 0:00:00 |b  |-100000000000000000000000|  inf| 11|
    | 1 |  1|    1|  1.1| 1000|    1| True|2023-06-09 09:12:06|2023-06-09 00:00:00|09:12:06|2 days, 0:06:40|嗨 | 100000000000000000000000| -inf|-11|
    +===+===+=====+=====+=====+=====+=====+===================+===================+========+===============+===+=========================+=====+===+
    """
    pass


def from_json(T, jsn):
    """
    Imports tables exported using .to_json
    """
    pass







def excel_reader(T, path, first_row_has_headers=True, header_row_index=0, sheet=None, columns=None, skip_empty="NONE", start=0, limit=sys.maxsize, tqdm=_tqdm, **kwargs):
    """
    returns Table from excel

    **kwargs are excess arguments that are ignored.
    """
    pass


def ods_reader(T, path, first_row_has_headers=True, header_row_index=0, sheet=None, columns=None, skip_empty="NONE", start=0, limit=sys.maxsize, **kwargs):
    """
    returns Table from .ODS
    """
    pass


class TRconfig(object):
    def __init__(
        self,
        source,
        destination,
        start,
        end,
        guess_datatypes,
        delimiter,
        text_qualifier,
        text_escape_openings,
        text_escape_closures,
        strip_leading_and_tailing_whitespace,
        encoding,
        newline_offsets,
        fields
    ) -> None:
        self.source = source
        self.destination = destination
        self.start = start
        self.end = end
        self.guess_datatypes = guess_datatypes
        self.delimiter = delimiter
        self.text_qualifier = text_qualifier
        self.text_escape_openings = text_escape_openings
        self.text_escape_closures = text_escape_closures
        self.strip_leading_and_tailing_whitespace = strip_leading_and_tailing_whitespace
        self.encoding = encoding
        self.newline_offsets = newline_offsets
        self.fields = fields
        type_check(start, int),
        type_check(end, int),
        type_check(delimiter, str),
        type_check(text_qualifier, (str, type(None))),
        type_check(text_escape_openings, str),
        type_check(text_escape_closures, str),
        type_check(encoding, str),
        type_check(strip_leading_and_tailing_whitespace, bool),
        type_check(newline_offsets, list)
        type_check(fields, dict)

    def copy(self):
        return TRconfig(**self.dict())





def text_reader_task(
    source,
    destination,
    start,
    end,
    guess_datatypes,
    delimiter,
    text_qualifier,
    text_escape_openings,
    text_escape_closures,
    strip_leading_and_tailing_whitespace,
    encoding,
    newline_offsets,
    fields
):
    """PARALLEL TASK FUNCTION
    reads columnsname + path[start:limit] into hdf5.

    source: csv or txt file
    destination: filename for page.
    start: int: start of page.
    end: int: end of page.
    guess_datatypes: bool: if True datatypes will be inferred by datatypes.Datatypes.guess
    delimiter: ',' ';' or '|'
    text_qualifier: str: commonly \"
    text_escape_openings: str: default: "({[
    text_escape_closures: str: default: ]})"
    strip_leading_and_tailing_whitespace: bool
    encoding: chardet encoding ('utf-8, 'ascii', ..., 'ISO-22022-CN')
    """
    pass






file_readers = {  # dict of file formats and functions used during Table.import_file
    "fods": excel_reader,
    "json": excel_reader,
    "html": from_html,
    "hdf5": from_hdf5,
    "simple": excel_reader,
    "rst": excel_reader,
    "mediawiki": excel_reader,
    "xlsx": excel_reader,
    "xls": excel_reader,
    "xlsm": excel_reader,
    "csv": text_reader,
    "tsv": text_reader,
    "txt": text_reader,
    "ods": ods_reader,
}

valid_readers = ",".join(list(file_readers.keys()))

