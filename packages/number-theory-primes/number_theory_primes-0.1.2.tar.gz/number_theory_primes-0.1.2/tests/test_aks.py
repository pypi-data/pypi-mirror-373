"""
Unit tests for the AKS primality test implementation.
"""

import pytest
from primes.aks import AKSPrimalityTest


class TestAKSPrimalityTest:
    """Test cases for the AKS primality test."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.aks = AKSPrimalityTest()
    
    def test_small_primes(self):
        """Test small prime numbers."""
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        for p in small_primes:
            assert self.aks.is_prime(p), f"{p} should be prime"
    
    def test_small_composites(self):
        """Test small composite numbers."""
        small_composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28, 30]
        for c in small_composites:
            assert not self.aks.is_prime(c), f"{c} should be composite"
    
    def test_edge_cases(self):
        """Test edge cases."""
        assert not self.aks.is_prime(0), "0 should be composite"
        assert not self.aks.is_prime(1), "1 should be composite"
        assert self.aks.is_prime(2), "2 should be prime"
        assert self.aks.is_prime(3), "3 should be prime"
    
    def test_perfect_powers(self):
        """Test perfect powers (should be composite)."""
        perfect_powers = [4, 8, 9, 16, 25, 27, 32, 49, 64, 81, 100, 121, 125, 128]
        for pp in perfect_powers:
            assert not self.aks.is_prime(pp), f"{pp} is a perfect power and should be composite"
    
    def test_detailed_output(self):
        """Test detailed output format."""
        result = self.aks.is_prime_detailed(31)
        
        assert isinstance(result, dict)
        assert "n" in result
        assert "is_prime" in result
        assert "steps" in result
        assert "algorithm" in result
        
        assert result["n"] == 31
        assert result["is_prime"] == True
        assert result["algorithm"] == "AKS"
        assert isinstance(result["steps"], list)
        assert len(result["steps"]) > 0
        
        # Check that each step has required fields
        for step in result["steps"]:
            assert "step" in step
            assert "description" in step
            assert "result" in step
    
    def test_larger_primes(self):
        """Test some larger prime numbers."""
        larger_primes = [37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
        for p in larger_primes:
            assert self.aks.is_prime(p), f"{p} should be prime"
    
    def test_larger_composites(self):
        """Test some larger composite numbers."""
        larger_composites = [33, 35, 39, 45, 49, 51, 55, 57, 63, 65, 69, 75, 77, 81, 85, 87, 91, 93, 95, 99]
        for c in larger_composites:
            assert not self.aks.is_prime(c), f"{c} should be composite"
    
    def test_consistency(self):
        """Test that multiple calls return consistent results."""
        test_numbers = [17, 25, 31, 49, 97]
        for n in test_numbers:
            result1 = self.aks.is_prime(n)
            result2 = self.aks.is_prime(n)
            assert result1 == result2, f"Inconsistent results for {n}"


if __name__ == "__main__":
    pytest.main([__file__])
