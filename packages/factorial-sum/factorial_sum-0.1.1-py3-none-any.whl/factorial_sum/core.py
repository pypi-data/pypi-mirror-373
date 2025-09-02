# factorial_sum/core.py
"""Robust implementations of S(n) = sum_{k=1}^n k!"""

from functools import lru_cache
import math
from typing import Union

Number = Union[int]

def _check_int_nonneg(n: Number) -> None:
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be a non-negative integer")

def factorial_sum(n: int) -> int:
    """
    Exact sum S(n) = 1! + 2! + ... + n! computed iteratively.
    - Works for n >= 0 (S(0) == 0).
    - Uses incremental factorial building (fast and memory-friendly).
    """
    _check_int_nonneg(n)
    total = 0
    fact = 1
    for k in range(1, n + 1):
        fact *= k
        total += fact
    return total

@lru_cache(maxsize=None)
def factorial_sum_recursive(n: int) -> int:
    """
    The original recursive identity:
        S(n) = n^2 * (n-2)! + S(n-3)  (for n >= 3)
    This wrapper uses safe base cases so recursion never calls invalid inputs.
    """
    _check_int_nonneg(n)
    if n == 0:
        return 0
    if n == 1:
        return 1
    if n == 2:
        return 3
    # now n >= 3
    return n**2 * math.factorial(n - 2) + factorial_sum_recursive(n - 3)
