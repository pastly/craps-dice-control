from argparse import ArgumentDefaultsHelpFormatter, FileType
import logging
import json
import sys

from ...lib.argparse import TryAppendFileType
from ...lib.rollevent import RollEvent

log = logging.getLogger(__name__)


class IncompleteRollSeriesError(ValueError):
    pass


class ImpossibleDieValueError(ValueError):
    pass


def roll_series_stream_to_dice_pairs(fd):
    ''' Turn the input plain-text-formatted roll series data into a generator
    producing pairs of dice values.

    Input: 33425316
    Output (as a generator): (3, 3), (4, 2), (5, 3), (1, 6)
    '''
    buf_int = None
    for line in fd:
        if '#' in line:
            line = line[0:line.find('#')]
        line = line.strip()
        if not len(line):
            continue
        for word in line.split():
            for c in word:
                try:
                    i = int(c)
                except ValueError:
                    raise ImpossibleDieValueError(c)
                if i < 1 or i > 6:
                    raise ImpossibleDieValueError(i)
                if buf_int is None:
                    buf_int = i
                    continue
                assert buf_int is not None
                yield (buf_int, i)
                buf_int = None
    if buf_int:
        raise IncompleteRollSeriesError


def _event(type_, dice, args):
    return RollEvent(type_, dice, args)


def _event_natural(dice):
    assert sum(dice) in {7, 11}
    return _event('natural', dice, {})


def _event_craps(dice):
    assert sum(dice) in {2, 3, 12}
    return _event('craps', dice, {})


def _event_point(dice, existing_point):
    assert sum(dice) in {4, 5, 6, 7, 8, 9, 10}
    assert existing_point in {None, 4, 5, 6, 8, 9, 10}
    e = _event(
        'point', dice, {
            'is_established': True if existing_point is None else False,
            'is_won': True if existing_point == sum(dice) else False,
            'is_lost': True if sum(dice) == 7 else False,
            'point_value': sum(dice) if not existing_point else existing_point,
        })
    # only one flag set
    assert sum(int(e.args[a])
               for a in {'is_established', 'is_won', 'is_lost'}) == 1
    # value must match existing_point if is_established or is_won, otherwise
    # must not match
    if e.args['is_established'] or e.args['is_won']:
        assert e.args['point_value'] == e.value
    else:
        assert e.args['point_value'] != e.value
    return e


def _event_roll(dice):
    return _event('roll', dice, {})


def dice_pairs_gen_to_events(input_pairs, starting_point=None):
    ''' Take a generator of pairs of dice, and parse them into craps game
    events. Optionally take a starting point value.

    Input (as generator): (1, 2), (2, 3), (6, 3)
    Output (as generator): {'type': 'craps', ...},
                           {'type': 'point', ...},
                           {'type': 'roll', ...},
    '''
    assert starting_point in {None, 4, 5, 6, 8, 9, 10}
    point = starting_point
    for pair in input_pairs:
        s = sum(pair)
        if point is None:
            if s in {7, 11}:
                yield _event_natural(pair)
            elif s in {2, 3, 12}:
                yield _event_craps(pair)
            else:
                yield _event_point(pair, point)
                point = s
        else:
            assert point in {4, 5, 6, 8, 9, 10}
            if s == 7 or s == point:
                yield _event_point(pair, point)
                point = None
            else:
                yield _event_roll(pair)


def do_stream(out_fd, roll_events):
    for ev in roll_events:
        json.dump(ev.to_dict(), out_fd)
        out_fd.write('\n')
    return 0


def gen_parser(sub):
    d = 'Read plain-text-formatted roll series data, convert it to some '\
        'other format, and output it'
    p = sub.add_parser(
        'rollseries', description=d,
        formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument(
        '-i', '--input', type=FileType('rt'), default=sys.stdin,
        help='From where to read data')
    p.add_argument(
        '-o', '--output', type=TryAppendFileType('at'), default=sys.stdout,
        help='File to which to write data. Will append to end, if possible.')
    p.add_argument(
        '-f', '--out-format', required=True,
        choices=('stream',))
    return p


def main(args, conf):
    roll_events = dice_pairs_gen_to_events(
        roll_series_stream_to_dice_pairs(args.input))
    if args.out_format == 'stream':
        return do_stream(args.output, roll_events)
    log.error('Unknown --out-format %s', args.out_format)
    return 1
