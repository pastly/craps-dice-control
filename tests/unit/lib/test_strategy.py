from cdc.lib.strategy import Strategy, CrapsRoll as R,\
    CBPass, CBDontPass,\
    CGEBetWon, CGEBetLost,\
    CGEPointEstablished, CGEPointWon, CGEPointLost

import pytest


def get_strat(bankroll=0):
    return Strategy('', bankroll)


def test_strat_init():
    strat = Strategy('buffalo', 5126)
    assert strat.name == 'buffalo'
    assert strat.bankroll == 5126
    assert not len(strat.bets)
    assert not len(strat.rolls)


def test_strat_point_est():
    strat = get_strat()
    assert strat.point is None
    evs = strat.after_roll(R(3, 6))
    # point is now set
    assert strat.point == 9
    # check the event
    assert len(evs) == 1
    assert isinstance(evs[0], CGEPointEstablished)
    assert evs[0].point_value == 9


def test_strat_point_won():
    strat = get_strat()
    assert strat.point is None
    evs = strat.after_roll(R(3, 6))
    assert strat.point == 9
    assert len(evs) == 1
    assert isinstance(evs[0], CGEPointEstablished)
    assert evs[0].point_value == 9
    evs = strat.after_roll(R(4, 5))
    assert strat.point is None
    assert len(evs) == 1
    assert isinstance(evs[0], CGEPointWon)
    assert evs[0].point_value == 9


def test_strat_point_lost():
    strat = get_strat()
    assert strat.point is None
    evs = strat.after_roll(R(3, 6))
    assert strat.point == 9
    assert len(evs) == 1
    assert isinstance(evs[0], CGEPointEstablished)
    evs = strat.after_roll(R(2, 5))
    assert strat.point is None
    assert len(evs) == 1
    assert isinstance(evs[0], CGEPointLost)


def test_bet_on():
    # A working bet loses
    strat = get_strat()
    strat.add_bet(CBPass(5))
    assert len(strat.bets) == 1
    assert strat.bets[0].is_working
    strat.after_roll(R(1, 1))
    assert len(strat.bets) == 0


def test_bet_off():
    # A not working bet avoids losing
    strat = get_strat()
    strat.add_bet(CBPass(5))
    assert len(strat.bets) == 1
    strat.bets[0].set_working(False)
    assert not strat.bets[0].is_working
    strat.after_roll(R(1, 1))
    assert len(strat.bets) == 1


def test_pass_win():
    amount = 5
    starting_bankroll = 0
    for roll in {R(1, 6), R(5, 6)}:
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBPass(amount))
        evs = strat.after_roll(roll)
        # Should have a winning event
        assert len(evs) == 1
        assert isinstance(evs[0], CGEBetWon)
        assert evs[0].bet == CBPass(amount)
        # Pass bet should be removed
        assert not len(strat.bets)
        # Bankroll should be increased
        assert strat.bankroll == starting_bankroll + amount


def test_pass_lose():
    amount = 5
    starting_bankroll = 0
    for roll in {R(1, 1), R(1, 2), R(6, 6)}:
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBPass(amount))
        evs = strat.after_roll(roll)
        # Should have a losing event
        assert len(evs) == 1
        assert isinstance(evs[0], CGEBetLost)
        assert evs[0].bet == CBPass(amount)
        # Pass bet should be removed
        assert not len(strat.bets)
        # Bankroll should same
        assert strat.bankroll == starting_bankroll


def test_pass_nothing():
    amount = 5
    starting_bankroll = 0
    for roll in {R(i, j) for i in range(1, 6+1) for j in range(i, 6+1)}:
        if roll.value in {2, 3, 12, 7, 11}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBPass(amount))
        evs = strat.after_roll(roll)
        # Should not have won or lost, just established a point
        assert len(evs) == 1
        assert isinstance(evs[0], CGEPointEstablished)
        # Pass bet should still exist
        assert len(strat.bets) == 1
        # Bankroll should same
        assert strat.bankroll == starting_bankroll


@pytest.mark.skip("Need to add this test")
def test_pass_point_win():
    pass


@pytest.mark.skip("Need to add this test")
def test_pass_point_lose():
    pass


@pytest.mark.skip("Need to add this test")
def test_pass_point_nothing():
    pass


@pytest.mark.skip("Need to add this test")
def test_dpass_point_win():
    pass


@pytest.mark.skip("Need to add this test")
def test_dpass_point_lose():
    pass


@pytest.mark.skip("Need to add this test")
def test_dpass_point_nothing():
    pass


def test_dpass_win():
    amount = 5
    starting_bankroll = 0
    for roll in {R(1, 1), R(1, 2)}:
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBDontPass(amount))
        evs = strat.after_roll(roll)
        # Should have a winning event
        assert len(evs) == 1
        assert isinstance(evs[0], CGEBetWon)
        assert evs[0].bet == CBDontPass(amount)
        # Dont Pass bet should be removed
        assert not len(strat.bets)
        # Bankroll be up
        assert strat.bankroll == starting_bankroll + amount


def test_dpass_lose():
    amount = 5
    starting_bankroll = 0
    for roll in {R(3, 4), R(5, 6)}:
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBDontPass(amount))
        evs = strat.after_roll(roll)
        # Should have a losing event
        assert len(evs) == 1
        assert isinstance(evs[0], CGEBetLost)
        assert evs[0].bet == CBDontPass(amount)
        # Dont Pass bet should be removed
        assert not len(strat.bets)
        # Bankroll be same
        assert strat.bankroll == starting_bankroll


def test_dpass_nothing():
    amount = 5
    starting_bankroll = 0
    for roll in {R(i, j) for i in range(1, 6+1) for j in range(i, 6+1)}:
        if roll.value in {2, 3, 7, 11}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBDontPass(amount))
        evs = strat.after_roll(roll)
        # Should not have won or lost, just established a point or nothing
        assert len(evs) <= 1
        if len(evs):
            assert isinstance(evs[0], CGEPointEstablished)
        # Dont Pass bet should still exist
        assert len(strat.bets) == 1
        # Bankroll be same
        assert strat.bankroll == starting_bankroll
