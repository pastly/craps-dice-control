from .util import rand
from .util import config
from .core import parse
from .core import plot
from .core import simulate
from .core import statistics
from cdc import __version__

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
import logging.config

log = logging.getLogger(__name__)


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
    sub = p.add_subparsers(dest='command', required=True)
    parse.gen_parser(sub)
    plot.gen_parser(sub)
    simulate.gen_parser(sub)
    statistics.gen_parser(sub)
    return p


def main():
    p = create_arg_parser()
    args = p.parse_args()
    conf = config.get_config(args)
    config.configure_logging(args, conf)
    def_args = [args, conf]
    def_kwargs = {}
    known_commands = {
        'parse': {'f': parse.main, 'a': def_args, 'kw': def_kwargs},
        'plot': {'f': plot.main, 'a': def_args, 'kw': def_kwargs},
        'simulate': {'f': simulate.main, 'a': def_args, 'kw': def_kwargs},
        'statistics': {'f': statistics.main, 'a': def_args, 'kw': def_kwargs},
    }
    if args.command not in known_commands:
        p.print_help()
        return
    rand.init(args.seed)
    c = known_commands[args.command]
    exit(c['f'](*c['a'], **c['kw']))
