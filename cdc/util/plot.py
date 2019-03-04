import matplotlib
matplotlib.use('Agg')
import pylab as plt

plt.rcParams.update({
    'axes.grid': True,
    'savefig.format': 'png',
})


def xy(
        out_file, *input_data_sets,
        xmin=None, xmax=None, ymin=None, ymax=None,
        x=None, y=None, title=None):
    colors = "krbgcmy"
    color_idx = 0
    min_x, max_x = None, None
    min_y, max_y = None, None
    for label, points in input_data_sets:
        xs, ys = zip(*points)
        if min_x is not None:
            min_x, max_x = min(min_x, *xs), max(max_x, *xs)
            min_y, max_y = min(min_y, *ys), max(max_y, *ys)
        else:
            min_x, max_x = min(*xs), max(*xs)
            min_y, max_y = min(*ys), max(*ys)
        plt.plot(xs, ys, label=label, c=colors[color_idx])
        color_idx += 1
    plt.xlim(
        left=min_x if xmin is None else xmin,
        right=max_x if xmax is None else xmax)
    plt.ylim(
        bottom=min_y if ymin is None else ymin,
        top=max_y if ymax is None else ymax)
    if x:
        plt.xlabel(x)
    if y:
        plt.ylabel(y)
    if title:
        plt.title(title)
    plt.legend(loc='best')
    plt.savefig(out_file)
