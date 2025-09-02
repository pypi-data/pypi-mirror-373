
# Factorial Sum

Factorial Sum is a Python library for efficient and exact computation of factorial sums
S(𝑛) = 1! + 2! + 3! + ... n!
using a novel recursive identity introduced by Abdelkrim Meziani (2025).
This approach improves numerical stability, reduces recursion depth, and provides better performance compared to naive methods.

## Installation

```bash
pip install factorial-sum
```

## Usage

```python
from factorial_sum import factorial_sum

# Compute the sum of the first 5 factorials
print(factorial_sum(5))  # Output: 153
```

## Features

- Efficient algorithm based on a new recursive identity:
  S(n) = n² * (n-2)! + S(n-3)
- Faster than naive summation for large n
- Safe for large n using iterative computation (no recursion errors).
- Mathematically exact with Python’s arbitrary-precision integers.
- Lightweight & dependency-free (only uses Python standard library)
- Includes caching for performance
- Fully tested with pytest

## Applications

- Combinatorics and permutation analysis
- Graph enumeration problems
- Factorial number systems
- Teaching recursion and algorithm optimization
- Benchmarking and computational mathematics research

## Citation

If you use this package in academic work, please cite:

Abdelkrim Meziani (2025).
A Novel Recursive Identity for the Sum of Factorials with Computational and Combinatorial Applications.
[https://zenodo.org/records/16994879 / https://orcid.org/0009-0003-1849-4985]

## Author

**Abdelkrim Meziani**