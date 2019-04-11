import cdc.core.statistics as stat
from copy import deepcopy
# from functools import lru_cache


# @lru_cache(maxsize=12)
# def dice_pair_from_value(val):
#     if val > 6:
#         return 6, val - 6
#     else:
#         return val - 1, 1


def test_combine_empty():
    assert stat.combine_statistics() == {}


def test_combine_identity():
    assert stat.combine_statistics({'foo': 1}) == {'foo': 1}


def test_combine_pairs():
    d = {'counts_pairs': {4: {4: 1}}}
    out = stat.combine_statistics(d, deepcopy(d))
    assert out['counts_pairs'][4][4] == 2


def test_combine_points():
    d1 = {'points': {'won': {4: 1}}}
    d2 = {'points': {'won': {4: 1, 5: 1}}}
    out = stat.combine_statistics(d1, d2)
    assert out['points']['won'][4] == 2
    assert out['points']['won'][5] == 1


def test_combine_hards():
    d = {'counts_hard': {4: 1}}
    out = stat.combine_statistics(d, deepcopy(d))
    assert out['counts_hard'][4] == 2


def test_combine_craps():
    d1 = {'craps': {2: 1}}
    d2 = {'craps': {3: 1}}
    d3 = {'craps': {12: 1}}
    out = stat.combine_statistics(d1, d2, d3)
    assert out['craps'][2] == 1
    assert out['craps'][3] == 1
    assert out['craps'][12] == 1


def test_combine_naturals():
    d1 = {'naturals': {7: 1}}
    d2 = {'naturals': {11: 1}}
    out = stat.combine_statistics(d1, d2)
    assert out['naturals'][7] == 1
    assert out['naturals'][11] == 1


def test_combine_counts():
    d = {'counts': {i: 1 for i in range(2, 12+1)}}
    out = stat.combine_statistics(d, deepcopy(d), deepcopy(d))
    for i in out['counts']:
        assert out['counts'][i] == 3


def test_combine_dice():
    d = {'counts_dice': {i: 1 for i in range(2, 6+1)}}
    out = stat.combine_statistics(d, deepcopy(d), deepcopy(d))
    for i in out['counts_dice']:
        assert out['counts_dice'][i] == 3


def test_combine_num_rolls():
    d = {'num_rolls': {'overall': 10, 'point': 1}}
    out = stat.combine_statistics(d, deepcopy(d), deepcopy(d))
    assert out['num_rolls']['overall'] == 30
    assert out['num_rolls']['point'] == 3
