from ..lib.rollevent import RollEvent
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
        yield RollEvent.from_dict(json.loads(line))


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


def combine_statistics(*a):
    ''' Given two or more statistic dictionaries from
    calculate_all_statistics(), aggregate the stats and return a new stat
    dictionary '''
    if not len(a):
        return {}
    if len(a) == 1:
        return a[0]
    out_stats, a = a[0], a[1:]
    for work in a:
        # parts of the stat dict that are 3 layers deep and can be simply
        # summed
        for k1 in {'points', 'counts_pairs'}:
            if k1 not in work:
                continue
            if k1 not in out_stats:
                out_stats[k1] = {}
            for k2 in work[k1]:
                if k2 not in out_stats[k1]:
                    out_stats[k1][k2] = {}
                for k3 in work[k1][k2]:
                    if k3 not in out_stats[k1][k2]:
                        out_stats[k1][k2][k3] = 0
                    out_stats[k1][k2][k3] += work[k1][k2][k3]
        # parts of the stat dict that are 2 layers deep and can be simply
        # summed
        for k1 in {
                'counts_hard', 'craps', 'naturals', 'counts', 'counts_dice',
                'num_rolls'}:
            if k1 not in work:
                continue
            if k1 not in out_stats:
                out_stats[k1] = {}
            for k2 in work[k1]:
                if k2 not in out_stats[k1]:
                    out_stats[k1][k2] = 0
                out_stats[k1][k2] += work[k1][k2]
    return out_stats


def calculate_all_statistics(roll_events):
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
    have_point = False
    num_rolls = 0
    num_rolls_point = 0
    # Begin consumption of events
    for ev in roll_events:
        num_rolls += 1
        if have_point:
            num_rolls_point += 1
        if ev.type == 'point':
            if ev.args['is_won']:
                assert have_point
                points['won'][ev.value] += 1
                have_point = False
            elif ev.args['is_lost']:
                assert have_point
                points['lost'][ev.args['point_value']] += 1
                have_point = False
            else:
                assert not have_point
                points['established'][ev.value] += 1
                have_point = True
        elif ev.type == 'craps':
            craps[ev.value] += 1
        elif ev.type == 'natural':
            naturals[ev.value] += 1
        if ev.value in {4, 6, 8, 10} and ev.dice[0] == ev.dice[1]:
            hards[ev.value] += 1
        counts[ev.value] += 1
        dice[ev.dice[0]] += 1
        dice[ev.dice[1]] += 1
        if ev.dice[0] <= ev.dice[1]:
            pairs[ev.dice[0]][ev.dice[1]] += 1
        else:
            pairs[ev.dice[1]][ev.dice[0]] += 1
    # End consumption of events
    return {
        'points': points,
        'craps': craps,
        'naturals': naturals,
        'counts_hard': hards,
        'counts': counts,
        'counts_dice': dice,
        'counts_pairs': pairs,
        'num_rolls': {
            'overall': num_rolls,
            'point': num_rolls_point,
        }
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
