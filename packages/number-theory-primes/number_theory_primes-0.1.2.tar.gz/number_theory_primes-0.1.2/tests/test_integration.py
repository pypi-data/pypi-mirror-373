#!/usr/bin/env python3
"""
Integration tests for the AKS primality test implementation.
"""

import pytest
from primes.aks import AKSPrimalityTest


class TestAKSIntegration:
    """Integration tests for the complete AKS algorithm."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.aks = AKSPrimalityTest()
    
    def test_known_primes(self):
        """Test known primes are correctly identified."""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        
        for p in primes:
            result = self.aks.is_prime(p)
            assert result, f"{p} should be identified as prime"
    
    def test_known_composites(self):
        """Test known composites are correctly identified."""
        composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28, 30]
        
        for c in composites:
            result = self.aks.is_prime(c)
            assert not result, f"{c} should be identified as composite"
    
    def test_detailed_analysis_prime(self):
        """Test detailed analysis for a known prime."""
        result = self.aks.is_prime_detailed(17)
        
        assert result['n'] == 17
        assert result['is_prime'] == True
        assert result['algorithm'] == 'AKS'
        assert isinstance(result['steps'], list)
        assert len(result['steps']) > 0
        
        # Check that the final step indicates prime
        final_step = result['steps'][-1]
        assert final_step['result'] == 'prime'
    
    def test_detailed_analysis_composite(self):
        """Test detailed analysis for a known composite."""
        result = self.aks.is_prime_detailed(25)
        
        assert result['n'] == 25
        assert result['is_prime'] == False
        assert result['algorithm'] == 'AKS'
        assert isinstance(result['steps'], list)
        assert len(result['steps']) > 0
        
        # Check that some step indicates composite
        composite_found = any(step['result'] == 'composite' for step in result['steps'])
        assert composite_found


def test_comprehensive_verification():
    """Comprehensive test function for manual verification."""
    aks = AKSPrimalityTest()
    
    # Known primes
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    # Known composites  
    composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28, 30]
    
    print("Testing known primes:")
    all_correct = True
    for p in primes:
        result = aks.is_prime(p)
        status = "✓" if result else "✗"
        if not result:
            all_correct = False
        print(f"{p:2d}: {status} ({'PRIME' if result else 'COMPOSITE'})")
    
    print("\nTesting known composites:")
    for c in composites:
        result = aks.is_prime(c)
        status = "✓" if not result else "✗"
        if result:
            all_correct = False
        print(f"{c:2d}: {status} ({'PRIME' if result else 'COMPOSITE'})")
    
    print(f"\nOverall result: {'✓ ALL CORRECT' if all_correct else '✗ SOME ERRORS'}")
    # Don't return anything to avoid pytest warning
    assert all_correct, "Some tests failed"


def test_detailed_17():
    """Test detailed output for 17."""
    aks = AKSPrimalityTest()
    result = aks.is_prime_detailed(17)
    
    print(f"\n=== Detailed Analysis for n = 17 ===")
    print(f"Number: {result['n']}")
    print(f"Is Prime: {result['is_prime']}")
    print(f"Algorithm: {result['algorithm']}")
    print("\nStep-by-step execution:")
    
    for step in result['steps']:
        print(f"Step {step['step']}: {step['description']} -> {step['result']}")


if __name__ == "__main__":
    test_comprehensive_verification()
    test_detailed_17()
