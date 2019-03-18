from ..lib.argparse import BoundedInt
from ..util.json import NumericKeyDecoder
from ..util.rand import roll_die_with_weights

from argparse import ArgumentDefaultsHelpFormatter, FileType
from datetime import datetime
import json
import logging
import sys

log = logging.getLogger(__name__)


# Split a list into batches of size n
# https://stackoverflow.com/q/8290397
def _batch(iterable, n=1):
    current_batch = []
    for item in iterable:
        current_batch.append(item)
        if len(current_batch) == n:
            yield current_batch
            current_batch = []
    if current_batch:
        yield current_batch


def _calc_die_weights(stats):
    weights = stats['counts_dice']
    for i in range(1, 6+1):
        assert i in weights
        assert isinstance(weights[i], int) or isinstance(weights[i], float)
    return [v for v in weights.values()]


def _roll_dice_repeatedly(weights, times):
    for _ in range(times):
        yield roll_die_with_weights(weights), roll_die_with_weights(weights)


def do_rollseries(args, stats):
    weights = _calc_die_weights(stats)
    header = '## cdc simluation run at %s\n'\
        '## simulating %d dice rolls\n'\
        '## weights: %s\n' % (datetime.now(), args.iterations, weights)
    args.output.write(header)
    for batch in _batch(_roll_dice_repeatedly(weights, args.iterations), n=20):
        s = ' '.join(str(pair[0])+str(pair[1]) for pair in batch)
        args.output.write('%s\n' % s)


def gen_parser(sub):
    d = 'As input, provide the output of the "cdc statistics" command. '\
        'Simulate a bunch of dice rolls using the probabilities calculated '\
        'from the input statistics. Outputs something about the simulation '\
        'based on what you ask for.'
    p = sub.add_parser(
        'simulate', description=d,
        formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument(
        '-i', '--input', type=FileType('rt'), default=sys.stdin,
        help='From where to read statistics')
    p.add_argument(
        '-o', '--output', type=FileType('wt'), default=sys.stdout,
        help='To where to write output')
    p.add_argument(
        '-f', '--out-format', required=True,
        choices=('rollseries',))
    p.add_argument(
        '--iterations', type=BoundedInt(1, None), default=100000,
        help='How many time to roll the dice using the given probabilities')


def main(args, conf):
    stats = json.load(args.input, cls=NumericKeyDecoder)
    assert args.out_format == 'rollseries'
    return do_rollseries(args, stats)
