from cdc.lib.strategy import Strategy, CrapsRoll as R,\
    CBPass, CBDontPass, CBField, CBPlace, CBCome, CBDontCome, CBOdds,\
    CGEBetWon, CGEBetLost, CGEBetConverted,\
    CGEPointEstablished, CGEPointWon, CGEPointLost,\
    MartingaleFieldStrategy

# import pytest


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
        bankroll_before = strat.bankroll
        evs = strat.after_roll(roll)
        # Should have a losing event
        assert len(evs) == 1
        assert isinstance(evs[0], CGEBetLost)
        assert evs[0].bet == CBPass(amount)
        # Pass bet should be removed
        assert not len(strat.bets)
        # Bankroll should same
        assert strat.bankroll == bankroll_before


def test_pass_nothing():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 12, 7, 11}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBPass(amount))
        bankroll_before = strat.bankroll
        evs = strat.after_roll(roll)
        # Should not have won or lost, just established a point
        assert len(evs) == 1
        assert isinstance(evs[0], CGEPointEstablished)
        # Pass bet should still exist
        assert len(strat.bets) == 1
        # Bankroll should same
        assert strat.bankroll == bankroll_before


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
        bankroll_before = strat.bankroll
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
        # bankroll should be same
        assert strat.bankroll == bankroll_before
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
        bankroll_before = strat.bankroll
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
            # bankroll should be same
            assert strat.bankroll == bankroll_before
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
        bankroll_before = strat.bankroll
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
        # bankroll should be same
        assert strat.bankroll == bankroll_before
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
        bankroll_before = strat.bankroll
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
            # bankroll should be same
            assert strat.bankroll == bankroll_before
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
        bankroll_before = strat.bankroll
        evs = strat.after_roll(roll)
        # Should have a losing event
        assert len(evs) == 1
        assert isinstance(evs[0], CGEBetLost)
        assert evs[0].bet == CBDontPass(amount)
        # Dont Pass bet should be removed
        assert not len(strat.bets)
        # Bankroll be same
        assert strat.bankroll == bankroll_before


def test_dpass_nothing():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 7, 11}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBDontPass(amount))
        bankroll_before = strat.bankroll
        evs = strat.after_roll(roll)
        # Should not have won or lost, just established a point or nothing
        assert len(evs) <= 1
        if len(evs):
            assert isinstance(evs[0], CGEPointEstablished)
        # Dont Pass bet should still exist
        assert len(strat.bets) == 1
        # Bankroll be same
        assert strat.bankroll == bankroll_before


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
        bankroll_before = strat.bankroll
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == bankroll_before


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
            bankroll_before = strat.bankroll
            evs = strat.after_roll(roll)
            assert len(strat.bets) == 1
            assert not len([e for e in evs if isinstance(e, CGEBetWon)])
            assert not len([e for e in evs if isinstance(e, CGEBetLost)])
            assert strat.bankroll == bankroll_before


def test_come_win():
    amount = 5
    starting_bankroll = 0
    for roll in {R(3, 4), R(5, 6)}:
        strat = get_strat(starting_bankroll)
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
        strat.add_bet(CBCome(amount))
        bankroll_before = strat.bankroll
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == bankroll_before


def test_come_convert():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBCome(amount))
        bankroll_before = strat.bankroll
        assert strat.bets[0].point is None
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        assert evs[0].from_bet.point is None
        assert evs[0].to_bet.point == roll.value
        assert len(strat.bets) == 1
        assert strat.bets[0].point == roll.value
        assert strat.bankroll == bankroll_before


def test_come_point_win():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
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
        strat.add_bet(CBCome(amount))
        bankroll_before = strat.bankroll
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        evs = strat.after_roll(R(3, 4))
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == bankroll_before


def test_come_point_nothing():
    amount = 5
    starting_bankroll = 0
    for first_roll in all_dice_combos():
        if first_roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBCome(amount))
        bankroll_before = strat.bankroll
        evs = strat.after_roll(first_roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        for second_roll in all_dice_combos():
            if second_roll.value in {first_roll.value, 7}:
                continue
            evs = strat.after_roll(second_roll)
            assert not len(evs)
            assert len(strat.bets) == 1
            assert strat.bankroll == bankroll_before


def test_dcome_win():
    amount = 5
    starting_bankroll = 0
    for roll in {R(1, 1), R(1, 2)}:
        strat = get_strat(starting_bankroll)
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
        strat.add_bet(CBDontCome(amount))
        bankroll_before = strat.bankroll
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == bankroll_before


def test_dcome_convert():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBDontCome(amount))
        bankroll_before = strat.bankroll
        assert strat.bets[0].point is None
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        assert evs[0].from_bet.point is None
        assert evs[0].to_bet.point == roll.value
        assert len(strat.bets) == 1
        assert strat.bets[0].point == roll.value
        assert strat.bankroll == bankroll_before


def test_dcome_point_win():
    amount = 5
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
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
        strat.add_bet(CBDontCome(amount))
        bankroll_before = strat.bankroll
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == bankroll_before


def test_dcome_point_nothing():
    amount = 5
    starting_bankroll = 0
    for first_roll in all_dice_combos():
        if first_roll.value in {2, 3, 7, 11, 12}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBDontCome(amount))
        bankroll_before = strat.bankroll
        evs = strat.after_roll(first_roll)
        assert len([e for e in evs if isinstance(e, CGEBetConverted)]) == 1
        for second_roll in all_dice_combos():
            if second_roll.value in {first_roll.value, 7}:
                continue
            evs = strat.after_roll(second_roll)
            assert not len(evs)
            assert len(strat.bets) == 1
            assert strat.bankroll == bankroll_before


def test_odds_win():
    amount = 10
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBOdds(roll.value, False, amount))
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 1
        assert not len(strat.bets)
        if roll.value in {4, 10}:
            expected = starting_bankroll + amount * 2 / 1
        elif roll.value in {5, 9}:
            expected = starting_bankroll + amount * 3 / 2
        else:
            expected = starting_bankroll + amount * 6 / 5
        assert strat.bankroll == expected


def test_odds_lose():
    amount = 10
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBOdds(roll.value, False, amount))
        bankroll_before = strat.bankroll
        evs = strat.after_roll(R(3, 4))
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == bankroll_before


def test_odds_nothing():
    amount = 10
    starting_bankroll = 0
    for point in {4, 5, 6, 8, 9, 10}:
        for roll in all_dice_combos():
            if roll.value in {point, 7}:
                continue
            strat = get_strat(starting_bankroll)
            strat.add_bet(CBOdds(point, False, amount))
            evs = strat.after_roll(roll)
            assert not len([e for e in evs if isinstance(e, CGEBetWon)])
            assert not len([e for e in evs if isinstance(e, CGEBetLost)])
            assert len(strat.bets) == 1
            assert strat.bankroll == starting_bankroll - amount


def test_dodds_win():
    amount = 30
    starting_bankroll = 30
    for point in {4, 5, 6, 8, 9, 10}:
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBOdds(point, True, amount))
        evs = strat.after_roll(R(3, 4))
        assert len([e for e in evs if isinstance(e, CGEBetWon)]) == 1
        assert not len(strat.bets)
        if point in {4, 10}:
            expected = starting_bankroll + amount * 1 / 2
        elif point in {5, 9}:
            expected = starting_bankroll + amount * 2 / 3
        else:
            expected = starting_bankroll + amount * 5 / 6
        assert strat.bankroll == expected


def test_dodds_lose():
    amount = 30
    starting_bankroll = 0
    for roll in all_dice_combos():
        if roll.value not in {4, 5, 6, 8, 9, 10}:
            continue
        strat = get_strat(starting_bankroll)
        strat.add_bet(CBOdds(roll.value, True, amount))
        bankroll_before = strat.bankroll
        evs = strat.after_roll(roll)
        assert len([e for e in evs if isinstance(e, CGEBetLost)]) == 1
        assert not len(strat.bets)
        assert strat.bankroll == bankroll_before


def test_dodds_nothing():
    amount = 10
    starting_bankroll = 0
    for point in {4, 5, 6, 8, 9, 10}:
        for roll in all_dice_combos():
            if roll.value in {point, 7}:
                continue
            strat = get_strat(starting_bankroll)
            strat.add_bet(CBOdds(point, True, amount))
            bankroll_before = strat.bankroll
            evs = strat.after_roll(roll)
            assert not len([e for e in evs if isinstance(e, CGEBetWon)])
            assert not len([e for e in evs if isinstance(e, CGEBetLost)])
            assert len(strat.bets) == 1
            assert strat.bankroll == bankroll_before


def test_martingale_field_strat():
    strat = MartingaleFieldStrategy(5)
    for roll in sorted(all_dice_combos(), key=lambda r: r.value):
        strat.make_bets()
        strat.after_roll(roll)
    assert strat.bankroll == 90
