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

**Producers**: simulate

**Consumers**: plot

## Schema

    [
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
    ]

## Example

    [
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
        },
        {
            label: "Friday Night",
            counts: {
                2: 8,
                3: 13,
                4: 26,
                5: 15,
                6: 24,
                7: 32,
                8: 29,
                9: 25,
                10: 10,
                11: 11,
                12: 7,
            },
            counts_hard: {
                4: 4,
                6: 7,
                8: 7,
                10: 6,
            },
        },
    ]
