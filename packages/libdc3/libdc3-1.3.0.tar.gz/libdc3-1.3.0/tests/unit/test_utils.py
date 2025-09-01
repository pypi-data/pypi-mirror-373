from libdc3.utils import flatten_ranges, yield_range


def test_yield_range():
    data = [1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 14, 38, 39, 40, 41]
    result = list(yield_range(data))
    assert result == [[1, 4], [7, 12], [14, 14], [38, 41]]


def test_flatten_ranges():
    ranges = [[1, 4], [7, 12], [14, 14], [38, 41]]
    flat = list(flatten_ranges(ranges))
    assert flat == [1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 14, 38, 39, 40, 41]
