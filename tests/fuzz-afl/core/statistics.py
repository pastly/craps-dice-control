import cdc.core.statistics as s

from json.decoder import JSONDecodeError
import os
import sys

import afl


# afl.init()

while afl.loop(100000):
    sys.stdin.seek(0)
    try:
        list(s.roll_events_from_input(sys.stdin))
    # except rs.IncompleteRollSeriesError:
    #     pass
    # except rs.ImpossibleDieValueError:
    #     pass
    except UnicodeDecodeError:
        pass
    except JSONDecodeError:
        pass

os._exit(0)
