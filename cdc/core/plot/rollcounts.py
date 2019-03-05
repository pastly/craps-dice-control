from ...util.json import NumericKeyDecoder

from argparse import ArgumentDefaultsHelpFormatter, FileType
import json
import logging

import matplotlib
matplotlib.use('Agg')
import pylab as plt  # noqa

plt.rcParams.update({
    'axes.grid': True,
    'savefig.format': 'png',
})
log = logging.getLogger(__name__)


def read_input(fd):
    return json.load(fd, cls=NumericKeyDecoder)


def validate_input_data(data):
    ''' Returns list of error strings if issues, otherwise None '''
    err = []
    for dset in data:
        for i in range(2, 12+1):
            val = dset['counts'][i]
            if val < 0:
                err.append(
                    'Count for %d cannot be negative (%d)' % (i, val))
        for i in [4, 6, 8, 10]:
            val = dset['counts'][i]
            hard_val = dset['counts_hard'][i]
            if hard_val < 0:
                err.append(
                    'Hard count for %d cannot be negative (%d)' %
                    (i, hard_val))
            if hard_val > val:
                err.append(
                    'Hard count cannot be greater than count for %d '
                    '(%d > %d)' % (i, hard_val, val))
    return err if len(err) else None


def plot(out_fd, data):
    colors = "krbgcmy"
    color_idx = 0
    ymax = 0
    for dset in data:
        label = dset['label']
        counts = dset['counts']
        num_rolls = sum(counts[i] for i in counts)
        points = []
        for i in range(2, 12+1):
            y = counts[i]/num_rolls
            if y > ymax:
                ymax = y
            points.append((i, y))
        xs, ys = zip(*points)
        plt.plot(xs, ys, label=label, c=colors[color_idx])
        color_idx += 1
    ymax = round(ymax*1.1, 2)
    plt.legend(loc='best')
    plt.xlim(left=2, right=12)
    plt.ylim(bottom=0, top=ymax)
    plt.xlabel('Roll')
    plt.ylabel('Probability (fraction of 1)')
    plt.title('Roll Probability Density Function')
    plt.savefig(out_fd)


def gen_parser(sub):
    d = 'Plot Probability Density Function of roll counts'
    p = sub.add_parser(
        'rollcounts', description=d,
        formatter_class=ArgumentDefaultsHelpFormatter)
    p.add_argument(
        '-i', '--input', type=FileType('rt'), default='/dev/stdin',
        help='From where to read json-formatted data')
    p.add_argument(
        '-o', '--output', type=FileType('wb'), default='/dev/stdout',
        help='File to which to write graph')
    return p


def main(args, conf):
    data = read_input(args.input)
    errs = validate_input_data(data)
    if errs is not None:
        for err in errs:
            log.error(err)
        return 1
    log.warn('We do not currently support plotting anything about hard ways')
    plot(args.output, data)
    return 0
