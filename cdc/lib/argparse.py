from argparse import ArgumentTypeError, FileType
import sys


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


class TryAppendFileType(FileType):
    ''' As argparse.FileType, but when the open mode contains 'a' (append),
    only *try* to open the file as append. If it doesn't work, consume
    the exception and open the file with 'w' instead '''

    def __call__(self, fname):
        # First allow the user to specify - (stdin or stdout), just like
        # argparse.FileType does
        if fname == '-':
            if 'r' in self._mode:
                return sys.stdin
            elif 'w' in self._mode:
                return sys.stdout
            elif 'a' in self._mode:
                return sys.stdout
            else:
                msg = 'argument "-" with mode %s' % self._mode
                raise ValueError(msg)
        # If the user doesn't want to append, don't do anything special
        if 'a' not in self._mode:
            return super().__call__(fname)
        # The user wants to append. Try opening the file ...
        assert 'a' in self._mode
        try:
            return open(
                fname, self._mode, self._bufsize, self._encoding, self._errors)
        except OSError as e:
            # If it doesn't work, open it as write intead
            if 'Illegal seek' not in e:
                raise e
            self._mode.replace('a', 'w')
            return super().__call__(fname)
