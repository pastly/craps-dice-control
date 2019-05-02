from cdc.lib.stratlang import parse, InvalidValueError, ListId, VarId,\
    _test_parse_complexity, StrategyTooComplexError, AssignOp
from cdc.lib.strategy import CBPass, CBDontPass, CBCome, CBDontCome, CBField,\
    CBPlace, CBHardWay, CBOdds

from sly.lex import LexError

import pytest


def test_int_literal_valid():
    for i in {'0', '1', '98794', '-1', '-98794'}:
        s = '%s done' % i
        ret = [_ for _ in parse(s)]
        assert len(ret) == 1
        assert ret[0] == int(i)


def test_float_literal_valid():
    for i in {'0.0', '.1', '1.0', '813.15', '-0.0', '-.1', '-1.0', '-813.15'}:
        s = '%s done' % i
        ret = [_ for _ in parse(s)]
        assert len(ret) == 1
        assert ret[0] == float(i)


def test_forms_of_eq_are_same():
    ret1 = [_ for _ in parse('if 1 is 2 then done')]
    ret2 = [_ for _ in parse('if 1 == 2 then done')]
    assert len(ret1) == 1
    assert len(ret1) == len(ret2)
    ret1, ret2 = ret1[0], ret2[0]
    assert ret1 is not None
    assert ret1 == ret2


def test_forms_of_neq_are_same():
    ret1 = [_ for _ in parse('if 1 is not 2 then done')]
    ret2 = [_ for _ in parse('if 1 != 2 then done')]
    assert len(ret1) == 1
    assert len(ret1) == len(ret2)
    ret1, ret2 = ret1[0], ret2[0]
    assert ret1 == ret2


def test_forms_of_len_are_same():
    ret1 = [_ for _ in parse('length of rolls done')]
    ret2 = [_ for _ in parse('number of rolls done')]
    assert len(ret1) == 1
    assert len(ret1) == len(ret2)
    ret1, ret2 = ret1[0], ret2[0]
    assert ret1 == ret2


def test_forms_of_and_are_same():
    ret1 = [_ for _ in parse('if 1 and 2 then done')]
    ret2 = [_ for _ in parse('if 1 && 2 then done')]
    assert len(ret1) == 1
    assert len(ret1) == len(ret2)
    ret1, ret2 = ret1[0], ret2[0]
    assert ret1 == ret2


def test_forms_of_or_are_same():
    ret1 = [_ for _ in parse('if 1 or 2 then done')]
    ret2 = [_ for _ in parse('if 1 or 2 then done')]
    assert len(ret1) == 1
    assert len(ret1) == len(ret2)
    ret1, ret2 = ret1[0], ret2[0]
    assert ret1 == ret2


def test_tail_op_single():
    ret1 = [_ for _ in parse('last rolls done')]
    ret2 = [_ for _ in parse('last 1 rolls done')]
    assert len(ret1) == 1
    assert len(ret1) == len(ret2)
    ret1, ret2 = ret1[0], ret2[0]
    assert ret1 == ret2


def test_bet_no_arg():
    amount = 5
    for b in {'pass', 'dont pass', 'come', 'dont come', 'field'}:
        s = 'make bet %s %d done' % (b, amount)
        ret = [_ for _ in parse(s)]
        assert len(ret) == 1
        ret = ret[0]
        assert ret.bet == {
            'pass': CBPass(amount),
            'dont pass': CBDontPass(amount),
            'come': CBCome(amount),
            'dont come': CBDontCome(amount),
            'field': CBField(amount),
        }[b]


def test_bet_place():
    amount = 5
    for value in {4, 5, 6, 8, 9, 10}:
        s = 'make bet place %d %d done' % (value, amount)
        ret = [_ for _ in parse(s)]
        assert len(ret) == 1
        ret = ret[0]
        assert ret.bet == CBPlace(value, amount)


def test_bet_place_invalid():
    amount = 5
    for value in {2, 3, 7, 11, 12}:
        s = 'make bet place %d %d done' % (value, amount)
        with pytest.raises(InvalidValueError) as e:
            [_ for _ in parse(s)]
        assert e.value.value == value
    for value in {0, 1, 13, 1589}:
        s = 'make bet place %d %d done' % (value, amount)
        with pytest.raises(InvalidValueError) as e:
            [_ for _ in parse(s)]
        assert e.value.value == value


def test_bet_hard():
    amount = 5
    for value in {4, 6, 8, 10}:
        s = 'make bet hard %d %d done' % (value, amount)
        ret = [_ for _ in parse(s)]
        assert len(ret) == 1
        ret = ret[0]
        assert ret.bet == CBHardWay(value, amount)


def test_bet_hard_invalid():
    amount = 5
    for value in {2, 3, 5, 7, 9, 11, 12}:
        s = 'make bet hard %d %d done' % (value, amount)
        with pytest.raises(InvalidValueError) as e:
            [_ for _ in parse(s)]
        assert e.value.value == value
    for value in {0, 1, 13, 1589}:
        s = 'make bet hard %d %d done' % (value, amount)
        with pytest.raises(InvalidValueError) as e:
            [_ for _ in parse(s)]
        assert e.value.value == value


def test_bet_odds():
    amount = 5
    for point in {4, 5, 6, 8, 9, 10}:
        for is_dont_str in {'True', 'true', 'False', 'false'}:
            s = 'make bet odds %d %s %d done' % (point, is_dont_str, amount)
            ret = [_ for _ in parse(s)]
            assert len(ret) == 1
            ret = ret[0]
            is_dont = is_dont_str.lower() == 'true'
            assert ret.bet == CBOdds(point, is_dont, amount)


def test_bet_odds_invalid_point():
    amount = 5
    for point in {0, 1, 2, 3, 7, 11, 12, 13, 1589}:
        for is_dont_str in {'True', 'true', 'False', 'false'}:
            s = 'make bet odds %d %s %d done' % (point, is_dont_str, amount)
            with pytest.raises(InvalidValueError) as e:
                [_ for _ in parse(s)]
            assert e.value.value == point


def test_bet_odds_invalid_is_dont():
    amount = 5
    for point in {4, 5, 6, 8, 9, 10}:
        for is_dont_str in {'T', 't', 'F', 'f', 'foo', 'FaLsE', 'TrUe'}:
            s = 'make bet odds %d %s %d done' % (point, is_dont_str, amount)
            with pytest.raises(SyntaxError):
                [_ for _ in parse(s)]
        for is_dont_str in {'12'}:
            s = 'make bet odds %d %s %d done' % (point, is_dont_str, amount)
            with pytest.raises(SyntaxError):
                [_ for _ in parse(s)]


def test_list_id_valid():
    for list_id, list_strs in (
            (ListId.Rolls, ('roll', 'rolls', 'Roll')),
            (ListId.Points, ('point', 'points', 'Points')),
            (ListId.RollsSincePoint, ('rolls since point established',))):
        for list_str in list_strs:
            assert ListId.from_string(list_str) == list_id


def test_list_id_invalid():
    for s in {'aaaaaa', '', '1986'}:
        with pytest.raises(NotImplementedError):
            ListId.from_string(s)


def test_var_id_valid():
    for var_id, var_strs in (
            (VarId.Point, ('current point', 'cUrReNt pOiNt')),
            (VarId.Bankroll, ('bankroll', 'BaNkRoLl'))):
        for var_str in var_strs:
            assert VarId.from_string(var_str) == var_id


def test_var_id_invalid():
    for s in {'aaaaaa', '', '1986'}:
        with pytest.raises(NotImplementedError):
            VarId.from_string(s)


def test_complex_done():
    s = '{' + ' '.join(['done'] * 100) + '}'
    assert _test_parse_complexity(s) == 0
    s = '{' + '\n'.join(['done'] * 100) + '}'
    assert _test_parse_complexity(s) == 0


def test_complex_literal_expr():
    s = '1 done'
    assert _test_parse_complexity(s) == 1
    s = '{' + ' '.join(['1 done'] * 100) + '}'
    assert _test_parse_complexity(s) == 100
    s = '{' + '\n'.join(['1 done'] * 100) + '}'
    assert _test_parse_complexity(s) == 100


def test_complex_last_list_expr():
    s = 'last roll done'
    assert _test_parse_complexity(s) == 1
    s = 'last 3 roll done'
    assert _test_parse_complexity(s) == 1


def test_complex_var_expr():
    s = 'current point done'
    assert _test_parse_complexity(s) == 1
    s = 'bankroll done'
    assert _test_parse_complexity(s) == 1


def test_complex_len_list_expr():
    s = 'length of rolls done'
    assert _test_parse_complexity(s) == 1


def test_complex_make_bet_expr():
    s = 'make bet pass 5 done'
    assert _test_parse_complexity(s) == 1
    s = 'make bet hard 4 5 done'
    assert _test_parse_complexity(s) == 1
    s = 'make bet odds 4 true 5 done'
    assert _test_parse_complexity(s) == 1


def test_complex_literal_cond():
    s = 'if 1 then done'
    assert _test_parse_complexity(s) == 1
    s = 'if %s then done' % ' and'.join(['1'] * 100)
    assert _test_parse_complexity(s) == 100
    s = 'if %s then done' % ' or'.join(['1'] * 100)
    assert _test_parse_complexity(s) == 100


def test_complex_true_block_1():
    # 1 for the ten in the condition, 1 for the 10 in the "then" block
    s = 'if 10 then 10 done'
    assert _test_parse_complexity(s) == 2


def test_complex_true_block_2():
    s = 'if 10 then {10 done 10 done}'
    assert _test_parse_complexity(s) == 3


def test_complex_false_block_1():
    # 1 for the ten in the condition, 1 for the 10 in the "else" block
    s = 'if 10 then done else 10 done'
    assert _test_parse_complexity(s) == 2


def test_complex_false_block_2():
    s = 'if 10 then done else {10 done 10 done}'
    assert _test_parse_complexity(s) == 3


def test_complex_both_true_false_block_1():
    s = 'if 10 then 10 done else 10 done'
    assert _test_parse_complexity(s) == 3


def test_complex_both_true_false_block_2():
    s = 'if 10 then {10 done 10 done} else {10 done 10 done}'
    assert _test_parse_complexity(s) == 5


def test_complex_nested_if_1():
    s = 'if 1 then if 2 then done'
    assert _test_parse_complexity(s) == 2


def test_complex_nested_if_2():
    s = 'if 1 then if 2 then done else done else done'
    assert _test_parse_complexity(s) == 2


def test_complex_nested_if_3():
    s = 'if 1 then if 2 then if 3 then if 4 then done else '\
        'make bet pass 5 done'
    assert _test_parse_complexity(s) == 5


def test_complex_nested_if_4():
    s = 'if 1 then if 2 then if 3 then if 4 then done else '\
        '{make bet pass 5 done 6 done}'
    assert _test_parse_complexity(s) == 6


def test_complex_almost_too_complex():
    max_complex = 10
    for reps in {max_complex - 1, max_complex}:
        s = '{' + ' '.join(['1 done'] * reps) + '}'
        # Would raise StrategyTooComplexError if too complex
        _test_parse_complexity(s, max_complexity=max_complex)


def test_complex_too_complex():
    max_complex = 10
    reps = max_complex + 1
    s = '{' + ' '.join(['1 done'] * reps) + '}'
    # Would raise StrategyTooComplexError if too complex
    with pytest.raises(StrategyTooComplexError):
        _test_parse_complexity(s, max_complexity=max_complex)


def test_simple_assign_op():
    var_id = 'foo'
    for val in [1, 0, 14623, True, False]:
        s = 'set %s to %s done' % (var_id, str(val))
        ret = [_ for _ in parse(s)]
        assert len(ret) == 1
        ret = ret[0]
        assert isinstance(ret, AssignOp)
        assert ret.var == var_id
        assert ret.expr == val


def test_simple_assign_op_empty():
    var_id = 'foo'
    s = 'set %s to done' % var_id
    ret = [_ for _ in parse(s)]
    assert len(ret) == 1
    ret = ret[0]
    assert isinstance(ret, AssignOp)
    assert ret.var == var_id
    assert ret.expr is None


def test_simple_assign_op_invalid():
    var_id = 'foo'
    for val in {'bar'}:
        s = 'set %s to %s done' % (var_id, str(val))
        with pytest.raises(SyntaxError):
            [_ for _ in parse(s)]


def test_complex_simple_assign_op():
    var_id = 'foo'
    for val in {1, True}:
        s = 'set %s to %s done' % (var_id, str(val))
        assert _test_parse_complexity(s) == 2


def test_complex_assign_op_special():
    var_id = 'foo'
    for val in {'last roll', 'length of points', 'current point', 'bankroll'}:
        s = 'set %s to %s done' % (var_id, val)
        assert _test_parse_complexity(s) == 2


def test_complex_assign_op_empty_expr():
    var_id = 'foo'
    s = 'set %s to done' % (var_id,)
    assert _test_parse_complexity(s) == 1
