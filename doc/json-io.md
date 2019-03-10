# Roll Counts

- All `counts` **MUST** be non-negative
- All `counts_hard` **MUST** be non-negative
- `counts_hard` **SHOULD NOT** have keys other than 4, 6, 8, 10. If it does,
  they **MUST** be ignored
- `counts` **MUST** have all 2-12 inclusive
- `label` **MAY** be empty
- The following **MUST** be true: `counts_hard[x] <= counts[x]` for all `x` in
  `counts_hard`.
- All `counts` and `counts_hard` do not have to *be* floats, just interpretable
  as them: both `1` and `1.0` are allowed.

## Notes

- `counts_hard` is a *subset* of `counts`. If `counts["4"] == 10` and
  `counts_hard["4"] == 4`, that means there were 6 easy fours.
- `counts_hard` does not have to be accurate. The user may have chosen to not
  record hard rolls separately. In this case they should be all zero as there
is no known count for them
- Fractional roll counts are allowed in order to support theoretical data.
  Requiring a whole number would -- for example -- mean a 37 roll simulation of
a perfectly fair distribution would not output perfectly fair data.

## Producers/Consumers

**Producers**: `simulate`, `parse rollseries`

**Consumers**: `plot rollcounts`

## Schema

        {
            label: str,
            counts: {
                2: float,
                3: float,
                4: float,
                5: float,
                6: float,
                7: float,
                8: float,
                9: float,
                10: float,
                11: float,
                12: float,
            },
            counts_hard: {
                4: float,
                6: float,
                8: float,
                10: float,
            },
        },
        ...

## Example

        {
            label: "Thursday Night",
            counts: {
                2: 7,
                3: 9,
                4: 21,
                5: 24,
                6: 27,
                7: 33,
                8: 24,
                9: 26,
                10: 16,
                11: 8,
                12: 5,
            },
            counts_hard: {
                4: 6,
                6: 9,
                8: 8,
                10: 6,
            },
        }


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
- The `args` object for `type` 'point' **MUST** contain exactly 1 `True` flag.

## Schema

    {
        'type': str,
        'dice': (int, int),
        'value': int,
        'args': {},
    }

## Producers/Consumers

**Producers**: `parse rollseries`

**Consumers**:


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
        },
    }

    {
        'type': point,
        'dice': (6, 3),
        'value': 9,
        'args': {
            'is_established': False,
            'is_won': False,
            'is_lost': True,
        },
    }
