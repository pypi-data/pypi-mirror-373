
# Factorial Sum

Efficient computation of factorial sums using a novel recursive identity discovered by Abdelkrim Meziani.

## Installation

```bash
pip install factorial-sum
```

## Usage

```python
from factorial_sum import factorial_sum

print(factorial_sum(5))  # Output: 153
```

## Features

- Implements the identity S(n) = n² * (n-2)! + S(n-3)
- Faster than naive summation for large n
- Includes caching for performance
- Fully tested with pytest

## Author

**Abdelkrim Meziani**
