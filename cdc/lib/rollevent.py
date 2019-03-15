class RollEvent:
    def __init__(self, type_, dice, args):
        self._type = type_
        self._dice = dice
        self._args = args

    @staticmethod
    def from_dict(d):
        return RollEvent(d['type'], d['dice'], d['args'])

    def to_dict(self):
        return {
            'type': self.type,
            'dice': self.dice,
            'value': self.value,
            'args': self.args,
        }

    @property
    def type(self):
        return self._type

    @property
    def dice(self):
        return self._dice

    @property
    def value(self):
        return sum(self.dice)

    @property
    def args(self):
        return self._args

    def __eq__(self, other):
        return self.type == other.type and \
            list(self.dice) == list(other.dice) and \
            self.args == other.args
