#!/usr/bin/env python3
import io
import enum
import sys

import sly


class _Lexer(sly.Lexer):
    tokens = {
        INT, FLOAT,
        IF, THEN, ELSE, DONE,
        AND, OR,
        LAST,
        LEN,
        EQ, NEQ, GT, LT, GTEQ, LTEQ,
        LIST_ID,
    }

    literals = {'{', '}', '(', ')'}
    ignore = ' \t\n'
    ignore_comment = r'\#.*'

    IF = r'if'
    THEN = r'then'
    ELSE = r'else'
    DONE = r'done'
    AND = r'(and|&&)'
    OR = r'(or|\|\|)'
    LAST = r'last'
    LEN = r'(length|number) of'
    GTEQ = r'>='
    LTEQ = r'<='
    GT = r'>'
    LT = r'<'
    NEQ = r'(is not|!=)'
    EQ = r'(is|==)'
    LIST_ID = r'('\
        'rolls since point established|'\
        'rolls?|'\
        'points?)'

    @_(r'\d*\.\d+')
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def INT(self, t):
        t.value = int(t.value)
        return t


class Expr:
    pass


class BinOpId(enum.Enum):
    Eq = enum.auto()
    Neq = enum.auto()
    Gt = enum.auto()
    Lt = enum.auto()
    Gteq = enum.auto()
    Lteq = enum.auto()
    And = enum.auto()
    Or = enum.auto()

    @staticmethod
    def from_string(s):
        return {
            'is': BinOpId.Eq,
            '==': BinOpId.Eq,
            'is not': BinOpId.Neq,
            '!=': BinOpId.Neq,
            '>': BinOpId.Gt,
            '<': BinOpId.Lt,
            '>=': BinOpId.Gteq,
            '<=': BinOpId.Lteq,
            'and': BinOpId.And,
            '&&': BinOpId.And,
            'or': BinOpId.Or,
            '||': BinOpId.Or,
        }[s.lower()]

    def __str__(self):
        return {
            BinOpId.Eq: '==',
            BinOpId.Neq: '!=',
            BinOpId.Gt: '>',
            BinOpId.Lt: '<',
            BinOpId.Gteq: '>=',
            BinOpId.Lteq: '<=',
            BinOpId.And: '&&',
            BinOpId.Or: '||',
        }[self]


class BinOp(Expr):
    def __init__(self, op, left, right):
        self.op = BinOpId.from_string(op)
        self.left = left
        self.right = right

    def __str__(self):
        return '(%s %s %s)' % (
            self.left, self.op, self.right,
        )

    def __eq__(self, rhs):
        return self.op == rhs.op and \
            self.left == rhs.left and \
            self.right == rhs.right

    def __ne__(self, rhs):
        return not self == rhs


class CondOp(Expr):
    def __init__(self, cond, true_case, false_case):
        self.cond = cond
        self.true_case = true_case
        self.false_case = false_case

    def __str__(self):
        return 'if ( %s ) then { %s } else { %s }' % (
            self.cond, self.true_case, self.false_case,
        )

    def __eq__(self, rhs):
        if not isinstance(rhs, CondOp):
            raise NotImplementedError()
        return self.cond == rhs.cond and \
            self.true_case == rhs.true_case and \
            self.false_case == rhs.false_case

    def __ne__(self, rhs):
        return not self == rhs


class ListId(enum.Enum):
    Rolls = enum.auto()
    Points = enum.auto()
    RollsSincePoint = enum.auto()

    @staticmethod
    def from_string(orig_s):
        orig_s
        s = orig_s.lower()
        if s in {'roll', 'rolls'}:
            return ListId.Rolls
        if s in {'point', 'points'}:
            return ListId.Points
        elif s == 'rolls since point established':
            return ListId.RollsSincePoint
        raise NotImplementedError('Can\'t convert "%s" to ListId' % orig_s)


class TailOp(Expr):
    def __init__(self, list_id, num):
        self.list_id = ListId.from_string(list_id)
        self.num = num

    def __str__(self):
        return '%s[-%d:]' % (self.list_id.name, self.num)

    def __eq__(self, rhs):
        return self.list_id == rhs.list_id and \
            self.num == rhs.num

    def __ne__(self, rhs):
        return not self == rhs


class LenOp(Expr):
    def __init__(self, list_id):
        self.list_id = ListId.from_string(list_id)

    def __str__(self):
        return 'len(%s)' % self.list_id.name

    def __eq__(self, rhs):
        return self.list_id == rhs.list_id

    def __ne__(self, rhs):
        return not self == rhs


class _Parser(sly.Parser):
    # debugfile = '/dev/stderr'
    tokens = _Lexer.tokens

    def error(self, t):
        raise SyntaxError(t)

    @_('"{" stmtlist "}"')
    def block(self, p):
        return p.stmtlist

    @_('stmt')
    def block(self, p):
        return p.stmt

    @_('stmt stmtlist')
    def stmtlist(self, p):
        return p.stmt, p.stmtlist

    @_('stmt')
    def stmtlist(self, p):
        return p.stmt

    @_('expr DONE')
    def stmt(self, p):
        return p.expr

    @_('literal')
    def expr(self, p):
        return p.literal

    @_('empty')
    def expr(self, p):
        return p.empty

    @_('')
    def empty(self, p):
        return None

    @_('numeric')
    def literal(self, p):
        return p.numeric

    @_('INT', 'FLOAT')
    def numeric(self, p):
        return p[0]

    @_('IF cond THEN block')
    def stmt(self, p):
        return CondOp(p.cond, p.block, None)

    @_('IF cond THEN block ELSE block')
    def stmt(self, p):
        return CondOp(p.cond, p.block0, p.block1)

    @_('"(" cond ")"')
    def cond(self, p):
        return p.cond

    @_('literal')
    def cond(self, p):
        return p.literal

    @_('cond AND cond', 'cond OR cond')
    def cond(self, p):
        return BinOp(p[1], p.cond0, p.cond1)

    @_(
        'expr EQ expr',
        'expr NEQ expr',
        'expr GT expr',
        'expr LT expr',
        'expr GTEQ expr',
        'expr LTEQ expr',
    )
    def cond(self, p):
        return BinOp(p[1], p.expr0, p.expr1)

    @_('LAST LIST_ID')
    def expr(self, p):
        return TailOp(p.LIST_ID, 1)

    @_('LAST INT LIST_ID')
    def expr(self, p):
        return TailOp(p.LIST_ID, p.INT)

    @_('LEN LIST_ID')
    def expr(self, p):
        return LenOp(p.LIST_ID)


def _flatten(result):
    while True:
        if not isinstance(result, (list, tuple)):
            yield result
            return
        else:
            item, result = result
            yield item


def parse_stream(stream_fd):
    yield from _flatten(_Parser().parse(_Lexer().tokenize(stream_fd.read())))


def parse(s):
    yield from parse_stream(io.StringIO(s))


if __name__ == '__main__':
    for item in parse_stream(sys.stdin):
        print(type(item), item)
