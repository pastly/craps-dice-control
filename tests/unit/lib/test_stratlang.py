from cdc.lib.stratlang import parse, InvalidValueError
from cdc.lib.strategy import CBPass, CBDontPass, CBCome, CBDontCome, CBField,\
    CBPlace, CBHardWay, CBOdds

from sly.lex import LexError

import pytest


def test_int_literal_valid():
    for i in {'0', '1', '98794'}:
        s = '%s done' % i
        ret = [_ for _ in parse(s)]
        assert len(ret) == 1
        assert ret[0] == int(i)


def test_int_literal_invalid():
    for i in {'-10', '-1', '-98794'}:
        s = '%s done' % i
        with pytest.raises(LexError) as e:
            [_ for _ in parse(s)]
        assert e.value.error_index == 0


def test_float_literal_valid():
    for i in {'0.0', '.1', '1.0', '813.15'}:
        s = '%s done' % i
        ret = [_ for _ in parse(s)]
        assert len(ret) == 1
        assert ret[0] == float(i)


def test_float_literal_invalid():
    for i in {'-0.0', '-.1', '-1.0', '-813.15'}:
        s = '%s done' % i
        with pytest.raises(LexError) as e:
            [_ for _ in parse(s)]
        assert e.value.error_index == 0


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
            with pytest.raises(LexError) as e:
                [_ for _ in parse(s)]
            assert e.value.error_index in {16, 17}
        for is_dont_str in {'12'}:
            s = 'make bet odds %d %s %d done' % (point, is_dont_str, amount)
            with pytest.raises(SyntaxError) as e:
                [_ for _ in parse(s)]
