# 词法分析器：从语言文本解析程序Token串
from enum import Enum

# Token的类型
class TokenKind(Enum):
    Keyword = 1
    Identifier = 2
    StringLiteral = 3
    IntegerLiteral = 4
    DecimalLiteral = 5
    Seperator = 6
    Operator = 7
    EOF = 8
    Error = 9  # 新增错误类型


# Token的code
class Seperator(Enum):
    OpenBracket = 0  # [
    CloseBracket = 1  # ]
    OpenParen = 2  # (
    CloseParen = 3  # )
    OpenBrace = 4  # {
    CloseBrace = 5  # }
    Colon = 6  # :
    SemiColon = 7  # ;


# 运算符
class Op(Enum):
    Plus = 0  # +
    Minus = 1  # -
    Multiply = 3  # *
    Divide = 4  # /
    Comma = 5  # ,
    Dot = 6  # .
    Assign = 7  # =
    In = 8


class KeyWord(Enum):
    Function = 0


# 记录Token在源代码中的位置，方便报错和调试
class Position:
    def __init__(self, begin, end, line, col):
        self.begin = begin
        self.end = end
        self.line = line
        self.col = col

    def __str__(self):
        return '(行号: {}, 列号: {}, 位置: {})'.format(self.line, self.col, self.begin)


# 代表一个Token的数据结构
class Token:
    def __init__(self, kind, text, pos, code=None):
        self.kind = kind
        self.text = text
        self.pos = pos
        self.code = code

    def __str__(self):
        return 'Token @ {} \t {} \t {} \t{}'.format(self.pos, self.kind, self.text, self.code)


'''
 * 一个字符串流。其操作为：
 * peek():预读下一个字符，但不移动指针；
 * next():读取下一个字符，并且移动指针；
 * eof():判断是否已经到了结尾。
'''


class CharStream:
    def __init__(self, data):
        # 将输入程序的开始和末尾去掉及增加回车
        if data[-1] != '\n':  # 如果字符串末尾不能于回车，加上一个
            data = data + '\n'
        d = data[0]
        i = 0
        while d == '\n':
            i = i + 1
            d = data[i]
        data = data[i:]
        self.data = data
        self.pos = 0
        self.line = 1
        self.col = 1

    def peek(self):
        if len(self.data) <= self.pos:
            return None
        else:
            return self.data[self.pos]

    def next(self):
        if self.pos >= len(self.data):  # 检查是否越界
            return ''
        ch = self.data[self.pos]
        if self.pos > 0 and self.pos - 1 < len(self.data):
            ch_pre = self.data[self.pos - 1]
        else:
            ch_pre = ch
        if ch_pre == '\n':
            self.line = self.line + 1
            self.col = 1
        else:
            self.col = self.col + 1
        self.pos = self.pos + 1
        return ch

    def eof(self):
        return self.peek() is None

    # def get_position(self):
    #     return Position(self.pos + 1, self.pos + 1, self.line, self.col)

    def get_position(self):
        return Position(self.pos, self.pos, self.line, self.col)


'''
 * 词法分析器。
 * 词法分析器的接口像是一个流，词法解析是按需进行的。
 * 支持下面两个操作：
 * next(): 返回当前的Token，并移向下一个Token。
 * peek(): 预读当前的Token，但不移动当前位置。
 * peek2(): 预读第二个Token。
'''


class Scanner:
    KeyWords = {'function': KeyWord.Function}

    def __init__(self, stream):
        self.stream = stream
        self.tokens = list()
        self.lastPos = Position(0, 0, 0, 0)

    def next(self):
        if len(self.tokens) > 0:
            t = self.tokens.pop(0)
            if t is None:
                return self.get_token()
            else:
                return t
        else:
            return self.get_token()

    def peek(self):
        if len(self.tokens) > 0:
            t = self.tokens[0]
            if t is None:
                t = self.get_token()
                self.tokens.append(t)
        else:
            t = self.get_token()
            self.tokens.append(t)
        return t

    def peek2(self):
        if len(self.tokens) > 1:
            t = self.tokens[1]
            if t is None:
                while t is None:
                    self.tokens.append(self.get_token())
                    t = self.tokens[1]
        else:
            t = None
            while t is None:
                self.tokens.append(self.get_token())
                t = self.tokens[1]
        return t

    def get_next_pos(self):
        return self.peek().pos

    def get_last_pos(self):
        return self.lastPos

    @staticmethod
    def is_white_space(ch):
        return ch == ' ' or ch == '\t'

    @staticmethod
    def is_letter_digit_or_underscore(ch):
        return str.isdigit(ch) or str.isalpha(ch) or ch == '_' or ch == '（' or ch == '）'

    def skip_white_spaces(self):
        while self.is_white_space(self.stream.peek()):
            self.stream.next()

    # 字符串自变量
    def parse_string_literal(self, quotation_mark):
        pos = self.stream.get_position()
        token = Token(TokenKind.StringLiteral, '', pos)
        self.stream.next()  # 跳过开始的引号

        while True:
            ch = self.stream.peek()
            if ch is None or ch == '':  # 检查 EOF 或空字符
                token.kind = TokenKind.Error
                token.text = f'以{quotation_mark}开始的语句没有使用{quotation_mark}进行结尾'
                break
            elif ch == quotation_mark:
                self.stream.next()  # 跳过结束引号
                break
            else:
                next_char = self.stream.next()
                if next_char:  # 确保不是空字符串
                    token.text += next_char
                else:
                    token.kind = TokenKind.Error
                    token.text = f'Unexpected end of string literal'
                    break

        token.pos.end = self.stream.pos
        return token

    # 解析标识符
    def parse_identifier(self):
        pos = self.stream.get_position()
        token = Token(TokenKind.Identifier, '', pos)
        token.text += self.stream.next()
        while not self.stream.eof() and self.is_letter_digit_or_underscore(self.stream.peek()):
            token.text += self.stream.next()
        # pos.end = self.stream.pos + 1
        token.pos.end = self.stream.pos
        # 关键字是一种特殊的标识符
        if token.text in Scanner.KeyWords:
            token.kind = TokenKind.Keyword
            token.code = Scanner.KeyWords[token.text]
        if token.text == 'in':
            token.kind = TokenKind.Operator
            token.code = Op.In
        return token

    def get_token(self):
        pos = self.stream.get_position()
        self.skip_white_spaces()
        if self.stream.eof():
            token = Token(TokenKind.EOF, 'EOF', pos)
        else:
            ch = self.stream.peek()
            if str.isalpha(ch) or ch == '_':
                token =  self.parse_identifier()
            elif ch == '"' or ch == "'":
                token =  self.parse_string_literal(ch)
            elif ch == '(':
                self.stream.next()
                token = Token(TokenKind.Seperator, ch, pos, Seperator.OpenParen)
            elif ch == ')':
                self.stream.next()
                token = Token(TokenKind.Seperator, ch, pos, Seperator.CloseParen)
            elif ch == '[':
                self.stream.next()
                token = Token(TokenKind.Seperator, ch, pos, Seperator.OpenBracket)
            elif ch == ']':
                self.stream.next()
                token = Token(TokenKind.Seperator, ch, pos, Seperator.CloseBracket)
            elif ch == '{':
                self.stream.next()
                token = Token(TokenKind.Seperator, ch, pos, Seperator.OpenBrace)
            elif ch == '}':
                self.stream.next()
                token = Token(TokenKind.Seperator, ch, pos, Seperator.CloseBrace)
            elif ch == ':':
                self.stream.next()
                token = Token(TokenKind.Seperator, ch, pos, Seperator.Colon)
            elif ch == ',':
                self.stream.next()
                token = Token(TokenKind.Seperator, ch, pos, Op.Comma)
            elif ch == ';':
                self.stream.next()
                token = Token(TokenKind.Seperator, ch, pos, Seperator.SemiColon)
            elif ch == '\n':  # 如果是一个空行
                self.stream.next()
                token = Token(TokenKind.Seperator, ch, pos, Seperator.SemiColon)

            # 解析数字
            elif str.isdigit(ch):
                self.stream.next()
                ch_num = int(ch)
                ch1 = self.stream.peek()
                literal = ''
                if ch_num == 0:
                    if str.isdigit(ch1):
                        print('0 cannot be followed by other digit now, at line: ' + str(
                            self.stream.line) + ' col: ' + str(self.stream.col))
                        # 先暂时跳过去
                        self.stream.next()
                        token = self.get_token()
                    else:
                        literal = '0'
                elif 1 <= ch_num <= 9:
                    literal += ch
                    while str.isdigit(ch1):
                        ch = self.stream.next()
                        literal += ch
                        ch1 = self.stream.peek()
                if ch1 == '.':
                    literal += '.'
                    self.stream.next()
                    ch1 = self.stream.peek()
                    while str.isdigit(ch1):
                        ch = self.stream.next()
                        literal += ch
                        ch1 = self.stream.peek()
                    # 返回一个浮点型token
                    # pos.end = self.stream.pos + 1
                    token = Token(TokenKind.DecimalLiteral, literal, pos)
                    token.pos.end = self.stream.pos
                    # return Token(TokenKind.DecimalLiteral, literal, pos)
                else:
                    # 返回一个整型token
                    token = Token(TokenKind.IntegerLiteral, literal, pos)
            elif ch == '.':
                self.stream.next()
                ch1 = self.stream.peek()
                if str.isdigit(ch1):
                    literal = '.'
                    while str.isdigit(ch1):
                        ch = self.stream.next()
                        literal += ch
                        ch1 = self.stream.peek()
                    # pos.end = self.stream.pos + 1
                    token = Token(TokenKind.DecimalLiteral, literal, pos)
                    token.pos.end = self.stream.pos
                    # pos.end = self.stream.pos + 1
                    # return Token(TokenKind.DecimalLiteral, literal, pos)
                else:
                    token = Token(TokenKind.Operator, '.', pos, Op.Dot)

            elif ch == '/':
                self.stream.next()
                token = Token(TokenKind.Operator, '/', pos, Op.Divide)
            elif ch == '+':
                self.stream.next()
                token = Token(TokenKind.Operator, '+', pos, Op.Plus)
            elif ch == '-':
                self.stream.next()
                token = Token(TokenKind.Operator, '-', pos, Op.Minus)
            elif ch == '*':
                self.stream.next()
                token = Token(TokenKind.Operator, '*', pos, Op.Multiply)
            elif ch == '=':
                self.stream.next()
                token = Token(TokenKind.Operator, '=', pos, Op.Assign)
            else:
                # 暂时去掉不能识别的字符
                print("Unrecognized pattern meeting:'" + ch + "', at ln:"
                      + str(self.stream.line) + " col: " + str(self.stream.col))
                self.stream.next()
                token = self.get_token()

        self.lastPos = token.pos
        return token
