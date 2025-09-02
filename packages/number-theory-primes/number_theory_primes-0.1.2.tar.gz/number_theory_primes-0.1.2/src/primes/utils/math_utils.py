"""
Mathematical utility functions for primality testing.
"""

import math
from typing import Tuple, Optional


def gcd(a: int, b: int) -> int:
    """
    Compute the greatest common divisor of two integers using Euclidean algorithm.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Greatest common divisor of a and b
    """
    while b:
        a, b = b, a % b
    return abs(a)


def mod_exp(base: int, exp: int, mod: int) -> int:
    """
    Compute (base^exp) % mod efficiently using binary exponentiation.
    
    Args:
        base: Base number
        exp: Exponent
        mod: Modulus
        
    Returns:
        (base^exp) % mod
    """
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return result


def euler_totient(n: int) -> int:
    """
    Compute Euler's totient function φ(n).
    
    Args:
        n: Input number
        
    Returns:
        φ(n) - count of integers from 1 to n that are coprime to n
    """
    result = n
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    if n > 1:
        result -= result // n
    return result


def multiplicative_order(a: int, n: int) -> int:
    """
    Find the multiplicative order of a modulo n.
    
    Args:
        a: Base number
        n: Modulus
        
    Returns:
        Smallest positive integer k such that a^k ≡ 1 (mod n)
    """
    if gcd(a, n) != 1:
        raise ValueError("a and n must be coprime")
    
    order = 1
    current = a % n
    while current != 1:
        current = (current * a) % n
        order += 1
        if order > n:  # Safety check
            raise ValueError("Order not found within reasonable bounds")
    return order


def is_perfect_power(n: int) -> Tuple[bool, Optional[Tuple[int, int]]]:
    """
    Check if n is a perfect power (n = a^b for integers a > 1, b > 1).
    
    Args:
        n: Number to check
        
    Returns:
        Tuple of (is_perfect_power, (base, exponent) or None)
    """
    if n <= 1:
        return False, None
    
    max_exp = int(math.log2(n)) + 1
    
    for b in range(2, max_exp + 1):
        a = round(n ** (1.0 / b))
        
        # Check a and a±1 to handle floating point precision issues
        for candidate in [a - 1, a, a + 1]:
            if candidate > 1 and candidate ** b == n:
                return True, (candidate, b)
    
    return False, None


def trial_division(n: int, limit: Optional[int] = None) -> Optional[int]:
    """
    Perform trial division to find a factor of n.
    
    Args:
        n: Number to factor
        limit: Maximum divisor to check (default: sqrt(n))
        
    Returns:
        A factor of n if found, None if n is prime up to the limit
    """
    if n <= 1:
        return None
    if n <= 3:
        return None  # 2 and 3 are prime
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    
    if limit is None:
        limit = int(math.sqrt(n)) + 1
    
    # Check divisors of the form 6k ± 1
    i = 5
    while i <= limit:
        if n % i == 0:
            return i
        if n % (i + 2) == 0:
            return i + 2
        i += 6
    
    return None
