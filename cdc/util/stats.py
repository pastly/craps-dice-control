from . import rand
from .. import globals as G


def simulate_roll_distribution(num_rolls, dist=None):
    if dist is None:
        dist = G.FAIR_DIST
    assert len(dist) == 11
    counts = {}
    for i in range(2, 12+1):
        counts[i] = 0
    for _ in range(num_rolls):
        out = rand.roll_dice_with_weights(dist)
        counts[out] += 1
    return counts


def theoretical_fair_distribution(num_rolls):
    s = sum(G.FAIR_DIST)
    counts = {}
    for i, c in enumerate(G.FAIR_DIST):
        counts[i+2] = c*num_rolls/s
    return counts
