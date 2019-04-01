from cdc.lib.strategy import Strategy, CrapsRoll as R,\
    CBPass, CBDontPass, CBField, CBPlace, CBCome, CBDontCome, CBOdds,\
    CBHardWay,\
    CGEWithBets, CGEBetWon, CGEBetLost, CGEBetPush, CGEBetConverted,\
    CGEPoint, CGEPointEstablished, CGEPointWon, CGEPointLost,\
    MartingaleFieldStrategy, BasicPassStrategy, BasicComeStrategy,\
    BasicPlaceStrategy,\
    IllegalBet, IllegalBetChange

import pytest


def get_strat(bankroll=0):
    return Strategy('', bankroll)


def all_dice_combos():
    for roll in {R(i, j) for i in range(1, 6+1) for j in range(1, 6+1)}:
        yield roll


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
    assert evs[0].point == 9


def test_strat_point_won():
    strat = get_strat()
    assert strat.point is None
    evs = strat.after_roll(R(3, 6))
    assert strat.point == 9
    assert len(evs) == 1
    assert isinstance(evs[0], CGEPointEstablished)
    assert evs[0].point == 9
    evs = strat.after_roll(R(4, 5))
    assert strat.point is None
    assert len(evs) == 1
    assert isinstance(evs[0], CGEPointWon)
    assert evs[0].point == 9


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
    strat.add_bet(CBPlace(4, 25))
    assert len(strat.bets) == 1
    strat.bets[0].set_working(False)
    assert not strat.bets[0].is_working
    strat.after_roll(R(3, 4))
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
        assert strat.bankroll == starting_bankroll - amount


def test_pass_nothing():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
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
        assert strat.bankroll == starting_bankroll - amount


def test_pass_point_win():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBPass(amount))
        evs = strat.after_roll(roll)
        # should establish point
        assert len(evs) == 1
        assert isinstance(evs[0], CGEPointEstablished)
        # Pass bet should still exist
        assert len(strat.bets) == 1
        # point should be set
        assert strat.point == roll.value
        evs = strat.after_roll(roll)
        # should win point
        assert len(evs) == 2
        assert len([e for e in evs if isinstance(e, CGEPointWon)]) == 1
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 1
        # point should be none
        assert strat.point is None
        # bankroll should increase
        assert strat.bankroll == starting_bankroll + amount
        # bet should be gone
        assert not len(strat.bets)


def test_pass_point_lose():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBPass(amount))
        evs = strat.after_roll(roll)
        # should establish point
        assert len(evs) == 1
        assert isinstance(evs[0], CGEPointEstablished)
        # Pass bet should still exist
        assert len(strat.bets) == 1
        # point should be set
        assert strat.point == roll.value
        # roll a 7
        evs = strat.after_roll(R(1, 6))
        # should lose point
        assert len(evs) == 2
        assert len([e for e in evs if isinstance(e, CGEPointLost)]) == 1
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        # point should be none
        assert strat.point is None
        assert strat.bankroll == starting_bankroll - amount
        # bet should be gone
        assert not len(strat.bets)


def test_pass_point_nothing():
    amount = 5
    starting_bankroll = 0
    for first_roll in all_dice_combos():
        if first_roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBPass(amount))
        evs = strat.after_roll(first_roll)
        # should establish point
        assert len(evs) == 1
        assert isinstance(evs[0], CGEPointEstablished)
        # Pass bet should still exist
        assert len(strat.bets) == 1
        # point should be set
        assert strat.point == first_roll.value
        # roll all possibilites that aren't the point value (which would cause
        # a win) or 7 (which would cause a lose)
        for second_roll in all_dice_combos():
            if first_roll.value == second_roll.value:
                continue
            if second_roll.value == 7:
                continue
            evs = strat.after_roll(second_roll)
            # nothing should happen
            assert len(evs) == 0
            # point should be same
            assert strat.point is first_roll.value
            assert strat.bankroll == starting_bankroll - amount
            # bet should stay
            assert len(strat.bets) == 1


def test_dpass_point_win():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBDontPass(amount))
        evs = strat.after_roll(roll)
        # should establish point
        assert len(evs) == 1
        assert isinstance(evs[0], CGEPointEstablished)
        # DontPass bet should still exist
        assert len(strat.bets) == 1
        # point should be set
        assert strat.point == roll.value
        # roll a 7
        evs = strat.after_roll(R(1, 6))
        # should win point
        assert len(evs) == 2
        assert len([e for e in evs if isinstance(e, CGEPointLost)]) == 1
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 1
        # point should be none
        assert strat.point is None
        # bankroll should increase
        assert strat.bankroll == starting_bankroll + amount
        # bet should be gone
        assert not len(strat.bets)


def test_dpass_point_lose():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBDontPass(amount))
        evs = strat.after_roll(roll)
        # should establish point
        assert len(evs) == 1
        assert isinstance(evs[0], CGEPointEstablished)
        # DontPass bet should still exist
        assert len(strat.bets) == 1
        # point should be set
        assert strat.point == roll.value
        # roll the point
        evs = strat.after_roll(roll)
        # should lose point
        assert len(evs) == 2
        assert len([e for e in evs if isinstance(e, CGEPointWon)]) == 1
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        # point should be none
        assert strat.point is None
        assert strat.bankroll == starting_bankroll - amount
        # bet should be gone
        assert not len(strat.bets)


def test_dpass_point_nothing():
    amount = 5
    starting_bankroll = 0
    for first_roll in all_dice_combos():
        if first_roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBDontPass(amount))
        evs = strat.after_roll(first_roll)
        # should establish point
        assert len(evs) == 1
        assert isinstance(evs[0], CGEPointEstablished)
        # DontPass bet should still exist
        assert len(strat.bets) == 1
        # point should be set
        assert strat.point == first_roll.value
        # roll all possibilites that aren't the point value (which would cause
        # a lose) or 7 (which would cause a win)
        for second_roll in all_dice_combos():
            if first_roll.value == second_roll.value:
                continue
            if second_roll.value == 7:
                continue
            evs = strat.after_roll(second_roll)
            # nothing should happen
            assert len(evs) == 0
            # point should be same
            assert strat.point is first_roll.value
            assert strat.bankroll == starting_bankroll - amount
            # bet should stay
            assert len(strat.bets) == 1


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
        assert strat.bankroll == starting_bankroll - amount


def test_dpass_nothing():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 7, 11, 12}:
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
        assert strat.bankroll == starting_bankroll - amount


def test_dpass_push():
    amount = 5
    starting_bankroll = 0
    strat = get_strat(starting_bankroll)
    strat.add_bet(CBDontPass(amount))
    evs = strat.after_roll(R(6, 6))
    assert len(evs) == 1
    assert isinstance(evs[0], CGEBetPush)
    assert not len(strat.bets)
    assert strat.bankroll == starting_bankroll


def test_field_win():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value not in {3, 4, 9, 10, 11}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBField(amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll + amount
    for roll in {R(1, 1), R(6, 6)}:
        for mult in {2, 3}:
            strat = get_strat(starting_bankroll)
            strat.add_bet(CBField(amount, mult2=mult, mult12=mult))
            evs = strat.after_roll(roll)
            assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 1
            assert not len(strat.bets)
            assert strat.bankroll == starting_bankroll + amount * mult


def test_field_lose():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value not in {5, 6, 7, 8}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBField(amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll - amount


def test_place_win():
    amount = 30
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBPlace(roll.value, amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 1
        assert not len(strat.bets)
        if roll.value in {4, 10}:
            expected = amount * 9 / 5
        elif roll.value in {5, 9}:
            expected = amount * 7 / 5
        else:
            expected = amount * 7 / 6
        assert strat.bankroll == starting_bankroll + expected


def test_place_lost():
    amount = 30
    starting_bankroll = 0
    for roll_value in {4, 5, 6, 8, 9, 10}:
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBPlace(roll_value, amount))
        evs = strat.after_roll(R(1, 6))
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll - amount


def test_place_nothing():
    amount = 30
    starting_bankroll = 0
    for value in {4, 5, 6, 8, 9, 10}:
        for roll in all_dice_combos():
            if roll.value == 7 or roll.value == value:
                continue
            strat = get_strat(starting_bankroll)
            strat.add_bet(CBPlace(value, amount))
            evs = strat.after_roll(roll)
            assert len(strat.bets) == 1
            assert not len([e for e in evs if isinstance(e, CGEBetWon)])
            assert not len([e for e in evs if isinstance(e, CGEBetLost)])
            assert strat.bankroll == starting_bankroll - amount


def test_place_properties():
    amount = 5
    for value in {4, 5, 6, 8, 9, 10}:
        bet = CBPlace(value, amount)
        assert bet.value == value
        assert bet.is_working
        assert bet.amount == amount
        if bet.value in {4, 10}:
            assert bet.win_amount() == amount * 9 / 5
        elif bet.value in {5, 9}:
            assert bet.win_amount() == amount * 7 / 5
        else:
            assert bet.win_amount() == amount * 7 / 6
        bet.set_working(False)
        assert not bet.is_working


def test_come_win():
    amount = 5
    starting_bankroll = 0
    for roll in {R(3, 4), R(5, 6)}:
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(R(2, 2))
        strat.add_bet(CBCome(amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll + amount


def test_come_lose():
    amount = 5
    starting_bankroll = 0
    for roll in {R(1, 1), R(1, 2), R(6, 6)}:
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(R(2, 2))
        strat.add_bet(CBCome(amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll - amount


def test_come_convert():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(R(2, 2))
        strat.add_bet(CBCome(amount))
        assert strat.bets[0].point is None
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        assert evs[0].from_bet.point is None
        assert evs[0].to_bet.point == roll.value
        assert len(strat.bets) == 1
        assert strat.bets[0].point == roll.value
        assert strat.bankroll == starting_bankroll - amount


def test_come_point_win():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(R(2, 2))
        strat.add_bet(CBCome(amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll + amount


def test_come_point_lose():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(R(2, 2))
        strat.add_bet(CBCome(amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        evs = strat.after_roll(R(3, 4))
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll - amount


def test_come_point_nothing():
    amount = 5
    starting_bankroll = 0
    for first_roll in all_dice_combos():
        if first_roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(R(2, 2))
        strat.add_bet(CBCome(amount))
        evs = strat.after_roll(first_roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        for second_roll in all_dice_combos():
            if second_roll.value in {first_roll.value, 7}:
                continue
            evs = strat.after_roll(second_roll)
            assert len(evs) <= 1
            if len(evs) == 1:
                assert isinstance(evs[0], CGEPoint)
                # assert isinstance(evs[0], CGEPointWon) \
                #     or isinstance(evs[0], CGEPointEstablished)
            assert len(strat.bets) == 1
            assert strat.bankroll == starting_bankroll - amount


def test_dcome_win():
    amount = 5
    starting_bankroll = 0
    for roll in {R(1, 1), R(1, 2)}:
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(R(2, 2))
        strat.add_bet(CBDontCome(amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll + amount


def test_dcome_lose():
    amount = 5
    starting_bankroll = 0
    for roll in {R(3, 4), R(5, 6)}:
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(R(2, 2))
        strat.add_bet(CBDontCome(amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll - amount


def test_dcome_convert():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(R(2, 2))
        strat.add_bet(CBDontCome(amount))
        assert strat.bets[0].point is None
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        assert evs[0].from_bet.point is None
        assert evs[0].to_bet.point == roll.value
        assert len(strat.bets) == 1
        assert strat.bets[0].point == roll.value
        assert strat.bankroll == starting_bankroll - amount


def test_dcome_point_win():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(R(2, 2))
        strat.add_bet(CBDontCome(amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        evs = strat.after_roll(R(3, 4))
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll + amount


def test_dcome_point_lose():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(R(2, 2))
        strat.add_bet(CBDontCome(amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll - amount


def test_dcome_point_nothing():
    amount = 5
    starting_bankroll = 0
    for first_roll in all_dice_combos():
        if first_roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(R(2, 2))
        strat.add_bet(CBDontCome(amount))
        evs = strat.after_roll(first_roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        for second_roll in all_dice_combos():
            if second_roll.value in {first_roll.value, 7}:
                continue
            evs = strat.after_roll(second_roll)
            assert len(evs) <= 1
            if len(evs) == 1:
                assert isinstance(evs[0], CGEPoint)
            assert len(strat.bets) == 1
            assert strat.bankroll == starting_bankroll - amount


def test_dcome_push():
    amount = 5
    starting_bankroll = 0
    strat = get_strat(starting_bankroll)
    strat.after_roll(R(2, 2))
    assert strat.point == 4
    strat.add_bet(CBDontCome(amount))
    assert strat.bankroll == starting_bankroll - amount
    evs = strat.after_roll(R(6, 6))
    assert len(evs) == 1
    assert isinstance(evs[0], CGEBetPush)
    assert not len(strat.bets)
    assert strat.bankroll == starting_bankroll


def test_odds_win():
    flat_amount = 5
    amount = 10
    starting_bankroll = 0
    # Pass odds
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBPass(flat_amount))
        # set point
        strat.after_roll(roll)
        assert strat.point == roll.value
        # make odds bet
        strat.add_bet(CBOdds(roll.value, False, amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 2
        assert not len(strat.bets)
        if roll.value in {4, 10}:
            expected = starting_bankroll + flat_amount + amount * 2 / 1
        elif roll.value in {5, 9}:
            expected = starting_bankroll + flat_amount + amount * 3 / 2
        else:
            expected = starting_bankroll + flat_amount + amount * 6 / 5
        assert strat.bankroll == expected
    # Come odds
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        # Set a point so come bets are legal
        strat.after_roll(R(2, 3 if roll.value != 5 else 2))
        assert strat.point is not None
        # Make that flat bet
        strat.add_bet(CBCome(flat_amount))
        # And set its point so a come odds bet is legal
        strat.after_roll(roll)
        # Hack to make sure its point is set
        assert sum([b.point for b in strat.bets if isinstance(b, CBCome)]) \
            == roll.value
        # Finally add the odds bet
        strat.add_bet(CBOdds(roll.value, False, amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 2
        assert not len(strat.bets)
        if roll.value in {4, 10}:
            expected = starting_bankroll + flat_amount + amount * 2 / 1
        elif roll.value in {5, 9}:
            expected = starting_bankroll + flat_amount + amount * 3 / 2
        else:
            expected = starting_bankroll + flat_amount + amount * 6 / 5
        assert strat.bankroll == expected


def test_odds_lose():
    flat_amount = 5
    amount = 10
    starting_bankroll = 0
    # Pass odds
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBPass(flat_amount))
        # set point
        strat.after_roll(roll)
        assert strat.point == roll.value
        # make odds bet
        strat.add_bet(CBOdds(roll.value, False, amount))
        evs = strat.after_roll(R(3, 4))
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 2
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll - flat_amount - amount
    # Come odds
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        # Set a point so come bets are legal
        strat.after_roll(R(2, 3 if roll.value != 5 else 2))
        assert strat.point is not None
        # Make that flat bet
        strat.add_bet(CBCome(flat_amount))
        # And set its point so a come odds bet is legal
        strat.after_roll(roll)
        # Hack to make sure its point is set
        assert sum([b.point for b in strat.bets if isinstance(b, CBCome)]) \
            == roll.value
        # Finally add the odds bet
        strat.add_bet(CBOdds(roll.value, False, amount))
        evs = strat.after_roll(R(3, 4))
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 2
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll - flat_amount - amount


def test_odds_nothing():
    flat_amount = 5
    amount = 10
    starting_bankroll = 0
    for first_roll in {R(1, 3), R(1, 4), R(1, 5), R(2, 6), R(3, 6), R(4, 6)}:
        for second_roll in all_dice_combos():
            if second_roll.value in {first_roll.value, 7}:
                continue
            strat = get_strat(starting_bankroll)
            # Make flat bet
            strat.add_bet(CBPass(flat_amount))
            # Establish point so pass odds are legal
            strat.after_roll(first_roll)
            # Make odds bet
            strat.add_bet(CBOdds(first_roll.value, False, amount))
            evs = strat.after_roll(second_roll)
            assert not len([e for e in evs if isinstance(e, CGEBetWon)])
            assert not len([e for e in evs if isinstance(e, CGEBetLost)])
            assert len(strat.bets) == 2
            assert strat.bankroll == starting_bankroll - flat_amount - amount


def test_odds_push():
    flat_amount = 5
    amount = 10
    starting_bankroll = 0
    for come_point in {4, 5, 6, 8, 9, 10}:
        come_roll = R(
            int(come_point / 2),
            int(come_point / 2) + come_point % 2)
        pass_point = 4 if come_point != 4 else 5
        pass_roll = R(2, 2 if pass_point == 4 else 3)
        strat = get_strat(starting_bankroll)
        # set a point so come bets are legal
        strat.after_roll(pass_roll)
        assert strat.point is pass_point
        # make a come bet and make it travel to its point
        strat.add_bet(CBCome(flat_amount))
        strat.after_roll(come_roll)
        # Make the come odds bet
        strat.add_bet(CBOdds(come_point, False, amount))
        assert len(strat.bets) == 2
        # Win the pass line point (no bet on it, just so puck goes off)
        strat.after_roll(pass_roll)
        assert strat.point is None
        # Come odds should still be working (because that's how it's coded. It
        # isn't like real life where dealers will turn them off by default) so
        # we need to turn them off
        assert len(strat.bets) == 2
        for bet in [b for b in strat.bets if isinstance(b, CBOdds)]:
            assert bet.is_working
            bet.set_working(False)
        # Hack to assure the bet is off
        assert len([b for b in strat.bets if isinstance(b, CBOdds)]) == 1
        assert not sum(
            int(b.is_working) for b in strat.bets if isinstance(b, CBOdds))
        # Roll 7 on come out roll. Come will lose, Come Odds will push
        evs = strat.after_roll(R(3, 4))
        assert len([e for e in evs if isinstance(e, CGEBetPush)]) == 1
        assert not len(strat.bets)
        # Should be down just the flat amount. AKA should get the odds back in
        # our bankroll
        assert strat.bankroll == starting_bankroll - flat_amount


def test_dodds_win():
    flat_amount = 5
    amount = 30
    starting_bankroll = 0
    # Don't Pass odds
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBDontPass(flat_amount))
        # set point
        strat.after_roll(roll)
        assert strat.point == roll.value
        # make odds bet
        strat.add_bet(CBOdds(roll.value, True, amount))
        evs = strat.after_roll(R(3, 4))
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 2
        assert not len(strat.bets)
        if roll.value in {4, 10}:
            expected = starting_bankroll + flat_amount + amount * 1 / 2
        elif roll.value in {5, 9}:
            expected = starting_bankroll + flat_amount + amount * 2 / 3
        else:
            expected = starting_bankroll + flat_amount + amount * 5 / 6
        assert strat.bankroll == expected
    # Don't Come odds
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        # Set a point so come bets are legal
        strat.after_roll(R(2, 3 if roll.value != 5 else 2))
        assert strat.point is not None
        # Make that flat bet
        strat.add_bet(CBDontCome(flat_amount))
        # And set its point so a come odds bet is legal
        strat.after_roll(roll)
        # Hack to make sure its point is set
        assert sum([b.point for b in strat.bets
                    if isinstance(b, CBDontCome)]) == roll.value
        # Finally add the odds bet
        strat.add_bet(CBOdds(roll.value, True, amount))
        evs = strat.after_roll(R(3, 4))
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 2
        assert not len(strat.bets)
        if roll.value in {4, 10}:
            expected = starting_bankroll + flat_amount + amount * 1 / 2
        elif roll.value in {5, 9}:
            expected = starting_bankroll + flat_amount + amount * 2 / 3
        else:
            expected = starting_bankroll + flat_amount + amount * 5 / 6
        assert strat.bankroll == expected


def test_dodds_lose():
    flat_amount = 5
    amount = 10
    starting_bankroll = 0
    # Pass odds
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBDontPass(flat_amount))
        # set point
        strat.after_roll(roll)
        assert strat.point == roll.value
        # make odds bet
        strat.add_bet(CBOdds(roll.value, True, amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 2
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll - flat_amount - amount
    # Come odds
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        # Set a point so come bets are legal
        strat.after_roll(R(2, 3 if roll.value != 5 else 2))
        assert strat.point is not None
        # Make that flat bet
        strat.add_bet(CBDontCome(flat_amount))
        # And set its point so a come odds bet is legal
        strat.after_roll(roll)
        # Hack to make sure its point is set
        assert sum([b.point for b in strat.bets
                    if isinstance(b, CBDontCome)]) == roll.value
        # Finally add the odds bet
        strat.add_bet(CBOdds(roll.value, True, amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 2
        assert not len(strat.bets)
        assert strat.bankroll == starting_bankroll - flat_amount - amount


def test_dodds_nothing():
    flat_amount = 5
    amount = 10
    starting_bankroll = 0
    for first_roll in {R(1, 3), R(1, 4), R(1, 5), R(2, 6), R(3, 6), R(4, 6)}:
        for second_roll in all_dice_combos():
            if second_roll.value in {first_roll.value, 7}:
                continue
            strat = get_strat(starting_bankroll)
            # Make flat bet
            strat.add_bet(CBDontPass(flat_amount))
            # Establish point so pass odds are legal
            strat.after_roll(first_roll)
            # Make odds bet
            strat.add_bet(CBOdds(first_roll.value, True, amount))
            evs = strat.after_roll(second_roll)
            assert not len([e for e in evs if isinstance(e, CGEBetWon)])
            assert not len([e for e in evs if isinstance(e, CGEBetLost)])
            assert len(strat.bets) == 2
            assert strat.bankroll == starting_bankroll - flat_amount - amount


def test_dodds_push():
    flat_amount = 5
    amount = 10
    starting_bankroll = 0
    for dcome_point in {4, 5, 6, 8, 9, 10}:
        dcome_roll = R(
            int(dcome_point / 2),
            int(dcome_point / 2) + dcome_point % 2)
        pass_point = 4 if dcome_point != 4 else 5
        pass_roll = R(2, 2 if pass_point == 4 else 3)
        strat = get_strat(starting_bankroll)
        # set a point so dcome bets are legal
        strat.after_roll(pass_roll)
        assert strat.point is pass_point
        # make a dcome bet and make it travel to its point
        strat.add_bet(CBDontCome(flat_amount))
        strat.after_roll(dcome_roll)
        # Make the dcome odds bet
        strat.add_bet(CBOdds(dcome_point, True, amount))
        assert len(strat.bets) == 2
        # Win the pass line point (no bet on it, just so puck goes off)
        strat.after_roll(pass_roll)
        assert strat.point is None
        # Dont Come odds should still be working (because that's how it's
        # coded. It isn't like real life where dealers will turn them off by
        # default) so we need to turn them off
        assert len(strat.bets) == 2
        for bet in [b for b in strat.bets if isinstance(b, CBOdds)]:
            assert bet.is_working
            bet.set_working(False)
        # Hack to assure the bet is off
        assert len([b for b in strat.bets if isinstance(b, CBOdds)]) == 1
        assert not sum(
            int(b.is_working) for b in strat.bets if isinstance(b, CBOdds))
        # Roll the Don't Come's point on come out roll. Don't Come will lose,
        # Don't Come Odds will push
        evs = strat.after_roll(dcome_roll)
        assert len([e for e in evs if isinstance(e, CGEBetPush)]) == 1
        assert not len(strat.bets)
        # Should be down just the flat amount. AKA should get the odds back in
        # our bankroll
        assert strat.bankroll == starting_bankroll - flat_amount


def test_hardways_win():
    amount = 1
    starting_bankroll = 0
    for roll in {R(2, 2), R(3, 3), R(4, 4), R(5, 5)}:
        expected_bankroll = starting_bankroll + \
            7 if roll.value in {4, 10} else 9
        strat = get_strat(starting_bankroll)
        bet = CBHardWay(roll.value, amount)
        strat.add_bet(bet)
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == expected_bankroll


def test_hardways_lose():
    amount = 1
    starting_bankroll = 0
    for bet_value in {4, 6, 8, 10}:
        for roll in all_dice_combos():
            if roll.value not in {bet_value, 7}:
                continue
            if roll.dice[0] == roll.dice[1]:
                continue
            strat = get_strat(starting_bankroll)
            bet = CBHardWay(bet_value, amount)
            strat.add_bet(bet)
            evs = strat.after_roll(roll)
            assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
            assert not len(strat.bets)
            assert strat.bankroll == starting_bankroll - amount


def test_hardways_nothing():
    amount = 1
    starting_bankroll = 0
    for bet_value in {4, 6, 8, 10}:
        for roll in all_dice_combos():
            if roll.value in {bet_value, 7}:
                continue
            strat = get_strat(starting_bankroll)
            bet = CBHardWay(bet_value, amount)
            strat.add_bet(bet)
            evs = strat.after_roll(roll)
            assert not len([e for e in evs if isinstance(e, CGEWithBets)])
            assert len(strat.bets) == 1
            assert strat.bankroll == starting_bankroll - amount


def test_impossible_bets_come():
    ''' Can't make come bet if game has no point '''
    strat = get_strat(0)
    bet = CBCome(5)
    assert strat.point is None
    with pytest.raises(IllegalBet):
        strat.add_bet(bet)


def test_impossible_bets_dcome():
    ''' Can't make dont come bet if game has no point '''
    strat = get_strat(0)
    bet = CBDontCome(5)
    assert strat.point is None
    with pytest.raises(IllegalBet):
        strat.add_bet(bet)


def test_impossible_bets_pass():
    ''' Can't make pass bet if game has a point '''
    strat = get_strat(0)
    strat.after_roll(R(1, 3))
    assert strat.point == 4
    bet = CBPass(5)
    with pytest.raises(IllegalBet):
        strat.add_bet(bet)


def test_impossible_bets_dpass():
    ''' Can't make dpass bet if game has a point '''
    strat = get_strat(0)
    strat.after_roll(R(1, 3))
    assert strat.point == 4
    bet = CBDontPass(5)
    with pytest.raises(IllegalBet):
        strat.add_bet(bet)


def test_impossible_bets_come_point():
    ''' Making a come bet that has its own point set already should be illegal
    '''
    bet = CBCome(5)
    bet.set_point(9)
    strat = get_strat(0)
    # establish point so come bets are legal
    strat.after_roll(R(1, 3))
    with pytest.raises(IllegalBet):
        strat.add_bet(bet)


def test_impossible_bets_dcome_point():
    ''' Making a dcome bet that has its own point set already should be illegal
    '''
    bet = CBDontCome(5)
    bet.set_point(9)
    strat = get_strat(0)
    # establish point so come bets are legal
    strat.after_roll(R(1, 3))
    with pytest.raises(IllegalBet):
        strat.add_bet(bet)


def test_impossible_bets_passcome_odds():
    ''' Impossible to make a Pass/Come Odds bet without corresponding Pass/Come
    bet existing '''
    amount = 10
    # Pass odds
    strat = get_strat(0)
    bet = CBOdds(6, False, amount)
    with pytest.raises(IllegalBet):
        strat.add_bet(bet)
    # Come odds
    strat = get_strat(0)
    strat.after_roll(R(1, 3))
    assert strat.point == 4
    bet = CBOdds(6, False, amount)
    with pytest.raises(IllegalBet):
        strat.add_bet(bet)


def test_impossible_bets_dpass_odds():
    ''' Impossible to make Don't Pass/Come Odds bet without corresponding
    dpass/dcome bet existing '''
    amount = 10
    # Don't Pass odds
    strat = get_strat(0)
    bet = CBOdds(6, True, amount)
    with pytest.raises(IllegalBet):
        strat.add_bet(bet)
    # Don't Come odds
    strat = get_strat(0)
    strat.after_roll(R(1, 3))
    assert strat.point == 4
    bet = CBOdds(6, True, amount)
    with pytest.raises(IllegalBet):
        strat.add_bet(bet)


def test_impossible_bets_off_pass():
    ''' Cannot turn pass off '''
    bet = CBPass(5)
    with pytest.raises(IllegalBetChange):
        bet.set_working(False)


def test_impossible_bets_off_dpass():
    ''' Cannot turn dpass off '''
    bet = CBDontPass(5)
    with pytest.raises(IllegalBetChange):
        bet.set_working(False)


def test_impossible_bets_off_come():
    ''' Cannot turn come off '''
    bet = CBCome(5)
    with pytest.raises(IllegalBetChange):
        bet.set_working(False)


def test_impossible_bets_off_dcome():
    ''' Cannot turn dcome off '''
    bet = CBDontCome(5)
    with pytest.raises(IllegalBetChange):
        bet.set_working(False)


def test_impossible_bets_off_field():
    bet = CBField(5)
    with pytest.raises(IllegalBetChange):
        bet.set_working(False)


def test_martingale_field_strat():
    strat = MartingaleFieldStrategy(5)
    for roll in sorted(all_dice_combos(), key=lambda r: r.value):
        strat.make_bets()
        strat.after_roll(roll)
    assert strat.bankroll == 90


def test_basic_pass_strat():
    strat = BasicPassStrategy(5)
    for roll in sorted(all_dice_combos(), key=lambda r: r.value):
        strat.make_bets()
        strat.after_roll(roll)
    assert strat.bankroll == 15


def test_basic_come_strat():
    strat = BasicComeStrategy(5, 6)
    for roll in sorted(all_dice_combos(), key=lambda r: r.value):
        strat.make_bets()
        strat.after_roll(roll)
    assert strat.bankroll == 65
    strat = BasicComeStrategy(5, 1)
    for roll in sorted(all_dice_combos(), key=lambda r: r.value):
        strat.make_bets()
        strat.after_roll(roll)
    assert strat.bankroll == 40


def test_basic_place_strat():
    strat = BasicPlaceStrategy(5, {4, 5, 6, 8, 9, 10})
    for roll in sorted(all_dice_combos(), key=lambda r: r.value):
        strat.make_bets()
        strat.after_roll(roll)
    assert strat.bankroll == 77
