from collections import defaultdict
import numpy as np

from tablite.base import BaseTable
from tablite.utils import unique_name, sub_cls_check
from tablite.nimlite import groupby
from tablite.config import Config

from tqdm import tqdm as _tqdm

def pivot(T, rows, columns, functions, values_as_rows=True, tqdm=_tqdm, pbar=None):
    """
    param: rows: column names to keep as rows
    param: columns: column names to keep as columns
    param: functions: aggregation functions from the Groupby class as

    example:
    ```
    >>> t.show()
    +=====+=====+=====+
    |  A  |  B  |  C  |
    | int | int | int |
    +-----+-----+-----+
    |    1|    1|    6|
    |    1|    2|    5|
    |    2|    3|    4|
    |    2|    4|    3|
    |    3|    5|    2|
    |    3|    6|    1|
    |    1|    1|    6|
    |    1|    2|    5|
    |    2|    3|    4|
    |    2|    4|    3|
    |    3|    5|    2|
    |    3|    6|    1|
    +=====+=====+=====+

    >>> t2 = t.pivot(rows=['C'], columns=['A'], functions=[('B', gb.sum)])
    >>> t2.show()
    +===+===+========+=====+=====+=====+
    | # | C |function|(A=1)|(A=2)|(A=3)|
    |row|int|  str   |mixed|mixed|mixed|
    +---+---+--------+-----+-----+-----+
    |0  |  6|Sum(B)  |    2|None |None |
    |1  |  5|Sum(B)  |    4|None |None |
    |2  |  4|Sum(B)  |None |    6|None |
    |3  |  3|Sum(B)  |None |    8|None |
    |4  |  2|Sum(B)  |None |None |   10|
    |5  |  1|Sum(B)  |None |None |   12|
    +===+===+========+=====+=====+=====+
    ```

    """
    pass


def transpose(T, tqdm=_tqdm):
    """performs a CCW matrix rotation of the table."""
    pass


def pivot_transpose(T, columns, keep=None, column_name="transpose", value_name="value", tqdm=_tqdm):
    """Transpose a selection of columns to rows.

    Args:
        columns (list of column names): column names to transpose
        keep (list of column names): column names to keep (repeat)

    Returns:
        Table: with columns transposed to rows

    Example:
        transpose columns 1,2 and 3 and transpose the remaining columns, except `sum`.

    Input:
    ```
    | col1 | col2 | col3 | sun | mon | tue | ... | sat | sum  |
    |------|------|------|-----|-----|-----|-----|-----|------|
    | 1234 | 2345 | 3456 | 456 | 567 |     | ... |     | 1023 |
    | 1244 | 2445 | 4456 |     |   7 |     | ... |     |    7 |
    | ...  |      |      |     |     |     |     |     |      |

    >>> t.transpose(keep=[col1, col2, col3], transpose=[sun,mon,tue,wed,thu,fri,sat])`

    Output:
    |col1| col2| col3| transpose| value|
    |----|-----|-----|----------|------|
    |1234| 2345| 3456| sun      |   456|
    |1234| 2345| 3456| mon      |   567|
    |1244| 2445| 4456| mon      |     7|
    ```

    """
    pass
