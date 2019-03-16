import cdc.core.parse.rollseries as rs

import os
import sys

import afl


# afl.init()

while afl.loop(100000):
    sys.stdin.seek(0)
    try:
        list(rs.dice_pairs_gen_to_events(
            rs.roll_series_stream_to_dice_pairs(sys.stdin)))
    except rs.IncompleteRollSeriesError:
        pass
    except rs.ImpossibleDieValueError:
        pass
    except UnicodeDecodeError:
        pass

os._exit(0)
