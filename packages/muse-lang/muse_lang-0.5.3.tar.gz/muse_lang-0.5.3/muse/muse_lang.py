from mpmath.libmp import trailing

from muse.scanner import Scanner, CharStream, TokenKind
from muse.ast_struct import AstDumper, Prog
from muse.interpreter import Interpreter
from muse.resolver import Resolver
from muse.parser import Parser
import muse.engines.rule_engine as rule_engine
import muse.sample as sample
from muse.auto_complete import parse_info
from muse.data_source.base import DataSourceInterface
from muse.data_source.ds_manager import ds_manager
import traceback
from collections import OrderedDict
import polars as pl
import re
SEP_LINE = '\n' + '-' * 100


# 词法分析
def token_analyse(program: str):
    # print('源代码: ' + SEP_LINE)
    # print(program)
    # print('词法分析结果: ' + SEP_LINE)
    scanner = Scanner(CharStream(program))
    tokens = list()
    while scanner.peek().kind != TokenKind.EOF:
        tokens.append(scanner.next())
    # for t in tokens:
    #     print(t)
    scanner = Scanner(CharStream(program))
    return scanner


# 语法分析
def ast_build(scanner: Scanner):
    parser = Parser(scanner)
    prog = parser.parse_prog()
    # print('\n语法分析后的AST: ' + SEP_LINE)
    ast_dumper = AstDumper()
    ast_dumper.visit(prog, '')
    return prog, parser.errors, ast_dumper.statements


# 语法消融及编译器错误排查
def resolve(prog: Prog):
    # print('\n编译器前检查: ' + SEP_LINE)
    resolver = Resolver()
    resolver.visit(prog, '')
    return resolver.props, resolver.errors, resolver.prompts


def run_program(prog: Prog, props: list):
    # print('\n执行AST: ' + SEP_LINE)
    interpreter = Interpreter(props)
    interpreter.visit(prog, '')
    # 增加监控规则的处理逻辑
    results = interpreter.results
    return results, interpreter.errors


def compile_and_run(program: str, ast_only=False, run_only=True):
    try:
        scanner = token_analyse(program)
        prog, parse_errors, statements = ast_build(scanner)
    except Exception:
        traceback.print_exc()
        return {'code': 'FAIL', 'data': ['语法解析出错，问题可能原因: 1) 包含中文的引号或其他特殊符号；2) 程序以非法结束符；']}

    # 如果只是想获得AST
    if ast_only:
        if len(parse_errors) > 0:
            p_errors = [{'error_pos': str(error.begin_pos), 'error_msg': error.msg} for error in parse_errors]
            return {'code': 'FAIL', 'parse_errors': p_errors, 'statements': statements}
        else:
            props, compile_errors, repositories = resolve(prog)
            if len(compile_errors) > 0:
                c_errors = [{'error_pos': str(error.begin_pos), 'error_msg': error.msg} for error in compile_errors]
                return {'code': 'FAIL', 'parse_errors': c_errors, 'statements': statements}
            else:
                return {'code': 'SUCCESS', 'repositories': repositories, 'statements': statements}
    # 如果是完全编译和运行程序
    else:
        # 如果AST分析时没有报错
        if len(parse_errors) == 0:
            props, compile_errors, repositories = resolve(prog)
            # 如果编译时没有报错
            if len(compile_errors) == 0:
                results, run_errors = run_program(prog, props)
                # 如果运行时没有问题
                # if len(run_errors) == 0:
                    # 变换之后的信息
                result_dict = rule_engine.parse_result(results)
                if run_only:
                    val = list(result_dict.values())[-1]
                    result_dict = dict()
                    result_dict['结果'] = val
                else:
                    result_dict = OrderedDict(reversed(result_dict.items()))
                error_msgs = [str(error) for error in run_errors]
                return {'code': 'SUCCESS', 'data': result_dict, 'error_msgs': error_msgs}
                # else:
                #     return {'code': 'FAIL', 'data': run_errors}

            else:
                error_msgs = [str(error) for error in compile_errors]
                return {'code': 'FAIL', 'data': error_msgs, 'error_msgs': error_msgs}
        else:
            error_msgs = [str(error) for error in parse_errors]
            return {'code': 'FAIL', 'data': error_msgs, 'error_msgs': error_msgs}


def run(program: str):
    ast_only = False
    run_only = True
    return compile_and_run(program, ast_only, run_only)


def trial(program: str):
    ast_only = False
    run_only = False
    return compile_and_run(program, ast_only, run_only)

def run_with_params(program: str, params: dict, head=0):
    # 先替换program中的所有参数
    appendix= ''
    for p_name, p_value in params.items():
        pattern = r"('{{p_name}}':\s*)(?:\[[^\]]*\]|'[^']*'|\{[^}]*\})(?=\s*[,}])"
        pattern = pattern.replace('{{p_name}}', p_name)
        replacement = rf"\1{p_name}"
        program = re.sub(pattern, replacement, program)
        if p_value == '' or p_value is None:
            appendix += f'{p_name} = ""\n'
        elif isinstance(p_value, str):
            appendix += f'{p_name} = "{p_value}"\n'
        else:
            appendix += f'{p_name} = {p_value}\n'

    full_program = appendix + program
    print('变换后的muse语句:')
    print(full_program)
    trial_result = trial(full_program)
    df_dict = dict()
    if trial_result['code'] == 'SUCCESS':
        result_data = trial_result['data']
        for k, df in result_data.items():
            if isinstance(df, dict):
                for kk, val in df.items():
                    if isinstance(val, pl.DataFrame):
                        if head == 0:
                            df_dict[kk] = val
                        else:
                            df_dict[kk] = val.head(head)
            elif isinstance(df, pl.DataFrame):
                if head == 0:
                    df_dict[k] = df
                else:
                    df_dict[k] = df.head(head)
    print(trial_result['error_msgs'])
    return df_dict


def compile_run_all():
    print(compile_and_run(sample.demo0))
    print(compile_and_run(sample.demo1))
    print(compile_and_run(sample.demo2))
    print(compile_and_run(sample.demo3))
    print(compile_and_run(sample.demo4))
    print(compile_and_run(sample.demo5))
    print(compile_and_run(sample.demo6))
    print(compile_and_run(sample.demo7))
    print(compile_and_run(sample.demo18))
    print(trial(sample.demo0))

def ast_check(program: str):
    ast_only = True
    run_only = True
    response = compile_and_run(program, ast_only=ast_only, run_only=run_only)

    statements = list()

    stms = response.get('statements', list())
    for s in stms:
        if '空语句' not in s:
            statements.append(s)

    colors, prompts = parse_info(statements)
    reps = response.get('repositories', list())
    for r in reps:
        colors['指标'] = colors['指标'] + r[1]

    response['prompts'] = prompts
    response['colors'] = colors
    if 'statements' in response:
        del response['statements']
    return response

def init_ds(data_source: DataSourceInterface):
    ds_manager.init_ds(data_source)

if __name__ == '__main__':
    # code1 = '''单一资产持仓 = 资产(['单一资产'], ['全价市值']) in 产品([])
    # 产品指标库 = 指标('产品估值指标库', ['当日单位净值', '当日净资产', '产品代码', '统计日期'], {'START_DATE': '2025-05-01', 'END_DATE': '2025-05-03'})
    # 监控规则 = {'触发超限': '全价市值 > 30000000', '触发预警': '(全价市值 > 15000000) & (全价市值 <= 30000000)', '正常': '全价市值 <= 15000000'}
    # '''
    # code = '''单一资产持仓 = 资产(['''
    # # print(trial(code1))
    # print(ast_check(code1))
    # print(compile_and_run(sample.demo5, ast_only=True, run_only=True))
    # parameters = {'PORT_ID': 'abc,bcd', 'port_tags': ['公募开放式', '封闭式'], 'asset_tags': '', 'test_param': {'a': 1, 'c': 'd'}}
    # result = run_with_params(sample.demo5, parameters, head=3)
    params = {'PORT_IDS': '1801ZQ0265,2001XA0006', 'START_DATE': '2024-04-01', 'END_DATE': '2024-04-01'}
    result = run_with_params(sample.demo8, params)
    print(result)