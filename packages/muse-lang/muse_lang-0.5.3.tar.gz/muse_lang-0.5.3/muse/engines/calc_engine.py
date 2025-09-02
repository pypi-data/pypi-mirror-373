# 四则运算解析
# Dataframe之间的广播类和向量计算
# 先merge相关dataframe再进行计算
from muse.scanner import Op
import polars as pl
import logging


def handle_in_op(exp1, exp2):
    logging.debug('调用in处理函数 {} in {}; 调用结果: {}'.format(exp1, exp2, 5))
    return 5


def handle_binary_op(op: Op, exp1, exp2):
    # 准备默认值
    if isinstance(exp1, tuple):
        exp1_var, exp1 = exp1
    else:
        exp1_var, exp1 = None, exp1

    if isinstance(exp2, tuple):
        exp2_var, exp2 = exp2
    else:
        exp2_var, exp2 = None, exp2

    if isinstance(exp1, pl.DataFrame) and exp1.is_empty():
        return pl.DataFrame()
    if isinstance(exp2, pl.DataFrame) and exp2.is_empty():
        return pl.DataFrame()

        # DataFrame与标量之间的操作
    if exp1_var is not None and exp2_var is None:
        exp1 = perform_operation_on_df_and_scalar(op, exp1, exp1_var, exp2)
        result = exp1

        # 标量与DataFrame之间的操作
    elif exp1_var is None and exp2_var is not None:
        exp2 = perform_operation_on_scalar_and_df(op, exp1, exp2, exp2_var)
        result = exp2

        # 两个都是DataFrame
    elif exp1_var is not None and exp2_var is not None:
        result = perform_operation_on_dfs(op, exp1, exp2, exp1_var, exp2_var)

        # 两个都是标量
    else:
        result = perform_operation_on_scalars(op, exp1, exp2)

    logging.debug('调用二元运算: {} {} {}; 调用结果: {}'.format(exp1, op.name, exp2, result))
    return result


def perform_operation_on_df_and_scalar(op, exp1, exp1_var, exp2):
    if op == Op.Plus:
        return exp1.with_columns((pl.col(exp1_var) + exp2).alias(exp1_var))
    elif op == Op.Minus:
        if exp1.select(exp1_var).to_series().dtype == pl.String and isinstance(exp2, str):
            return exp1.with_columns(
                (pl.col(exp1_var).str.to_datetime("%Y-%m-%d") - pl.Series([exp2]).str.to_datetime("%Y-%m-%d"))
                .dt.total_days().alias(exp1_var))
        else:
            return exp1.with_columns((pl.col(exp1_var) - exp2).alias(exp1_var))
    elif op == Op.Multiply:
        return exp1.with_columns((pl.col(exp1_var) * exp2).alias(exp1_var))
    elif op == Op.Divide:
        return exp1.with_columns((pl.col(exp1_var) / exp2).alias(exp1_var))


def perform_operation_on_scalar_and_df(op, exp1, exp2, exp2_var):
    if op == Op.Plus:
        return exp2.with_columns((exp1 + pl.col(exp2_var)).alias(exp2_var))
    elif op == Op.Minus:
        if exp2.select(exp2_var).to_series().dtype == pl.String and isinstance(exp1, str):
            return exp2.with_columns(
                pl.Series([exp1]).str.to_datetime("%Y-%m-%d") - (pl.col(exp2_var).str.to_datetime("%Y-%m-%d"))
                .dt.total_days().alias(exp2_var))
        else:
            return exp2.with_columns((exp1 - pl.col(exp2_var)).alias(exp2_var))
    elif op == Op.Multiply:
        return exp2.with_columns((exp1 * pl.col(exp2_var)).alias(exp2_var))
    elif op == Op.Divide:
        return exp2.with_columns((exp1 / pl.col(exp2_var)).alias(exp2_var))


def perform_operation_on_dfs(op, exp1, exp2, exp1_var, exp2_var):
    # 打印并清理列重命名
    common_cols = list(set(exp1.columns).intersection(exp2.columns))
    if len(common_cols) == len(exp1.columns) and len(common_cols) == len(exp2.columns):
        df = exp1
    else:
        df = exp1.join(exp2, on=common_cols, how='left')

    if op == Op.Plus:
        result = df.with_columns((pl.col(exp1_var) + pl.col(exp2_var)).alias(exp1_var + '+' + exp2_var))
    elif op == Op.Minus:
        if df.select(exp1_var).to_series().dtype == pl.String and df.select(exp2_var).to_series().dtype == pl.String:
            result = df.with_columns(
                (pl.col(exp1_var).str.to_datetime("%Y-%m-%d") - pl.col(exp2_var).str.to_datetime("%Y-%m-%d"))
                .dt.total_days().cast(pl.Int64).alias(exp1_var + '-' + exp2_var))
        elif df.select(exp1_var).to_series().dtype == pl.UInt16 and df.select(exp2_var).to_series().dtype == pl.UInt16:
            result = df.with_columns(
                (pl.col(exp1_var).cast(pl.Int64) - pl.col(exp2_var).cast(pl.Int64)).cast(pl.Int64).alias(f"{exp1_var}-{exp2_var}")
            )
        else:
            result = df.with_columns((pl.col(exp1_var) - pl.col(exp2_var)).alias(exp1_var + '-' + exp2_var))
    elif op == Op.Multiply:
        result = df.with_columns((pl.col(exp1_var) * pl.col(exp2_var)).alias(exp1_var + '*' + exp2_var))
    elif op == Op.Divide:
        result = df.with_columns((pl.col(exp1_var) / pl.col(exp2_var)).alias(exp1_var + '/' + exp2_var))

    return result
    # return result.drop([exp1_var, exp2_var])


def perform_operation_on_scalars(op, exp1, exp2):
    if op == Op.Plus:
        return exp1 + exp2
    elif op == Op.Minus:
        return exp1 - exp2
    elif op == Op.Multiply:
        return exp1 * exp2
    elif op == Op.Divide:
        return exp1 / exp2