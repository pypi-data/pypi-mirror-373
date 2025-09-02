"""
Utility functions for primality testing algorithms.
"""

from .math_utils import (
    gcd,
    mod_exp,
    euler_totient,
    multiplicative_order,
    is_perfect_power,
    trial_division
)

from .polynomial import (
    PolynomialMod,
    polynomial_mod_exp,
    polynomial_remainder
)

__all__ = [
    "gcd",
    "mod_exp", 
    "euler_totient",
    "multiplicative_order",
    "is_perfect_power",
    "trial_division",
    "PolynomialMod",
    "polynomial_mod_exp",
    "polynomial_remainder"
]
