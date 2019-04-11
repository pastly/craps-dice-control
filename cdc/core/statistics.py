from ..lib.rollevent import RollEvent
from ..lib.statistics import Statistics

from argparse import ArgumentDefaultsHelpFormatter, FileType
import json
import logging
import sys

log = logging.getLogger(__name__)


def roll_events_from_input(fd):
    for line in fd:
        yield RollEvent.from_dict(json.loads(line))


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
    stats = Statistics.from_roll_events(roll_events_from_input(args.input))
    json.dump(stats.to_dict(), args.output)
    args.output.write('\n')
    return 0
