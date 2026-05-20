import sys
import psutil
import platform
import numpy as np
from pathlib import Path
from tqdm import tqdm as _tqdm
from tablite.config import Config
from mplite import Task, TaskChain, TaskManager
from tablite.base import BaseTable, Column
from typing import TYPE_CHECKING, Literal, Type, TypeVar, TypedDict, Union, List, Tuple


if True:
    paths = sys.argv[:]
    if Config.USE_NIMPORTER:
        import nimporter

        nimporter.Nimporter.IGNORE_CACHE = True
    import nimlite.libnimlite as nl

    sys.argv.clear()
    sys.argv.extend(paths)  # importing nim module messes with pythons launch arguments!!!


K = TypeVar("K", bound=BaseTable)
ValidEncoders = Literal["ENC_UTF8", "ENC_UTF16", "ENC_WIN1250"]
ValidQuoting = Literal["QUOTE_MINIMAL", "QUOTE_ALL", "QUOTE_NONNUMERIC", "QUOTE_NONE", "QUOTE_STRINGS", "QUOTE_NOTNULL"]
ValidSkipEmpty = Literal["NONE", "ANY", "ALL"]
ColumnSelectorDict = TypedDict(
    "ColumnSelectorDict", {
        "column": str,
        "type": Literal["int", "float", "bool", "str", "date", "time", "datetime"],
        "allow_empty": Union[bool, None],
        "rename": Union[str, None]
    }
)

FilterCriteria = Literal[">", ">=", "==", "<", "<=", "!=", "in"]
FilterType = Literal["all", "any"]
FilterDict = TypedDict(
    "FilterDict", {
        "column1": str,
        "value1": Union[str, None],
        "criteria": FilterCriteria,
        "column2": str,
        "value2": Union[str, None],
    }
)



def get_headers(
    path: Union[str, Path],
    encoding: ValidEncoders ="ENC_UTF8",
    *,
    header_row_index: int=0,
    newline: str='\n', delimiter: str=',', text_qualifier: str='"',
    quoting: ValidQuoting, strip_leading_and_tailing_whitespace: bool=True,
    linecount: int = 10
) -> list[list[str]]:
    return nl.get_headers(
            path=str(path),
            encoding=encoding,
            newline=newline, delimiter=delimiter, text_qualifier=text_qualifier,
            strip_leading_and_tailing_whitespace=strip_leading_and_tailing_whitespace,
            header_row_index=header_row_index,
            quoting=quoting,
            linecount=linecount
        )






def _collect_cs_info(i: int, columns: dict, res_cols_pass: list, res_cols_fail: list, original_pages_map: list):
    el = {
        name: (column[i], original_pages_map[name][i])
        for name, column in columns.items()
    }

    col_pass = res_cols_pass[i]
    col_fail = res_cols_fail[i]

    return el, col_pass, col_fail


def column_select(table: K, cols: list[ColumnSelectorDict], tqdm=_tqdm, pbar:_tqdm = None, TaskManager=TaskManager) -> Tuple[K, K]:
    if pbar is None:
        pbar = tqdm(total=100, desc="column select", bar_format='{desc}: {percentage:.1f}%|{bar}{r_bar}')
        pbar_close = True
    else:
        pbar_close = False

    try:
        T = type(table)
        dir_pid = Config.workdir / Config.pid

        col_infos = nl.collect_column_select_info(table, cols, str(dir_pid), pbar)

        columns = col_infos["columns"]
        page_count = col_infos["page_count"]
        is_correct_type = col_infos["is_correct_type"]
        desired_column_map = col_infos["desired_column_map"]
        original_pages_map = col_infos["original_pages_map"]
        passed_column_data = col_infos["passed_column_data"]
        failed_column_data = col_infos["failed_column_data"]
        res_cols_pass = col_infos["res_cols_pass"]
        res_cols_fail = col_infos["res_cols_fail"]
        column_names = col_infos["column_names"]
        reject_reason_name = col_infos["reject_reason_name"]

        if all(is_correct_type.values()):
            tbl_pass_columns = {
                desired_name: table[desired_info[0]]
                for desired_name, desired_info in desired_column_map.items()
            }

            tbl_fail_columns = {
                desired_name: []
                for desired_name in failed_column_data
            }

            tbl_pass = T(columns=tbl_pass_columns)
            tbl_fail = T(columns=tbl_fail_columns)

            return (tbl_pass, tbl_fail)

        task_list_inp = (
            _collect_cs_info(i, columns, res_cols_pass, res_cols_fail, original_pages_map)
            for i in range(page_count)
        )

        page_size = Config.PAGE_SIZE

        tasks = (
            Task(
                nl.do_slice_convert, str(dir_pid), page_size, columns, reject_reason_name, res_pass, res_fail, desired_column_map, column_names, is_correct_type
            )
            for columns, res_pass, res_fail in task_list_inp
        )

        cpu_count = max(psutil.cpu_count(), 1)

        if Config.MULTIPROCESSING_MODE == Config.FORCE:
            is_mp = True
        elif Config.MULTIPROCESSING_MODE == Config.FALSE:
            is_mp = False
        elif Config.MULTIPROCESSING_MODE == Config.AUTO:
            is_multithreaded = cpu_count > 1
            is_multipage = page_count > 1

            is_mp = is_multithreaded and is_multipage

        tbl_pass = T({k: [] for k in passed_column_data})
        tbl_fail = T({k: [] for k in failed_column_data})

        converted = []
        step_size = 45 / max(page_count, 1)

        if is_mp:
            class WrapUpdate:
                def update(self, n):
                    pbar.update(n * step_size)

            with TaskManager(min(cpu_count, page_count), error_mode="exception") as tm:
                res = tm.execute(list(tasks), pbar=WrapUpdate())

                converted.extend(res)
        else:
            for task in tasks:
                res = task.f(*task.args, **task.kwargs)

                converted.append(res)
                pbar.update(step_size)

        def extend_table(table, columns):
            for (col_name, pg) in columns:
                table[col_name].pages.append(pg)

        for pg_pass, pg_fail in converted:
            extend_table(tbl_pass, pg_pass)
            extend_table(tbl_fail, pg_fail)

        pbar.update(pbar.total - pbar.n)

        return tbl_pass, tbl_fail
    finally:
        if pbar_close:
            pbar.close()

def read_page(path: Union[str, Path]) -> np.ndarray:
    return nl.read_page(str(path))


def nearest_neighbour(T: BaseTable, sources: Union[list[str], None], missing: Union[list, None], targets: Union[list[str], None], tqdm=_tqdm, pbar: _tqdm = None):
    return nl.nearest_neighbour(T, sources, list(missing), targets, tqdm, pbar)

def groupby(T, keys, functions, tqdm=_tqdm, pbar: _tqdm=None):
    return nl.groupby(T, keys, functions, tqdm, pbar)

