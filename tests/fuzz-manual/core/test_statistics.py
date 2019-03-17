import cdc.core.parse.rollseries as rs
import cdc.core.statistics as stat
import random


def rand_dice_pairs(num):
    for _ in range(num):
        yield (random.randint(1, 6), random.randint(1, 6))


def test_statistics():  # noqa: C901
    for _ in range(100):
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

        point = None
        evs = list(
            rs.dice_pairs_gen_to_events(
                rand_dice_pairs(random.randint(1, 2000))))
        for e in evs:
            assert e.type in {'roll', 'point', 'craps', 'natural'}
            assert sum(e.dice) == e.value
            counts[e.value] += 1
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
        out_stats = stat.calculate_all_statistics(evs)
        assert out_stats == {
            'points': points,
            'craps': craps,
            'naturals': naturals,
            'counts_hard': hards,
            'counts': counts,
        }
        for i in {4, 6, 8, 10}:
            assert hards[i] <= counts[i]
        for i in {4, 5, 6, 8, 9, 10}:
            allowed = {points['established'][i]}
            if point is not None and point == i:
                allowed = {points['established'][i] - 1}
            assert points['won'][i] + points['lost'][i] in allowed