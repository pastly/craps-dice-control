from argparse import ArgumentTypeError


class BoundedInt:
    def __init__(self, mini=None, maxi=None, clamp=False):
        self.mini = mini
        self.maxi = maxi
        self.clamp = clamp

    def __call__(self, str_value):
        try:
            i = int(str_value)
        except Exception as e:
            raise ArgumentTypeError(e)
        if self.mini is not None and i < self.mini:
            if self.clamp:
                i = self.mini
            else:
                raise ArgumentTypeError(
                    '%d cannot be less than %d' % (i, self.mini))
        if self.maxi is not None and i > self.maxi:
            if self.clamp:
                i = self.maxi
            else:
                raise ArgumentTypeError(
                    '%d cannot be more than %d' % (i, self.maxi))
        return i
