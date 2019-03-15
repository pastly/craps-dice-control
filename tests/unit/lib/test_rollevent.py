from cdc.lib.rollevent import RollEvent


def test_identity_craps():
    for dice in [(1, 1), (1, 2), (6, 6)]:
        ev = RollEvent('craps', dice, {})
        assert ev == RollEvent.from_dict(ev.to_dict())


def test_identity_natural():
    for dice in [(3, 4), (5, 6)]:
        ev = RollEvent('natural', dice, {})
        assert ev == RollEvent.from_dict(ev.to_dict())


def test_identity_roll():
    # all but 7
    for dice in [
            (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 6), (3, 6), (4, 6),
            (5, 6), (6, 6)]:
        ev = RollEvent('roll', dice, {})
        assert ev == RollEvent.from_dict(ev.to_dict())


def test_identity_point():
    for dice in [(1, 3), (1, 4), (1, 5), (2, 6), (3, 6), (4, 6)]:
        for true_arg in ['is_established', 'is_won', 'is_lost']:
            a = {
                'is_established': False, 'is_won': False, 'is_lost': False,
            }
            a[true_arg] = True
            ev = RollEvent('point', dice, a)
            assert ev == RollEvent.from_dict(ev.to_dict())
