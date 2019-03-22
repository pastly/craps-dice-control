from . import pdf
from . import medrange

from argparse import ArgumentDefaultsHelpFormatter


def gen_parser(sub):
    d = 'From either stdin or the given file, read some json-formatted data '\
        'to plot'
    p = sub.add_parser(
        'plot', description=d,
        formatter_class=ArgumentDefaultsHelpFormatter)
    sub = p.add_subparsers(dest='plot_command', required=True)
    pdf.gen_parser(sub)
    medrange.gen_parser(sub)
    return p


def main(args, conf):
    def_args = [args, conf]
    def_kwargs = {}
    known_commands = {
        'pdf': {'f': pdf.main, 'a': def_args, 'kw': def_kwargs},
        'medrange': {'f': medrange.main, 'a': def_args, 'kw': def_kwargs},
    }
    assert args.plot_command in known_commands
    c = known_commands[args.plot_command]
    return c['f'](*c['a'], **c['kw'])
