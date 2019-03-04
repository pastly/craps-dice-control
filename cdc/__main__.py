from .util import rand
from .util import config
from .core import simulate
from cdc import __version__

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
import logging.config

from scipy.stats import chisquare

FAIR_DIST = [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]
log = logging.getLogger(__name__)


def output(fname, counts, cdf=False):
    log.info('Writing counts to %s', fname)
    acc = 0
    with open(fname, 'wt') as fd:
        for i in range(2, 12+1):
            acc += counts[i]
            x, y = i, acc if cdf else counts[i]
            print(x, y, file=fd)


def normalize_counts(counts):
    total = sum(counts[i] for i in counts)
    out = {}
    for i in counts:
        out[i] = counts[i] / total
    return out


def log_stuff(observed_counts, expected_counts, ddof=0):
    obs = []
    exp = []
    for i in range(2, 12+1):
        obs.append(observed_counts[i])
        exp.append(expected_counts[i])
    chisq, p = chisquare(exp, obs, ddof=ddof)
    log.debug("chisq=%0.2f p=%0.5f", chisq, p)


def _main2(args):
    assert args.normalize
    # rand.init(2)
    counts = {}
    for i in range(2, 12+1):
        counts[i] = 0
    for _ in range(args.iterations):
        out = rand.roll_dice_with_weights([
            1, 2, 3, 4, 5, 5, 5, 4, 3, 2, 1
        ])
        counts[out] += 1
    for i in counts:
        if counts[i] < 5:
            log.error(
                "All values must be rolled at least 5 times. "
                "%d was rolled %d times", i, counts[i])
            return
    expected = [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]
    sum_expected = sum(expected)
    expected = [i/sum_expected*args.iterations for i in expected]
    actual = [counts[i] for i in range(2, 12+1)]
    for i, ea in enumerate(zip(expected, actual)):
        log.debug('%d: %0.2f\t%0.2f', i+2, ea[0], ea[1])
    chisq, p = chisquare(expected, actual)
    log.debug("chisq=%0.2f p=%0.5f", chisq, p)
    log.info(
        "You rolled significantly different than would be expected from a "
        "random roller" if p < 0.05 else
        "You did not roll significantly different than a random roller")


def create_arg_parser():
    p = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument(
        '--seed', type=int,
        help='Seed the RNG with this value for reproducible results')
    p.add_argument(
        '--log-level', type=str, default='info',
        choices=('debug', 'info', 'warn', 'error'),
        help='Set the log level')
    p.add_argument(
        '-v', '--version', action='version', version=__version__)
    sub = p.add_subparsers(dest='command')
    simulate.gen_parser(sub)
    return p


def main():
    p = create_arg_parser()
    args = p.parse_args()
    conf = config.get_config(args)
    config.configure_logging(args, conf)
    def_args = [args, conf]
    def_kwargs = {}
    known_commands = {
        'simulate': {'f': simulate.main, 'a': def_args, 'kw': def_kwargs},
    }
    if args.command not in known_commands:
        p.print_help()
        return
    rand.init(args.seed)
    c = known_commands[args.command]
    exit(c['f'](*c['a'], **c['kw']))
