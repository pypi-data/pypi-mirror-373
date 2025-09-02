# 语法分析器：根据token串生成AST树(树的每个节点是一个AST Node)
from muse.scanner import TokenKind, Op, Seperator, Scanner, Position
from muse.ast_struct import (Prog, ErrorStatement, ExpressionStatement, Binary, Unary, Variable, ArrayLiteral, ErrorExp, DotExp,
                        IntegerLiteral, DecimalLiteral, StringLiteral, FunctionCall, MapLiteral, EmptyStatement)
from muse.error import CompileError


class Parser:
    def __init__(self, scanner: Scanner):
        self.scanner = scanner
        self.errors = list()
        self.warnings = list()

    def add_error(self, msg: str, pos: Position):
        self.errors.append(CompileError(msg, pos, False))
        print('@{} : {}'.format(pos, msg))

    def add_warning(self, msg: str, pos: Position):
        self.warnings.append(CompileError(msg, pos, True))
        print('@{} : {}'.format(pos, msg))

    # 解析整个程序，语法分析器主入口
    def parse_prog(self):
        begin_pos = self.scanner.peek().pos
        statements = self.parse_statement_list()
        return Prog(begin_pos, self.scanner.get_last_pos(), statements)

    def parse_statement_list(self):
        statements = []
        t = self.scanner.peek()
        while t.kind != TokenKind.EOF:
            statement = self.parse_statement()
            if isinstance(statement, ErrorStatement):
                statements = list()
                break
            else:
                statements.append(statement)
            t = self.scanner.peek()
        return statements

    def parse_statement(self):
        t = self.scanner.peek()
        if t.kind == TokenKind.Identifier or t.kind == TokenKind.DecimalLiteral or t.kind == TokenKind.IntegerLiteral or t.kind == TokenKind.StringLiteral or t.code == Seperator.OpenParen:
            return self.parse_expression_statement()
        elif t.code == Seperator.SemiColon:
            self.scanner.next()
            return EmptyStatement(self.scanner.get_last_pos())
        else:
            txt = self.scanner.peek().text.strip()
            txt = '空字符' if txt == '' else txt
            self.add_error('无法识别语句, 语句开始于 ' + txt, self.scanner.get_last_pos())
            begin_pos = self.scanner.get_next_pos()
            self.skip()
            return ErrorStatement(begin_pos, self.scanner.get_last_pos())

    def parse_expression_statement(self):
        exp = self.parse_expression()
        t = self.scanner.peek()
        statement = ExpressionStatement(self.scanner.get_last_pos(), exp)
        # 看看在真实的语言中可不可以把这个去掉，不用;作为结束
        if t.code == Seperator.SemiColon:
            self.scanner.next()
        else:
            txt = t.text.strip()
            txt = '空字符' if txt == '' else txt
            self.add_error('非法语句结束符号 ' + txt, self.scanner.get_last_pos())
            self.skip()
            statement.end_pos = self.scanner.get_last_pos()
            statement.is_error = True
        return statement

    # 重点来了解析表达式
    def parse_expression(self):
        return self.parse_assignment()

    # 二元运算符的优先级
    op_priority = {
        Op.Assign: 2,
        Op.Plus: 12,
        Op.Minus: 12,
        Op.Divide: 13,
        Op.Multiply: 13,
        Op.In: 4
    }

    def get_priority(self, op):
        if op in self.op_priority:
            return self.op_priority[op]
        else:
            return -1

    # 解析赋值表达式 -- 这段代码我看不太懂
    def parse_assignment(self):
        assign_priority = self.get_priority(Op.Assign)
        # 先解析一个优先级更高的表达式
        exp1 = self.parse_binary(assign_priority)
        t = self.scanner.peek()
        t_priority = self.get_priority(t.code)
        # 存放赋值运算符量表的表达式
        exp_stack = list()
        exp_stack.append(exp1)
        # 存放赋值运算符
        op_stack = list()

        # 解析赋值表达式
        while t.kind == TokenKind.Operator and t_priority == assign_priority:
            op_stack.append(t.code)
            self.scanner.next()  # 跳过运算符
            # 获取运算符优先级高于赋值的二元表达式
            exp1 = self.parse_binary(assign_priority)
            exp_stack.append(exp1)
            t = self.scanner.peek()
            t_priority = self.get_priority(t.code)

        # 组装右结合的AST
        exp1 = exp_stack[-1]
        if len(op_stack) > 0:
            i = len(exp_stack) - 2
            while i >= 0:
                exp1 = Binary(op_stack[i], exp_stack[i], exp1)
                i = i - 1
        return exp1

    # 采用运算符优先级算法，解析二元表达式。
    # 这是一个递归算法。一开始，提供的参数是最低优先级，
    def parse_binary(self, prec: int):
        exp1 = self.parse_unary()
        t = self.scanner.peek()
        tprec = self.get_priority(t.code)

        while t.kind == TokenKind.Operator and tprec > prec:
            self.scanner.next()  # 跳过运算符
            exp2 = self.parse_binary(tprec)
            exp = Binary(t.code, exp1, exp2)
            exp1 = exp
            t = self.scanner.peek()
            tprec = self.get_priority(t.code)

        return exp1

    # 解析一元运算
    def parse_unary(self):
        begin_pos = self.scanner.get_next_pos()
        t = self.scanner.peek()
        if t.code == Op.Minus:
            self.scanner.next()
            exp = self.parse_unary()
            return Unary(begin_pos, self.scanner.get_last_pos(), t.code, exp, is_prefix=True)
        else:
            exp = self.parse_primary()
            return exp

    # 解析基础表达式
    def parse_primary(self):
        begin_pos = self.scanner.get_next_pos()
        t = self.scanner.peek()
        exp = None

        if t.kind == TokenKind.IntegerLiteral or t.kind == TokenKind.DecimalLiteral or t.kind == TokenKind.StringLiteral:
            exp = self.parse_literal()
        elif t.kind == TokenKind.Identifier:
            if self.scanner.peek2().code == Seperator.OpenParen:
                exp = self.parse_function_call()
            else:
                self.scanner.next()
                exp = Variable(begin_pos, self.scanner.get_last_pos(), t.text)
        elif t.code == Seperator.OpenParen:  # (
            self.scanner.next()
            exp = self.parse_expression()
            t1 = self.scanner.peek()
            if t1.code == Seperator.CloseParen:  # )
                self.scanner.next()
            else:
                txt = t.text.strip()
                txt = '空字符' if txt == '' else txt
                self.add_error('在主表达式的末尾需要一个), 但是程序找到了: ' + txt, self.scanner.get_last_pos())
                self.skip()
        elif t.code == Seperator.OpenBracket:  # [ 解析数组
            self.scanner.next()
            t1 = self.scanner.peek()
            exps = list()
            while t1.code != Seperator.CloseBracket and t1.kind != TokenKind.EOF:  # 添加EOF检查
                exp1 = self.parse_expression()
                exps.append(exp1)

                t1 = self.scanner.peek()
                if t1.code == Op.Comma:
                    self.scanner.next()
                    t1 = self.scanner.peek()
                elif t1.code != Seperator.CloseBracket:
                    txt = t.text.strip()
                    txt = '空字符' if txt == '' else txt
                    self.add_error('在数组末尾需要], 但是程序得到了: ' + txt, self.scanner.get_last_pos())
                    self.skip()
                    break  # 添加break以避免无限循环
            if t1.code == Seperator.CloseBracket:  # 跳过最后一个]
                self.scanner.next()
            exp = ArrayLiteral(begin_pos, self.scanner.get_last_pos(), exps)
        elif t.code == Seperator.OpenBrace:  # { 解析字典
            self.scanner.next()
            t1 = self.scanner.peek()
            exps = list()
            while t1.code != Seperator.CloseBrace and t1.kind != TokenKind.EOF:  # 添加EOF检查
                exp1 = self.parse_expression()
                k = exp1
                t1 = self.scanner.peek()
                if t1.code == Seperator.Colon:
                    self.scanner.next()
                    v = self.parse_expression()
                else:  # 如果不是:, 那肯定出错了
                    txt = t.text.strip()
                    txt = '空字符' if txt == '' else txt
                    self.add_error('字典的其中一个元素要包含:把key和value分开, 但是程序得到了: ' + txt,
                                   self.scanner.get_last_pos())
                    self.skip()
                    v = None
                    break  # 添加break以避免无限循环
                exps.append({'key': k, 'val': v})
                t1 = self.scanner.peek()
                if t1.code == Op.Comma:
                    self.scanner.next()
                    t1 = self.scanner.peek()
                elif t1.code != Seperator.CloseBrace:
                    txt = t.text.strip()
                    txt = '空字符' if txt == '' else txt
                    self.add_error('在字典末尾需要}, 但是程序得到了: ' + txt, self.scanner.get_last_pos())
                    self.skip()
                    break  # 添加break以避免无限循环
            if t1.code == Seperator.CloseBrace:  # 跳过最后一个}
                self.scanner.next()
            exp = MapLiteral(begin_pos, self.scanner.get_last_pos(), exps)
        else:
            # 遇到一些负载First集合中的Token
            txt = t.text.strip()
            txt = '空字符' if txt == '' else txt
            self.add_error('无法识别语法: ' + txt, self.scanner.get_last_pos())
            exp = ErrorExp(begin_pos, self.scanner.get_last_pos())

        # 带有后缀的表达式，比如数组
        t = self.scanner.peek()
        while t.code == Op.Dot and t.kind != TokenKind.EOF:  # 添加EOF检查
            self.scanner.next()
            exp1 = self.parse_primary()
            exp = DotExp(begin_pos, self.scanner.get_last_pos(), exp, exp1)
            t = self.scanner.peek()

        return exp

    def skip(self):
        t = self.scanner.peek()
        while t.kind != TokenKind.EOF:
            if t.kind == TokenKind.Keyword:
                return
            elif t.kind == TokenKind.Seperator and (
                    t.text == ',' or t.text == ';' or t.text == '{' or t.text == '}' or t.text == '(' or t.text == ')'):
                return
            else:
                self.scanner.next()
                t = self.scanner.peek()

    # 解析字面量
    def parse_literal(self):
        begin_pos = self.scanner.get_next_pos()
        t = self.scanner.peek()
        # 知识点：以Identifier开头，可能是函数调用，也可能是一个变量，所以要再多向后看一个Token，
        # 这相当于在局部使用了LL(2)算法。
        if t.kind == TokenKind.IntegerLiteral:
            self.scanner.next()
            return IntegerLiteral(begin_pos, int(t.text))
        elif t.kind == TokenKind.DecimalLiteral:
            self.scanner.next()
            return DecimalLiteral(begin_pos, float(t.text))
        else:
            self.scanner.next()
            return StringLiteral(begin_pos, t.text)

    # 解析函数调用
    def parse_function_call(self):
        begin_pos = self.scanner.get_next_pos()
        params = list()
        name = self.scanner.next().text

        self.scanner.next()  # 跳过(
        # 循环读出所有参数
        t1 = self.scanner.peek()
        while t1.code != Seperator.CloseParen and t1.kind != TokenKind.EOF:
            exp = self.parse_expression()
            params.append(exp)

            if exp.is_error:
                self.add_error('在解析函数调用时出现问题: ' + name, self.scanner.get_last_pos())
            t1 = self.scanner.peek()
            if t1.code != Seperator.CloseParen:
                if t1.code == Op.Comma:
                    t1 = self.scanner.next()
                else:
                    txt = t1.text.strip()
                    txt = '空字符' if txt == '' else txt
                    self.add_error('函数调用末尾需要一个), 但程序得到了一个 ' + txt, self.scanner.get_last_pos())
                    self.skip()
                    return FunctionCall(begin_pos, self.scanner.get_last_pos(), name, params, True)

        if t1.code == Seperator.CloseParen:
            self.scanner.next()

        return FunctionCall(begin_pos, self.scanner.get_last_pos(), name, params)

    def skip(self):
        t = self.scanner.peek();
        while t.kind != TokenKind.EOF:
            if t.kind == TokenKind.Keyword:
                return
            elif t.kind == TokenKind.Seperator and (t.text == ',' or t.text == ';' or t.text == '{' or t.text == '}' or t.text == '(' or t.text == ')'):
                return
            else:
                self.scanner.next()
                t = self.scanner.peek()



