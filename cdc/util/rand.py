import bisect
import itertools
import logging
import random

log = logging.getLogger(__name__)


def init(seed):
    random.seed(seed)


def _weighted_select(outcomes, weights):
    # https://docs.python.org/3.5/library/random.html#examples-and-recipes
    assert len(weights) == len(outcomes)
    cumdist = list(itertools.accumulate(weights))
    idx = random.random() * cumdist[-1]
    return outcomes[bisect.bisect(cumdist, idx)]


def roll_die_with_weights(weights):
    assert len(weights) == 6
    sides = [1, 2, 3, 4, 5, 6]
    return _weighted_select(sides, weights)


def roll_fair_die():
    return roll_die_with_weights([1, 1, 1, 1, 1, 1])


def roll_dice_with_weights(weights):
    assert len(weights) == 11
    outcomes = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    return _weighted_select(outcomes, weights)


def roll_fair_dice():
    return roll_dice_with_weights([1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1])
