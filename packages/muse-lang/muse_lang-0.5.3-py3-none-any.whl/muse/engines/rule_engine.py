from collections import OrderedDict
import polars as pl
import traceback
import re
import logging

def extract_fields(expression):
    # 匹配中文字符、英文字母、数字和下划线组成的字段名
    # pattern = r'([\u4e00-\u9fa5a-zA-Z0-9_（）()+-]+)\s*(?:<|>|==|!=|<=|>=)\s*'
    pattern = r'(?:\(*([\u4e00-\u9fa5a-zA-Z0-9_（）+-]+)\)*)\s*(?:<|>|==|!=|<=|>=)\s*'
    fields = re.findall(pattern, expression)
    # 去重并返回
    return list(set(fields))

def use_rule(rules: dict, df: pl.DataFrame) -> pl.DataFrame:
    if df is None or df.is_empty():
        return df
    result_dfs = []
    monitor_rule = list(rules.values())[0]
    # 将每个rule中需要的字段都提取出来
    all_filter_fields = list()
    for _, rule in rules.items():
        fields = extract_fields(rule)
        all_filter_fields = all_filter_fields + fields

    all_filter_fields = list(set(all_filter_fields))
    normal_df = df
    # 将空值和inf过滤出来
    for col in all_filter_fields:
        try:
            inf_df = normal_df.filter(pl.col(col).is_infinite())
        except:
            inf_df = pl.DataFrame()
        if not inf_df.is_empty():
            inf_df_after_rule = inf_df.with_columns(pl.lit('除0异常').alias('监控结果'), pl.lit(monitor_rule).alias('监控规则'))
            normal_df = normal_df.filter(~(pl.col(col).is_infinite()))
            result_dfs.append(inf_df_after_rule)
        try:
            none_df = normal_df.filter(pl.col(col).is_null() | pl.col(col).is_nan())
        except:
            none_df = pl.DataFrame()
        if not none_df.is_empty():
            none_df_after_rule = none_df.with_columns(pl.lit('其他异常').alias('监控结果'), pl.lit(monitor_rule).alias('监控规则'))
            normal_df = normal_df.filter(~(pl.col(col).is_null() | pl.col(col).is_nan()))
            result_dfs.append(none_df_after_rule)
    try:
        expressions = {
            rule_result: build_expression(rule_expr, all_filter_fields) for rule_result, rule_expr in rules.items()
        }
    except Exception:
        logging.info(traceback.format_exc())
        return df.with_columns(
                pl.lit('监控规则出现错误：请检查是否在监测规则中引用了没有的字段。').alias("监控结果")
        )

    for rule_result, mask in expressions.items():
        try:
            # 直接使用生成的 mask
            filtered_df = normal_df.filter(mask[0])
            filtered_df = filtered_df.with_columns(
                pl.lit(rule_result).alias("监控结果"),
                # pl.lit(monitor_rule) # 所有同一规则
                pl.lit(mask[1]).alias("监控规则")  # 不同规则
            )
            result_dfs.append(filtered_df)
        except Exception:
            logging.error(traceback.format_exc())
            return df.with_columns(
                pl.lit('监控规则出现错误：请检查是否在监测规则中引用了没有的字段。').alias("监控结果")
            )

    if result_dfs:
        sorted_col = all_filter_fields[0]
        result = pl.concat(result_dfs)
        # 对result进行排序
        custom_order = ['触发超限', '触发预警', '除0异常', '其他异常', '未达到条件', '正常']
        existing_values = result["监控结果"].unique().to_list()

        # 合并custom_order和未定义值（去重）
        full_order = custom_order + [v for v in existing_values if v not in custom_order]
        result = result.with_columns(
            pl.col("监控结果")
            .cast(pl.Enum(full_order))
        ).sort("监控结果", sorted_col, descending=[False, True])
        return result
    else:
        return df


def build_expression(rule_str: str, df_columns: list) -> pl.Expr:
    # 构造表达式
    rule_logic = rule_str
    for col in sorted(df_columns, key=len, reverse=True):
        rule_logic = rule_logic.replace(col, f'pl.col("{col}")')

        # 使用 Polars 表达式解析
    return eval(rule_logic), rule_str

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


def parse_result(results: OrderedDict):
    r = OrderedDict()
    rules = dict()
    for k, v in results.items():
        if k == '监控规则':
            rules = v
        else:
            r[k] = v

    if len(r) > 0 and len(rules) > 0:
        name, df = r.popitem()
        r[name] = use_rule(rules, df)
    return r