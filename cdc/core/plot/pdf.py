from ...lib.rollevent import RollEvent

from argparse import ArgumentDefaultsHelpFormatter, FileType
import json
import logging
import sys

import matplotlib
matplotlib.use('Agg')
import pylab as plt  # noqa

plt.rcParams.update({
    'axes.grid': True,
    'savefig.format': 'png',
})
log = logging.getLogger(__name__)


def roll_events_from_input(fd):
    for line in fd:
        yield RollEvent.from_dict(json.loads(line))


def make_counts(roll_events):
    counts = {i: 0 for i in range(2, 12+1)}
    hards = {4: 0, 6: 0, 8: 0, 10: 0}
    for e in roll_events:
        counts[e.value] += 1
        if e.value in {4, 6, 8, 10} and e.dice[0] == e.dice[1]:
            hards[e.value] += 1
    return counts, hards


def make_expected_counts(num_rolls):
    counts = {
        2: num_rolls * 1 / 36,
        3: num_rolls * 2 / 36,
        4: num_rolls * 3 / 36,
        5: num_rolls * 4 / 36,
        6: num_rolls * 5 / 36,
        7: num_rolls * 6 / 36,
        8: num_rolls * 5 / 36,
        9: num_rolls * 4 / 36,
        10: num_rolls * 3 / 36,
        11: num_rolls * 2 / 36,
        12: num_rolls * 1 / 36,
    }
    hards = {
        4: num_rolls * 1 / 36,
        6: num_rolls * 1 / 36,
        8: num_rolls * 1 / 36,
        10: num_rolls * 1 / 36,
    }
    return counts, hards


def plot(out_fd, data_sets):
    colors = "krbgcmy"
    color_idx = 0
    ymax = 0
    for label, counts, hards in data_sets:
        num_rolls = sum(counts[i] for i in counts)
        points = []
        for i in range(2, 12+1):
            y = counts[i]/num_rolls
            if y > ymax:
                ymax = y
            points.append((i, y))
        xs, ys = zip(*points)
        plt.plot(xs, ys, label=label, c=colors[color_idx])
        color_idx += 1
    ymax = round(ymax*1.1, 2)
    plt.legend(loc='best')
    plt.xlim(left=2, right=12)
    plt.ylim(bottom=0, top=ymax)
    plt.xlabel('Roll')
    plt.ylabel('Probability (fraction of 1)')
    plt.title('Roll Probability Density Function')
    plt.savefig(out_fd)


def gen_parser(sub):
    d = 'Plot Probability Density Function from the input stream of roll '\
        'events'
    p = sub.add_parser(
        'pdf', description=d,
        formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument(
        '-i', '--input', type=FileType('rt'), default=sys.stdin,
        help='From where to read a stream of json-formatted roll events, one '
        'per line')
    p.add_argument(
        '-o', '--output', type=FileType('wb'), default='/dev/stdout',
        help='File to which to write graph')
    p.add_argument(
        '-e', '--with-expected', action='store_true',
        help='Also plot expected PDF based on number of rolls')
    p.add_argument(
        '-l', '--label', type=str, help='What to label the input line as')
    return p


def main(args, conf):
    data_sets = []
    roll_events = roll_events_from_input(args.input)
    counts, hards = make_counts(roll_events)
    label = args.label or 'foo'
    data_sets.append((label, counts, hards))
    if args.with_expected:
        data_sets.append((
            'Expected', *make_expected_counts(
                sum(counts[i] for i in counts))))
    plot(args.output, data_sets)
    return 0
