import io
import pytest

from cdc.core.parse import rollseries as rs


def assert_unreached(msg=None):
    if msg:
        assert False, msg
    else:
        assert False, "Unreachable code path was reached"


def event_gen_from_str(s, starting_point=None):
    fd = io.StringIO(s)
    pair_gen = rs.roll_series_stream_to_dice_pairs(fd)
    event_gen = rs.dice_pairs_gen_to_events(
        pair_gen, starting_point=starting_point)
    return event_gen


def assert_dice_event(event, type_, dice, args):
    assert event['type'] == type_
    assert event['dice'] == dice
    assert event['value'] == sum(dice)
    assert event['args'] == args


def test_simple_roll():
    event_gen = event_gen_from_str("11", starting_point=4)
    evs = list(event_gen)
    assert len(evs) == 1
    assert_dice_event(evs[0], 'roll', (1, 1), {})


def test_simple_natural():
    event_gen = event_gen_from_str("3456")
    evs = list(event_gen)
    assert len(evs) == 2
    for ev, dice in [(evs[0], (3, 4)), (evs[1], (5, 6))]:
        assert_dice_event(ev, 'natural', dice, {})


def test_simple_craps():
    event_gen = event_gen_from_str("111266")
    evs = list(event_gen)
    assert len(evs) == 3
    for ev, dice in [(evs[0], (1, 1)), (evs[1], (1, 2)), (evs[2], (6, 6))]:
        assert_dice_event(ev, 'craps', dice, {})


def test_simple_point_established():
    event_gen = event_gen_from_str("44")
    ev = list(event_gen)[0]
    assert_dice_event(ev, 'point', (4, 4), {
        'is_established': True,
        'is_won': False,
        'is_lost': False,
    })


def test_simple_point_won():
    event_gen = event_gen_from_str("4426")
    ev = list(event_gen)[1]
    assert_dice_event(ev, 'point', (2, 6), {
        'is_established': False,
        'is_won': True,
        'is_lost': False,
    })


def test_simple_point_lost():
    event_gen = event_gen_from_str("4416")
    ev = list(event_gen)[1]
    assert_dice_event(ev, 'point', (1, 6), {
        'is_established': False,
        'is_won': False,
        'is_lost': True,
    })


def test_simple_comment_1():
    event_gen = event_gen_from_str("1#1\n2")
    ev = list(event_gen)[0]
    assert_dice_event(ev, 'craps', (1, 2), {})


def test_simple_comment_2():
    event_gen = event_gen_from_str("1# 1\n2")
    ev = list(event_gen)[0]
    assert_dice_event(ev, 'craps', (1, 2), {})


def test_simple_comment_3():
    event_gen = event_gen_from_str("1  #  \n2")
    ev = list(event_gen)[0]
    assert_dice_event(ev, 'craps', (1, 2), {})


def test_simple_empty_line():
    event_gen = event_gen_from_str("\n\n1\n2")
    ev = list(event_gen)[0]
    assert_dice_event(ev, 'craps', (1, 2), {})


def test_simple_bad_die_1():
    event_gen = event_gen_from_str("71")
    with pytest.raises(ValueError) as ex_info:
        list(event_gen)[0]
    assert 'Impossible die value 7' in str(ex_info)


def test_simple_bad_die_2():
    event_gen = event_gen_from_str(".1")
    with pytest.raises(ValueError) as ex_info:
        list(event_gen)[0]
    assert 'invalid literal' in str(ex_info)


def test_simple_no_events_1():
    event_gen = event_gen_from_str("")
    assert not len(list(event_gen))


def test_simple_no_events_2():
    event_gen = event_gen_from_str("  #  ")
    assert not len(list(event_gen))


def test_simple_no_events_3():
    event_gen = event_gen_from_str("  \n #  12  ")
    assert not len(list(event_gen))


def test_odd_num_dice():
    event_gen = event_gen_from_str("666")
    try:
        list(event_gen)
    except rs.IncompleteRollSeriesError:
        pass
    else:
        assert_unreached()
