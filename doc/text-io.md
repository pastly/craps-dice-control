# Roll Series

A roll series is a textual representation of a series of rolls.  It is simply
an ordered series of pairs of integers representing the face values of the
dice.

- Input **MUST** contain an even number of integers
- Values **MUST** be between 1 and 6 inclusive
- White space **MUST** be ignored
- Lines with `'#'` as the first non-white space character are comments and
  **MUST** be ignored for the purposes of roll processing, and **MAY** be
included in output in a reasonable way
- Consumers **MAY** process input as a stream and error out in whatever
  reasonable way in response to bad input, even if output has already been
generated

## Notes

- integers are represented as a single 1-byte char, **not** as their byte
  value. `1` is represented as `'1'` (AKA `0x36`, AKA `0b00110110`)
not `1` (AKA `0x01`, AKA `0b00000001`)

## Producers/Consumers

**Producers**:

**Consumers**: rollstats

## Examples

    33

Is a single roll where both dice landed on 3, for a total of 6.
This is a "hard six."

    34 44 26

Is three rolls: 7, hard 8, and 8.

    344426

Is the same as the previous example, but with no white space

    34 44
    # Pause for drink orders
    26

Is the same as the previous example, but with a comment

    # Perfectly fair
    1111111111
    12121212121212121212
    131313131313131313131313131313
    1414141414141414141414141414141414141414
    15151515151515151515151515151515151515151515151515
    161616161616161616161616161616161616161616161616161616161616
    26262626262626262626262626262626262626262626262626
    3636363636363636363636363636363636363636
    464646464646464646464646464646
    56565656565656565656
    6666666666

A series of dice rolls that 100% fit with expectations of fair dice

    # 6 rolls each
    111111111111
    121212121212
    131313131313
    141414141414
    151515151515
    161616161616
    262626262626
    363636363636
    464646464646
    565656565656
    666666666666

A very unlikely series of dice rolls where each value is rolled the same number
of times
