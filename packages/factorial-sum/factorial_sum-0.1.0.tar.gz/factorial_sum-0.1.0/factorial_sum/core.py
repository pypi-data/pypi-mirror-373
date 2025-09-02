
import math
from functools import lru_cache

@lru_cache(maxsize=None)
def factorial_sum(n: int) -> int:
    """
    Compute S(n) = 1! + 2! + ... + n! using the recursive identity:
        S(n) = n^2 * (n-2)! + S(n-3), for n >= 3
    Base cases:
        S(1) = 1
        S(2) = 3
    """
    if n < 1:
        raise ValueError("n must be a positive integer")
    if n == 1:
        return 1
    if n == 2:
        return 3
    return n**2 * math.factorial(n - 2) + factorial_sum(n - 3)