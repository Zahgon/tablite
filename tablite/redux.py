from tablite.base import BaseTable
import numpy as np
import warnings
from tablite.utils import sub_cls_check, type_check, expression_interpreter
from tablite.mp_utils import filter_ops
from tablite.datatypes import list_to_np_array
from tablite.config import Config
from tablite.nimlite import filter as _filter_using_list_of_dicts_native
from tqdm import tqdm as _tqdm


def _filter_using_expression(T, expression):
    """
    filters based on an expression, such as:

        "all((A==B, C!=4, 200<D))"

    which is interpreted using python's compiler to:

        def _f(A,B,C,D):
            return all((A==B, C!=4, 200<D))
    """
    pass

def filter_all(T, **kwargs):
    """
    returns Table for rows where ALL kwargs match
    :param kwargs: dictionary with headers and values / boolean callable

    Examples:

        t = Table()
        t['a'] = [1,2,3,4]
        t['b'] = [10,20,30,40]

        def f(x):
            return x == 4
        def g(x):
            return x < 20

        t2 = t.any( **{"a":f, "b":g})
        assert [r for r in t2.rows] == [[1, 10], [4, 40]]

        t2 = t.any(a=f,b=g)
        assert [r for r in t2.rows] == [[1, 10], [4, 40]]

        def h(x):
            return x>=2

        def i(x):
            return x<=30

        t2 = t.all(a=h,b=i)
        assert [r for r in t2.rows] == [[2,20], [3, 30]]


    """
    pass


def drop(T, *args):
    """drops all rows that contain args

    Args:
        T (Table):
    """
    pass


def filter_any(T, **kwargs):
    """
    returns Table for rows where ANY kwargs match
    :param kwargs: dictionary with headers and values / boolean callable
    """
    pass







def _filter_using_list_of_dicts(T, expressions, filter_type, pbar: _tqdm):
    """
    enables filtering across columns for multiple criteria.

    expressions:

        str: Expression that can be compiled and executed row by row.
            exampLe: "all((A==B and C!=4 and 200<D))"

        list of dicts: (example):

            L = [
                {'column1':'A', 'criteria': "==", 'column2': 'B'},
                {'column1':'C', 'criteria': "!=", "value2": '4'},
                {'value1': 200, 'criteria': "<", column2: 'D' }
            ]

        accepted dictionary keys: 'column1', 'column2', 'criteria', 'value1', 'value2'

    filter_type: 'all' or 'any'
    """
    pass

def filter_non_primitive(T, expressions, filter_type="all", tqdm=_tqdm):
    """
    OBSOLETE
    filters table


    Args:
        T (Table subclass): Table.
        expressions (list or str):
            str:
                filters based on an expression, such as:
                "all((A==B, C!=4, 200<D))"
                which is interpreted using python's compiler to:

                def _f(A,B,C,D):
                    return all((A==B, C!=4, 200<D))

            list of dicts: (example):

            L = [
                {'column1':'A', 'criteria': "==", 'column2': 'B'},
                {'column1':'C', 'criteria': "!=", "value2": '4'},
                {'value1': 200, 'criteria': "<", column2: 'D' }
            ]

        accepted dictionary keys: 'column1', 'column2', 'criteria', 'value1', 'value2'

        filter_type (str, optional): Ignored if expressions is str.
            'all' or 'any'. Defaults to "all".
        tqdm (tqdm, optional): progressbar. Defaults to _tqdm.

    Returns:
        2xTables: trues, falses
    """
    pass

def filter(T, expressions, filter_type="all", tqdm=_tqdm):
    """filters table
    Note: At the moment only tablite primitive types are supported

    Args:
        T (Table subclass): Table.
        expressions (list or str):
            str:
                filters based on an expression, such as:
                "all((A==B, C!=4, 200<D))"
                which is interpreted using python's compiler to:

                def _f(A,B,C,D):
                    return all((A==B, C!=4, 200<D))

            list of dicts: (example):

            L = [
                {'column1':'A', 'criteria': "==", 'column2': 'B'},
                {'column1':'C', 'criteria': "!=", "value2": '4'},
                {'value1': 200, 'criteria': "<", column2: 'D' }
            ]

        accepted dictionary keys: 'column1', 'column2', 'criteria', 'value1', 'value2'

        filter_type (str, optional): Ignored if expressions is str.
            'all' or 'any'. Defaults to "all".
        tqdm (tqdm, optional): progressbar. Defaults to _tqdm.

    Returns:
        2xTables: trues, falses
    """
    pass
