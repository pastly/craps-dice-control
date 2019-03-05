import json


class NumericKeyDecoder(json.JSONDecoder):
    ''' Python allows ints to be keys in a dict but JSON doesn't. It's nice to
    be able to use ints as keys in dicts, so parse numeric-looking keys in the
    given JSON into their numeric types. '''
    def decode(self, s):
        res = super().decode(s)
        return self._decode(res)

    def _decode(self, o):
        if isinstance(o, dict):
            d = {}
            for k, v in o.items():
                try:
                    int(k)
                except ValueError:
                    pass
                else:
                    d[int(k)] = self._decode(v)
                    continue
                try:
                    float(k)
                except ValueError:
                    pass
                else:
                    d[float(k)] = self._decode(v)
                    continue
                d[k] = self._decode(v)
            return d
        elif isinstance(o, list):
            return [self._decode(l) for l in o]
        else:
            return o
