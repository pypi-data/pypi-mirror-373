# Intro
Though `more-itertools` contains *many* functions, it can never be 'complete'.

Below extensions were proposed, but not (yet) added to `more-itertools`.
Module `more-more-itertools` acts as their abode until they get added to `more-itertools`.

# Functions
`at_least_n(iterable, n, too_short=None)`

Validate that `iterable` has *at least* `n` items and return them if it does. 
If it has *fewer* than `n` items, call function `too_short` with its item-count.

Suggested for addition to `more-itertools` as [#1053](https://github.com/more-itertools/more-itertools/issues/1053) on 9 Aug 2025.

`at_most_n(iterable, n, too_long=None)`

Validate that `iterable` has *at most* `n` items and return them if it does.
If it has *more* than `n` items, call function `too_long` with the number `n + 1`.

Suggested for addition to `more-itertools` as [#1053](https://github.com/more-itertools/more-itertools/issues/1053) on 9 Aug 2025.
