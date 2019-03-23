from ..lib.argparse import BoundedInt
from ..util.json import NumericKeyDecoder
from ..util.rand import roll_die_with_weights
from ..lib.strategy import BasicPassStrategy, CrapsRoll as R

from argparse import ArgumentDefaultsHelpFormatter, FileType
from datetime import datetime
import multiprocessing as mp
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


def roll_weighted_dice_repeatedly(weights, times):
    for _ in range(times):
        yield roll_die_with_weights(weights), roll_die_with_weights(weights)


def do_rollseries(args, stats):
    weights = _calc_die_weights(stats)
    header = '## cdc simluation run at %s\n'\
        '## simulating %d dice rolls\n'\
        '## weights: %s\n' % (datetime.now(), args.rolls, weights)
    args.output.write(header)
    for batch in _batch(
            roll_weighted_dice_repeatedly(weights, args.rolls), n=20):
        s = ' '.join(str(pair[0])+str(pair[1]) for pair in batch)
        args.output.write('%s\n' % s)


def f(_):
    strat = strat_class(5)
    data_set = {}
    next_jump = 10
    for i, pair in enumerate(
            roll_weighted_dice_repeatedly(weights, num_rolls)):
        strat.make_bets()
        strat.after_roll(R(*pair))
        if True or not i % int(next_jump / 10):
            data_set[i] = strat.bankroll
        if i == next_jump:
            next_jump *= 10
    semaphore.acquire()
    return data_set


def _init_bankroll_globals(semaphore_, weights_, num_rolls_, strat_class_):
    global semaphore, weights, num_rolls, strat_class
    semaphore = semaphore_
    weights = weights_
    num_rolls = num_rolls_
    strat_class = strat_class_


def bankroll_over_time_repeatedly(stats, strat_class, num_rolls, num_repeat):
    weights = _calc_die_weights(stats)
    chunk_size = 32
    cpu_count = mp.cpu_count()
    semaphore = mp.Semaphore(chunk_size * cpu_count)
    with mp.Pool(
            initializer=_init_bankroll_globals,
            initargs=(semaphore, weights, num_rolls, strat_class)) as pool:
        for res in pool.imap_unordered(f, range(num_repeat), chunk_size):
            yield res
            semaphore.release()


def do_bankroll(args, stats):
    for res in bankroll_over_time_repeatedly(
            stats, BasicPassStrategy, args.rolls, args.repeat):
        json.dump(res, args.output)
        args.output.write('\n')


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
        choices=('rollseries', 'bankroll',))
    p.add_argument(
        '--rolls', type=BoundedInt(1, None), default=100000,
        help='How many time to roll the dice using the given probabilities')
    p.add_argument(
        '--repeat', type=BoundedInt(1, None), default=1,
        help='How many times to simulate a bunch of rolls, for the types of '
        'output that allow repeats')


def main(args, conf):
    stats = json.load(args.input, cls=NumericKeyDecoder)
    #
    assert args.out_format in {'rollseries', 'bankroll'}, 'if this fails, '\
        'I need to think about if --repeat applies to the new output format'
    if args.out_format not in {'bankroll'} and args.repeat != 1:
        log.warn('Ignoring --repeat %d', args.repeat)
    #
    if args.out_format == 'rollseries':
        return do_rollseries(args, stats)
    assert args.out_format == 'bankroll'
    return do_bankroll(args, stats)
