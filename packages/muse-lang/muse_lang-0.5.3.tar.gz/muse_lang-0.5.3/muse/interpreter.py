# 运行解释器：遍历AST节点，根据树结构顺序分别解析运行
# 调用tag_engine(标签处理), ind_engine(指标获取), calc_engine(四则运算引擎), algo_engine(金融算法引擎)来对语句进行处理
import traceback
from turtledemo.penrose import start

from muse.ast_struct import AstVisitor,  Binary, Unary, Variable, FunctionCall, DotExp
from muse.scanner import Op
from muse.engines import tag_engine, algo_engine, calc_engine, indicator_engine
from collections import OrderedDict
import logging
from datetime import datetime


blanks = '-' * 4


# 打印AST的调试程序
class Interpreter(AstVisitor):
    def __init__(self, props):
        super().__init__()
        self.results = OrderedDict()
        self.props = set(props)
        # self.start_date = datetime.now().date().strftime('%Y-%m-%d')
        # self.end_date = self.start_date
        self.start_date = None
        self.end_date = None
        self.search_mode = '单元测试'

    def visit_function_call(self, func_call: FunctionCall, additional):
        # 获得函数调用名称
        name = func_call.name
        ps = list()
        for p in func_call.params:
            ps.append(self.visit(p, additional))

        try:
            #  如果是以下三个函数调用，则使用
            tags, fields, pen, drop_duplicate = tag_engine.parse_tags_and_fields(func_call.params)
            props = list(set(fields + list(self.props)))
            if name == '资产':
                if '资产代码' in self.results:
                    return tag_engine.asset_tag(tags, props, sec_ids=self.results['资产代码'], start_date=self.start_date, end_date=self.end_date, drop_duplicate=drop_duplicate, search_mode=self.search_mode)
                else:
                    return tag_engine.asset_tag(tags, props, start_date=self.start_date, end_date=self.end_date, drop_duplicate=drop_duplicate, search_mode=self.search_mode)
            elif name == '主体':
                return tag_engine.issuer_tag(tags, props, start_date=self.start_date, end_date=self.end_date, drop_duplicate=drop_duplicate, search_mode=self.search_mode)
            elif name == '产品':
                if '产品代码' in self.results:
                    return tag_engine.port_tag(tags, props, port_ids=self.results['产品代码'], start_date=self.start_date, end_date=self.end_date, drop_duplicate=drop_duplicate, search_mode=self.search_mode)
                return tag_engine.port_tag(tags, props, start_date=self.start_date, end_date=self.end_date, drop_duplicate=drop_duplicate, search_mode=self.search_mode)
            elif name == 'filter':
                return tag_engine.filter_algo(ps, self.props)
            elif name == '指标':
                p_ids = self.results.get('产品代码', None)
                s_ids = self.results.get('资产代码', None)
                return indicator_engine.fetch_inds(ps, port_ids=p_ids, sec_ids=s_ids, start_date=self.start_date, end_date=self.end_date, search_mode=self.search_mode)
            else:
                return algo_engine.algo_handler(name, ps)
        except Exception:
            self.add_error(traceback.format_exc(), func_call.begin_pos)
            return

    def visit_binary(self, binary: Binary, additional):
        exp1 = binary.exp1
        exp2 = binary.exp2
        op = binary.op
        sec_ids = None
        port_ids = None
        if '资产代码' in self.results:
            sec_ids = self.results['资产代码']
        if '产品代码' in self.results:
            port_ids = self.results['产品代码']
        # 如果是in操作，要保证左侧和右侧都是函数调用
        if op == Op.In and isinstance(exp1, FunctionCall) and isinstance(exp2, FunctionCall):
            try:
                result = tag_engine.in_tag(exp1, exp2, self.props, sec_ids=sec_ids, port_ids=port_ids, start_date=self.start_date, end_date=self.end_date, search_mode=self.search_mode)
            except Exception:
                self.add_error(traceback.format_exc(), binary.begin_pos)
                result = None
        elif op == Op.In and isinstance(exp1, Binary) and isinstance(exp2, FunctionCall):
            try:
                result = tag_engine.in_tag2(exp1, exp2, self.props, sec_ids=sec_ids, port_ids=port_ids, start_date=self.start_date, end_date=self.end_date, search_mode=self.search_mode)
            except Exception:
                self.add_error(traceback.format_exc(), binary.begin_pos)
                result = None
        elif op == Op.In and isinstance(exp1, Variable) and isinstance(exp2, Variable):
            try:
                result = tag_engine.in_tag3(self.results[exp1.name], self.results[exp2.name], self.props, sec_ids=sec_ids, port_ids=port_ids, start_date=self.start_date, end_date=self.end_date, search_mode=self.search_mode)
            except Exception:
                self.add_error(traceback.format_exc(), binary.begin_pos)
                result = None
        else:
            v1 = self.visit(exp1, None)
            v2 = self.visit(exp2, None)
            if op == Op.Assign:
                v1 = self.visit(exp1, 'left')
                if v1 == '开始日期':
                    self.start_date = v2
                    logging.debug('调用赋值表达式, 把 {} 放入 {}'.format(v2, 'start_date'))
                elif v1 == '结束日期':
                    self.end_date = v2
                    logging.debug('调用赋值表达式, 把 {} 放入 {}'.format(v2, 'end_date'))
                elif v1 == '查询模式':
                    self.search_mode = v2
                else:
                    self.results[v1] = v2
                    logging.debug('调用赋值表达式, 把 {} 放入 {}'.format(v1, self.results))

                result = v2
            else:
                try:
                    result = calc_engine.handle_binary_op(op, v1, v2)
                except Exception:
                    self.add_error(traceback.format_exc(), binary.begin_pos)
                    result = None
        return result

    def visit_unary(self, unary: Unary, additional):
        v = self.visit(unary.exp, additional)
        if unary.op == Op.Minus:
            return -1 * v
        else:
            self.add_error('一元运算只支持 "-"', unary.begin_pos)
            return None

    def visit_dot_exp(self, dot_exp: DotExp, additional):
        base_exp = self.visit(dot_exp.base_exp, additional)
        prop_exp = self.visit(dot_exp.prop, additional)
        try:
            return indicator_engine.indicator_handle(base_exp, prop_exp)
        except Exception:
            self.add_error(traceback.format_exc(), dot_exp.begin_pos)
            return None

    def visit_variable(self, variable: Variable, additional):
        var_name = variable.name
        if additional is not None and additional == 'left':
            return var_name
        else:
            if var_name in self.results:
                logging.debug('{} 已经被解析过直接使用. 之前解析的结果为 {}'.format(var_name, self.results[var_name]))
                return self.results[var_name]
            else:
                logging.debug('没有在{} 中 发现 {}.这一定是个需要的指标'.format(self.results, var_name))
                return var_name



