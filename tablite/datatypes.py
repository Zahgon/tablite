from datetime import date, datetime, time, timedelta, timezone
from collections import defaultdict, Counter
import numpy as np
import pickle
from typing import Any


class DataTypes(object):
    """DataTypes is the conversion library for all datatypes.

    It supports any / all python datatypes.
    """

    # supported datatypes.
    int = int
    str = str
    float = float
    bool = bool
    date = date
    datetime = datetime
    time = time
    timedelta = timedelta

    numeric_types = {int, float, date, time, datetime}
    epoch = datetime(2000, 1, 1, 0, 0, 0, 0, timezone.utc)
    epoch_no_tz = datetime(2000, 1, 1, 0, 0, 0, 0)
    digits = "1234567890"
    decimals = set("1234567890-+eE.")
    integers = set("1234567890-+")
    nones = {"null", "Null", "NULL", "#N/A", "#n/a", "", "None", None, np.nan}
    none_type = type(None)

    _type_codes = {
        type(None): 1,
        bool: 2,
        int: 3,
        float: 4,
        str: 5,
        bytes: 6,
        datetime: 7,
        date: 8,
        time: 9,
        timedelta: 10,
        "pickle": 11,
    }













    bytes_functions = {
        type(None): b_none,
        bool: b_bool,
        int: b_int,
        float: b_float,
        str: b_str,
        bytes: b_bytes,
        datetime: b_datetime,
        date: b_date,
        time: b_time,
        timedelta: b_timedelta,
    }













    type_code_functions = {
        1: _none,
        2: _bool,
        3: _int,
        4: _float,
        5: _str,
        6: _bytes,
        7: _datetime,
        8: _date,
        9: _time,
        10: _timedelta,
        11: _unpickle,
    }

    pytype_from_type_code = {
        1: type(None),
        2: bool,
        3: int,
        4: float,
        5: str,
        6: bytes,
        7: datetime,
        8: date,
        9: time,
        10: timedelta,
        11: "pickled object",
    }


    date_formats = {  # Note: Only recognised ISO8601 formats are accepted.
        "NNNN-NN-NN": lambda x: date(*(int(i) for i in x.split("-"))),
        "NNNN-N-NN": lambda x: date(*(int(i) for i in x.split("-"))),
        "NNNN-NN-N": lambda x: date(*(int(i) for i in x.split("-"))),
        "NNNN-N-N": lambda x: date(*(int(i) for i in x.split("-"))),
        "NN-NN-NNNN": lambda x: date(*[int(i) for i in x.split("-")][::-1]),
        "N-NN-NNNN": lambda x: date(*[int(i) for i in x.split("-")][::-1]),
        "NN-N-NNNN": lambda x: date(*[int(i) for i in x.split("-")][::-1]),
        "N-N-NNNN": lambda x: date(*[int(i) for i in x.split("-")][::-1]),
        "NNNN.NN.NN": lambda x: date(*(int(i) for i in x.split("."))),
        "NNNN.N.NN": lambda x: date(*(int(i) for i in x.split("."))),
        "NNNN.NN.N": lambda x: date(*(int(i) for i in x.split("."))),
        "NNNN.N.N": lambda x: date(*(int(i) for i in x.split("."))),
        "NN.NN.NNNN": lambda x: date(*[int(i) for i in x.split(".")][::-1]),
        "N.NN.NNNN": lambda x: date(*[int(i) for i in x.split(".")][::-1]),
        "NN.N.NNNN": lambda x: date(*[int(i) for i in x.split(".")][::-1]),
        "N.N.NNNN": lambda x: date(*[int(i) for i in x.split(".")][::-1]),
        "NNNN/NN/NN": lambda x: date(*(int(i) for i in x.split("/"))),
        "NNNN/N/NN": lambda x: date(*(int(i) for i in x.split("/"))),
        "NNNN/NN/N": lambda x: date(*(int(i) for i in x.split("/"))),
        "NNNN/N/N": lambda x: date(*(int(i) for i in x.split("/"))),
        "NN/NN/NNNN": lambda x: date(*[int(i) for i in x.split("/")][::-1]),
        "N/NN/NNNN": lambda x: date(*[int(i) for i in x.split("/")][::-1]),
        "NN/N/NNNN": lambda x: date(*[int(i) for i in x.split("/")][::-1]),
        "N/N/NNNN": lambda x: date(*[int(i) for i in x.split("/")][::-1]),
        "NNNN NN NN": lambda x: date(*(int(i) for i in x.split(" "))),
        "NNNN N NN": lambda x: date(*(int(i) for i in x.split(" "))),
        "NNNN NN N": lambda x: date(*(int(i) for i in x.split(" "))),
        "NNNN N N": lambda x: date(*(int(i) for i in x.split(" "))),
        "NN NN NNNN": lambda x: date(*[int(i) for i in x.split(" ")][::-1]),
        "N N NNNN": lambda x: date(*[int(i) for i in x.split(" ")][::-1]),
        "NN N NNNN": lambda x: date(*[int(i) for i in x.split(" ")][::-1]),
        "N NN NNNN": lambda x: date(*[int(i) for i in x.split(" ")][::-1]),
        "NNNNNNNN": lambda x: date(*(int(x[:4]), int(x[4:6]), int(x[6:]))),
    }

    # fmt:off
    datetime_formats = {
        # Note: Only recognised ISO8601 formats are accepted.
        # year first
        "NNNN-NN-NNTNN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x),  # -T
        "NNNN-NN-NNTNN:NN": lambda x: DataTypes.pattern_to_datetime(x),
        "NNNN-NN-NN NN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, T=" "),  # - space
        "NNNN-NN-NN NN:NN": lambda x: DataTypes.pattern_to_datetime(x, T=" "),
        "NNNN/NN/NNTNN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="/"),  # / T
        "NNNN/NN/NNTNN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="/"),
        "NNNN/NN/NN NN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="/", T=" "),  # / space
        "NNNN/NN/NN NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="/", T=" "),
        "NNNN NN NNTNN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd=" "),  # space T
        "NNNN NN NNTNN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd=" "),
        "NNNN NN NN NN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd=" ", T=" "),  # space
        "NNNN NN NN NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd=" ", T=" "),
        "NNNN.NN.NNTNN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="."),  # dot T
        "NNNN.NN.NNTNN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="."),
        "NNNN.NN.NN NN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd=".", T=" "),  # dot
        "NNNN.NN.NN NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd=".", T=" "),
        # day first
        "NN-NN-NNNNTNN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="-", T=" ", day_first=True),  # - T
        "NN-NN-NNNNTNN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="-", T=" ", day_first=True),
        "NN-NN-NNNN NN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="-", T=" ", day_first=True),  # - space
        "NN-NN-NNNN NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="-", T=" ", day_first=True),
        "NN/NN/NNNNTNN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="/", day_first=True),  # / T
        "NN/NN/NNNNTNN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="/", day_first=True),
        "NN/NN/NNNN NN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="/", T=" ", day_first=True),  # / space
        "NN/NN/NNNN NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="/", T=" ", day_first=True),
        "NN NN NNNNTNN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="/", day_first=True),  # space T
        "NN NN NNNNTNN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="/", day_first=True),
        "NN NN NNNN NN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="/", day_first=True),  # space
        "NN NN NNNN NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd="/", day_first=True),
        "NN.NN.NNNNTNN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd=".", day_first=True),  # space T
        "NN.NN.NNNNTNN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd=".", day_first=True),
        "NN.NN.NNNN NN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd=".", day_first=True),  # space
        "NN.NN.NNNN NN:NN": lambda x: DataTypes.pattern_to_datetime(x, ymd=".", day_first=True),
        # compact formats - type 1
        "NNNNNNNNTNNNNNN": lambda x: DataTypes.pattern_to_datetime(x, compact=1),
        "NNNNNNNNTNNNN": lambda x: DataTypes.pattern_to_datetime(x, compact=1),
        "NNNNNNNNTNN": lambda x: DataTypes.pattern_to_datetime(x, compact=1),
        # compact formats - type 2
        "NNNNNNNNNN": lambda x: DataTypes.pattern_to_datetime(x, compact=2),
        "NNNNNNNNNNNN": lambda x: DataTypes.pattern_to_datetime(x, compact=2),
        "NNNNNNNNNNNNNN": lambda x: DataTypes.pattern_to_datetime(x, compact=2),
        # compact formats - type 3
        "NNNNNNNNTNN:NN:NN": lambda x: DataTypes.pattern_to_datetime(x, compact=3),
    }
    # fmt:on

    @staticmethod
    def pattern_to_datetime(iso_string, ymd=None, T=None, compact=0, day_first=False):
        assert isinstance(iso_string, str)
        if compact:
            s = iso_string
            if compact == 1:  # has T
                slices = [
                    (0, 4, "-"),
                    (4, 6, "-"),
                    (6, 8, "T"),
                    (9, 11, ":"),
                    (11, 13, ":"),
                    (13, len(s), ""),
                ]
            elif compact == 2:  # has no T.
                slices = [
                    (0, 4, "-"),
                    (4, 6, "-"),
                    (6, 8, "T"),
                    (8, 10, ":"),
                    (10, 12, ":"),
                    (12, len(s), ""),
                ]
            elif compact == 3:  # has T and :
                slices = [
                    (0, 4, "-"),
                    (4, 6, "-"),
                    (6, 8, "T"),
                    (9, 11, ":"),
                    (12, 14, ":"),
                    (15, len(s), ""),
                ]
            else:
                raise TypeError
            iso_string = "".join([s[a:b] + c for a, b, c in slices if b <= len(s)])
            iso_string = iso_string.rstrip(":")

        if day_first:
            s = iso_string
            iso_string = "".join((s[6:10], "-", s[3:5], "-", s[0:2], s[10:]))

        if "," in iso_string:
            iso_string = iso_string.replace(",", ".")

        dot = iso_string[::-1].find(".")
        if 0 < dot < 10:
            ix = len(iso_string) - dot
            microsecond = int(float(f"0{iso_string[ix - 1:]}") * 10**6)
            # fmt:off
            iso_string = iso_string[: len(iso_string) - dot] + str(microsecond).rjust(6, "0")
            # fmt:on
        if ymd:
            iso_string = iso_string.replace(ymd, "-", 2)
        if T:
            iso_string = iso_string.replace(T, "T")
        return datetime.fromisoformat(iso_string)

    @classmethod
    def round(cls, value, multiple, up=None):
        """a nicer way to round numbers.

        Args:
            value (float,integer,datetime): value to be rounded

            multiple (float,integer,timedelta): value to be used as the based of rounding.
                1) multiple = 1 is the same as rounding to whole integers.
                2) multiple = 0.001 is the same as rounding to 3 digits precision.
                3) mulitple = 3.1415 is rounding to nearest multiplier of 3.1415
                4) value = datetime(2022,8,18,11,14,53,440)
                5) multiple = timedelta(hours=0.5)
                6) xround(value,multiple) is datetime(2022,8,18,11,0)

            up (None, bool, optional):
                None (default) or boolean rounds half, up or down.
                round(1.6, 1) rounds to 2.
                round(1.4, 1) rounds to 1.
                round(1.5, 1, up=True) rounds to 2.
                round(1.5, 1, up=False) rounds to 1.

        Returns:
            float,integer,datetime: rounded value in same type as input.
        """
        pass

    @staticmethod
    def to_json(v):
        """converts any python type to json.

        Args:
            v (any): value to convert to json

        Returns:
            json compatible value from v
        """
        pass

    @staticmethod
    def from_json(v, dtype):
        """converts json to python datatype

        Args:
            v (any): value
            dtype (python type): any python type

        Returns:
            python type of value v
        """
        pass

    # Order is very important!
    types = [datetime, date, time, int, bool, float, str]

    @staticmethod
    def guess_types(*values):
        """Attempts to guess the datatype for *values
        returns dict with matching datatypes and probabilities

        Returns:
            dict: {key: type, value: probability}
        """
        pass

    @staticmethod
    def guess(*values):
        """Makes a best guess the datatype for *values
        returns list of native python values

        Returns:
            list: list of native python values
        """
        pass











def numpy_to_python(obj: Any) -> Any:
    """Converts numpy types to python types.

    See https://numpy.org/doc/stable/reference/arrays.scalars.html

    Args:
        obj (Any): A numpy object

    Returns:
        python object: A python object
    """
    if isinstance(obj, np.generic):
        return obj.item()
    return obj


def pytype(obj):
    """Returns the python type of any object

    Args:
        obj (Any): any numpy or python object

    Returns:
        type: type of obj
    """
    if isinstance(obj, np.generic):
        return type(obj.item())
    return type(obj)


class Rank(object):
    def __init__(self, *items):
        self.items = {i: ix for i, ix in zip(items, range(len(items)))}
        self.ranks = [0 for _ in items]
        self.items_list = [i for i in items]

    def match(self, k):  # k+=1
        ix = self.items[k]
        r = self.ranks
        r[ix] += 1

        if ix > 0:
            p = self.items_list
            while (
                r[ix] > r[ix - 1] and ix > 0
            ):  # use a simple bubble sort to maintain rank
                r[ix], r[ix - 1] = r[ix - 1], r[ix]
                p[ix], p[ix - 1] = p[ix - 1], p[ix]
                old = p[ix]
                self.items[old] = ix
                self.items[k] = ix - 1
                ix -= 1

    def __iter__(self):
        return iter(self.items_list)


def pytype_from_iterable(iterable: {tuple, list}) -> {np.dtype, dict}:
    """helper to make correct np array from python types.

    Args:
        iterable (tuple,list): values to be converted to numpy array.

    Raises:
        NotImplementedError: if datatype is not supported.

    Returns:
        np.dtype: python type of the iterable.
    """
    py_types = {}
    if isinstance(iterable, (tuple, list)):
        type_counter = Counter((pytype(v) for v in iterable))

        for k, v in type_counter.items():
            py_types[k] = v

        if len(py_types) == 0:
            np_dtype, py_dtype = object, bool
        elif len(py_types) == 1:
            py_dtype = list(py_types.keys())[0]
            if py_dtype == datetime:
                np_dtype = np.datetime64
            elif py_dtype == date:
                np_dtype = np.datetime64
            elif py_dtype == timedelta:
                np_dtype = np.timedelta64
            else:
                np_dtype = None
        else:
            np_dtype = object
    elif isinstance(iterable, np.ndarray):
        if iterable.dtype == object:
            np_dtype = object
            py_types = dict(Counter((pytype(v) for v in iterable)))
        else:
            np_dtype = iterable.dtype
            if len(iterable) > 0:
                py_types = {pytype(iterable[0]): len(iterable)}
            else:
                py_types = {pytype(np_dtype.type()): len(iterable)}
    else:
        raise NotImplementedError(f"No handler for {type(iterable)}")

    return np_dtype, py_types


class MetaArray(np.ndarray):
    """Array with metadata."""

    def __new__(cls, array, dtype=None, order=None, **kwargs):
        obj = np.asarray(array, dtype=dtype, order=order).view(cls)
        obj.metadata = kwargs
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.metadata = getattr(obj, "metadata", None)


def list_to_np_array(iterable):
    """helper to make correct np array from python types.
    Example of problem where numpy turns mixed types into strings.
    >>> np.array([4, '5'])
    np.ndarray(['4', '5'])

    returns:
        np.array
        datatypes
    """
    np_dtype, py_dtype = pytype_from_iterable(iterable)

    value = MetaArray(iterable, dtype=np_dtype, py_dtype=py_dtype)
    return value


def np_type_unify(arrays):
    """unifies numpy types.

    Args:
        arrays (list): List of numpy arrays

    Returns:
        np.ndarray: numpy array of a single type.
    """
    dtypes = {arr.dtype: len(arr) for arr in arrays}
    if len(dtypes) == 1:
        dtype, _ = dtypes.popitem()
    else:
        for ix, arr in enumerate(arrays):
            arrays[ix] = np.array(arr, dtype=object)
        dtype = object
    return np.concatenate(arrays, dtype=dtype)


def multitype_set(arr):
    """prevents loss of True, False when calling sets.

    python looses values when called returning a set. Example:
    >>> {1, True, 0, False}
    {0,1}

    Args:
        arr (Iterable): iterable of mixed types.

    Returns:
        np.array: with unique values.
    """
    L = [(type(v), v) for v in arr]
    L = list(set(L))
    L = [v for _, v in L]
    return np.array(L, dtype=object)


matched_types = {
    int: DataTypes._infer_int,
    str: DataTypes._infer_str,
    float: DataTypes._infer_float,
    bool: DataTypes._infer_bool,
    date: DataTypes._infer_date,
    datetime: DataTypes._infer_datetime,
    time: DataTypes._infer_time,
}
