from __future__ import annotations

import math
import typing as t


def percentile(seq: t.Iterable[float], percent: float) -> float:
    """
    Find the percentile of a list of values.
    prometheus-client 0.6.0 doesn't support percentiles, so we use this implementation
    Stolen from https://github.com/heaviss/percentiles that was stolen
    from http://code.activestate.com/recipes/511478-finding-the-percentile-of-the-values/
    """
    if not seq:
        raise ValueError('seq must be non-empty iterable')

    if not (0 < percent < 100):
        raise ValueError('percent parameter must be between 0 and 100')

    seq = sorted(seq)

    k = (len(seq) - 1) * percent / 100
    prev_index = math.floor(k)
    next_index = math.ceil(k)

    if prev_index == next_index:
        return seq[int(k)]

    d0 = seq[prev_index] * (next_index - k)
    d1 = seq[next_index] * (k - prev_index)

    return d0 + d1
