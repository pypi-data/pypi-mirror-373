# AST结构定义
from muse.scanner import Position, Op
from muse.error import CompileError
import logging


# AST节点基类
class AstNode:
    def __init__(self, begin_pos: Position, end_pos: Position, is_error=False):
        self.begin_pos = begin_pos
        self.end_pos = end_pos
        self.is_error = is_error

    # visitor模式中, 用于接受visitor的访问
    def accept(self, visitor, additional) :
        pass


# 声明: 所有声明都会对应一个符号
class Decl(AstNode):
    def __init__(self, begin_pos: Position, end_pos: Position, name: str, is_error=False):
        super().__init__(begin_pos, end_pos, is_error)
        self.name = name


##### 程序语句开始
class Statement(AstNode):
    def __init__(self, begin_pos: Position, end_pos: Position, is_error=False):
        super().__init__(begin_pos, end_pos, is_error)


# 调用签名
class ParameterList(AstNode):
    def __init__(self, begin_pos: Position, end_pos: Position, params: list, is_error=False):
        super().__init__(begin_pos, end_pos, is_error)
        self.params = params

    def __str__(self):
        return '参数列表'

    def accept(self, visitor, additional) :
        return visitor.visit_parameter_list(self, additional)


# 程序块
class Block(Statement):
    def __init__(self, begin_pos: Position, end_pos: Position, statements: list, is_error=False):
        super().__init__(begin_pos, end_pos, is_error)
        self.statements = statements

    def __str__(self):
        return '程序块'

    def accept(self, visitor, additional):
        return visitor.visit_block(self, additional)


# 整个程序
class Prog(Block):
    def __init__(self, begin_pos: Position, end_pos: Position, statements: list, is_error=False):
        super().__init__(begin_pos, end_pos, statements, is_error)
        self.statements = statements

    def __str__(self):
        return '程序整体'

    def accept(self, visitor, additional) :
        return visitor.visit_prog(self, additional)


##### 表达式开始
class Expression(AstNode):
    def __init__(self, begin_pos: Position, end_pos: Position, is_error=False):
        super().__init__(begin_pos, end_pos, is_error)


# 变量引用
class Variable(Expression):
    def __init__(self, begin_pos: Position, end_pos: Position, name: str, is_error=False):
        super().__init__(begin_pos, end_pos, is_error)
        self.name = name

    def __str__(self):
        return self.name

    def accept(self, visitor, additional) :
        return visitor.visit_variable(self, additional)


# 二元表达式
class Binary(Expression):
    def __init__(self, op: Op, exp1: Expression, exp2: Expression, is_error=False):
        super().__init__(exp1.begin_pos, exp2.end_pos, is_error)
        self.op = op
        self.exp1 = exp1
        self.exp2 = exp2
        self.exp1.parent_node = self
        self.exp2.parent_node = self

    def __str__(self):
        return '二元表达式: ' + self.op.name

    def accept(self, visitor, additional) :
        return visitor.visit_binary(self, additional)


# 一元表达式
class Unary(Expression):
    def __init__(self, begin_pos: Position, end_pos: Position, op: Op, exp: Expression, is_prefix, is_error=False):
        super().__init__(begin_pos, end_pos, is_error)
        self.op = op
        self.exp = exp
        self.is_prefix = is_prefix
        self.exp.parent_node = self

    def __str__(self):
        return '一元表达式: ' + self.op.name

    def accept(self, visitor, additional) :
        return visitor.visit_unary(self, additional)


# 函数调用
class FunctionCall(Expression):
    def __init__(self, begin_pos: Position, end_pos: Position, name: str, params: list, is_error=False):
        super().__init__(begin_pos, end_pos, is_error)
        self.name = name  # 函数名
        self.params = params  # 函数参数列表
        for v in self.params:
            v.parent_node = self

    def __str__(self):
        return '函数调用: ' + self.name

    def accept(self, visitor, additional) :
        return visitor.visit_function_call(self, additional)


# 字符串字面值
class StringLiteral(Expression):
    def __init__(self, pos: Position, value: str, is_error=False):
        super().__init__(pos, pos, is_error)
        self.value = value
        self.the_type = '字符串'

    def accept(self, visitor, additional) :
        return visitor.visit_string_literal(self, additional)


# 整型字面值
class IntegerLiteral(Expression):
    def __init__(self, pos: Position, value: int, is_error=False):
        super().__init__(pos, pos, is_error)
        self.value = value
        self.the_type = '整数'

    def accept(self, visitor, additional) :
        return visitor.visit_integer_literal(self, additional)


# 实数字面值
class DecimalLiteral(Expression):
    def __init__(self, pos: Position, value: float, is_error=False):
        super().__init__(pos, pos, is_error)
        self.value = value
        self.the_type = '浮点数'

    def accept(self, visitor, additional) :
        return visitor.visit_decimal_literal(self, additional)


# 点表达式
class DotExp(Expression):
    def __init__(self, begin_pos: Position, end_pos: Position, base_exp: Expression, prop: Expression, is_error=False):
        super().__init__(begin_pos, end_pos, is_error)
        self.base_exp = base_exp
        self.prop = prop
        self.base_exp.parent_node = self
        self.prop.parent_node = self

    def __str__(self):
        return '点表达式'

    def accept(self, visitor, additional) :
        return visitor.visit_dot_exp(self, additional)


# 数组字面量
class ArrayLiteral(Expression):
    def __init__(self, begin_pos: Position, end_pos: Position, exps: list, is_error=False):
        super().__init__(begin_pos, end_pos, is_error)
        self.exps = exps

    def __str__(self):
        return '数组'

    def accept(self, visitor, additional) :
        return visitor.visit_array_literal(self, additional)


class MapLiteral(Expression):
    def __init__(self, begin_pos: Position, end_pos: Position, exps: list, is_error=False):
        super().__init__(begin_pos, end_pos, is_error)
        self.exps = exps

    def accept(self, visitor, additional) :
        return visitor.visit_map_literal(self, additional)


# 错误表达式
class ErrorExp(Expression):
    def __init__(self, begin_pos: Position, end_pos: Position):
        super().__init__(begin_pos, end_pos, True)
        self.is_error = True

    def accept(self, visitor, additional):
        return visitor.visit_error_expression(self, additional)


# 变量声明
class VariableDeclare(Decl):
    def __init__(self, begin_pos: Position, end_pos: Position, name: str, exp: Expression, is_error=False):
        super().__init__(begin_pos, end_pos, name, is_error)
        self.exp = exp

    def __str__(self):
        return '变量声明: ' + self.name

    def accept(self, visitor, additional) :
        return visitor.visit_variable_declare(self, additional)


# 变量声明语句
class VariableStatement(Statement):
    def __init__(self, begin_pos: Position, end_pos: Position, variable_declare: VariableDeclare, is_error=False):
        super().__init__(begin_pos, end_pos, variable_declare, is_error)
        self.variable_declare = variable_declare

    def __str__(self):
        return '变量声明语句'

    def accept(self, visitor, additional) :
        return visitor.visit_variable_statement(self, additional)


# 表达式语句
class ExpressionStatement(Statement):
    def __init__(self, end_pos: Position, exp: Expression, is_error=False):
        super().__init__(exp.begin_pos, end_pos, is_error)
        self.exp = exp
        self.parent_node = self

    def __str__(self):
        return '表达式语句'

    def accept(self, visitor, additional) :
        return visitor.visit_expression_statement(self, additional)


class ErrorStatement(Statement):
    def __init__(self, begin_pos: Position, end_pos: Position):
        super().__init__(begin_pos, end_pos, True)
        self.is_error = True

    def accept(self, visitor, additional) :
        return visitor.visit_error_statement(self, additional)


class EmptyStatement(Statement):
    def __init__(self, pos: Position, is_error=False):
        super().__init__(pos, pos, is_error)

    def __str__(self):
        return '空语句'

    def accept(self, visitor, additional) :
        return visitor.visit_empty_statement(self, additional)


#  * 对AST做遍历的Vistor。
#  * 这是一个基类，定义了缺省的遍历方式。子类可以覆盖某些方法，修改遍历方式。
class AstVisitor:
    def __init__(self):
        self.errors = list()
        self.warnings = list()

    def add_error(self, msg: str, pos: Position):
        self.errors.append(CompileError(msg, pos, False))
        logging.info('@{} : {}'.format(pos, msg))

    def add_warning(self, msg: str, pos: Position):
        self.warnings.append(CompileError(msg, pos, True))
        logging.info('@{} : {}'.format(pos, msg))

    def visit(self, ast_node: AstNode, additional=None):
        return ast_node.accept(self, additional)

    def visit_prog(self, prog: Prog, additional=None):
        return self.visit_block(prog, additional)

    def visit_block(self, block: Block, additional=None):
        result = None
        for s in block.statements:
            result = self.visit(s, additional)
        return result

    def visit_parameter_list(self, param_list: ParameterList, additional=None):
        ps = list()
        for p in param_list.params:
            ps.append(self.visit(p, additional))
        return ps

    def visit_variable_declare(self, var_declare: VariableDeclare, additional):
        if var_declare.exp is not None:
            return self.visit(var_declare.exp, additional)

    def visit_variable_statement(self, var_statement: VariableStatement, additional):
        return self.visit(var_statement.variable_declare, additional)

    def visit_variable(self, variable: Variable, additional):
        return None

    def visit_expression_statement(self, statement: ExpressionStatement, additional):
        return self.visit(statement.exp, additional)

    def visit_error_statement(self, statement: ErrorStatement, additional):
        return None

    def visit_empty_statement(self, statement: EmptyStatement, additional):
        return None

    def visit_binary(self, binary: Binary, additional):
        self.visit(binary.exp1, additional)
        self.visit(binary.exp2, additional)

    def visit_unary(self, unary: Unary, additional):
        self.visit(unary.exp, additional)

    def visit_function_call(self, func_call: FunctionCall, additional):
        for param in func_call.params:
            self.visit(param, additional)
        return None

    def visit_string_literal(self, literal: StringLiteral, additional):
        return literal.value

    def visit_integer_literal(self, literal: IntegerLiteral, additional):
        return literal.value

    def visit_decimal_literal(self, literal: DecimalLiteral, additional):
        return literal.value

    def visit_dot_exp(self, dot_exp: DotExp, additional):
        self.visit(dot_exp.base_exp, additional)
        self.visit(dot_exp.prop, additional)

    def visit_array_literal(self, array: ArrayLiteral, additional):
        values = list()
        for exp in array.exps:
            values.append(self.visit(exp, additional))
        return values

    def visit_map_literal(self, map_exp: MapLiteral, additional):
        values = dict()
        for exp in map_exp.exps:
            k = self.visit(exp['key'], additional)
            v = self.visit(exp['val'], additional)
            values[k] = v
        return values

    def visit_error_expression(self, error_exp: ErrorExp, additional):
        return None


blanks = '@'
# blanks = ''

# 打印AST的调试程序
class AstDumper(AstVisitor):
    def __init__(self):
        self.statements = list()

    def display(self, msg: str):
        self.statements.append(msg)
        # print(msg)

    def visit_prog(self, prog: Prog, prefix=None):
        self.display(prefix + '主程序')
        for s in prog.statements:
            self.visit(s, prefix + blanks)

    def visit_variable_statement(self, var_statement: VariableStatement, prefix):
        self.display(prefix + '变量声明语句 ')
        self.visit(var_statement.variable_declare, prefix + blanks)

    def visit_variable_declare(self, var_declare: VariableDeclare, prefix):
        self.display(prefix + '声明变量 ' + var_declare.name)
        if var_declare.exp is not None:
            self.visit(var_declare.exp, prefix + blanks)
        else:
            self.display(prefix + blanks + ' 没有声明表达式.')

    def visit_parameter_list(self, param_list: ParameterList, prefix):
        self.display(prefix + '参数列表:')
        for p in param_list.params:
            self.visit(p, prefix + blanks)

    def visit_block(self, block: Block, prefix):
        self.display(prefix + '程序片段')
        for b in block.statements:
            self.visit(b, prefix + blanks)

    def visit_expression_statement(self, statement: ExpressionStatement, prefix):
        self.display(prefix + '表达式语句')
        return self.visit(statement.exp, prefix + blanks)

    def visit_empty_statement(self, statement: EmptyStatement, prefix):
        self.display(prefix + '空语句')

    def visit_binary(self, binary: Binary, prefix):
        self.display(prefix + '二元表达式 ' + binary.op.name)
        self.display(prefix + blanks + '二元表达式 左侧式子:')
        self.visit(binary.exp1, prefix + blanks * 2)
        self.display(prefix + blanks + '二元表达式 右侧式子:')
        self.visit(binary.exp2, prefix + blanks * 2)

    def visit_unary(self, unary: Unary, prefix):
        self.display(prefix + unary.op.name + '一元表达式')
        self.visit(unary.exp, prefix + blanks)

    def visit_integer_literal(self, literal: IntegerLiteral, prefix):
        self.display(prefix + '整数字面值: ' + str(literal.value))

    def visit_decimal_literal(self, literal: DecimalLiteral, prefix):
        self.display(prefix + '浮点数字面值: ' + str(literal.value))

    def visit_string_literal(self, literal: StringLiteral, prefix):
        self.display(prefix + '字符串字面值: ' + literal.value)

    def visit_array_literal(self, array: ArrayLiteral, prefix):
        self.display(prefix + '数组:' + str(array))
        i = 1
        for elem in array.exps:
            self.display(prefix + blanks + '数组第' + str(i) + '要素:')
            self.visit(elem, prefix + blanks * 2)
            i = i + 1

    def visit_map_literal(self, map_exp: MapLiteral, prefix):
        self.display(prefix + '字典:' + str(map_exp))
        i = 1
        for elem in map_exp.exps:
            self.display(prefix + blanks + '字典第' + str(i) + '要素Key:')
            self.visit(elem['key'], prefix + blanks * 2)
            self.display(prefix + blanks + '字典第' + str(i) + '要素value:')
            self.visit(elem['val'], prefix + blanks * 2)
            i = i + 1

    def visit_variable(self, variable: Variable, prefix):
        self.display(prefix + '变量:' + variable.name)

    def visit_function_call(self, func_call: FunctionCall, prefix):
        self.display(prefix + '函数调用:' + func_call.name)
        i = 1
        for param in func_call.params:
            self.display(prefix + blanks + '函数参数' + str(i))
            self.visit(param, prefix + blanks * 2)
            i = i + 1

    def visit_dot_exp(self, dot_exp: DotExp, prefix):
        self.display(prefix + '点运算')
        self.display(prefix + '  基础部分:')
        self.visit(dot_exp.base_exp, prefix + blanks * 2)
        self.display(prefix + '  指标部分:')
        self.visit(dot_exp.prop, prefix + blanks * 2)

