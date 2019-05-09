from ..lib.argparse import BoundedInt
from ..util.json import NumericKeyDecoder
from ..util.rand import roll_die_with_weights
from ..lib.strategy import CrapsRoll as R, Strategy

from ..lib import stratlang as lang

from argparse import ArgumentDefaultsHelpFormatter, FileType
from datetime import datetime
import multiprocessing as mp
import json
import logging
import sys

log = logging.getLogger(__name__)


class UserDefinedStrategy(Strategy):
    def __init__(self, logic, *a, **kw):
        self._logic = [_ for _ in logic]
        super().__init__('User Strat', *a, **kw)

    @staticmethod
    def _from(logic):
        return UserDefinedStrategy(logic)

    @staticmethod
    def from_string(s):
        logic = lang.parse(s)
        return UserDefinedStrategy._from(logic)

    @staticmethod
    def from_stream(fd):
        logic = lang.parse_stream(fd)
        return UserDefinedStrategy._from(logic)

    def _varid_to_value(self, var_id):
        try:
            return {
                lang.VarId.Bankroll: self.bankroll,
                lang.VarId.Point: self.point,
            }[var_id]
        except KeyError:
            raise NotImplementedError('Can\'t get value for %s' % var_id)

    def _listid_to_value(self, list_id):
        try:
            return {
                lang.ListId.Rolls: self.rolls,
            }[list_id]
        except KeyError:
            raise NotImplementedError('Can\'t get list value for %s' % list_id)

    def _reduce_binop(self, bin_op):
        # print('Reducing:', bin_op)
        ii = isinstance
        left = self._reduce_binop(bin_op.left)\
            if ii(bin_op.left, lang.BinOp) else bin_op.left
        right = self._reduce_binop(bin_op.right)\
            if ii(bin_op.right, lang.BinOp) else bin_op.right
        left = self._varid_to_value(left)\
            if ii(left, lang.VarId) else left
        right = self._varid_to_value(right)\
            if ii(right, lang.VarId) else right
        left = left.get(self._listid_to_value(left.list_id))\
            if ii(left, lang.TailOp) else left
        right = right.get(self._listid_to_value(right.list_id))\
            if ii(right, lang.TailOp) else right
        left = left.value if ii(left, R) else left
        right = right.value if ii(right, R) else right
        # print('l/r', left, right)
        return {
            lang.BinOpId.Eq:    lambda l_, r_: l_  == r_,
            lang.BinOpId.Neq:   lambda l_, r_: l_  != r_,
            lang.BinOpId.Gt:    lambda l_, r_: l_   > r_,
            lang.BinOpId.Lt:    lambda l_, r_: l_   < r_,
            lang.BinOpId.Gteq:  lambda l_, r_: l_  >= r_,
            lang.BinOpId.Lteq:  lambda l_, r_: l_  <= r_,
            lang.BinOpId.And:   lambda l_, r_: l_ and r_,
            lang.BinOpId.Or:    lambda l_, r_: l_  or r_,
            lang.BinOpId.Plus:  lambda l_, r_: l_   + r_,
            lang.BinOpId.Minus: lambda l_, r_: l_   - r_,
            lang.BinOpId.Mult:  lambda l_, r_: l_   * r_,
            lang.BinOpId.Div:   lambda l_, r_: l_   / r_,
        }[bin_op.op](left, right)

    def make_bets(self):
        ii = isinstance
        user_vars = {}
        # make a copy of logic in reverse. Use this as a call stack of sorts
        stack = self._logic[::-1]
        while len(stack):
            # Get item off top of stack
            item = stack.pop()
            # Begin: determine what type it is, and act as necessary
            if ii(item, lang.MakeBetOp):
                # print('Making bet', item.bet)
                self.add_bet(item.bet)
            elif ii(item, lang.CondOp):
                if ii(item.cond, lang.BinOp):
                    res = self._reduce_binop(item.cond)
                else:
                    res = bool(item.cond)
                if res:
                    stack.append(item.true_case)
                else:
                    stack.append(item.false_case)
            elif ii(item, lang.AssignOp):
                if ii(item.expr, lang.BinOp):
                    res = self._reduce_binop(item.expr)
                else:
                    res = item.expr
                # print('Setting', item.var, 'to', res)
                user_vars[item.var] = item.expr
            elif ii(item, tuple):
                # reverse so first is on top of stack
                stack.extend(item[::-1])
            elif ii(item, (int, float)) or item is None:
                pass
            else:
                print('WARN IGNORING :::', type(item), item)
                raise NotImplementedError(
                    'Did not handle item type %s' % type(item).__name__)
            # End: determine what type it is


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
    weights = stats['dice']
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
    strat = make_new_strat()
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


def _init_bankroll_globals(semaphore_, weights_, num_rolls_, make_new_strat_):
    global semaphore, weights, num_rolls, make_new_strat
    semaphore = semaphore_
    weights = weights_
    num_rolls = num_rolls_
    make_new_strat = make_new_strat_


def bankroll_over_time_repeatedly(
        stats, make_new_strat, num_rolls, num_repeat):
    weights = _calc_die_weights(stats)
    chunk_size = 32
    cpu_count = mp.cpu_count()
    semaphore = mp.Semaphore(chunk_size * cpu_count)
    with mp.Pool(
            initializer=_init_bankroll_globals,
            initargs=(semaphore, weights, num_rolls, make_new_strat)) as pool:
        for res in pool.imap_unordered(f, range(num_repeat), chunk_size):
            yield res
            semaphore.release()


def do_bankroll(args, stats):
    count = 0
    strat_text = args.input_strategy.read()
    for res in bankroll_over_time_repeatedly(
            stats,
            lambda: UserDefinedStrategy.from_string(strat_text),
            args.rolls, args.repeat):
        json.dump(res, args.output)
        args.output.write('\n')
        count += 1
        if not count % 1000:
            log.debug(
                '%0.2f%% (%d/%d) done', 100*count/args.repeat, count,
                args.repeat)


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
        '--input-strategy', type=FileType('rt'), default='custom.strategy',
        help='File containing the code for your strategy')
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
