import polars as pl
from datetime import datetime
def filter_dates(pdf: pl.DataFrame, start_date, end_date):
    if '日期' in pdf.columns:
        pdf = pdf.with_columns(
            pl.col("日期").str.to_date("%Y-%m-%d")
        )
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            return pdf.filter(pl.col("日期").is_between(start_date, end_date, closed="both"))
    return pdf


# 根据产品代码或者资产代码过滤
def filter_ports_sec(pdf: pl.DataFrame, port_ids: list = [], sec_ids: list = [], start_date=None, end_date=None):
    pdf = filter_dates(pdf, start_date, end_date)
    if (port_ids is not None) and (len(port_ids) > 0) and (
            '查询所有组合' not in port_ids) and '产品代码' in pdf.columns:
        pdf = pdf.filter(pl.col("产品代码").is_in(port_ids))
    if sec_ids is not None and len(sec_ids) > 0 and '资产代码' in pdf.columns:
        pdf = pdf.filter(pl.col("资产代码").is_in(sec_ids))
    return pdf


def filter_ports(pdf: pl.DataFrame, port_ids: list = [], start_date=None, end_date=None):
    pdf = filter_dates(pdf, start_date, end_date)
    if (port_ids is not None) and (len(port_ids) > 0) and ('查询所有组合' not in port_ids):
        pdf = pdf.filter(pl.col("产品代码").is_in(port_ids))
    return pdf

def filter_hld_data(df: pl.dataframe, penetrate: str):
    ctlx = []
    if penetrate is None:
        ctlx = ['00', '01', '02']
    elif penetrate == '不穿透':
        ctlx = ['00', '01', '02']
    elif penetrate == '全穿透':
        ctlx = ['00', '11', '12']
    elif penetrate == '自主管理穿透':
        ctlx = ['00', '11', '02']
    elif penetrate == '委外投资穿透':
        ctlx = ['00', '01', '12']
    df = df.filter(pl.col("穿透类型").is_in(ctlx))
    return df

def convert_decimal_to_float(df: pl.DataFrame) -> pl.DataFrame:
    exprs = []
    for col_name, dtype in df.schema.items():
        if str(dtype).startswith("Decimal"):
            exprs.append(pl.col(col_name).cast(pl.Float64).alias(col_name))
        # 其他类型（如 Struct/List）可在此扩展
    return df.with_columns(exprs) if exprs else df

def get_all_unique_fields(cols: list, basic_cols: list) -> list:
    """返回 cols 和 basic_cols 的并集（去重后的所有字段）

    Args:
        cols: 额外字段列表
        basic_cols: 基础字段列表

    Returns:
        去重后的所有字段列表（顺序不保证）
    """
    return list(set(cols) | set(basic_cols))