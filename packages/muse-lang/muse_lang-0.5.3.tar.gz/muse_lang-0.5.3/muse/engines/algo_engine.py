# 内置金融算法库的调用和执行
import pandas as pd
import polars as pl
import muse.data_interface as t
from muse.utils.code_utils import run_script_in_venv, get_files_in_dir
from muse.muse_config import PYTHON_PATH
import json
# from empyrical import stats
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import os
import logging

def get_result_col(columns):
    score_list = list()
    for col in columns:
        score = 0
        if '-' in str(col):
            score += 1
        if '+' in str(col):
            score += 1
        if '*' in str(col):
            score += 1
        if '/' in str(col):
            score += 1
        score_list.append(score)

    result_col = None
    if len(score_list):
        max_value = max(score_list)  # 最大值
        if max_value > 0:
            max_index = score_list.index(max_value)  # 第一个最大值的索引
            result_col = columns[max_index]
    return result_col

def algo_handler(algo_name, params):
    logging.debug('调用算法函数: {}, 参数: {}, 调用结果: {}'.format(algo_name, params, 4))
    if algo_name == 'agg':
        df = params[0]
        group_keys = params[1]
        method_name = params[2]
        alias_name = None
        if len(params) > 3:
            alias_name = params[3]
        if method_name == 'single_ann_return':
            # method_name = stats.cum_returns_final
            method_name = np.sum
        return agg_algo(df, group_keys, method_name, alias_name)
    elif algo_name == '平台日':
        return platform_date()
    elif algo_name == '近N天':
        current_date = params[0]
        days = params[1]
        return n_days(current_date, days)
    elif algo_name == '近N月':
        current_date = params[0]
        months = params[1]
        return n_months(current_date, months)
    elif algo_name == 'sum':
        df = params[0]
        col_name = params[1]
        return sum_algo(df, col_name)
    elif algo_name == 'mean':
        df = params[0]
        col_name = params[1]
        return mean_algo(df, col_name)
    elif algo_name == 'median':
        df = params[0]
        col_name = params[1]
        return median_algo(df, col_name)
    elif algo_name == 'min':
        df = params[0]
        col_name = params[1]
        return min_algo(df, col_name)
    elif algo_name == 'max':
        df = params[0]
        col_name = params[1]
        return max_algo(df, col_name)
    elif algo_name == 'count':
        df = params[0]
        col_name = params[1]
        return count_algo(df, col_name)
    elif algo_name == 'sort':
        df = params[0]
        sort_by = params[1]
        is_asc = None
        if len(params) > 2:
            is_asc = params[2]
        return sort_algo(df, sort_by, is_asc)
    elif algo_name == 'limit':
        df = params[0]
        limit_no = params[1]
        return limit_algo(df, limit_no)
    elif algo_name == 'alias':
        df = params[0]
        alias_name = params[1]
        if len(params) > 2:
            col_to_change = params[2]
        else:
            col_to_change = None
        return alias_algo(df, alias_name, col_to_change)
    elif algo_name == 'merge':
        df1 = params[0]
        df2 = params[1]
        on_cols = params[2]
        how = params[3]
        return merge_algo(df1, df2, on_cols, how)
    elif algo_name == 'concat':
        df1 = params[0]
        df2 = params[1]
        return concat_algo(df1, df2)
    elif algo_name == 'select':
        df = params[0]
        cols = params[1]
        return select_algo(df, cols)
    elif algo_name == '调用':
        file_locate = params[0]
        params = params[1]
        return invoke_py_algo(file_locate, params)
    return 0

def concat_algo(df1, df2):
    if df1.is_empty() and not df2.is_empty():
        return df2
    elif not df1.is_empty and df2.is_empty():
        return df1
    elif df1.is_empty and df2.is_empty():
        return pl.DataFrame()

    df = pl.concat([df1, df2], how='vertical')
    return df


def select_algo(df, cols):
    if df.is_empty():
        return df
    else:
        existing_columns = [col for col in cols if col in df.columns]
        selected_df = df.select(existing_columns)
        return selected_df

def select_algo(df, cols):
    if df.is_empty():
        return df
    else:
        existing_columns = [col for col in cols if col in df.columns]
        selected_df = df.select(existing_columns)
        return selected_df

def platform_date():
    current_date = datetime.now()
    return current_date.strftime('%Y-%m-%d')


def n_days(current_date, days):
    current_d = datetime.strptime(current_date, '%Y-%m-%d')
    previous_date = current_d - timedelta(days=days)
    return previous_date.strftime('%Y-%m-%d')


def n_months(current_date, months):
    current_d = datetime.strptime(current_date, '%Y-%m-%d')
    previous_date = current_d - timedelta(days=months * 30)
    return previous_date.strftime('%Y-%m-%d')


def agg_algo(df: pl.DataFrame, group_keys: list, algos:str, alias_name=None):
    # 假设没有任何额外指标提供，资产代码又在dataframe里，用资产代码作为该字段
    # 支持字典
    if df is None or df.is_empty():
        return pl.DataFrame()
    if isinstance(algos, dict):
        oper_list = []
        for ind, algo_name in algos.items():
            alias = ind
            if alias_name and isinstance(alias_name, dict):
                if ind in alias_name.keys():
                    alias = alias_name[ind]
            if ind in df.columns:
                if algo_name == 'sum':
                    oper_list.append(pl.col(ind).fill_null(0).sum().alias(alias))
                elif algo_name == 'mean' or algo_name == 'avg' or algo_name == 'average':
                    oper_list.append(pl.col(ind).fill_null(0).mean().alias(alias))
                elif algo_name == 'count' or algo_name == 'len':
                    oper_list.append(pl.col(ind).fill_null(0).len().alias(alias))
                elif algo_name == 'first':
                    oper_list.append(pl.col(ind).fill_null(0).first().alias(alias))
                elif algo_name == 'last':
                    oper_list.append(pl.col(ind).fill_null(0).last().alias(alias))
                elif algo_name == 'max':
                    oper_list.append(pl.col(ind).fill_null(0).max().alias(alias))
                elif algo_name == 'min':
                    oper_list.append(pl.col(ind).fill_null(0).min().alias(alias))
                elif algo_name == 'concat' or algo_name == 'cat':
                    oper_list.append(pl.col(ind).str.concat(",").alias(alias))
        lz = (
            df.lazy().group_by(group_keys).agg(oper_list)
        )
    else:
        if alias_name is not None and isinstance(alias_name, dict) and len(alias_name.keys()) > 0:
            ind = list(alias_name.keys())[0]
            alias = alias_name[ind]

        else:
            ind = t.find_prop(list(df.columns))
            if ind is None:
                ind = list(set(df.columns) - set(group_keys))[0]
            alias = ind
        if algos == 'sum':
            lz = (
                df.lazy().group_by(group_keys).agg(pl.col(ind).fill_null(0).sum().alias(alias))
            )
        elif algos == 'mean' or algos == 'avg' or algos == 'average':
            lz = (
                df.lazy().group_by(group_keys).agg(pl.col(ind).fill_null(0).mean().alias(alias))
            )
        elif algos == 'count' or algos == 'len':
            lz = (
                df.lazy().group_by(group_keys).agg(pl.col(ind).fill_null(0).len().alias(alias))
            )
        elif algos == 'first':
            lz = (
                df.lazy().group_by(group_keys).agg(pl.col(ind).fill_null(0).first().alias(alias))
            )
        elif algos == 'last':
            lz = (
                df.lazy().group_by(group_keys).agg(pl.col(ind).fill_null(0).last().alias(alias))
            )
        elif algos == 'max':
            lz = (
                df.lazy().group_by(group_keys).agg(pl.col(ind).fill_null(0).max().alias(alias))
            )
        elif algos == 'min':
            lz = (
                df.lazy().group_by(group_keys).agg(pl.col(ind).fill_null(0).min().alias(alias))
            )
        else:
            lz = (
                df.lazy().group_by(group_keys).agg(pl.col(ind).fill_null(0).sum().alias(alias))
            )
    df = lz.collect()
    return df


def sum_algo(df: pl.DataFrame, col_name: str):
    if df.is_empty():
        return 0
    return df.select(col_name).to_series().sum()


def mean_algo(df: pl.DataFrame, col_name: str):
    if df.is_empty():
        return 0
    return df.select(col_name).to_series().mean()


def max_algo(df: pl.DataFrame, col_name: str):
    if df.is_empty():
        return 0
    return df.select(col_name).to_series().max()


def min_algo(df: pl.DataFrame, col_name: str):
    if df.is_empty():
        return 0
    return df.select(col_name).to_series().min()


def median_algo(df: pl.DataFrame, col_name: str):
    if df.is_empty():
        return 0
    return df.select(col_name).to_series().median()


def count_algo(df: pl.DataFrame, col_name: str):
    if df.is_empty():
        return 0
    return df.select(col_name).to_series().len()


def sort_algo(df: pl.DataFrame, sort_bys, is_asc=None):
    if df.is_empty():
        return df
    if is_asc is None or is_asc == '升序':
        lz = (df.lazy().sort(by=sort_bys, descending=False))
        return lz.collect()
    else:
        lz = (df.lazy().sort(by=sort_bys, descending=True))
        return lz.collect()


def limit_algo(df: pl.DataFrame, limit_no):
    if df.is_empty():
        return df
    return df.head(limit_no)


def alias_algo(df: pl.DataFrame, alias_name: str, col_to_change):
    if not df.is_empty():
        cols = list(df.columns)
        if col_to_change is None:
            col_to_change = get_result_col(cols)
        df = df.rename({col_to_change: alias_name})
        return df
    else:
        return df


def merge_algo(df1: pl.DataFrame, df2: pl.DataFrame, on_cols: list, how='left'):
    if df1.is_empty() and not df2.is_empty():
        return df2
    elif not df1.is_empty() and df2.is_empty():
        return df1
    else:
        return df1.join(df2, on=on_cols, how=how)

def invoke_py_algo(file_locate: str, params: dict):
    params_str = json.dumps(params, ensure_ascii=False)
    python_result = run_script_in_venv(PYTHON_PATH, file_locate, params_str)
    if python_result['success']:
        result = dict()
        parent_dir = str(os.path.dirname(file_locate))
        if python_result['success']:
            new_files = get_files_in_dir(parent_dir)
            for file_addr in new_files:
                file_path = Path(file_addr)
                ext = file_path.suffix
                if ext.lower() == '.csv':
                    base_name = os.path.basename(file_addr)
                    file_name = os.path.splitext(base_name)[0]
                    df = pl.read_csv(file_addr)
                    result[file_name] = df
        return result
    else:
        raise Exception(python_result['stderr'])


