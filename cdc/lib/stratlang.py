#!/usr/bin/env python3
import io
import enum
import sys

import sly

from cdc.lib.strategy import CBPass, CBDontPass, CBCome, CBDontCome, CBField,\
    CBPlace, CBHardWay, CBOdds


class InvalidValueError(Exception):
    def __init__(self, value, valid):
        self.value = value
        self.valid = valid

    def __str__(self):
        return '%s is not a valid option (%s)' % (self.value, self.valid)


class StrategyTooComplexError(Exception):
    def __init__(self, complexity, max_complexity):
        self.complexity = complexity
        self.max_complexity = max_complexity

    def __str__(self):
        return 'The strategy is too complex (stopped_at=%s max=%s)' % \
            (self.complexity, self.max_complexity)


class _Lexer(sly.Lexer):
    tokens = {
        INT, FLOAT, BOOL,
        IF, THEN, ELSE, DONE,
        AND, OR,
        LAST, LEN,
        SET, TO, USER_VAR_ID,
        EQ, NEQ, GT, LT, GTEQ, LTEQ,
        VAR_ID, LIST_ID,
        MAKE_BET,
        BET_TYPE_NO_ARG,
        BET_TYPE_1_ARG_POINT_VALUE,
        BET_TYPE_1_ARG_HARD_WAY,
        BET_TYPE_2_ARG_ODDS,
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
    SET = r'set'
    TO = r'to'
    GTEQ = r'>='
    LTEQ = r'<='
    GT = r'>'
    LT = r'<'
    NEQ = r'(is not|!=)'
    EQ = r'(is|==)'
    VAR_ID = r'(point|bankroll)'
    LIST_ID = r'('\
        'rolls since point established|'\
        'rolls?|'\
        'points?)'
    MAKE_BET = r'make bet'
    BET_TYPE_NO_ARG = r'('\
        'dont pass|'\
        'pass|'\
        'dont come|'\
        'come|'\
        'field)'
    BET_TYPE_1_ARG_POINT_VALUE = r'place'
    BET_TYPE_1_ARG_HARD_WAY = r'hard'
    BET_TYPE_2_ARG_ODDS = r'odds'

    @_(r'\d*\.\d+')
    def FLOAT(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def INT(self, t):
        t.value = int(t.value)
        return t

    @_(r'([Tt]rue|[Ff]alse)')
    def BOOL(self, t):
        t.value = t.value.lower() == 'true'
        return t

    USER_VAR_ID = r'[A-Za-z_][A-Za-z0-9_]*'


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


class AssignOp(Expr):
    def __init__(self, user_var, expr):
        self._var = user_var
        self._expr = expr

    @property
    def var(self):
        return self._var

    @property
    def expr(self):
        return self._expr

    def __str__(self):
        return '%s = %s' % (self.var, self.expr)


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


class VarId(enum.Enum):
    Point = enum.auto()
    Bankroll = enum.auto()

    @staticmethod
    def from_string(s):
        try:
            return {
                'point': VarId.Point,
                'bankroll': VarId.Bankroll,
            }[s.lower()]
        except KeyError:
            raise NotImplementedError('Can\'t convert "%s" to VarId' % s)


class ListId(enum.Enum):
    Rolls = enum.auto()
    Points = enum.auto()
    RollsSincePoint = enum.auto()

    @staticmethod
    def from_string(orig_s):
        s = orig_s.lower()
        if s in {'roll', 'rolls'}:
            return ListId.Rolls
        if s in {'point', 'points'}:
            return ListId.Points
        elif s == 'rolls since point established':
            return ListId.RollsSincePoint
        raise NotImplementedError('Can\'t convert "%s" to ListId' % orig_s)


class MakeBetOp(Expr):
    def __init__(self, bet):
        self.bet = bet

    def __str__(self):
        return 'MakeBet(%s)' % self.bet


def bet_type_from_str(s):
    return {
        'pass': CBPass,
        'dont pass': CBDontPass,
        'come': CBCome,
        'dont come': CBDontCome,
        'field': CBField,
        'place': CBPlace,
        'hard': CBHardWay,
        'odds': CBOdds,
    }[s.lower()]


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
    _complexity = 0

    def __init__(self, *a, max_complexity=None, **kw):
        super().__init__(*a, **kw)
        self._max_complexity = max_complexity

    @property
    def complexity(self):
        return self._complexity

    def add_complexity(self, amount=1):
        self._complexity += amount
        if self._max_complexity and self.complexity > self._max_complexity:
            raise StrategyTooComplexError(
                self.complexity, self._max_complexity)

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

    @_('assign DONE')
    def stmt(self, p):
        return p.assign

    @_('SET USER_VAR_ID TO expr')
    def assign(self, p):
        return AssignOp(p.USER_VAR_ID, p.expr)

    @_('expr DONE')
    def stmt(self, p):
        return p.expr

    @_('literal')
    def expr(self, p):
        self.add_complexity()
        return p.literal

    @_('empty')
    def expr(self, p):
        # self.add_complexity()
        return p.empty

    @_('')
    def empty(self, p):
        return None

    @_('BOOL')
    def literal(self, p):
        return p.BOOL

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
        self.add_complexity()
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
        self.add_complexity()
        return TailOp(p.LIST_ID, 1)

    @_('LAST INT LIST_ID')
    def expr(self, p):
        self.add_complexity()
        return TailOp(p.LIST_ID, p.INT)

    @_('LEN LIST_ID')
    def expr(self, p):
        self.add_complexity()
        return LenOp(p.LIST_ID)

    @_('VAR_ID')
    def expr(self, p):
        self.add_complexity()
        return VarId.from_string(p.VAR_ID)

    @_('MAKE_BET bet')
    def expr(self, p):
        self.add_complexity()
        return MakeBetOp(p.bet)

    @_('BET_TYPE_NO_ARG amount')
    def bet(self, p):
        return bet_type_from_str(p.BET_TYPE_NO_ARG)(p.amount)

    @_('BET_TYPE_1_ARG_POINT_VALUE point_value amount')
    def bet(self, p):
        return bet_type_from_str(p[0])(p.point_value, p.amount)

    @_('BET_TYPE_1_ARG_HARD_WAY hard_value amount')
    def bet(self, p):
        return bet_type_from_str(p[0])(p.hard_value, p.amount)

    @_('BET_TYPE_2_ARG_ODDS point_value BOOL amount')
    def bet(self, p):
        return bet_type_from_str(p[0])(p.point_value, p.BOOL, p.amount)

    @_('INT')
    def amount(self, p):
        return p.INT

    @_('INT')
    def point_value(self, p):
        valid = {4, 5, 6, 8, 9, 10}
        if p.INT in valid:
            return p.INT
        raise InvalidValueError(p.INT, valid)

    @_('INT')
    def hard_value(self, p):
        valid = {4, 6, 8, 10}
        if p.INT in valid:
            return p.INT
        raise InvalidValueError(p.INT, valid)


def _flatten(result):
    while True:
        if not isinstance(result, (list, tuple)):
            yield result
            return
        else:
            item, result = result
            yield item


def parse_stream(stream_fd, max_complexity=None):
    p = _Parser(max_complexity=max_complexity)
    yield from _flatten(p.parse(_Lexer().tokenize(stream_fd.read())))
    # print('The complexity is', p.complexity)


def parse(s, max_complexity=None):
    yield from parse_stream(io.StringIO(s), max_complexity)


def _test_parse_complexity(s, max_complexity=None):
    p = _Parser(max_complexity=max_complexity)
    for _ in _flatten(p.parse(_Lexer().tokenize(io.StringIO(s).read()))):
        pass
    return p.complexity


if __name__ == '__main__':
    for item in parse_stream(sys.stdin):
        print(type(item), item)
