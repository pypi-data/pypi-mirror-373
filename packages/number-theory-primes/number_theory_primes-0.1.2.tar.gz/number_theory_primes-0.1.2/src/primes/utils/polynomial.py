"""
Polynomial operations for the AKS primality test.
"""

from typing import List, Dict
import math


class PolynomialMod:
    """
    Represents a polynomial with coefficients modulo n.
    Used for polynomial arithmetic in the AKS algorithm.
    """
    
    def __init__(self, coefficients: List[int], modulus: int):
        """
        Initialize a polynomial modulo n.
        
        Args:
            coefficients: List of coefficients [a0, a1, a2, ...] for a0 + a1*x + a2*x^2 + ...
            modulus: Modulus for coefficient arithmetic
        """
        self.modulus = modulus
        self.coeffs = [c % modulus for c in coefficients]
        self._trim()
    
    def _trim(self):
        """Remove leading zero coefficients."""
        while len(self.coeffs) > 1 and self.coeffs[-1] == 0:
            self.coeffs.pop()
    
    def degree(self) -> int:
        """Return the degree of the polynomial."""
        return len(self.coeffs) - 1
    
    def __add__(self, other: 'PolynomialMod') -> 'PolynomialMod':
        """Add two polynomials."""
        if self.modulus != other.modulus:
            raise ValueError("Polynomials must have the same modulus")
        
        max_len = max(len(self.coeffs), len(other.coeffs))
        result = []
        
        for i in range(max_len):
            a = self.coeffs[i] if i < len(self.coeffs) else 0
            b = other.coeffs[i] if i < len(other.coeffs) else 0
            result.append((a + b) % self.modulus)
        
        return PolynomialMod(result, self.modulus)
    
    def __sub__(self, other: 'PolynomialMod') -> 'PolynomialMod':
        """Subtract two polynomials."""
        if self.modulus != other.modulus:
            raise ValueError("Polynomials must have the same modulus")
        
        max_len = max(len(self.coeffs), len(other.coeffs))
        result = []
        
        for i in range(max_len):
            a = self.coeffs[i] if i < len(self.coeffs) else 0
            b = other.coeffs[i] if i < len(other.coeffs) else 0
            result.append((a - b) % self.modulus)
        
        return PolynomialMod(result, self.modulus)
    
    def __mul__(self, other: 'PolynomialMod') -> 'PolynomialMod':
        """Multiply two polynomials."""
        if self.modulus != other.modulus:
            raise ValueError("Polynomials must have the same modulus")
        
        if not self.coeffs or not other.coeffs:
            return PolynomialMod([0], self.modulus)
        
        result_degree = len(self.coeffs) + len(other.coeffs) - 1
        result = [0] * result_degree
        
        for i in range(len(self.coeffs)):
            for j in range(len(other.coeffs)):
                result[i + j] = (result[i + j] + self.coeffs[i] * other.coeffs[j]) % self.modulus
        
        return PolynomialMod(result, self.modulus)
    
    def __eq__(self, other: 'PolynomialMod') -> bool:
        """Check if two polynomials are equal."""
        if self.modulus != other.modulus:
            return False
        return self.coeffs == other.coeffs
    
    def __repr__(self) -> str:
        """String representation of the polynomial."""
        if not self.coeffs:
            return "0"
        
        terms = []
        for i, coeff in enumerate(self.coeffs):
            if coeff == 0:
                continue
            
            if i == 0:
                terms.append(str(coeff))
            elif i == 1:
                if coeff == 1:
                    terms.append("x")
                else:
                    terms.append(f"{coeff}*x")
            else:
                if coeff == 1:
                    terms.append(f"x^{i}")
                else:
                    terms.append(f"{coeff}*x^{i}")
        
        if not terms:
            return "0"
        
        return " + ".join(reversed(terms)) + f" (mod {self.modulus})"


def polynomial_remainder(dividend: PolynomialMod, divisor: PolynomialMod) -> PolynomialMod:
    """
    Compute polynomial remainder using polynomial long division.
    
    Args:
        dividend: Polynomial to be divided
        divisor: Polynomial to divide by
        
    Returns:
        Remainder polynomial
    """
    if divisor.modulus != dividend.modulus:
        raise ValueError("Polynomials must have the same modulus")
    
    if all(c == 0 for c in divisor.coeffs):
        raise ValueError("Cannot divide by zero polynomial")
    
    remainder = PolynomialMod(dividend.coeffs[:], dividend.modulus)
    divisor_degree = divisor.degree()
    divisor_lead = divisor.coeffs[-1]
    
    # Find modular inverse of leading coefficient
    try:
        divisor_lead_inv = pow(divisor_lead, -1, divisor.modulus)
    except ValueError:
        # If modular inverse doesn't exist, we can't perform division
        # This happens when gcd(divisor_lead, modulus) != 1
        return remainder
    
    while remainder.degree() >= divisor_degree and not all(c == 0 for c in remainder.coeffs):
        # Calculate the leading term of the quotient
        lead_coeff = (remainder.coeffs[-1] * divisor_lead_inv) % remainder.modulus
        lead_degree = remainder.degree() - divisor_degree
        
        # Create the term to subtract
        term_coeffs = [0] * (lead_degree + 1)
        term_coeffs[-1] = lead_coeff
        term = PolynomialMod(term_coeffs, remainder.modulus)
        
        # Multiply term by divisor and subtract from remainder
        to_subtract = term * divisor
        remainder = remainder - to_subtract
    
    return remainder


def polynomial_mod_exp(base: PolynomialMod, exp: int, mod_poly: PolynomialMod) -> PolynomialMod:
    """
    Compute (base^exp) mod (mod_poly) efficiently.
    
    Args:
        base: Base polynomial
        exp: Exponent
        mod_poly: Modular polynomial (e.g., x^r - 1)
        
    Returns:
        (base^exp) mod mod_poly
    """
    if exp == 0:
        return PolynomialMod([1], base.modulus)
    
    result = PolynomialMod([1], base.modulus)
    base = polynomial_remainder(base, mod_poly)
    
    while exp > 0:
        if exp % 2 == 1:
            result = polynomial_remainder(result * base, mod_poly)
        exp = exp >> 1
        base = polynomial_remainder(base * base, mod_poly)
    
    return result
