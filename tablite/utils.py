from collections import defaultdict
import math
import re
import os
from time import time as now
from pathlib import Path
import numpy as np
import ast
from datetime import datetime, date, time, timedelta  # noqa
from itertools import compress
import string
import random
import xml.parsers.expat as expat
import logging
from tablite.config import Config

letters = string.ascii_lowercase + string.digits
NoneType = type(None)




def type_check(var, kind):
    if not isinstance(var, kind):
        raise TypeError(f"Expected {kind}, not {type(var)}")


def sub_cls_check(c, kind):
    if not issubclass(type(c), kind):
        raise TypeError(f"Expected {kind}, not {type(c)}")


def name_check(options, *names):
    for n in names:
        if n not in options:
            raise ValueError(f"{n} not in {options}")


def unique_name(wanted_name, set_of_names):
    """
    returns a wanted_name as wanted_name_i given a list of names
    which guarantees unique naming.
    """
    if not isinstance(set_of_names, set):
        set_of_names = set(set_of_names)
    name, i = wanted_name, 1
    while name in set_of_names:
        name = f"{wanted_name}_{i}"
        i += 1
    return name


def expression_interpreter(expression, columns):
    """
    Interprets valid expressions such as:

        "all((A==B, C!=4, 200<D))"

    as:
        def _f(A,B,C,D):
            return all((A==B, C!=4, 200<D))

    using python's compiler.
    """
    if not isinstance(expression, str):
        raise TypeError(f"`{expression}` is not a str")
    if not isinstance(columns, list):
        raise TypeError
    if not all(isinstance(i, str) for i in columns):
        raise TypeError

    req_columns = ", ".join(i for i in columns if i in expression)
    script = f"def f({req_columns}):\n    return {expression}"
    tree = ast.parse(script)
    code = compile(tree, filename="blah", mode="exec")
    namespace = {}
    exec(code, namespace)
    f = namespace["f"]
    if not callable(f):
        raise ValueError(f"The expression could not be parse: {expression}")
    return f


def intercept(A, B):
    """Enables calculation of the intercept of two range objects.
    Used to determine if a datablock contains a slice.

    Args:
        A: range
        B: range

    Returns:
        range: The intercept of ranges A and B.
    """
    type_check(A, range)
    type_check(B, range)

    if A.step < 1:
        A = range(A.stop + 1, A.start + 1, 1)
    if B.step < 1:
        B = range(B.stop + 1, B.start + 1, 1)

    if len(A) == 0:
        return range(0)
    if len(B) == 0:
        return range(0)

    if A.stop <= B.start:
        return range(0)
    if A.start >= B.stop:
        return range(0)

    if A.start <= B.start:
        if A.stop <= B.stop:
            start, end = B.start, A.stop
        elif A.stop > B.stop:
            start, end = B.start, B.stop
        else:
            raise ValueError("bad logic")
    elif A.start < B.stop:
        if A.stop <= B.stop:
            start, end = A.start, A.stop
        elif A.stop > B.stop:
            start, end = A.start, B.stop
        else:
            raise ValueError("bad logic")
    else:
        raise ValueError("bad logic")

    a_steps = math.ceil((start - A.start) / A.step)
    a_start = (a_steps * A.step) + A.start

    b_steps = math.ceil((start - B.start) / B.step)
    b_start = (b_steps * B.step) + B.start

    if A.step == 1 or B.step == 1:
        start = max(a_start, b_start)
        step = max(A.step, B.step)
        return range(start, end, step)
    elif A.step == B.step:
        a, b = min(A.start, B.start), max(A.start, B.start)
        if (b - a) % A.step != 0:  # then the ranges are offset.
            return range(0)
        else:
            return range(b, end, step)
    else:
        # determine common step size:
        step = max(A.step, B.step) if math.gcd(A.step, B.step) != 1 else A.step * B.step
        # examples:
        # 119 <-- 17 if 1 != 1 else 119 <-- max(7, 17) if math.gcd(7, 17) != 1 else 7 * 17
        #  30 <-- 30 if 3 != 1 else 90 <-- max(3, 30) if math.gcd(3, 30) != 1 else 3*30
        if A.step < B.step:
            for n in range(a_start, end, A.step):  # increment in smallest step to identify the first common value.
                if n < b_start:
                    continue
                elif (n - b_start) % B.step == 0:
                    return range(n, end, step)  # common value found.
        else:
            for n in range(b_start, end, B.step):
                if n < a_start:
                    continue
                elif (n - a_start) % A.step == 0:
                    return range(n, end, step)

        return range(0)


# This list is the contract:
required_keys = {
    "min",
    "max",
    "mean",
    "median",
    "stdev",
    "mode",
    "distinct",
    "iqr_low",
    "iqr_high",
    "iqr",
    "sum",
    "summary type",
    "histogram",
}


def summary_statistics(values, counts):
    """
    values: any type
    counts: integer

    returns dict with:
    - min (int/float, length of str, date)
    - max (int/float, length of str, date)
    - mean (int/float, length of str, date)
    - median (int/float, length of str, date)
    - stdev (int/float, length of str, date)
    - mode (int/float, length of str, date)
    - distinct (number of distinct values)
    - iqr (int/float, length of str, date)
    - sum (int/float, length of str, date)
    - histogram (2 arrays: values, count of each values)
    """
    # determine the dominant datatype:
    dtypes = defaultdict(int)
    most_frequent, most_frequent_dtype = 0, int
    for v, c in zip(values, counts):
        dtype = type(v)
        total = dtypes[dtype] + c
        dtypes[dtype] = total
        if total > most_frequent:
            most_frequent_dtype = dtype
            most_frequent = total

    if most_frequent == 0:
        return {}

    most_frequent_dtype = max(dtypes, key=dtypes.get)
    mask = [type(v) == most_frequent_dtype for v in values]
    v = list(compress(values, mask))
    c = list(compress(counts, mask))

    f = summary_methods.get(most_frequent_dtype, int)
    result = f(v, c)
    result["distinct"] = len(values)
    result["summary type"] = most_frequent_dtype.__name__
    result["histogram"] = [values, counts]
    assert set(result.keys()) == required_keys, "Key missing!"
    return result


















summary_methods = {
    bool: _boolean_statistics_summary,
    int: _numeric_statistics_summary,
    float: _numeric_statistics_summary,
    str: _string_statistics_summary,
    date: _date_statistics_summary,
    datetime: _datetime_statistics_summary,
    time: _time_statistics_summary,
    timedelta: _timedelta_statistics_summary,
    type(None): _none_type_summary,
}


def date_range(start, stop, step):
    if not isinstance(start, datetime):
        raise TypeError("start is not datetime")
    if not isinstance(stop, datetime):
        raise TypeError("stop is not datetime")
    if not isinstance(step, timedelta):
        raise TypeError("step is not timedelta")
    n = (stop - start) // step
    return [start + step * i for i in range(n)]


def dict_to_rows(d):
    type_check(d, dict)
    rows = []
    max_length = max(len(i) for i in d.values())
    order = list(d.keys())
    rows.append(order)
    for i in range(max_length):
        row = [d[k][i] for k in order]
        rows.append(row)
    return rows


def calc_col_count(letters: str):
    ord_nil = ord("A") - 1
    cols_per_letter = ord("Z") - ord_nil
    col_count = 0

    for i, v in enumerate(reversed(letters)):
        col_count = col_count + (ord(v) - ord_nil) * pow(cols_per_letter, i)

    return col_count


def calc_true_dims(sheet):
    src = sheet._get_source()
    max_col, max_row = 0, 0

    regex = re.compile("\d+")


    parser = expat.ParserCreate()
    parser.buffer_text = True
    parser.StartElementHandler = handleStartElement
    parser.ParseFile(src)

    return max_col, max_row


def fixup_worksheet(worksheet):
    try:
        ws_cols, ws_rows = calc_true_dims(worksheet)

        worksheet._max_column = ws_cols
        worksheet._max_row = ws_rows
    except Exception as e:
        logging.error(f"Failed to fetch true dimensions: {e}")


def update_access_time(path):
    path = Path(path)
    stat = path.stat()
    os.utime(path, (now(), stat.st_mtime))


def load_numpy(path):
    update_access_time(path)

    return np.load(path, allow_pickle=True, fix_imports=False)






def py_to_nim_encoding(encoding: str) -> str:
    if encoding is None or encoding.lower() in ["ascii", "utf8", "utf-8", "utf-8-sig"]:
        return "ENC_UTF8"
    elif encoding.lower() in ["utf16", "utf-16"]:
        return "ENC_UTF16"
    elif encoding in Config.NIM_SUPPORTED_CONV_TYPES:
        return f"ENC_CONV|{encoding}"

    raise NotImplementedError(f"encoding not implemented: {encoding}")


def strip_escape(str_: str) -> str:
    if not isinstance(str_, str):
        return str_

    seqs = (
        ("\t", ""),
        ("\n", ""),
        ("\r", ""),
        ("\t", ""),
        ("\n", ""),
        ("\r", "")
    )

    for (i, o) in seqs:
        str_ = str_.replace(i, o)

    return str_
