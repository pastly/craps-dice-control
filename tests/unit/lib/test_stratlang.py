from cdc.lib.stratlang import parse

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
