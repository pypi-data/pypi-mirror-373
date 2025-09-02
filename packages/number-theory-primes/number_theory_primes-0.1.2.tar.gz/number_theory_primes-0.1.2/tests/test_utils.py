"""
Unit tests for utility functions.
"""

import pytest
from primes.utils.math_utils import (
    gcd, mod_exp, euler_totient, multiplicative_order,
    is_perfect_power, trial_division
)
from primes.utils.polynomial import PolynomialMod, polynomial_remainder, polynomial_mod_exp


class TestMathUtils:
    """Test mathematical utility functions."""
    
    def test_gcd(self):
        """Test GCD function."""
        assert gcd(12, 8) == 4
        assert gcd(17, 13) == 1
        assert gcd(0, 5) == 5
        assert gcd(5, 0) == 5
        assert gcd(-12, 8) == 4
    
    def test_mod_exp(self):
        """Test modular exponentiation."""
        assert mod_exp(2, 10, 1000) == 1024 % 1000
        assert mod_exp(3, 5, 7) == 243 % 7
        assert mod_exp(2, 0, 5) == 1
        assert mod_exp(0, 5, 7) == 0
    
    def test_euler_totient(self):
        """Test Euler's totient function."""
        assert euler_totient(1) == 1
        assert euler_totient(2) == 1
        assert euler_totient(6) == 2  # φ(6) = φ(2×3) = 6×(1-1/2)×(1-1/3) = 2
        assert euler_totient(9) == 6  # φ(9) = φ(3²) = 9×(1-1/3) = 6
        assert euler_totient(17) == 16  # φ(prime) = prime - 1
    
    def test_multiplicative_order(self):
        """Test multiplicative order function."""
        assert multiplicative_order(2, 7) == 3  # 2³ ≡ 1 (mod 7)
        assert multiplicative_order(3, 7) == 6  # 3⁶ ≡ 1 (mod 7)
        
        with pytest.raises(ValueError):
            multiplicative_order(2, 4)  # gcd(2,4) = 2 ≠ 1
    
    def test_is_perfect_power(self):
        """Test perfect power detection."""
        assert is_perfect_power(8) == (True, (2, 3))
        assert is_perfect_power(9) == (True, (3, 2))
        # 16 can be 2^4 or 4^2, both are valid - check for either
        result = is_perfect_power(16)
        assert result[0] == True
        assert result[1] in [(2, 4), (4, 2)]
        assert is_perfect_power(7) == (False, None)
        assert is_perfect_power(1) == (False, None)
    
    def test_trial_division(self):
        """Test trial division."""
        assert trial_division(15) == 3
        assert trial_division(21) == 3
        assert trial_division(17) is None  # 17 is prime
        assert trial_division(4) == 2


class TestPolynomialMod:
    """Test polynomial modular arithmetic."""
    
    def test_polynomial_creation(self):
        """Test polynomial creation and basic properties."""
        p = PolynomialMod([1, 2, 3], 5)  # 1 + 2x + 3x²
        assert p.coeffs == [1, 2, 3]
        assert p.modulus == 5
        assert p.degree() == 2
    
    def test_polynomial_addition(self):
        """Test polynomial addition."""
        p1 = PolynomialMod([1, 2], 5)  # 1 + 2x
        p2 = PolynomialMod([3, 1], 5)  # 3 + x
        result = p1 + p2
        assert result.coeffs == [4, 3]  # 4 + 3x
    
    def test_polynomial_subtraction(self):
        """Test polynomial subtraction."""
        p1 = PolynomialMod([5, 3], 7)  # 5 + 3x
        p2 = PolynomialMod([2, 1], 7)  # 2 + x
        result = p1 - p2
        assert result.coeffs == [3, 2]  # 3 + 2x
    
    def test_polynomial_multiplication(self):
        """Test polynomial multiplication."""
        p1 = PolynomialMod([1, 1], 5)  # 1 + x
        p2 = PolynomialMod([1, 1], 5)  # 1 + x
        result = p1 * p2
        assert result.coeffs == [1, 2, 1]  # 1 + 2x + x²
    
    def test_polynomial_equality(self):
        """Test polynomial equality."""
        p1 = PolynomialMod([1, 2, 3], 5)
        p2 = PolynomialMod([1, 2, 3], 5)
        p3 = PolynomialMod([1, 2, 4], 5)
        
        assert p1 == p2
        assert p1 != p3
    
    def test_polynomial_remainder(self):
        """Test polynomial remainder operation."""
        # Test x² mod (x - 1) = 1
        dividend = PolynomialMod([0, 0, 1], 5)  # x²
        divisor = PolynomialMod([-1, 1], 5)     # x - 1
        remainder = polynomial_remainder(dividend, divisor)
        assert remainder.coeffs == [1]  # Should be 1
    
    def test_polynomial_mod_exp(self):
        """Test polynomial modular exponentiation."""
        base = PolynomialMod([1, 1], 5)  # 1 + x
        mod_poly = PolynomialMod([-1, 0, 1], 5)  # x² - 1
        result = polynomial_mod_exp(base, 2, mod_poly)
        # (1 + x)² = 1 + 2x + x² ≡ 2x + 2 (mod x² - 1)
        # Since x² ≡ 1 (mod x² - 1), we get 1 + 2x + 1 = 2 + 2x
        expected = PolynomialMod([2, 2], 5)
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
