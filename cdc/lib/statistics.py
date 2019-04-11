class Statistics:
    def __init__(self, called_interally__=False):
        if not called_interally__:
            raise NotImplementedError

    def to_dict(self):
        return {
            'points': self.points,
            'craps': self.craps,
            'naturals': self.naturals,
            'hards': self.hards,
            'counts': self.counts,
            'dice': self.dice,
            'pairs': self.pairs,
            'num_rolls': {
                'overall': self.num_rolls(point_only=False),
                'point': self.num_rolls(point_only=True),
            },
        }

    @staticmethod
    def from_roll_events(roll_events):
        points = {
            'won': {
                4: 0, 5: 0, 6: 0, 8: 0, 9: 0, 10: 0,
            },
            'lost': {
                4: 0, 5: 0, 6: 0, 8: 0, 9: 0, 10: 0,
            },
            'established': {
                4: 0, 5: 0, 6: 0, 8: 0, 9: 0, 10: 0,
            },
        }
        hards = {4: 0, 6: 0, 8: 0, 10: 0}
        craps = {2: 0, 3: 0, 12: 0}
        naturals = {7: 0, 11: 0}
        counts = {i: 0 for i in range(2, 12+1)}
        dice = {i: 0 for i in range(1, 6+1)}
        pairs = {i: {j: 0 for j in range(i, 6+1)} for i in range(1, 6+1)}
        have_point = False
        num_rolls = 0
        num_rolls_point = 0
        # Begin consumption of events
        for ev in roll_events:
            num_rolls += 1
            if have_point:
                num_rolls_point += 1
            if ev.type == 'point':
                if ev.args['is_won']:
                    assert have_point
                    points['won'][ev.value] += 1
                    have_point = False
                elif ev.args['is_lost']:
                    assert have_point
                    points['lost'][ev.args['point_value']] += 1
                    have_point = False
                else:
                    assert not have_point
                    points['established'][ev.value] += 1
                    have_point = True
            elif ev.type == 'craps':
                craps[ev.value] += 1
            elif ev.type == 'natural':
                naturals[ev.value] += 1
            if ev.value in {4, 6, 8, 10} and ev.dice[0] == ev.dice[1]:
                hards[ev.value] += 1
            counts[ev.value] += 1
            dice[ev.dice[0]] += 1
            dice[ev.dice[1]] += 1
            if ev.dice[0] <= ev.dice[1]:
                pairs[ev.dice[0]][ev.dice[1]] += 1
            else:
                pairs[ev.dice[1]][ev.dice[0]] += 1
        # End consumption of events
        o = Statistics(called_interally__=True)
        o._points = points
        o._craps = craps
        o._naturals = naturals
        o._hards = hards
        o._counts = counts
        o._dice = dice
        o._pairs = pairs
        o._num_rolls = {'overall': num_rolls, 'point': num_rolls_point}
        return o

    @property
    def points(self):
        ''' dict of num of times we recorded winning/losing/establishing each
        possible point value '''
        return self._points

    @property
    def craps(self):
        ''' dict of num of times we recorded rolling a 2, 3, or 12 when there
        is no point '''
        return self._craps

    @property
    def naturals(self):
        ''' dict of num of times we recorded rolling a 7, or 11 when there
        is no point '''
        return self._naturals

    @property
    def hards(self):
        ''' dict of num of times we recorded rolling a hard 4, 6, 8, or 10
        is no point '''
        return self._hards

    @property
    def counts(self):
        ''' dict of num of times we recorded rolling a each possible dice combo
        between 2 and 12 '''
        return self._counts

    @property
    def pairs(self):
        ''' 2-layer dict of num of times we recorded rolling a each possible
        dice combo. Rolling 3,4 (7) is different than rolling 2,5 (7). Note how
        .counts doesn't differentiate, but .pairs does. '''
        return self._pairs

    @property
    def dice(self):
        ''' dict of num of times we recorded rolling a each die face value
        between 1 and 6. Note how a single roll of a pair of craps dice involes
        two dice, so when this dict is being built, either (1) a value in it
        gets incremented twice (if the two dice were the same), or (2) two
        values in it will get incremented once each '''
        return self._dice

    def num_rolls(self, point_only=False):
        ''' returns the number of times the dice were rolled. Optionally
        doesn't count times the dice were rolled when there was no point set
        '''
        if point_only:
            return self._num_rolls['point']
        return self._num_rolls['overall']

    def rsr(self, point_only=False):
        ''' returns the rolls:seven ratio (RSR) over all recorded dice rolls.
        Optionally doesn't count dice rolls (of any value, 7 or otherwise) when
        there wasn't a point currently set.

        This will raise ZeroDivisionError if there were no 7s rolled (wrt the
        given point_only value)
        '''
        if point_only:
            return self.num_rolls(point_only=True) / \
                sum(self.points['lost'][i] for i in self.points['lost'])
        return self.num_rolls() / self.counts[7]

    def combine(self, rhs):
        ''' Update self with stats from rhs. Most stats just need incrementing
        (in fact, that's true for all of them at the time of writing of this
        comment) '''
        for k1 in self._points:
            for k2 in rhs.points[k1]:
                self._points[k1][k2] += rhs.points[k1][k2]
        for k1 in self._pairs:
            for k2 in rhs.pairs[k1]:
                self._pairs[k1][k2] += rhs.pairs[k1][k2]
        for i in rhs.craps:
            self._craps[i] += rhs.craps[i]
        for i in rhs.naturals:
            self._naturals[i] += rhs.naturals[i]
        for i in rhs.hards:
            self._hards[i] += rhs.hards[i]
        for i in rhs.counts:
            self._counts[i] += rhs.counts[i]
        for i in rhs.dice:
            self._dice[i] += rhs.dice[i]
        for i in rhs._num_rolls:
            self._num_rolls[i] += rhs._num_rolls[i]
        return self
