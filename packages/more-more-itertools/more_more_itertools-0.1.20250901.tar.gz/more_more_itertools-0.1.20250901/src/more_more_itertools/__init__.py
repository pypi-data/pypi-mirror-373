import itertools
import time
from collections.abc import Callable, Iterable, Iterator
from typing import NoReturn, overload

from more_itertools import raise_

__all__ = ['at_least_n', 'at_most_n', 'throttle']

type NoneReturningFunction[**PS] = Callable[PS, None]  # function without result (but side effect), 'procedure'
type NoReturnFunction[**PS] = Callable[PS, NoReturn]   # raising function, which doesn't return
type NoneOrNotReturningFunction[**PS] = NoneReturningFunction[PS] | NoReturnFunction[PS]  # one of the above


def at_least_n[T](iterable: Iterable[T], /, n: int,
                  too_short: NoneOrNotReturningFunction[int] | None = None
                  ) -> Iterator[T]:
    """Iterate over `iterable`, which must contain *at least* `n` elements; otherwise, call `too_short()`.

    >>> test = 1, 2, 3
    >>> for n in range(3):                             # verify for `n` 0..3 elements
    ...     assert tuple(at_least_n(test, n)) == test  # succeed as `test` has at least `n` elements
    >>> tuple(at_least_n(test, 4))                     # fail because NOT at least 4 elements # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ValueError: Too short...
    >>> tuple(at_least_n(test, 4, too_short=print))    # succeed even with <4 elements as `print` doesn't raise
    3
    (1, 2, 3)
    """
    iterator = iter(iterable)

    count = 0  # in case of empty iterable
    for count, element in enumerate(itertools.islice(iterator, n), 1):  # first n elements, or less if too short
        yield element

    if count < n:  # too few
        if too_short is None:
            too_short = lambda items: raise_(ValueError, f"Too short: iterable must have at least {n} elements, "
                                                         f"found only {count}")
        too_short(count)

    yield from iterator  # remainder > n


def at_most_n[T](iterable: Iterable[T], /, n: int,
                 too_long: NoneOrNotReturningFunction[int] | None = None
                 ) -> Iterator[T]:
    """Iterate over `iterable`, which must contain *at least* `n` elements; otherwise, call `too_short()`.

    >>> test = 1, 2, 3
    >>> for n in range(3, 10):                        # verify for `n` 3..10 elements
    ...     assert tuple(at_most_n(test, n)) == test  # succeed as `test` has at most `n` elements
    >>> tuple(at_most_n(test, 2))                     # fail because NOT at most 2 elements # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ValueError: Too long...
    >>> tuple(at_most_n(test, 2, too_long=print))     # succeed even with >4 elements as `print` doesn't raise
    3
    (1, 2)
    """
    iterator = iter(iterable)

    count = 0  # in case of empty iterable
    for count, element in enumerate(itertools.islice(iterator, n), 1):  # first n elements, or less if shorter
        yield element

    if count >= n:  # at max, can be too many
        for _ in iterator:  # too many if one more
            if too_long is None:
                too_long = lambda items: raise_(ValueError, f"Too long: iterable must have at most {n} elements, "
                                                            f"found {count + 1} at minimum")
            too_long(count + 1)


@overload
def throttle[T](iterable: Iterable[T], /, *, unit: float) -> Iterator[T]:
    ...

@overload
def throttle[T](iterable: Iterable[T], /, *, speed: float) -> Iterator[T]:
    ...

def throttle[T](iterable: Iterable[T], /, *,
                unit: float | None = None, speed: float | None = None) -> Iterator[T]:
    """Iterate over `iterable` at min `unit` time (sec per item), or at max `speed` (items per sec).

    Note `unit=0` runs at full speed.

    >>> start = time.perf_counter()
    >>> for _ in throttle(range(10), speed=10_000):          # 10 iterations * <=10_000 per sec, i.e. >=0.001 sec
    ...     pass
    >>> assert 0.001 <= time.perf_counter() - start <= 0.01  # allow 0.01 sec (10* slower) for slow CPU/high load
    """
    match unit, speed:
        case float() | int(), None if unit >= 0:
            pass              # unit given; full speed (no throttling), if 0
        case None, float() | int() if speed > 0:
            unit = 1 / speed  # unit calculated from given speed
        case _:
            raise TypeError(f"{throttle.__qualname__!r} expects `unit>=0` *xor* `speed>0`, not {unit=}, {speed=}")

    if unit == 0:             # full speed, omit overhead
        yield from iterable
        return

    start = time.perf_counter()
    for count, element in enumerate(iterable):
        earliest = start + count * unit
        wait = earliest - time.perf_counter()
        if wait > 0:
            time.sleep(wait)
        assert time.perf_counter() >= earliest
        yield element


if __name__ == '__main__':
    import doctest
    doctest.testmod()
