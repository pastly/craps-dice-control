from argparse import ArgumentDefaultsHelpFormatter, FileType
import logging
import json
import sys

from ...lib.argparse import TryAppendFileType

log = logging.getLogger(__name__)


def read_input_into_gen(fd):
    buf_int = None
    for line in fd:
        line = line.strip()
        if not len(line):
            continue
        if line[0] == '#':
            continue
        for word in line.split():
            for c in word:
                try:
                    i = int(c)
                except ValueError as e:
                    raise e
                if i < 1 or i > 6:
                    raise ValueError("Impossible die value %d" % i)
                if buf_int is None:
                    buf_int = i
                    continue
                assert buf_int is not None
                yield (buf_int, i)
                buf_int = None


def do_counts(out_fd, input_pairs, label):
    d = {
        'label': label,
        'counts': {},
        'counts_hard': {},
    }
    for i in range(2, 12+1):
        d['counts'][i] = 0
    for i in {4, 6, 8, 10}:
        d['counts_hard'][i] = 0
    for pair in input_pairs:
        s = sum(pair)
        d['counts'][s] += 1
        if pair[0] == pair[1] and s in {4, 6, 8, 10}:
            d['counts_hard'][s] += 1
    json.dump(d, out_fd)
    out_fd.write('\n')
    return 0


def _event(type_, dice, args):
    return {
        'type': type_,
        'dice': dice,
        'value': sum(dice),
        'args': args,
    }


def _event_natural(dice):
    assert sum(dice) in {7, 11}
    return _event('natural', dice, {})


def _event_craps(dice):
    assert sum(dice) in {2, 3, 12}
    return _event('craps', dice, {})


def _event_point(dice, existing_point):
    assert sum(dice) in {4, 5, 6, 8, 9, 10}
    assert existing_point in {None, 4, 5, 6, 8, 9, 10}
    e = _event(
        'point', dice, {
            'is_established': True if existing_point is None else False,
            'is_won': True if existing_point == sum(dice) else False,
            'is_lost': True if sum(dice) == 7 else False,
        })
    assert len(list(filter(None, e['args'].values()))) == 1


def _event_roll(dice):
    return _event('roll', dice, {})


def event_gen(input_pairs):
    point = None
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


def do_chrono(out_fd, input_pairs, label):
    json.dump({
        'label': label,
        'events': list(event_gen(input_pairs)),
    }, out_fd)
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
        '-f', '--out-format', choices=('counts', 'chrono'), required=True)
    p.add_argument(
        '--label', type=str, default=None,
        help='Add this label to the output data for supported output formats')
    return p


def main(args, conf):
    if args.label and args.out_format not in {'counts'}:
        log.warn('Input label "%s" will be ignored', args.label)
    data = read_input_into_gen(args.input)
    if args.out_format == 'counts':
        return do_counts(args.output, data, args.label)
    elif args.out_format == 'chrono':
        return do_chrono(args.output, data, args.label)
    log.error('Unknown --out-format %s', args.out_format)
    return 1
