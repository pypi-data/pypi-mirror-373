from muse.ast_struct import FunctionCall, Binary, AstVisitor, ArrayLiteral
from muse.engines import rule_engine
import pandas as pd
import polars as pl
import muse.data_interface as di
from muse.scanner import Op
import logging
import ast
import operator
import logging as logger
interpreter = AstVisitor()


def asset_tag(tags: list, props=None, sec_ids=None, start_date='', end_date='', drop_duplicate=False, search_mode='测试'):
    logging.debug('调用资产标签成功 {} with props {}'.format(tags, props))
    sec_list = []
    if sec_ids is not None:
        sec_list = [i.strip() for i in sec_ids.split(',')]
    ast = di.get_assets(search_mode, start_date, end_date, tags, sec_list, props)
    return ast


def issuer_tag(tags: list, props=None, start_date='', end_date='', drop_duplicate=False, search_mode='测试'):
    logging.debug('调用主体标签 {} with props {}'.format(tags, props))
    issuer_list = list()
    issuers = di.get_issuers(search_mode, start_date, end_date, tags, issuer_list, props)
    return issuers


def port_tag(tags: list, props=None, port_ids=None, start_date='', end_date ='', drop_duplicate=False, search_mode='测试'):
    logging.debug('调用产品标签  {} with props {}'.format(tags, props))
    # 对着所有的有效产品来处理
    port_list = list()
    if port_ids is not None:
        port_list = [i.strip() for i in port_ids.split(',')]
    port = di.get_ports(search_mode, start_date, end_date, tags, port_list, props)
    return port

def parse_tags_and_fields(params):
    tags = list()
    fields = list()
    pen = False
    drop_duplicates = True
    if len(params) > 0:
        if not isinstance(params[0], ArrayLiteral):
            for p in params:
                tags.append(interpreter.visit(p, None))
        else:
            tp = interpreter.visit(params[0], None)
            for tag in tp:
                tags.append(tag)
            if len(params) > 1:
                if isinstance(params[1], ArrayLiteral):
                    fp = interpreter.visit(params[1], None)
                    for field in fp:
                        fields.append(field)
                else:
                    result = interpreter.visit(params[1], None)
                    if result == '穿透' or result == '全穿透':
                        pen = '全穿透'
                    if result == '不去重':
                        drop_duplicates = False
            if len(params) > 2:
                result = interpreter.visit(params[2], None)
                if result == '穿透' or result == '全穿透':
                    pen = '全穿透'
                if result == '不去重':
                    drop_duplicates = False
            if len(params) > 3:
                result = interpreter.visit(params[3], None)
                if result == '穿透' or result == '全穿透':
                    pen = '全穿透'
                if result == '不去重':
                    drop_duplicates = False

    return tags, fields, pen, drop_duplicates

def in_tag(func1: FunctionCall, func2: FunctionCall, props=None, sec_ids=None, port_ids=None, start_date='', end_date='', search_mode='测试'):
    logging.debug('调用in标签成功 with func1: {} func2: {} props {}'.format(func1.name, func2.name, props))
    penetrate = '不穿透'
    # 解析第一个函数调用
    name1 = func1.name
    tags1, fields1, pen1, drop1 = parse_tags_and_fields(func1.params)

    # 解析第二个函数调用
    name2 = func2.name
    tags2, fields2, pen2, drop2 = parse_tags_and_fields(func2.params)


    # ps1里包含要取的字段
    if name2 == '产品' and name1 == '资产':
        asset_tags = tags1
        asset_fields = fields1
        asset_drop_duplicate = drop1
        penetrate = pen1

        port_tags = tags2
        port_fields = fields2
        port_drop_duplicate = drop2
    else:
        asset_tags = tags2
        asset_fields = fields2
        asset_drop_duplicate = drop2
        penetrate = pen2

        port_tags = tags1
        port_fields = fields1
        port_drop_duplicate = drop1

    if props is None:
        props = list()

    hld_props = list(set(asset_fields + port_fields + list(props)))
    hlds = di.get_hlds(search_mode, start_date, end_date, asset_tags, port_tags, list(hld_props), sec_ids=sec_ids, port_ids=port_ids, penetrate=penetrate)
    return hlds


def in_tag2(b1: Binary, func3: FunctionCall, props=None, sec_ids=None, port_ids=None, start_date='', end_date='', search_mode='测试'):
    logging.debug('调用2连in标签成功 with func1: {} func2: {} func3: {} props {}'.format(b1.exp1, b1.exp2, func3.name, props))
    penetrate = '不穿透'
    # 只有三种标签类型都在的情况下才能用这个函数来实现
    hlds = pd.DataFrame()
    if props is None:
        props = list()
    if b1.op == Op.In and isinstance(b1.exp1, FunctionCall) and isinstance(b1.exp2, FunctionCall):
        func1 = b1.exp1
        func2 = b1.exp2
        funcs = dict()
        hld_props =list()

        for f in [func1, func2, func3]:
            tags, a_props, pen, drop_duplicate = parse_tags_and_fields(f.params)
            a_props = list(set(a_props + list(props)))
            funcs[f.name] = [tags, a_props, pen, drop_duplicate]
            hld_props = list(set(hld_props + a_props))

        penetrate = funcs['资产'][2]
        asts = asset_tag(funcs['资产'][0], funcs['资产'][1], sec_ids, start_date, end_date, drop_duplicate=funcs['资产'][3])
        issuers = issuer_tag(funcs['主体'][0], funcs['主体'][1], start_date, end_date, drop_duplicate=funcs['主体'][3])
        ports = port_tag(funcs['产品'][0], funcs['产品'][1], port_ids, start_date, end_date, drop_duplicate=funcs['主体'][3])
        if isinstance(asts, pl.DataFrame) and asts.is_empty():
            return pl.DataFrame()
        if isinstance(ports, pl.DataFrame) and ports.is_empty():
            return pl.DataFrame()
        hlds = di.get_hlds2(search_mode, start_date, end_date, asts, issuers, ports, list(hld_props), penetrate=penetrate)
    return hlds


def in_tag3(df1: pl.DataFrame, df2: pl.DataFrame, props=None, sec_ids=None, port_ids=None, start_date='', end_date='', search_mode='测试'):
    asts = pl.DataFrame()
    ports = pl.DataFrame()
    if df1 is None:
        df1 = pl.DataFrame()
    if df2 is None:
        df2 = pl.DataFrame()

    if sec_ids is not None:
        sec_ids = [i.strip() for i in sec_ids.split(',')]
        asts = asset_tag([], props, sec_ids, start_date, end_date)
    else:
        if '资产代码' in df1:
            asts = df1
        if '资产代码' in df2:
            asts = df2

    if port_ids is not None:
        port_ids = [i.strip() for i in port_ids.split(',')]
        ports = port_tag([], props, port_ids, start_date, end_date)
    else:
        if '产品代码' in df1:
            ports = df1
        if '产品代码' in df2:
            ports = df2
    if isinstance(asts, pl.DataFrame) and asts.is_empty():
        return pl.DataFrame()
    if isinstance(ports, pl.DataFrame) and ports.is_empty():
        return pl.DataFrame()
    hlds = di.get_hlds3(search_mode, start_date, end_date, asts, ports, list(props))
    return hlds


def safe_eval_filter_rule(filter_rule: str):
    """安全地将类似Python的过滤表达式转换为Polars表达式"""
    # 支持的运算符映射
    op_map = {
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Or: operator.or_,
        ast.And: operator.and_,
    }

    def _convert(node):
        if isinstance(node, ast.Compare):
            left = _convert(node.left)
            ops = [op_map[type(op)] for op in node.ops]
            comparators = [_convert(comp) for comp in node.comparators]
            return ops[0](left, comparators[0])
        elif isinstance(node, ast.BoolOp):
            values = [_convert(v) for v in node.values]
            return op_map[type(node.op)](*values)
        elif isinstance(node, ast.Name):
            return pl.col(node.id)
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        else:
            raise ValueError(f"不支持的表达式节点: {type(node)}")

    try:
        tree = ast.parse(filter_rule, mode='eval')
        return _convert(tree.body)
    except Exception as e:
        raise ValueError(f"无法解析过滤规则: {e}")


def filter_algo(params: list, props: list, start_date='', end_date=''):
    df = params[0]
    filter_rule = params[1]
    if isinstance(df, pl.DataFrame) and df.is_empty():
        return pl.DataFrame()
    try:
        # 使用安全的表达式转换
        expr = safe_eval_filter_rule(filter_rule)
        f_df = df.filter(expr)
    except Exception as ex:
        logger.info(f"filter数据出错: {ex}")
        try:
            all_filter_fields = rule_engine.extract_fields(filter_rule)
            rule_expr = rule_engine.build_expression(filter_rule, all_filter_fields)
            f_df = df.filter(rule_expr[0])
        except Exception as exp:
            raise exp
    return f_df

if __name__ == '__main__':
    print(asset_tag([['债券', '股票']], ['修正久期']))
    print(issuer_tag([['主体评级AAA']], ['流通市值']))
    print(port_tag([['现金管理类']], ['万份收益', '单位净值', '净资产']))

