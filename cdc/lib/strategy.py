from copy import copy

_POINT_VALUES = {4, 5, 6, 8, 9, 10}


class Strategy:
    def __init__(self, name, bankroll=0):
        self._name = name
        self._bankroll = bankroll
        self._bets = []
        self._rolls = []
        self._point = None

    @property
    def name(self):
        return self._name

    @property
    def bankroll(self):
        return self._bankroll

    @property
    def point(self):
        return self._point

    @property
    def last_roll(self):
        return self._rolls[-1]

    @property
    def rolls(self):
        return self._rolls

    @property
    def bets(self):
        return self._bets

    def _adjust_bankroll(self, amount):
        ''' For use interally whenever a bet wins or a bet is made '''
        self._bankroll += amount

    def _handle_winners_and_losers(self):
        ''' Payout all winning bets, remove them, remove any losers, and return
        a list of events '''
        evs = []
        remove_bets = []
        for bet in self.bets:
            if not bet.is_working:
                continue
            if bet.is_loser(self.last_roll, self.point):
                evs.append(CGEBetLost(bet))
                remove_bets.append(bet)
            elif bet.is_winner(self.last_roll, self.point):
                evs.append(CGEBetWon(bet))
                self._adjust_bankroll(
                    bet.amount + bet.win_amount(self.last_roll))
                remove_bets.append(bet)
        self._bets = [b for b in self.bets if b not in remove_bets]
        return evs

    def _convert_comes(self):
        evs = []
        remove_bets = []
        for bet in self.bets:
            if not isinstance(bet, CBCome) and not isinstance(bet, CBDontCome):
                continue
            if not bet.is_working:
                continue
            if bet.point is not None:
                continue
            if self.last_roll.value not in {4, 5, 6, 8, 9, 10}:
                continue
            new_bet = copy(bet)
            new_bet.set_point(self.last_roll.value)
            remove_bets.append(bet)
            self.add_bet(new_bet, is_free=True)
            evs.append(CGEBetConverted(bet, new_bet))
        self._bets = [b for b in self.bets if b not in remove_bets]
        return evs

    def _adjust_point(self):
        if self.point is None and self.last_roll.value in _POINT_VALUES:
            self._point = self.last_roll.value
            return [CGEPointEstablished(self.last_roll.value)]
        elif self.point is not None and self.last_roll.value == 7:
            ret = [CGEPointLost(self.point)]
            self._point = None
            return ret
        elif self.point is not None and self.last_roll.value == self.point:
            self._point = None
            return [CGEPointWon(self.last_roll.value)]
        return []

    def after_roll(self, roll):
        self._rolls.append(roll)
        evs = []
        evs.extend(self._handle_winners_and_losers())
        evs.extend(self._convert_comes())
        evs.extend(self._adjust_point())
        return evs

    def add_bet(self, b, is_free=False):
        assert isinstance(b, CrapsBet)
        if not is_free:
            self._adjust_bankroll(-1 * b.amount)
        self._bets.append(b)

    def make_bets(self):
        ''' Subclasses should implement this '''
        raise NotImplementedError


class CrapsRoll:
    def __init__(self, d1, d2):
        self._dice = (d1, d2)
        self._value = sum(self.dice)

    @property
    def dice(self):
        return self._dice

    @property
    def value(self):
        return self._value


class CrapsBet:
    name = 'CrapsBet'
    roll_win = set()
    roll_lose = set()

    def __init__(self, amount, working=True):
        self._amount = amount
        self._working = working

    def __eq__(self, other):
        return self.amount == other.amount and \
            self.is_working == other.is_working and \
            self.name == other.name and \
            self.roll_win == other.roll_win and \
            self.roll_lose == other.roll_lose

    def __str__(self):
        return 'Bet<%s %d %s>' % (
            self.name, self.amount, 'on' if self.is_working else 'off')

    @property
    def amount(self):
        return self._amount

    @property
    def is_working(self):
        return self._working

    def set_working(self, working):
        self._working = working

    def is_winner(self, roll, *a, **kw):
        ''' Subclass should re-implement this if win condition is not simply
        the dice adding up to some value '''
        return roll.value in self.roll_win

    def is_loser(self, roll, *a, **kw):
        ''' Subclass should re-implement this if lose condition is not simply
        the dice adding up to some value '''
        return roll.value in self.roll_lose

    def win_amount(self, *a, **kw):
        ''' Subclass must implement this and calculate the winning amount based
        on self.amount '''
        raise NotImplementedError


class CBPass(CrapsBet):
    name = 'Pass'
    roll_win = {7, 11}
    roll_lose = {2, 3, 12}

    def win_amount(self, *a, **kw):
        return self.amount

    def is_winner(self, roll, point):
        return roll.value in self.roll_win\
            if point is None else roll.value == point

    def is_loser(self, roll, point):
        return roll.value in self.roll_lose\
            if point is None else roll.value == 7


class CBDontPass(CrapsBet):
    name = 'DontPass'
    roll_win = {2, 3}
    roll_lose = {7, 11}

    def win_amount(self, *a, **kw):
        return self.amount

    def is_winner(self, roll, point):
        return roll.value in self.roll_win\
            if point is None else roll.value == 7

    def is_loser(self, roll, point):
        return roll.value in self.roll_lose\
            if point is None else roll.value == point


class CBCome(CrapsBet):
    name = 'Come'
    roll_win = {7, 11}
    roll_lose = {2, 3, 12}

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._point = None

    def win_amount(self, *a, **kw):
        return self.amount

    def set_point(self, point):
        assert point in {4, 5, 6, 8, 9, 10}
        assert self.point is None
        self._point = point
        self.roll_win = {point}
        self.roll_lose = {7}

    @property
    def point(self):
        return self._point


class CBDontCome(CrapsBet):
    name = 'DontCome'
    roll_win = {2, 3}
    roll_lose = {7, 11}

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._point = None

    def win_amount(self, *a, **kw):
        return self.amount

    def set_point(self, point):
        assert point in {4, 5, 6, 8, 9, 10}
        assert self.point is None
        self._point = point
        self.roll_win = {7}
        self.roll_lose = {point}

    @property
    def point(self):
        return self._point


class CBOdds(CrapsBet):
    name = 'Odds'
    roll_win = set()
    roll_lose = set()

    def __init__(self, point, is_dont, *a, **kw):
        super().__init__(*a, **kw)
        assert point in {4, 5, 6, 8, 9, 10}
        self._point = point
        self._is_dont = is_dont
        if not is_dont:
            self.roll_win = {self.point}
            self.roll_lose = {7}
        else:
            self.roll_win = {7}
            self.roll_lose = {self.point}

    @property
    def point(self):
        return self._point

    def win_amount(self, *a, **kw):
        if self.point in {4, 10}:
            ratio = 1 / 2 if self._is_dont else 2 / 1
            return self.amount * ratio
        elif self.point in {5, 9}:
            ratio = 2 / 3 if self._is_dont else 3 / 2
            return self.amount * ratio
        ratio = 5 / 6 if self._is_dont else 6 / 5
        return self.amount * ratio


class CBField(CrapsBet):
    name = 'Field'
    roll_win = {2, 3, 4, 9, 10, 11, 12}
    roll_lose = {5, 6, 7, 8}

    def __init__(self, *a, mult2=2, mult12=2, **kw):
        super().__init__(*a, **kw)
        self._mult2 = mult2
        self._mult12 = mult12

    def win_amount(self, roll):
        if roll.value == 2:
            return self.amount * self._mult2
        elif roll.value == 12:
            return self.amount * self._mult12
        return self.amount


class CBPlace(CrapsBet):
    name = 'Place'
    roll_win = set()
    roll_lose = {7}

    def __init__(self, value, *a, **kw):
        super().__init__(*a, **kw)
        self.roll_win = {value}

    def win_amount(self, *a, **kw):
        rw = self.roll_win
        assert len(rw) == 1
        assert 4 in rw or 5 in rw or 6 in rw or 8 in rw or 9 in rw or 10 in rw
        if 4 in rw or 10 in rw:
            return self.amount * 9 / 5
        elif 5 in rw or 9 in rw:
            return self.amount * 7 / 5
        return self.amount * 7 / 6


class CrapsGameEvent:
    name = 'CrapsGameEvent'


class CGEWithBets(CrapsGameEvent):
    def __init__(self, bets, *a, **kw):
        super().__init__(*a, **kw)
        # If given an iterable of bets, store it directly. Otherwise we were
        # given a single bet, and should store it in a list
        try:
            iter(bets)
        except TypeError:
            self._bets = [bets]
        else:
            self._bets = bets


class CGEBetWon(CGEWithBets):
    name = 'BetWon'

    def __str__(self):
        return 'Win<%s>' % str(self.bet)

    @property
    def bet(self):
        return self._bets[0]


class CGEBetLost(CGEWithBets):
    name = 'BetLost'

    def __str__(self):
        return 'Lost<%s>' % str(self.bet)

    @property
    def bet(self):
        return self._bets[0]


class CGEBetConverted(CGEWithBets):
    name = 'BetConverted'

    def __init__(self, from_bet, to_bet, *a, **kw):
        super().__init__((from_bet, to_bet), *a, **kw)

    @property
    def from_bet(self):
        return self._bets[0]

    @property
    def to_bet(self):
        return self._bets[1]


class CGEPoint(CrapsGameEvent):
    def __init__(self, point, *a, **kw):
        super().__init__(*a, **kw)
        self._point = point

    @property
    def point(self):
        return self._point


class CGEPointEstablished(CGEPoint):
    def __str__(self):
        return 'PointEst<%d>' % self.point


class CGEPointWon(CGEPoint):
    def __str__(self):
        return 'PointWon<%d>' % self.point


class CGEPointLost(CGEPoint):
    def __str__(self):
        return 'PointLost<%d>' % self.point


class MartingaleFieldStrategy(Strategy):
    def __init__(self, base_bet, *a, **kw):
        self._base_bet = base_bet
        super().__init__('MartengaleFieldStrat', *a, **kw)

    def make_bets(self):
        amount = self._base_bet
        rolls_reverse = reversed(self.rolls)
        for roll in rolls_reverse:
            if roll.value in {2, 3, 4, 9, 10, 11, 12}:
                break
            amount *= 2
        assert not len(self.bets)
        self.add_bet(CBField(amount))
