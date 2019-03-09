from ..util import stats
from ..util.json import NumericKeyDecoder
from ..lib.argparse import TryAppendFileType

from argparse import ArgumentDefaultsHelpFormatter, FileType
import json
import logging
import sys

from scipy.stats import chisquare

log = logging.getLogger(__name__)
MIN_ALLOWED_COUNT = 5


def counts_from_input(fd):
    d = json.load(fd, cls=NumericKeyDecoder)
    return d['counts']


def is_something_to_do(args):
    possible_desired_outputs = [
        args.statistics,
    ]
    for out in possible_desired_outputs:
        if out:
            return True
    return False


def do_stats(out_fd, counts):
    too_few = set()
    for i in range(2, 12+1):
        if counts[i] < MIN_ALLOWED_COUNT:
            too_few.add(i)
    if too_few:
        log.error(
            "Didn't roll %s %d or more times",
            ",".join([str(c) for c in too_few]), MIN_ALLOWED_COUNT)
        return
    num_rolls = sum(counts[i] for i in counts)
    exp_counts = stats.theoretical_fair_distribution(num_rolls)
    act_dist = []
    exp_dist = []
    for i in range(2, 12+1):
        act_dist.append(counts[i])
        exp_dist.append(exp_counts[i])
    chisq, p = chisquare(exp_dist, act_dist)
    json.dump({
        'data': {
            'expected': exp_counts,
            'actual': counts,
        },
        'stats': {
            'chisq': chisq,
            'p': p,
        },
    }, out_fd)
    out_fd.write('\n')


def gen_parser(sub):
    d = 'From either stdin or the given file, read json-formatted roll count '\
        'data. Output a variety of information regarding the outcome.'
    p = sub.add_parser(
        'rollstats', description=d,
        formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument(
        '-i', '--input', type=FileType('rt'), default=sys.stdin,
        help='From where to read roll data')
    p.add_argument(
        '--statistics', type=TryAppendFileType('at'),
        help='Where to write json-formatted statistical information about '
        'rolls. Will append to end, if possible.')


def main(args, conf):
    if not is_something_to_do(args):
        log.error("Nothing to do")
        return 1
    counts = counts_from_input(args.input)
    if args.statistics:
        do_stats(args.statistics, counts)
    return 0
