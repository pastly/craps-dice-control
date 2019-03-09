from . import rollseries

from argparse import ArgumentDefaultsHelpFormatter


def gen_parser(sub):
    d = 'From either stdin or the given file, read in data in some format, '\
        'convert it in some way, and output it to stdout or the given file'
    p = sub.add_parser(
        'parse', description=d,
        formatter_class=ArgumentDefaultsHelpFormatter)
    sub = p.add_subparsers(dest='parse_command', required=True)
    rollseries.gen_parser(sub)
    return p


def main(args, conf):
    def_args = [args, conf]
    def_kwargs = {}
    known_commands = {
        'rollseries': {'f': rollseries.main, 'a': def_args, 'kw': def_kwargs},
    }
    assert args.parse_command in known_commands
    c = known_commands[args.parse_command]
    return c['f'](*c['a'], **c['kw'])
