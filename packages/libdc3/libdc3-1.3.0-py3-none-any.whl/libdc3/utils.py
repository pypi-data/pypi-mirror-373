import itertools


def yield_range(i):
    for _, b in itertools.groupby(enumerate(i), lambda pair: pair[1] - pair[0]):
        b = list(b)
        yield [b[0][1], b[-1][1]]


def flatten_ranges(ranges):
    for start, end in ranges:
        yield from range(start, end + 1)
