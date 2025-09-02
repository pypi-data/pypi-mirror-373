import pytest
from factorial_sum.core import factorial_sum, factorial_sum_recursive

def test_small_values():
    assert factorial_sum(0) == 0
    assert factorial_sum(1) == 1
    assert factorial_sum(2) == 3
    assert factorial_sum(3) == 9
    assert factorial_sum(4) == 33
    assert factorial_sum(5) == 153

def test_recursive_matches_iterative():
    for n in range(0, 12):
        assert factorial_sum(n) == factorial_sum_recursive(n)
