
import pytest
from factorial_sum.core import factorial_sum

def test_small_values():
    assert factorial_sum(1) == 1
    assert factorial_sum(2) == 3
    assert factorial_sum(3) == 9
    assert factorial_sum(4) == 33
    assert factorial_sum(5) == 153

