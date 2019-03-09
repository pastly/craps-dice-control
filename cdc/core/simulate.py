from ..util import stats
from ..lib.argparse import BoundedInt, TryAppendFileType
from .. import globals as G

from argparse import ArgumentDefaultsHelpFormatter
import json
import logging

log = logging.getLogger(__name__)


def is_something_to_do(args):
    possible_desired_outputs = [
        args.roll_counts,
    ]
    for out in possible_desired_outputs:
        if out:
            return True
    return False


def do_roll_counts(out_fd, obs_counts, exp_counts=None):
    j = []
    j.append({
        'label': 'Simulated',
        'counts': obs_counts,
        'counts_hard': {'4': 0, '6': 0, '8': 0, '10': 0},
    })
    if exp_counts:
        j.append({
            'label': 'Expected',
            'counts': exp_counts,
            'counts_hard': {'4': 0, '6': 0, '8': 0, '10': 0},
        })
    for item in j:
        json.dump(item, out_fd)
        out_fd.write('\n')


def gen_parser(sub):
    d = 'Give a list of the relative odds for each of the 11 possible '\
        'outcomes of rolling a pair of 6-sided dice. Simulates rolling '\
        'dice with the provided outcome weights, and then outputs a variety '\
        'of information regarding the outcome.'
    p = sub.add_parser(
        'simulate', description=d,
        formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument(
        'distribution', type=float, nargs=11, metavar='D', default=G.FAIR_DIST,
        help='The likelyhood of rolling 2, 3, 4, ... 12')
    p.add_argument(
        '-i', '--iterations', type=BoundedInt(1, None), default=100000,
        help='How many time to roll the dice using the given probabilities')
    p.add_argument(
        '--roll-counts', type=TryAppendFileType('at'),
        help='File to write json-formatted roll count data')
    p.add_argument(
        '--with-fair-distribution', action='store_true',
        help='When given, also simulate and output fair dice')


def main(args, conf):
    if not is_something_to_do(args):
        log.error("Nothing to do")
        return 1
    log.warn('We do not currently support plotting anything about hard ways')
    obs_counts = stats.simulate_roll_distribution(
        args.iterations, args.distribution)
    exp_counts = None
    if args.with_fair_distribution:
        exp_counts = stats.theoretical_fair_distribution(args.iterations)
    if args.roll_counts:
        do_roll_counts(args.roll_counts, obs_counts, exp_counts)
    return 0
