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
    json.dump(d, out_fd, indent=2)
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
        '-f', '--out-format', choices=('counts',), required=True)
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
    return 1
