"""
Primes - Advanced Primality Testing Algorithms

A Python library implementing state-of-the-art primality testing algorithms,
starting with the AKS (Agrawal-Kayal-Saxena) primality test.
"""

__version__ = "0.1.0"
__author__ = "Madhulatha Sandeep"

from .aks import AKSPrimalityTest

__all__ = ["AKSPrimalityTest"]
