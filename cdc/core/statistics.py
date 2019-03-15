from ..util import stats

from argparse import ArgumentDefaultsHelpFormatter, FileType
import json
import logging
import sys

from scipy.stats import chisquare

log = logging.getLogger(__name__)
MIN_ALLOWED_COUNT = 5


def roll_events_from_input(fd):
    for line in fd:
        yield json.loads(line)


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


def calculate_all_statistics(roll_events):
    points_won, points_lost = 0, 0
    hards = {4: 0, 6: 0, 8: 0, 10: 0,}
    for ev in roll_events:
        if ev['type'] == 'point':
            if ev['args']['is_won']:
                points_won += 1
            elif ev['args']['is_lost']:
                points_lost += 1
            if ev['value'] in {4, 6, 8, 10} and ev['dice'][0] == ev['dice'][1]:
                hards[ev['value']] += 1
    return {
        'points': {'won': points_won, 'lost': points_lost, },
        'hards': hards,
    }


def gen_parser(sub):
    d = 'From either stdin or the given file, read json-formatted roll event '\
        'data. Output a variety of information regarding the outcome.'
    p = sub.add_parser(
        'statistics', description=d,
        formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument(
        '-i', '--input', type=FileType('rt'), default=sys.stdin,
        help='From where to read roll events, one per line')
    p.add_argument(
        '-o', '--output', type=FileType('wt'), default=sys.stdout,
        help='File to which to write data')


def main(args, conf):
    stats = calculate_all_statistics(roll_events_from_input(args.input))
    json.dump(stats, args.output)
    args.output.write('\n')
    return 0
