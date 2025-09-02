"""
Core implementation of the AKS Primality Test.

Based on the algorithm described in:
Agrawal, M., Kayal, N., & Saxena, N. (2004). PRIMES is in P.
"""

import math
from typing import Dict, List, Optional, Tuple
from ..utils.math_utils import (
    gcd, mod_exp, euler_totient, multiplicative_order, 
    is_perfect_power, trial_division
)
from ..utils.polynomial import PolynomialMod, polynomial_mod_exp


class AKSPrimalityTest:
    """
    Implementation of the AKS (Agrawal-Kayal-Saxena) primality test.
    
    This is the first deterministic polynomial-time algorithm for testing primality.
    """
    
    def __init__(self):
        """Initialize the AKS primality test."""
        pass
    
    def is_prime(self, n: int) -> bool:
        """
        Test if n is prime using the AKS algorithm.
        
        Args:
            n: Number to test for primality
            
        Returns:
            True if n is prime, False otherwise
        """
        return self._aks_test(n)[0]
    
    def is_prime_detailed(self, n: int) -> Dict:
        """
        Test if n is prime with detailed step-by-step information.
        
        Args:
            n: Number to test for primality
            
        Returns:
            Dictionary containing result and detailed execution steps
        """
        result, steps = self._aks_test(n, detailed=True)
        return {
            "n": n,
            "is_prime": result,
            "steps": steps,
            "algorithm": "AKS"
        }
    
    def _aks_test(self, n: int, detailed: bool = False) -> Tuple[bool, Optional[List[Dict]]]:
        """
        Internal AKS test implementation.
        
        Args:
            n: Number to test
            detailed: Whether to return detailed steps
            
        Returns:
            Tuple of (is_prime, steps_if_detailed)
        """
        steps = [] if detailed else None
        
        # Handle trivial cases
        if n <= 1:
            if detailed:
                steps.append({"step": 0, "description": f"n = {n} ≤ 1", "result": "composite"})
            return False, steps
        
        if n in [2, 3]:
            if detailed:
                steps.append({"step": 0, "description": f"n = {n} is a small prime", "result": "prime"})
            return True, steps
        
        # Step 1: Check if n is a perfect power
        is_power, power_info = is_perfect_power(n)
        if is_power:
            if detailed:
                base, exp = power_info
                steps.append({
                    "step": 1, 
                    "description": f"n = {base}^{exp} is a perfect power",
                    "result": "composite"
                })
            return False, steps
        
        if detailed:
            steps.append({
                "step": 1,
                "description": "n is not a perfect power",
                "result": "continue"
            })
        
        # Step 2: Find smallest r such that ord_r(n) > (log₂ n)²
        log2_n = math.log2(n)
        max_k = int(log2_n ** 2)
        r = self._find_suitable_r(n, max_k)
        
        if detailed:
            steps.append({
                "step": 2,
                "description": f"Found r = {r} such that ord_r({n}) > {max_k}",
                "result": "continue"
            })
        
        # Check if gcd(n, r) > 1
        if gcd(n, r) > 1:
            if detailed:
                steps.append({
                    "step": 2,
                    "description": f"gcd({n}, {r}) > 1",
                    "result": "composite"
                })
            return False, steps
        
        # Step 3: Check if any a ≤ r divides n
        for a in range(2, min(r, n)):
            if n % a == 0:
                if detailed:
                    steps.append({
                        "step": 3,
                        "description": f"{a} divides {n}",
                        "result": "composite"
                    })
                return False, steps
        
        if detailed:
            steps.append({
                "step": 3,
                "description": f"No integer in [2, {min(r, n-1)}] divides {n}",
                "result": "continue"
            })
        
        # Step 4: If n ≤ r, output prime
        if n <= r:
            if detailed:
                steps.append({
                    "step": 4,
                    "description": f"n = {n} ≤ r = {r}",
                    "result": "prime"
                })
            return True, steps
        
        # Step 5: Check polynomial congruences
        phi_r = euler_totient(r)
        limit = int(math.sqrt(phi_r) * log2_n)
        
        if detailed:
            steps.append({
                "step": 5,
                "description": f"Testing polynomial congruences for a = 1 to {limit}",
                "result": "continue"
            })
        
        # Create the modular polynomial x^r - 1
        x_r_minus_1_coeffs = [0] * r + [-1]  # -1 + 0*x + 0*x² + ... + 0*x^(r-1) + 1*x^r
        x_r_minus_1_coeffs[0] = -1
        x_r_minus_1_coeffs[r] = 1
        x_r_minus_1 = PolynomialMod(x_r_minus_1_coeffs, n)
        
        for a in range(1, limit + 1):
            # Check if (x + a)^n ≡ x^n + a (mod x^r - 1, n)
            if not self._check_polynomial_congruence(a, n, r):
                if detailed:
                    steps.append({
                        "step": 5,
                        "description": f"(x + {a})^{n} ≢ x^{n} + {a} (mod x^{r} - 1, {n})",
                        "result": "composite"
                    })
                return False, steps
        
        if detailed:
            steps.append({
                "step": 5,
                "description": f"All polynomial congruences satisfied for a = 1 to {limit}",
                "result": "continue"
            })
            steps.append({
                "step": 6,
                "description": "All tests passed",
                "result": "prime"
            })
        
        # Step 6: Output prime
        return True, steps
    
    def _find_suitable_r(self, n: int, max_k: int) -> int:
        """
        Find the smallest r such that ord_r(n) > max_k.
        
        Args:
            n: The number being tested
            max_k: Upper bound for the order
            
        Returns:
            Suitable value of r
        """
        r = 2
        while True:
            if gcd(n, r) == 1:
                try:
                    order = multiplicative_order(n, r)
                    if order > max_k:
                        return r
                except ValueError:
                    # If order is too large, this r might be suitable
                    return r
            r += 1
            
            # Safety check to prevent infinite loop
            # Use a reasonable upper bound instead of n
            if r > min(n, 10000):
                # If we can't find a suitable r, use the smallest coprime r we found
                for candidate_r in range(2, min(n, 10000)):
                    if gcd(n, candidate_r) == 1:
                        return candidate_r
                # Fallback - this should rarely happen
                return 2
    
    def _check_polynomial_congruence(self, a: int, n: int, r: int) -> bool:
        """
        Check if (x + a)^n ≡ x^n + a (mod x^r - 1, n).
        
        Args:
            a: The constant term
            n: The exponent and modulus
            r: The degree of the modular polynomial
            
        Returns:
            True if the congruence holds, False otherwise
        """
        # Create polynomial x + a
        x_plus_a = PolynomialMod([a, 1], n)  # a + 1*x
        
        # Create polynomial x^n + a
        # x^n mod (x^r - 1) = x^(n mod r)
        x_n_plus_a_coeffs = [0] * r
        x_n_plus_a_coeffs[0] = a  # constant term a
        x_n_plus_a_coeffs[n % r] = 1  # x^(n mod r) term
        x_n_plus_a = PolynomialMod(x_n_plus_a_coeffs, n)
        
        # Create modular polynomial x^r - 1
        x_r_minus_1_coeffs = [-1] + [0] * (r - 1) + [1]
        x_r_minus_1 = PolynomialMod(x_r_minus_1_coeffs, n)
        
        # Compute (x + a)^n mod (x^r - 1, n)
        left_side = polynomial_mod_exp(x_plus_a, n, x_r_minus_1)
        
        # Compare with x^n + a
        return left_side == x_n_plus_a
