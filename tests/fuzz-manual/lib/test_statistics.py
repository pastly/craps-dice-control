import cdc.core.parse.rollseries as rs
from cdc.lib.statistics import Statistics
import random


def rand_dice_pairs(num):
    for _ in range(num):
        yield (random.randint(1, 6), random.randint(1, 6))


def test_statistics():  # noqa: C901
    for _ in range(1000):
        points = {
            'won': {
                4: 0, 5: 0, 6: 0, 8: 0, 9: 0, 10: 0,
            },
            'lost': {
                4: 0, 5: 0, 6: 0, 8: 0, 9: 0, 10: 0,
            },
            'established': {
                4: 0, 5: 0, 6: 0, 8: 0, 9: 0, 10: 0,
            },
        }
        hards = {4: 0, 6: 0, 8: 0, 10: 0}
        craps = {2: 0, 3: 0, 12: 0}
        naturals = {7: 0, 11: 0}
        counts = {i: 0 for i in range(2, 12+1)}
        dice = {i: 0 for i in range(1, 6+1)}
        pairs = {i: {j: 0 for j in range(i, 6+1)} for i in range(1, 6+1)}

        point = None
        num_rolls = 0
        num_rolls_point = 0
        num_7s = 0
        num_7s_point = 0
        evs = list(
            rs.dice_pairs_gen_to_events(
                rand_dice_pairs(random.randint(1, 200))))
        for e in evs:
            assert e.type in {'roll', 'point', 'craps', 'natural'}
            assert sum(e.dice) == e.value
            num_rolls += 1
            if point:
                num_rolls_point += 1
            if e.value == 7:
                num_7s += 1
                if point:
                    num_7s_point += 1
            counts[e.value] += 1
            dice[e.dice[0]] += 1
            dice[e.dice[1]] += 1
            if e.dice[0] <= e.dice[1]:
                pairs[e.dice[0]][e.dice[1]] += 1
            else:
                pairs[e.dice[1]][e.dice[0]] += 1
            if e.dice[0] == e.dice[1] and e.value in {4, 6, 8, 10}:
                hards[e.value] += 1
            if e.type == 'craps':
                assert e.value in {2, 3, 12}
                assert point is None
                craps[e.value] += 1
            elif e.type == 'natural':
                assert e.value in {7, 11}
                assert point is None
                naturals[e.value] += 1
            elif e.type == 'roll':
                assert point is not None
                assert e.value not in {point, 7}
            else:
                assert e.type == 'point'
                assert e.value in {4, 5, 6, 7, 8, 9, 10}
                assert sum(int(e.args[s]) for s in {
                    'is_established', 'is_won', 'is_lost'}) == 1
                if e.args['is_established']:
                    assert point is None
                    assert e.value == e.args['point_value']
                    assert e.value in {4, 5, 6, 8, 9, 10}
                    points['established'][e.value] += 1
                    point = e.value
                elif e.args['is_won']:
                    assert point is not None
                    assert e.value in {4, 5, 6, 8, 9, 10}
                    assert e.value == e.args['point_value']
                    assert point == e.value
                    points['won'][e.value] += 1
                    point = None
                elif e.args['is_lost']:
                    assert point is not None
                    assert e.value == 7
                    assert point == e.args['point_value']
                    points['lost'][point] += 1
                    point = None
        # Here we finally call the code that we're testing
        out_stats = Statistics.from_roll_events(evs)
        assert out_stats.to_dict() == {
            'points': points,
            'craps': craps,
            'naturals': naturals,
            'hards': hards,
            'pairs': pairs,
            'dice': dice,
            'counts': counts,
            'num_rolls': {'overall': num_rolls, 'point': num_rolls_point},
        }
        assert out_stats.points == points
        assert out_stats.craps == craps
        assert out_stats.naturals == naturals
        assert out_stats.hards == hards
        assert out_stats.pairs == pairs
        assert out_stats.dice == dice
        assert out_stats.counts == counts
        assert out_stats.num_rolls() == num_rolls
        assert out_stats.num_rolls(point_only=False) == num_rolls
        assert out_stats.num_rolls(point_only=True) == num_rolls_point
        try:
            assert out_stats.rsr() == num_rolls / counts[7]
            assert out_stats.rsr(point_only=False) == num_rolls / num_7s
        except ZeroDivisionError:
            assert not num_7s
        try:
            assert out_stats.rsr(point_only=True) == \
                num_rolls_point / num_7s_point
        except ZeroDivisionError:
            assert not num_7s_point
        assert num_rolls > num_rolls_point
        for i in {4, 6, 8, 10}:
            assert hards[i] <= counts[i]
        for i in {4, 5, 6, 8, 9, 10}:
            allowed = {points['established'][i]}
            if point is not None and point == i:
                allowed = {points['established'][i] - 1}
            assert points['won'][i] + points['lost'][i] in allowed
