import csv
from tablite.utils import sub_cls_check, type_check
from tablite.base import BaseTable
from tablite.config import Config
from tablite.datatypes import DataTypes
from pathlib import Path


from tqdm import tqdm as _tqdm


def to_sql(table, name):
    """
    generates ANSI-92 compliant SQL.

    args:
        name (str): name of SQL table.
    """
    pass


def to_pandas(table):
    """
    returns pandas.DataFrame
    """
    pass


def to_hdf5(table, path):
    # fmt: off
    """
    creates a copy of the table as hdf5

    Note that some loss of type information is to be expected in columns of mixed type:
    >>> t.show(dtype=True)
    +===+===+=====+=====+====+=====+=====+===================+==========+========+===============+===+=========================+=====+===+
    | # | A |  B  |  C  | D  |  E  |  F  |         G         |    H     |   I    |       J       | K |            L            |  M  | O |
    |row|int|mixed|float|str |mixed| bool|      datetime     |   date   |  time  |   timedelta   |str|           int           |float|int|
    +---+---+-----+-----+----+-----+-----+-------------------+----------+--------+---------------+---+-------------------------+-----+---+
    | 0 | -1|None | -1.1|    |None |False|2023-06-09 09:12:06|2023-06-09|09:12:06| 1 day, 0:00:00|b  |-100000000000000000000000|  inf| 11|
    | 1 |  1|    1|  1.1|1000|1    | True|2023-06-09 09:12:06|2023-06-09|09:12:06|2 days, 0:06:40|嗨  | 100000000000000000000000| -inf|-11|
    +===+===+=====+=====+====+=====+=====+===================+==========+========+===============+===+=========================+=====+===+
    >>> t.to_hdf5(filename)
    >>> t2 = Table.from_hdf5(filename)
    >>> t2.show(dtype=True)
    +===+===+=====+=====+=====+=====+=====+===================+===================+========+===============+===+=========================+=====+===+
    | # | A |  B  |  C  |  D  |  E  |  F  |         G         |         H         |   I    |       J       | K |            L            |  M  | O |
    |row|int|mixed|float|mixed|mixed| bool|      datetime     |      datetime     |  time  |      str      |str|           int           |float|int|
    +---+---+-----+-----+-----+-----+-----+-------------------+-------------------+--------+---------------+---+-------------------------+-----+---+
    | 0 | -1|None | -1.1|None |None |False|2023-06-09 09:12:06|2023-06-09 00:00:00|09:12:06|1 day, 0:00:00 |b  |-100000000000000000000000|  inf| 11|
    | 1 |  1|    1|  1.1| 1000|    1| True|2023-06-09 09:12:06|2023-06-09 00:00:00|09:12:06|2 days, 0:06:40|嗨  | 100000000000000000000000| -inf|-11|
    +===+===+=====+=====+=====+=====+=====+===================+===================+========+===============+===+=========================+=====+===+
    """
    pass


def excel_writer(table, path):
    """
    writer for excel files.

    This can create xlsx files beyond Excels.
    If you're using pyexcel to read the data, you'll see the data is there.
    If you're using Excel, Excel will stop loading after 1,048,576 rows.

    See pyexcel for more details:
    http://docs.pyexcel.org/
    """
    pass






def text_writer(table, path, tqdm=_tqdm):
    """exports table to csv, tsv or txt dependening on path suffix.
    follows the JSON norm. text escape is ON for all strings.

    Note:
    ----------------------
    If the delimiter is present in a string when the string is exported,
    text-escape is required, as the format otherwise is corrupted.
    When the file is being written, it is unknown whether any string in
    a column contrains the delimiter. As text escaping the few strings
    that may contain the delimiter would lead to an assymmetric format,
    the safer guess is to text escape all strings.
    """
    pass






