import psutil
import numpy as np
from typing import List, Union
from itertools import product
from pathlib import Path
from tablite.config import Config
from tablite.reindex import reindex
from tablite.merge import where
from tablite.base import BaseTable, Column
from tablite.utils import sub_cls_check, unique_name, type_check
from tablite.mp_utils import is_mp
from mplite import Task, TaskManager as _TaskManager
from tqdm import tqdm as _tqdm


def join(
    T: BaseTable,
    other: BaseTable,
    left_keys: List[str],
    right_keys: List[str],
    left_columns: Union[List[str], None],
    right_columns: Union[List[str], None],
    kind: str = "inner",
    merge_keys: bool = False,
    tqdm=_tqdm,
    pbar=None,
):
    """short-cut for all join functions.

    Args:
        T (Table): left table
        other (Table): right table
        left_keys (list): list of keys for the join from left table.
        right_keys (list): list of keys for the join from right table.
        left_columns (list): list of columns names to retain from left table.
            If None, all are retained.
        right_columns (list): list of columns names to retain from right table.
            If None, all are retained.
        kind (str, optional): 'inner', 'left', 'outer', 'cross'. Defaults to "inner".
        tqdm (tqdm, optional): tqdm progress counter. Defaults to _tqdm.
        pbar (tqdm.pbar, optional): tqdm.progressbar. Defaults to None.

    Raises:
        ValueError: if join type is unknown.

    Returns:
        Table: joined table.
    
    Example: "inner"
    ```
    SQL:   SELECT number, letter FROM numbers JOIN letters ON numbers.colour == letters.color
    ```
    Tablite: 
    ```
    >>> inner_join = numbers.inner_join(
        letters, 
        left_keys=['colour'], 
        right_keys=['color'], 
        left_columns=['number'], 
        right_columns=['letter']
    )
    ```
    
    Example: "left" 
    ```
    SQL:   SELECT number, letter FROM numbers LEFT JOIN letters ON numbers.colour == letters.color
    ```
    Tablite: 
    ```
    >>> left_join = numbers.left_join(
        letters, 
        left_keys=['colour'], 
        right_keys=['color'], 
        left_columns=['number'], 
        right_columns=['letter']
    )
    ```

    Example: "outer"
    ```
    SQL:   SELECT number, letter FROM numbers OUTER JOIN letters ON numbers.colour == letters.color
    ```

    Tablite: 
    ```
    >>> outer_join = numbers.outer_join(
        letters, 
        left_keys=['colour'], 
        right_keys=['color'], 
        left_columns=['number'], 
        right_columns=['letter']
        )
    ```

    Example: "cross"

    CROSS JOIN returns the Cartesian product of rows from tables in the join.
    In other words, it will produce rows which combine each row from the first table
    with each row from the second table
    """
    if left_columns is None:
        left_columns = list(T.columns)
    if right_columns is None:
        right_columns = list(other.columns)
    assert merge_keys in {True,False}

    _jointype_check(T, other, left_keys, right_keys, left_columns, right_columns)

    return _join(kind, T,other,left_keys, right_keys, left_columns, right_columns, merge_keys=merge_keys,
             tqdm=tqdm, pbar=pbar)

# fmt:off



# fmt: on


def _vpus(tasks):
    """private helper to determine how many VPUs there is memory for.

    Args:
        tasks (list): list of tasks

    Returns:
        integer: number of VPUs
    """
    if Config.MULTIPROCESSING_MODE == Config.FALSE:
        raise TypeError("Config.MULTIPROCESSING_MODE == Config.FALSE")
    else:
        memory_per_join = 300e6
        max_vpus = psutil.virtual_memory().free // memory_per_join
        return int(min(Config.vpus, len(tasks), max_vpus))


def _jointype_check(T, other, left_keys, right_keys, left_columns, right_columns):
    sub_cls_check(T, BaseTable)
    sub_cls_check(other, BaseTable)

    if not isinstance(left_keys, list) and all(isinstance(k, str) for k in left_keys):
        raise TypeError(f"Expected keys as list of strings, not {type(left_keys)}")
    if not isinstance(right_keys, list) and all(isinstance(k, str) for k in right_keys):
        raise TypeError(f"Expected keys as list of strings, not {type(right_keys)}")

    if any(key not in T.columns for key in left_keys):
        e = f"left key(s) not found: {[k for k in left_keys if k not in T.columns]}"
        raise ValueError(e)
    if any(key not in other.columns for key in right_keys):
        e = f"right key(s) not found: {[k for k in right_keys if k not in other.columns]}"
        raise ValueError(e)

    if len(left_keys) != len(right_keys):
        raise ValueError(f"Keys do not have same length: \n{left_keys}, \n{right_keys}")

    if not isinstance(left_columns, list) or not left_columns:
        raise TypeError("left_columns (list of strings) are required")
    if any(column not in T.columns for column in left_columns):
        e = f"Column not found: {[c for c in left_columns if c not in T.columns]}"
        raise ValueError(e)

    if not isinstance(right_columns, list) or not right_columns:
        raise TypeError("right_columns (list or strings) are required")
    if any(column not in other.columns for column in right_columns):
        e = f"Column not found: {[c for c in right_columns if c not in other.columns]}"
        raise ValueError(e)
    # Input is now guaranteed to be valid.


# -------------------------
# SINGLE PROCESSING SECTION
# -------------------------


def _sp_left_mapping(T, other, left_keys, right_keys, tqdm, pbar):
    """
    Args:
        T (Table): left table
        other (Table): right table
        left_keys (list): list of keys for the join from left table.
        right_keys (list): list of keys for the join from right table.
    
    Returns: 
        Table: joined table
    """
    pass


def _sp_inner_mapping(T, other, left_keys, right_keys, tqdm, pbar):
    """
    Args:
        T (Table): left table
        other (Table): right table
        left_keys (list): list of keys for the join from left table.
        right_keys (list): list of keys for the join from right table.
    
    Returns: 
        Table: joined table

    """
    pass


def _sp_outer_mapping(T, other, left_keys, right_keys, tqdm, pbar):
    """
    Args:
        T (Table): left table
        other (Table): right table
        left_keys (list): list of keys for the join from left table.
        right_keys (list): list of keys for the join from right table.
    
    Returns: 
        Table: joined table

    """
    pass


def _sp_cross_mapping(T, other, left_keys, right_keys, tqdm, pbar):
    """
    Args:
        T (Table): left table
        other (Table): right table
        left_keys (list): list of keys for the join from left table.
        right_keys (list): list of keys for the join from right table.
    
    Returns: 
        Table: joined table

    """
    pass


_sp_mapping_methods = {
    "inner": _sp_inner_mapping,
    "left":  _sp_left_mapping, 
    "outer": _sp_outer_mapping,
    "cross": _sp_cross_mapping,
}

# -----------------------
# MULTIPROCESSING SECTION
# -----------------------


def _mp_where(
    T: BaseTable,
    mapping: BaseTable,
    field: str,
    left: str,
    right: str,
    new: str,
    start: int,
    end: int,
    path: Path,
):
    """takes from LEFT where criteria is True else RIGHT.

    Args:
        T (Table): Table to change.
        mapping (Table): mapping table.
        field (str): bool field name in mapping
            if True take left column
            else take right column
        left (str): column name
        right (str): column name
        new (str): new name
        start (int): start index
        end (int): end index

    :returns: None
    """
    pass

def _mp_reindex_page(
    T: BaseTable,
    column_name: str,
    mapping: BaseTable,
    index: str,
    start: int,
    end: int,
    path: Path,
):
    """reindexes T on column_name using mapping between start and end.

    Args:
        T (Table): table to reindex
        column_name (str): column to reindex
        mapping (Table): table with mapping
        index (str): column name of index in mapping
        start (int): start of range
        end (int): end of range
        path (Path): directory of the main process

    Returns:
        Table: table initiated in the main process' working directory
    """
    pass


def _gets(task, *args):
    """helper to get kwargs of a task

    *Args:
        names from kwargs to retrieve.

    Returns:
        tuple: tuple with kw-values in same order as args

    Examples:

    Verbose way:
    ```
    >>> col = task.kwarg.get("left")
    >>> right = task.kwarg.get("right")
    >>> end = task.kwarg.get("end")
    ```
    Compact way:
    ```
    >>> col, start, end = task.gets("left", "start", "end")
    ```
    """
    result = tuple()
    for arg in args:
        result += (task.kwargs.get(arg),)
    return result

def _join(
        kind: str,
        T: BaseTable,
        other: BaseTable,
        left_keys: List[str],
        right_keys: List[str],
        left_columns: Union[List[str], None] = None,
        right_columns: Union[List[str], None] = None,
        merge_keys: bool = False,
        tqdm=_tqdm,
        pbar=None,
        TaskManager=None,
    ):

    Constr = type(T)
    fields = len(T)*len(T.columns) + len(other)*len(other.columns)
    use_mp = is_mp(fields)

    if pbar is None:
        _pbar_created_here = True
        pbar = tqdm(total=5, desc="join", disable=Config.TQDM_DISABLE)
    else:
        _pbar_created_here = False
    pbar.update(0)  # pbar start

    class ProgressBar(object):
        def update(self, n):
            pbar.update(n / len(tasks))

    # create left and right index
    if TaskManager is None:
        TaskManager = _TaskManager
    
    tasks = []

    _pid_dir = Path(Config.workdir) / Config.pid

    # step 1: create mapping tasks
    _mapping = _sp_mapping_methods.get(kind, None)
    if _mapping is None:
        raise ValueError(f"join type unknown: {kind}")

    """
        Ratchet:
        
        I thought real good about it and it is not possible to mapping tasks be
        multi-processed/constant memory, because every slice must know the entire right table dictionary
        and anything that is not the first slice must also have all previous other slice indices.

        Best we can do is reduce the RAM usage via using hash of a string or reduce memory usage via native implementation.
    """
    _left, _right = _mapping(T, other, left_keys, right_keys, None, None)

    # step 2: assemble mapping from tasks
    mapping = Constr({"left": _left, "right": _right})

    del _left, _right

    pbar.update(1)

    # step 3: initiate reindexing tasks
    tasks = []
    names = []  # will store (old name, new name) for derefences during assemble.
    new_table = Constr()
    n = len(mapping)
    step = Config.PAGE_SIZE
    for name in left_columns:
        new_table.add_column(name)

        for start in range(0, n + 1, step):
            names.append((name, name))
            task = Task(
                _mp_reindex_page,
                T=T,
                column_name=name,
                mapping=mapping,
                index="left",
                start=start,
                end=min(start + step, n),
                path=_pid_dir,
            )
            tasks.append(task)

    for name in right_columns:
        new_name = unique_name(name, new_table.columns)
        new_table.add_column(new_name)

        for start in range(0, n + 1, step):
            names.append((new_name, name))
            task = Task(
                _mp_reindex_page,
                T=other,
                column_name=name,
                mapping=mapping,
                index="right",
                start=start,
                end=min(start + step, n),
                path=_pid_dir,
            )
            tasks.append(task)

    if use_mp:
        with TaskManager(cpu_count=_vpus(tasks), error_mode="exception") as tm:
            results = tm.execute(tasks, pbar=ProgressBar())
    else:
        results = [t.f(*t.args, **t.kwargs) for t in tasks]

    # step 4: assemble the result
    for task, result, (new, old) in zip(tasks, results, names):
        arr = result[old]
        new_table[new].extend(arr)

    pbar.n = pbar.total - 1  # needed to overcome floating point error.
    pbar.refresh()

    # step 5: merge keys (if required)
    if merge_keys is True:
        if kind in ["outer", "left"]:
            mapping["boolean map"] = np.array(mapping["left"]) != -1 \
                if kind == "outer" else np.array(mapping["right"]) == -1

            step = 1 / len(left_keys)
            tasks = []
            for left_name, right_name in zip(left_keys, right_keys):
                right_name = unique_name(right_name, T.columns)
                for start, end in Config.page_steps(len(mapping)):
                    task = Task(
                        _mp_where,
                        T=new_table,
                        mapping=mapping,
                        field="boolean map",
                        left=left_name,
                        right=right_name,
                        new="bmap",
                        start=start,
                        end=end,
                        path=_pid_dir,
                    )
                    tasks.append(task)

            if use_mp:
                with TaskManager(cpu_count=_vpus(tasks), error_mode="exception") as tm:
                    results = tm.execute(tasks, pbar=ProgressBar())
            else:
                results = [t.f(*t.args, **t.kwargs) for t in tasks]

            for task, result in zip(tasks, results):
                col, start, end = _gets(task, "left", "start", "end")
                new_table[col][start:end] = result["bmap"][:]
        elif kind not in ["inner", "cross"]:
            raise TypeError(f"bad join type: {kind}")

        for right_name in right_keys:
            del new_table[unique_name(right_name, T.columns)]
    else:
        pbar.update(1)

    if _pbar_created_here:
        pbar.close()

    return new_table
