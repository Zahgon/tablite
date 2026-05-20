import math
import numpy as np
from tablite.config import Config
from tablite.base import BaseTable, Column
from tablite.reindex import reindex as _reindex
from tablite.utils import sub_cls_check, unique_name
from tablite.mp_utils import lookup_ops, share_mem, map_task, select_processing_method
from mplite import Task, TaskManager


from tqdm import tqdm as _tqdm


def lookup(T, other, *criteria, all=True, tqdm=_tqdm):
    """function for looking up values in `other` according to criteria in ascending order.
    :param: T: Table 
    :param: other: Table sorted in ascending search order.
    :param: criteria: Each criteria must be a tuple with value comparisons in the form:
        (LEFT, OPERATOR, RIGHT)
    :param: all: boolean: True=ALL, False=ANY

    OPERATOR must be a callable that returns a boolean
    LEFT must be a value that the OPERATOR can compare.
    RIGHT must be a value that the OPERATOR can compare.

    Examples:
        comparison of two columns:

            ('column A', "==", 'column B')

        compare value from column 'Date' with date 24/12.

            ('Date', "<", DataTypes.date(24,12) )

        uses custom function to compare value from column
        'text 1' with value from column 'text 2'

            f = lambda L,R: all( ord(L) < ord(R) )
            ('text 1', f, 'text 2')

    """
    sub_cls_check(T, BaseTable)
    sub_cls_check(other, BaseTable)

    all = all
    any = not all

    ops = lookup_ops

    functions, left_criteria, right_criteria = [], set(), set()

    for left, op, right in criteria:
        left_criteria.add(left)
        right_criteria.add(right)
        if callable(op):
            pass  # it's a custom function.
        else:
            op = ops.get(op, None)
            if not callable(op):
                raise ValueError(f"{op} not a recognised operator for comparison.")

        functions.append((op, left, right))
    left_columns = [n for n in left_criteria if n in T.columns]
    right_columns = [n for n in right_criteria if n in other.columns]

    result_index = np.empty(shape=(len(T)), dtype=np.int64)
    cache = {}
    left = T[left_columns]
    Constr = type(T)
    if isinstance(left, Column):
        tmp, left = left, Constr()
        left[left_columns[0]] = tmp
    right = other[right_columns]
    if isinstance(right, Column):
        tmp, right = right, Constr()
        right[right_columns[0]] = tmp
    assert isinstance(left, BaseTable)
    assert isinstance(right, BaseTable)

    for ix, row1 in tqdm(enumerate(left.rows), total=len(T), disable=Config.TQDM_DISABLE):
        row1_tup = tuple(row1)
        row1d = {name: value for name, value in zip(left_columns, row1)}
        row1_hash = hash(row1_tup)

        match_found = True if row1_hash in cache else False

        if not match_found:  # search.
            for row2ix, row2 in enumerate(right.rows):
                row2d = {name: value for name, value in zip(right_columns, row2)}

                evaluations = {op(row1d.get(left, left), row2d.get(right, right)) for op, left, right in functions}
                # The evaluations above does a neat trick:
                # as L is a dict, L.get(left, L) will return a value
                # from the columns IF left is a column name. If it isn't
                # the function will treat left as a value.
                # The same applies to right.
                all_ = all and (False not in evaluations)
                any_ = any and True in evaluations
                if all_ or any_:
                    match_found = True
                    cache[row1_hash] = row2ix
                    break

        if not match_found:  # no match found.
            cache[row1_hash] = -1  # -1 is replacement for None in the index as numpy can't handle Nones.

        result_index[ix] = cache[row1_hash]

    f = select_processing_method(2 * max(len(T), len(other)), _sp_lookup, _mp_lookup)
    return f(T, other, result_index)




