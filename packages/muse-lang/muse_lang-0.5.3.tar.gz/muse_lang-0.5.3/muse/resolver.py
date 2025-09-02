# 消解器：将AST节点中的变量进行消解匹配和语法检查
from muse.ast_struct import AstVisitor, DotExp, Variable, FunctionCall, Binary
from muse.scanner import Op
import muse.data_interface as t


class Resolver(AstVisitor):
    def __init__(self):
        super().__init__()
        self.props = list()
        self.errors = list()
        self.results = dict()
        self.prompts = list()

    def visit_dot_exp(self, dot_exp: DotExp, additional):
        base_exp = self.visit(dot_exp.base_exp, additional)
        prop_exp = self.visit(dot_exp.prop, additional)

        prop_name = dot_exp.prop.name
        # 检查点运算后面访问的prop(指标)是不是合理的，能够获取的指标
        if t.is_valid_indicator(prop_name):
            self.props.append(prop_name)
        else:
            # error_msg = '点运算后面引用的指标 "{}" 当前不支持. 当前支持的指标有: {}'.format(prop_name, t.VALID_INDS)
            error_msg = '点运算后面引用的指标 "{}" 当前不支持.'.format(prop_name)
            # self.add_error(error_msg, dot_exp.end_pos)
        return prop_name

    def visit_function_call(self, func_call: FunctionCall, additional):
        # 获得函数调用名称
        name = func_call.name
        ps = list()
        for p in func_call.params:
            ps.append(self.visit(p, additional))

        # 检查函数是不是合理的
        if not t.is_valid_func(name):
            error_msg = '函数: "{}" 当前不支持.'.format(name)
            self.add_error(error_msg, func_call.begin_pos)
        elif name == 'agg':
            if len(ps) < 3:
                error_msg = '函数: agg 需要3个参数: 分别为金融对象, [分组字段], 分组方法'
                self.add_error(error_msg, func_call.begin_pos)
        elif name == '指标':
            if len(ps) < 3:
                error_msg = '函数: 指标 需要3个参数，分别为指标库名，指标列表，参数字典'
                self.add_error(error_msg, func_call.begin_pos)
            else:
                self.prompts.append(ps)
        # elif name == '资产' or name == '主体' or name == '资产':
        #     if len(ps) < 1:
        #         error_msg = '函数: "{}" 需要至少1个参数: [标签列表]'
        #         self.add_error(error_msg, func_call.begin_pos)

    def visit_binary(self, binary: Binary, additional):
        exp1 = binary.exp1
        exp2 = binary.exp2

        op = binary.op
        error_msg = 'in 操作符号前后两部分均应该为标签函数调用，"{}" 不是支持的标签调用。目前支持的标签为 "{}"'
        # 如果是in操作，要保证左侧和右侧都是函数调用
        if op == Op.In and isinstance(exp1, FunctionCall) and isinstance(exp2, FunctionCall):
            func1_name = exp1.name
            func2_name = exp2.name
            if func1_name not in t.TAGS:
                self.add_error(error_msg.format(func1_name, t.TAGS), exp1.begin_pos)
            if func2_name not in t.TAGS:
                self.add_error(error_msg.format(func2_name, t.TAGS), exp2.begin_pos)

        elif op == Op.In and isinstance(exp1, Binary) and isinstance(exp2, FunctionCall):
            b1 = exp1
            if exp1.op == Op.In and isinstance(b1.exp1, FunctionCall) and isinstance(b1.exp2, FunctionCall):
                func1_name = b1.exp1.name
                func2_name = b1.exp2.name
                if func1_name not in t.TAGS:
                    self.add_error(error_msg.format(func1_name, t.TAGS), b1.exp1.begin_pos)
                if func2_name not in t.TAGS:
                    self.add_error(error_msg.format(func2_name, t.TAGS), b1.exp2.begin_pos)
        else:
            v1 = self.visit(exp1, 'left')
            v2 = self.visit(exp2, None)
            if op == Op.Assign:
                self.results[v1] = v2
                # print('调用赋值表达式, 把 {} 放入 {}'.format(v1, self.results))

    def visit_variable(self, variable: Variable, additional):
        var_name = variable.name
        if additional is not None and additional == 'left':
            return var_name
        # else:
        #     if var_name not in self.results and not t.is_valid_indicator(var_name):
        #         error_msg = '变量 "{}" 没有被定义就使用.'.format(var_name)
        #         self.add_error(error_msg, variable.begin_pos)
        return var_name
