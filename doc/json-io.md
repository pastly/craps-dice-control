# Roll Event

A small json object that includes some extra data about a roll. These are most
useful when you have an ordered series of them, as the included data is
stateful and can be used to replay an entire craps game.

A stream of these json roll events should not be confused with the plain-text
roll series that simply indicates dice values with no extra information.

- The `type` string **MUST** be one of the following:
   1. 'craps'
   2. 'natural'
   3. 'roll'
   4. 'point'
- Each `dice` int **MUST** be between 1 and 6 inclusive
- The `value` int **MUST** be the sum of the two `dice` ints
- The `args` object **MUST** be empty unless the `type` is 'point', in which
  case the `args` object **MUST** contain:
   1. `'is_established': bool
   2.  'is_won': bool
   3.  'is_lost': bool
   4.  'point_value': int
- The `args` object for `type` 'point' **MUST** contain exactly 1 `True` flag.
- `args.point_value` **MUST** be 4, 5, 6, 8, 9, or 10.

## Schema

    {
        'type': str,
        'dice': (int, int),
        'value': int,
        'args': {},
    }

## Producers/Consumers

**Producers**: `parse rollseries`

**Consumers**: `statistics`, `plot pdf`


## Examples

    {
        'type': craps,
        'dice': (1, 2),
        'value': 3,
        'args': {},
    }

    {
        'type': natural,
        'dice': (5, 6),
        'value': 11,
        'args': {},
    }

    {
        'type': point,
        'dice': (1, 3),
        'value': 4,
        'args': {
            'is_established': True,
            'is_won': False,
            'is_lost': False,
            'point_value': 4,
        },
    }

    {
        'type': point,
        'dice': (2, 5),
        'value': 7,
        'args': {
            'is_established': False,
            'is_won': False,
            'is_lost': True,
            'point_value': 5,
        },
    }
