
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
            if bet.is_loser(self.last_roll):
                evs.append(CGEBetLost(bet))
                remove_bets.append(bet)
            elif bet.is_winner(self.last_roll):
                evs.append(CGEBetWon(bet))
                self._adjust_bankroll(bet.win_amount())
                remove_bets.append(bet)
        self._bets = [b for b in self.bets if b not in remove_bets]
        return evs

    def _convert_comes(self):
        return []

    def _adjust_point(self):
        if self.point is None and self.last_roll.value in _POINT_VALUES:
            self._point = self.last_roll.value
            return [CGEPointEstablished(self.last_roll.value)]
        elif self.point is not None and self.last_roll.value == 7:
            self._point = None
            return [CGEPointLost(self.point)]
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

    def add_bet(self, b):
        assert isinstance(b, CrapsBet)
        self._bets.append(b)


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

    def is_winner(self, roll):
        ''' Subclass should re-implement this if win condition is not simply
        the dice adding up to some value '''
        return roll.value in self.roll_win

    def is_loser(self, roll):
        ''' Subclass should re-implement this if lose condition is not simply
        the dice adding up to some value '''
        return roll.value in self.roll_lose

    def win_amount(self):
        ''' Subclass must implement this and calculate the winning amount based
        on self.amount '''
        raise NotImplementedError


class CBPass(CrapsBet):
    name = 'Pass'
    roll_win = {7, 11}
    roll_lose = {2, 3, 12}

    def win_amount(self):
        return self.amount


class CBDontPass(CrapsBet):
    name = 'DontPass'
    roll_win = {2, 3}
    roll_lose = {7, 11}

    def win_amount(self):
        return self.amount


class CrapsGameEvent:
    name = 'CrapsGameEvent'


class CGEWithBet(CrapsGameEvent):
    def __init__(self, bet, *a, **kw):
        super().__init__(*a, **kw)
        self._bet = bet

    @property
    def bet(self):
        return self._bet


class CGEBetWon(CGEWithBet):
    name = 'BetWon'

    def __str__(self):
        return 'Win<%s>' % str(self.bet)


class CGEBetLost(CGEWithBet):
    name = 'BetLost'

    def __str__(self):
        return 'Lost<%s>' % str(self.bet)


class CGEPoint(CrapsGameEvent):
    def __init__(self, point_value, *a, **kw):
        super().__init__(*a, **kw)
        self._value = point_value

    @property
    def point_value(self):
        return self._value


class CGEPointEstablished(CGEPoint):
    def __str__(self):
        return 'PointEst<%d>' % self.point_value


class CGEPointWon(CGEPoint):
    def __str__(self):
        return 'PointWon<%d>' % self.point_value


class CGEPointLost(CGEPoint):
    def __str__(self):
        return 'PointLost<%d>' % self.point_value
