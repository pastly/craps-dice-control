import cdc.core.parse.rollseries as rs
from cdc.lib.statistics import Statistics as S
from copy import deepcopy
from functools import lru_cache


@lru_cache(maxsize=12)
def dice_pair_from_value(val):
    if val > 6:
        return 6, val - 6
    else:
        return val - 1, 1


def test_combine_empty():
    s = S.from_roll_events([])
    assert s.num_rolls() == 0


def test_combine_pairs():
    s = S.from_roll_events(
        rs.dice_pairs_gen_to_events(
            map(dice_pair_from_value, [2, 2])))
    out = s.combine(deepcopy(s))
    for i in range(1, 6+1):
        for j in range(i, 6+1):
            if i == 1 and j == 1:
                assert out.pairs[i][j] == 4
            else:
                assert out.pairs[i][j] == 0


def test_combine_points():
    s1 = S.from_roll_events(
        rs.dice_pairs_gen_to_events(
            map(dice_pair_from_value, [4, 4, 4, 7])))
    s2 = S.from_roll_events(
        rs.dice_pairs_gen_to_events(
            map(dice_pair_from_value, [5, 5, 5, 7])))
    out = s1.combine(s2)
    assert out.points['won'][4] == 1
    assert out.points['won'][5] == 1
    assert out.points['lost'][4] == 1
    assert out.points['lost'][5] == 1
    assert out.points['established'][4] == 2
    assert out.points['established'][5] == 2


def test_combine_hards():
    s1 = S.from_roll_events(
        rs.dice_pairs_gen_to_events([(2, 2)]))
    s2 = S.from_roll_events(
        rs.dice_pairs_gen_to_events([(3, 3)]))
    out = s1.combine(s2)
    assert out.hards[4] == 1
    assert out.hards[6] == 1
    assert out.hards[8] == 0
    assert out.hards[10] == 0


def test_combine_craps():
    s1 = S.from_roll_events(
        rs.dice_pairs_gen_to_events([(1, 1)]))
    s2 = S.from_roll_events(
        rs.dice_pairs_gen_to_events([(1, 2)]))
    s3 = S.from_roll_events(
        rs.dice_pairs_gen_to_events([(6, 6)]))
    out = s1.combine(s2).combine(s3)
    assert out.craps[2] == 1
    assert out.craps[3] == 1
    assert out.craps[12] == 1


def test_combine_naturals():
    s = S.from_roll_events(
        rs.dice_pairs_gen_to_events([(3, 4)]))
    out = s.combine(deepcopy(s))
    assert out.naturals[7] == 2
    assert out.naturals[11] == 0


def test_combine_counts():
    s1 = S.from_roll_events(
        rs.dice_pairs_gen_to_events(
            map(dice_pair_from_value, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])))
    s2 = deepcopy(s1)
    s3 = deepcopy(s1)
    out = s1.combine(s2).combine(s3)
    for i in out.counts:
        assert out.counts[i] == 3


def test_combine_dice():
    s1 = S.from_roll_events(
        rs.dice_pairs_gen_to_events([(3, 4)]))
    s2 = S.from_roll_events(
        rs.dice_pairs_gen_to_events([(3, 4)]))
    s3 = S.from_roll_events(
        rs.dice_pairs_gen_to_events([(1, 5)]))
    out = s1.combine(s2).combine(s3)
    assert out.dice[3] == 2
    assert out.dice[4] == 2
    assert out.dice[1] == 1
    assert out.dice[5] == 1


def test_combine_num_rolls():
    s1 = S.from_roll_events(
        rs.dice_pairs_gen_to_events(
            map(dice_pair_from_value, [9, 9, 9])))
    s2 = S.from_roll_events(
        rs.dice_pairs_gen_to_events(
            map(dice_pair_from_value, [6, 2, 2])))
    out = s1.combine(s2)
    assert out.num_rolls() == 6
    assert out.num_rolls(point_only=False) == 6
    assert out.num_rolls(point_only=True) == 3
