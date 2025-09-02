# Primes - Advanced Primality Testing Algorithms

A Python library implementing state-of-the-art primality testing algorithms, starting with the AKS (Agrawal-Kayal-Saxena) primality test.

## Overview

This repository contains implementations of various primality testing algorithms with a focus on theoretical significance and practical applications. The AKS primality test is the first deterministic polynomial-time algorithm for testing primality.

## Features

- **AKS Primality Test**: First deterministic polynomial-time primality test
- **Comprehensive Documentation**: Detailed explanations of algorithms and mathematical foundations
- **Performance Analysis**: Benchmarking and complexity analysis
- **Examples and Tutorials**: Step-by-step examples demonstrating algorithm usage

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from primes.aks import AKSPrimalityTest

# Create an instance of the AKS test
aks = AKSPrimalityTest()

# Test if a number is prime
result = aks.is_prime(31)
print(f"31 is prime: {result}")  # True

# Get detailed step-by-step execution
result_detailed = aks.is_prime_detailed(31)
print(result_detailed)
```

## Algorithms Implemented

### AKS Primality Test
- **Time Complexity**: O(log^6 n) (theoretical), optimized versions available
- **Space Complexity**: O(log^3 n)
- **Deterministic**: Yes
- **Paper**: [PRIMES is in P](https://www.cse.iitk.ac.in/users/manindra/algebra/primality_v6.pdf)

## Project Structure

```
primes/
├── src/
│   └── primes/
│       ├── __init__.py
│       ├── aks/
│       │   ├── __init__.py
│       │   ├── core.py
│       │   └── optimizations.py
│       └── utils/
│           ├── __init__.py
│           ├── math_utils.py
│           └── polynomial.py
├── tests/
│   ├── __init__.py
│   ├── test_aks.py
│   └── test_utils.py
├── examples/
│   ├── basic_usage.py
│   ├── performance_comparison.py
│   └── step_by_step_aks.py
├── docs/
│   ├── algorithms/
│   │   └── aks.md
│   └── mathematical_foundations.md
├── benchmarks/
│   └── aks_benchmark.py
├── requirements.txt
├── setup.py
└── README.md
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

1. Agrawal, M., Kayal, N., & Saxena, N. (2004). PRIMES is in P. Annals of Mathematics, 160(2), 781-793.
2. [AKS Primality Test - Wikipedia](https://en.wikipedia.org/wiki/AKS_primality_test)

## Acknowledgments

- Inspired by the VaidhyaMegha/optimization_algorithms repository structure
- Mathematical foundations based on the original AKS paper
