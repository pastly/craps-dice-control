from ...util.json import NumericKeyDecoder
from argparse import ArgumentDefaultsHelpFormatter, FileType
import json
import logging
import sys

from scipy.stats import scoreatpercentile as percentile
import matplotlib
matplotlib.use('Agg')
import pylab as plt  # noqa

plt.rcParams.update({
    'axes.grid': True,
    'savefig.format': 'png',
})
log = logging.getLogger(__name__)


def data_sets_from_input(fd):
    for line in fd:
        yield json.loads(line, cls=NumericKeyDecoder)


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
    ''' Plot the median value across many sets of data, as well as the area
    between the 1st and 3rd quartiles.

    Each input data set should be a dictionary of x,y pairs as specified below.
    All input data sets must have the same x values. At each specified x value,
    plot the median of the y values across all data sets. Also plot the 1st and
    3rd quartiles for the y values at this x value.

    out_fd: the file-like object to which to write the graph in PNG file format
    data_sets: an iterable, containing one or more data set dictionary

    An example data set dictionary:
        {
            0: 1,
            1: 4,
            2: 2,
            6: 7,
            9: 10,
            ...
        }
    Where each key is an x value and the key's value is the corresponding y
    value. All data sets must have the same exact set of keys.
    '''
    plt.figure()
    d = None
    for data_set in data_sets:
        if d is None:
            d = {}
            for x in data_set:
                d[x] = [data_set[x]]
            continue
        for x in data_set:
            d[x].append(data_set[x])
    stats_d = {}
    for x in d:
        stats_d[x] = (
            min(d[x]),
            percentile(d[x], 25),
            percentile(d[x], 50),
            percentile(d[x], 75),
            max(d[x]),
        )
    line_color = (0, 0, 1, 1)
    inner_range_color = (0.2, 0, 0.8, 0.5)
    outer_range_color = (0.5, 0, 0.5, 0.3)
    mins = [v[0] for v in stats_d.values()]
    first = [v[1] for v in stats_d.values()]
    second = [v[2] for v in stats_d.values()]
    third = [v[3] for v in stats_d.values()]
    maxes = [v[4] for v in stats_d.values()]
    plt.plot(stats_d.keys(), second, color=line_color, label='median')
    plt.plot(stats_d.keys(), mins, color=outer_range_color)
    plt.plot(stats_d.keys(), maxes, color=outer_range_color)
    plt.fill_between(
        stats_d.keys(), third, first, color=inner_range_color,
        label='1st-3rd quartile')
    plt.fill_between(
        stats_d.keys(), maxes, third, color=outer_range_color)
    plt.fill_between(stats_d.keys(), first, mins, color=outer_range_color)
    plt.xlim(left=0, right=max(stats_d.keys()))
    plt.ylim(top=max(third), bottom=min(first))
    plt.xlabel('Roll number')
    plt.ylabel('Change in bankroll')
    plt.legend(loc='best', fontsize=8)
    plt.title('Expected bankroll change over time')
    plt.savefig(out_fd, transparent=False)


def gen_parser(sub):
    d = 'Plot the median value across many sets of data, as well as the area '\
        'between the 1st and 3rd quartiles'
    p = sub.add_parser(
        'medrange', description=d,
        formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument(
        '-i', '--input', type=FileType('rt'), default=sys.stdin,
        help='From where to read a stream of dictionaries, one per line')
    p.add_argument(
        '-o', '--output', type=FileType('wb'), default='/dev/stdout',
        help='File to which to write graph')
    return p


def main(args, conf):
    plot(args.output, data_sets_from_input(args.input))
    return 0
