from ..util import stats
from ..util.plot import xy as plot_xy
from ..lib.argparse import BoundedInt
from .. import globals as G

from argparse import ArgumentDefaultsHelpFormatter, FileType
import json
import logging

log = logging.getLogger(__name__)


def is_something_to_do(args):
    possible_desired_outputs = [
        args.roll_counts,
        args.pdf_png,
    ]
    for out in possible_desired_outputs:
        if out:
            return True
    return False


def do_plot(out_fd, obs_counts, exp_counts=None):
    input_data_sets = []
    num_rolls = sum(obs_counts[i] for i in obs_counts)
    assert num_rolls == round(sum(exp_counts[i] for i in exp_counts)) \
        if exp_counts is not None else True
    ymax = 0
    for label, counts in [('Expected', exp_counts), ('Simulated', obs_counts)]:
        if counts is None:
            continue
        xys = []
        for i in range(2, 12+1):
            y = counts[i]/num_rolls
            if y > ymax:
                ymax = y
            xys.append((i, y))
        ymax = round(ymax*1.1, 2)
        input_data_sets.append((label, xys))
    plot_xy(
        out_fd, *input_data_sets, ymin=0, ymax=ymax,
        x='Roll',
        y='Probability (fraction of 1)',
        title='Roll Probability Distribution Function')


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
    json.dump(j, out_fd, indent=2)


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
        '--roll-counts', type=FileType('wt'),
        help='File to write json-formatted roll count data')
    p.add_argument(
        '--pdf-png', type=FileType('wb'),
        help='File to which to draw the Probability Distribution Function as '
        'a PNG')
    p.add_argument(
        '--with-fair-distribution', action='store_true',
        help='When given, also simulate and output fair dice')


def main(args, conf):
    if not is_something_to_do(args):
        log.error("Nothing to do")
        return 1
    obs_counts = stats.simulate_roll_distribution(
        args.iterations, args.distribution)
    exp_counts = None
    if args.with_fair_distribution:
        exp_counts = stats.theoretical_fair_distribution(args.iterations)
    if args.roll_counts:
        do_roll_counts(args.roll_counts, obs_counts, exp_counts)
    if args.pdf_png:
        do_plot(args.pdf_png, obs_counts, exp_counts)
    return 0
