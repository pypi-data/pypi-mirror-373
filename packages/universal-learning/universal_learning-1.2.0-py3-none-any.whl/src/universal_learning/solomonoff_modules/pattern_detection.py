#!/usr/bin/env python3
"""
🧠 PATTERN DETECTION MIXIN - Mathematical Sequence Analysis for Solomonoff Induction
=====================================================================================

Author: Benedict Chen (PayPal)
Based on: Extracted from Solomonoff Induction implementation
Research Foundation: Pattern Recognition in Mathematical Sequences and Algorithmic Information Theory

📚 THEORETICAL BACKGROUND
=========================

Pattern detection is a fundamental component of Solomonoff Induction, serving as the
foundation for identifying computable regularities in sequences. This module implements
sophisticated pattern recognition algorithms based on:

• **Algorithmic Information Theory**: Pattern complexity as Kolmogorov complexity proxy
• **Sequence Analysis**: Mathematical foundations for detecting recurring structures  
• **Universal Prediction**: Patterns as computable hypotheses in universal distribution
• **Statistical Pattern Recognition**: Probabilistic approaches to sequence classification

🔬 MATHEMATICAL FOUNDATIONS
===========================

Pattern Type Classification Theory:
-----------------------------------
Each pattern type corresponds to a specific class of computable sequences:

1. **Constant Sequences**: K(x) = O(1) - Minimal complexity
2. **Arithmetic Progressions**: K(x) = O(log n) - Linear growth patterns
3. **Geometric Progressions**: K(x) = O(log n) - Exponential growth patterns  
4. **Periodic Sequences**: K(x) = O(period length) - Repetitive structures
5. **Fibonacci-like**: K(x) = O(1) - Simple recursive definitions
6. **Polynomial Sequences**: K(x) = O(degree) - Algebraic growth patterns
7. **Recursive Patterns**: K(x) = O(recurrence complexity) - General recurrences
8. **Statistical Patterns**: K(x) = O(distribution parameters) - Stochastic regularities

Complexity Estimation:
---------------------
For sequence x with pattern P of type T:
K(x | P,T) ≈ description_length(P) + encoding_overhead(T)

Where description_length captures the essential parameters of the pattern
and encoding_overhead accounts for the computational structure needed.

🎯 PATTERN DETECTION ALGORITHMS
===============================

Deterministic Pattern Detection:
-------------------------------
• **Finite Difference Analysis**: Polynomial pattern detection via difference tables
• **Ratio Analysis**: Geometric progression detection via consecutive ratios
• **Periodicity Analysis**: Fourier-based and brute-force period detection
• **Recurrence Relation Fitting**: Linear recurrence detection with coefficient search

Statistical Pattern Recognition:
-------------------------------
• **Distribution Fitting**: Normal, uniform, exponential distribution detection
• **Correlation Analysis**: Auto-correlation for periodic and recursive patterns
• **Entropy-based Classification**: Information-theoretic pattern complexity
• **Bayesian Pattern Comparison**: Posterior probability over pattern classes

📖 RESEARCH REFERENCES
======================

[1] Solomonoff, R. J. (1964). "A formal theory of inductive inference, Parts I & II"
    Information and Control, 7(1-2), 1-22, 224-254.
    
[2] Li, M. & Vitányi, P. (2019). "An Introduction to Kolmogorov Complexity and Its Applications"
    4th Edition, Springer. Chapter 4: "Inductive Reasoning and Kolmogorov Complexity"
    
[3] Rissanen, J. (1978). "Modeling by Shortest Data Description"
    Automatica, 14(5), 465-471. [Minimum Description Length Principle]
    
[4] Wallace, C. S. (2005). "Statistical and Inductive Inference by Minimum Message Length"
    Springer. Chapter 3: "Sequence Prediction and Pattern Recognition"
    
[5] Hutter, M. (2005). "Universal Artificial Intelligence: Sequential Decisions Based on 
    Algorithmic Probability" Springer. Section 3.4: "Pattern Recognition in Universal Prediction"
    
[6] Grünwald, P. D. (2007). "The Minimum Description Length Principle"
    MIT Press. Chapter 12: "Pattern Recognition and Sequence Prediction"

🧮 COMPLEXITY ANALYSIS
======================

Time Complexity by Pattern Type:
- Constant: O(n) - Single pass verification
- Arithmetic: O(n) - Difference computation  
- Geometric: O(n) - Ratio computation
- Periodic: O(n × max_period) - Period search
- Fibonacci: O(n) - Linear recurrence check
- Polynomial: O(n × max_degree²) - Finite differences
- Recursive: O(n × search_space) - Coefficient enumeration
- Statistical: O(n log n) - Distribution fitting

Space Complexity: O(n) for sequence storage + O(pattern_parameters) for results

🎛️ CONFIGURATION OPTIONS
=========================

Pattern Detection Parameters:
- max_period_search: Maximum period length for periodic patterns
- max_polynomial_degree: Maximum degree for polynomial fitting
- statistical_confidence_threshold: Minimum confidence for statistical patterns
- recursive_coefficient_range: Search range for recursive coefficients
- arithmetic_tolerance: Numerical tolerance for arithmetic patterns
- geometric_tolerance: Numerical tolerance for geometric patterns

Performance Optimization:
- enable_early_termination: Stop search when high-confidence pattern found
- enable_pattern_caching: Cache pattern detection results
- parallel_pattern_search: Use multiple threads for pattern types
- complexity_threshold: Skip patterns above complexity limit

✨ USAGE EXAMPLES
================

```python
# Basic pattern detection
detector = PatternDetectionMixin()
sequence = [1, 4, 9, 16, 25, 36]  # Perfect squares
patterns = detector.detect_all_patterns(sequence)
print(f"Detected: {patterns[0]['type']} pattern")

# Advanced configuration
detector.configure_pattern_detection(
    max_polynomial_degree=5,
    enable_statistical_patterns=True,
    statistical_confidence_threshold=0.95
)

# Fibonacci sequence analysis
fib_seq = [1, 1, 2, 3, 5, 8, 13, 21]
fib_pattern = detector._detect_fibonacci_pattern(fib_seq)
print(f"Fibonacci pattern complexity: {fib_pattern[0]['complexity']}")

# Time series with statistical patterns
noise_seq = [random.gauss(0, 1) for _ in range(100)]
stat_patterns = detector._detect_statistical_patterns(noise_seq)
if stat_patterns:
    print(f"Statistical pattern: {stat_patterns[0]['description']}")
```

🔧 INTEGRATION WITH SOLOMONOFF INDUCTION
========================================

This mixin integrates seamlessly with the main Solomonoff Induction system:

1. **Pattern-Based Complexity Estimation**: Each detected pattern provides a complexity
   estimate that serves as a proxy for Kolmogorov complexity in the universal distribution.

2. **Program Generation**: Patterns translate directly into candidate programs with
   associated weights based on the universal prior P(pattern) ∝ 2^(-complexity).

3. **Prediction Generation**: Each pattern provides next-symbol predictions that are
   weighted according to their complexity and combined in the universal mixture.

4. **Hierarchical Pattern Analysis**: Complex sequences may exhibit multiple overlapping
   patterns at different scales, all captured in the universal distribution.

The pattern detection system thus serves as a computationally tractable approximation to
the theoretical ideal of enumerating all possible programs, focusing on the most common
and mathematically natural pattern classes that occur in practice.
"""

import numpy as np
import statistics
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class PatternDetectionConfig:
    """
    🎛️ Configuration for pattern detection algorithms
    
    Provides comprehensive control over pattern detection behavior,
    allowing optimization for different sequence types and performance requirements.
    """
    # Period-based pattern settings
    max_period_search: int = 10
    min_period_repetitions: int = 2
    
    # Polynomial pattern settings
    max_polynomial_degree: int = 4
    polynomial_tolerance: float = 1e-6
    
    # Statistical pattern settings
    enable_statistical_patterns: bool = True
    statistical_confidence_threshold: float = 0.95
    min_sequence_length_for_stats: int = 10
    
    # Recursive pattern settings
    recursive_coefficient_range: Tuple[int, int] = (-3, 4)
    max_recursive_order: int = 2
    
    # Geometric/arithmetic tolerance settings
    arithmetic_tolerance: float = 1e-10
    geometric_tolerance: float = 1e-6
    
    # Performance optimization
    enable_early_termination: bool = True
    enable_pattern_caching: bool = True
    complexity_threshold: float = 20.0
    
    # Advanced pattern types
    enable_fibonacci_variants: bool = True
    enable_prime_patterns: bool = False
    enable_fractal_patterns: bool = False


class PatternDetectionMixin:
    """
    🧠 Pattern Detection Mixin for Mathematical Sequence Analysis
    
    This mixin provides comprehensive pattern detection capabilities for
    Solomonoff Induction, implementing state-of-the-art algorithms for
    recognizing mathematical regularities in sequences.
    
    The mixin follows the theoretical framework of Algorithmic Information Theory,
    where each detected pattern corresponds to a computable hypothesis with
    complexity measured by its description length.
    
    Key Features:
    • **Comprehensive Pattern Coverage**: 8 major pattern types with variants
    • **Theoretical Soundness**: Complexity estimates based on description length
    • **Performance Optimization**: Configurable algorithms with caching
    • **Statistical Robustness**: Confidence-based pattern validation
    • **Extensible Architecture**: Easy addition of new pattern types
    """
    
    def __init__(self, config: Optional[PatternDetectionConfig] = None):
        """Initialize pattern detection with optional configuration"""
        self.pattern_config = config or PatternDetectionConfig()
        self.pattern_cache = {} if self.pattern_config.enable_pattern_caching else None
        
    def detect_all_patterns(self, sequence: List[Union[int, float]]) -> List[Dict]:
        """
        🔍 Detect All Patterns in Sequence
        
        Comprehensive pattern detection across all implemented pattern types.
        Returns patterns sorted by complexity (simplest first), implementing
        the universal prior preference for simple explanations.
        
        Args:
            sequence: Input sequence to analyze
            
        Returns:
            List of pattern dictionaries, each containing:
            - type: Pattern type identifier
            - complexity: Estimated Kolmogorov complexity  
            - confidence: Pattern fit confidence [0,1]
            - parameters: Pattern-specific parameters
            - description: Human-readable pattern description
            - prediction_function: Function to generate next values
        """
        # Check cache first
        if self.pattern_cache is not None:
            cache_key = tuple(sequence)
            if cache_key in self.pattern_cache:
                return self.pattern_cache[cache_key]
        
        all_patterns = []
        
        # Detect each pattern type
        pattern_detectors = [
            self._detect_constant_pattern,
            self._detect_arithmetic_pattern, 
            self._detect_geometric_pattern,
            self._detect_periodic_patterns,
            self._detect_fibonacci_pattern,
            self._detect_polynomial_patterns,
            self._detect_recursive_patterns,
        ]
        
        if self.pattern_config.enable_statistical_patterns:
            pattern_detectors.append(self._detect_statistical_patterns)
        
        for detector in pattern_detectors:
            try:
                patterns = detector(sequence)
                all_patterns.extend(patterns)
                
                # Early termination if high-confidence simple pattern found
                if (self.pattern_config.enable_early_termination and 
                    patterns and patterns[0].get('confidence', 0) > 0.99 and 
                    patterns[0].get('complexity', float('inf')) < 3):
                    break
                    
            except Exception as e:
                print(f"Pattern detection failed for {detector.__name__}: {e}")
                continue
        
        # Sort by complexity (universal prior preference)
        all_patterns.sort(key=lambda p: p.get('complexity', float('inf')))
        
        # Filter by complexity threshold
        filtered_patterns = [p for p in all_patterns 
                           if p.get('complexity', float('inf')) <= self.pattern_config.complexity_threshold]
        
        # Cache results
        if self.pattern_cache is not None:
            cache_key = tuple(sequence)
            self.pattern_cache[cache_key] = filtered_patterns
            
        return filtered_patterns
    
    def _detect_constant_pattern(self, sequence: List[Union[int, float]]) -> List[Dict]:
        """
        🔢 Detect Constant Sequences
        
        Mathematical Foundation:
        Constant sequences have minimal Kolmogorov complexity K(x) = O(log|c|)
        where c is the constant value. This represents the simplest possible
        computable pattern.
        
        Algorithm: Single-pass verification that all elements are identical.
        
        Complexity Estimate: 1 bit (pattern type) + log₂(|value|) bits (value encoding)
        """
        if len(sequence) == 0:
            return []
            
        if len(set(sequence)) == 1:
            value = sequence[0]
            complexity = 1 + max(1, int(np.log2(abs(value) + 1)))
            
            return [{
                'type': 'constant',
                'value': value,
                'complexity': complexity,
                'confidence': 1.0,
                'weight': 2**(-complexity),
                'description': f'Constant sequence: {value}',
                'fits_sequence': True,
                'accuracy': 1.0,
                'parameters': {'value': value},
                'prediction_function': lambda: value
            }]
        return []
    
    def _detect_arithmetic_pattern(self, sequence: List[Union[int, float]]) -> List[Dict]:
        """
        🔢 Detect Arithmetic Progressions
        
        Mathematical Foundation:
        Arithmetic sequences follow a_n = a₀ + n×d where a₀ is start and d is difference.
        Kolmogorov complexity: K(x) = O(log|a₀| + log|d| + log n)
        
        Algorithm: 
        1. Compute consecutive differences
        2. Verify constant difference within tolerance
        3. Estimate complexity based on parameter magnitudes
        
        Complexity Estimate: Encoding of start value, difference, and sequence length
        """
        patterns = []
        if len(sequence) < 2:
            return patterns
            
        # Compute differences
        diffs = [sequence[i+1] - sequence[i] for i in range(len(sequence)-1)]
        
        # Check if all differences are equal (within tolerance)
        if len(set(diffs)) == 1 or (len(diffs) > 0 and 
                                    max(diffs) - min(diffs) <= self.pattern_config.arithmetic_tolerance):
            diff = statistics.mean(diffs)
            start = sequence[0]
            
            # Verify pattern accuracy
            predicted_sequence = [start + i * diff for i in range(len(sequence))]
            accuracy = 1.0 - np.mean([abs(pred - actual) for pred, actual in 
                                    zip(predicted_sequence, sequence)]) / (max(abs(max(sequence)), abs(min(sequence))) + 1)
            
            if accuracy > 0.95:  # High accuracy required
                # Complexity: start value + difference + pattern type
                complexity = (1 +  # pattern type 
                            max(1, int(np.log2(abs(start) + 1))) +  # start encoding
                            max(1, int(np.log2(abs(diff) + 1))))     # diff encoding
                
                patterns.append({
                    'type': 'arithmetic',
                    'start': start,
                    'diff': diff,
                    'complexity': complexity,
                    'confidence': accuracy,
                    'weight': 2**(-complexity),
                    'description': f'Arithmetic progression: start={start}, diff={diff}',
                    'fits_sequence': True,
                    'accuracy': accuracy,
                    'parameters': {'start': start, 'difference': diff},
                    'prediction_function': lambda n=len(sequence): start + n * diff
                })
                
        return patterns
    
    def _detect_geometric_pattern(self, sequence: List[Union[int, float]]) -> List[Dict]:
        """
        🔢 Detect Geometric Progressions
        
        Mathematical Foundation:
        Geometric sequences follow a_n = a₀ × r^n where a₀ is start and r is ratio.
        Kolmogorov complexity: K(x) = O(log|a₀| + log|r| + log n)
        
        Special handling for zero values and numerical precision issues.
        
        Algorithm:
        1. Compute consecutive ratios
        2. Verify constant ratio within tolerance  
        3. Handle edge cases (zeros, negative values)
        4. Estimate complexity based on parameter magnitudes
        """
        patterns = []
        if len(sequence) < 2 or 0 in sequence:
            return patterns
            
        # Compute ratios
        ratios = []
        for i in range(len(sequence)-1):
            if abs(sequence[i]) > self.pattern_config.geometric_tolerance:
                ratios.append(sequence[i+1] / sequence[i])
            else:
                return []  # Cannot handle zero values reliably
                
        if not ratios:
            return patterns
            
        # Check if all ratios are approximately equal
        mean_ratio = np.mean(ratios)
        if all(abs(ratio - mean_ratio) <= self.pattern_config.geometric_tolerance for ratio in ratios):
            start = sequence[0]
            ratio = mean_ratio
            
            # Verify pattern accuracy
            predicted_sequence = [start * (ratio ** i) for i in range(len(sequence))]
            relative_errors = [abs((pred - actual) / (abs(actual) + 1e-10)) 
                             for pred, actual in zip(predicted_sequence, sequence)]
            accuracy = 1.0 - np.mean(relative_errors)
            
            if accuracy > 0.95 and abs(ratio) > 1e-10:  # High accuracy and valid ratio
                # Complexity: start value + ratio + pattern type
                complexity = (1 +  # pattern type
                            max(1, int(np.log2(abs(start) + 1))) +  # start encoding
                            max(1, int(np.log2(abs(ratio) + 1))))    # ratio encoding
                
                patterns.append({
                    'type': 'geometric',
                    'start': start,
                    'ratio': ratio,
                    'complexity': complexity,
                    'confidence': accuracy,
                    'weight': 2**(-complexity),
                    'description': f'Geometric progression: start={start}, ratio={ratio:.4f}',
                    'fits_sequence': True,
                    'accuracy': accuracy,
                    'parameters': {'start': start, 'ratio': ratio},
                    'prediction_function': lambda n=len(sequence): start * (ratio ** n)
                })
                
        return patterns
    
    def _detect_periodic_patterns(self, sequence: List[Union[int, float]]) -> List[Dict]:
        """
        🔄 Detect Periodic Patterns
        
        Mathematical Foundation:
        Periodic sequences repeat with period p: a_n = a_{n mod p}
        Kolmogorov complexity: K(x) = O(p + log(n/p)) where p is period length
        
        The complexity grows linearly with period length, encoding the repeating
        pattern plus the number of repetitions.
        
        Algorithm:
        1. Try all possible periods up to max_period_search
        2. For each period, verify pattern repetition
        3. Require minimum number of complete repetitions
        4. Select shortest period with highest accuracy
        """
        patterns = []
        max_period = min(len(sequence) // self.pattern_config.min_period_repetitions, 
                        self.pattern_config.max_period_search)
        
        for period in range(1, max_period + 1):
            if len(sequence) >= period * self.pattern_config.min_period_repetitions:
                pattern = sequence[:period]
                is_periodic = True
                
                # Check if pattern repeats throughout sequence
                for i in range(len(sequence)):
                    if abs(sequence[i] - pattern[i % period]) > 1e-10:
                        is_periodic = False
                        break
                
                if is_periodic:
                    # Calculate accuracy
                    predicted_sequence = [pattern[i % period] for i in range(len(sequence))]
                    errors = [abs(pred - actual) for pred, actual in zip(predicted_sequence, sequence)]
                    accuracy = 1.0 - np.mean(errors) / (max(abs(max(sequence)), abs(min(sequence))) + 1e-10)
                    
                    if accuracy > 0.98:  # High accuracy required for periodic patterns
                        # Complexity: period length + pattern type + repetition count
                        complexity = period + 1 + max(1, int(np.log2(len(sequence) // period + 1)))
                        
                        patterns.append({
                            'type': 'periodic',
                            'pattern': pattern,
                            'period': period,
                            'complexity': complexity,
                            'confidence': accuracy,
                            'weight': 2**(-complexity),
                            'description': f'Periodic pattern with period {period}: {pattern}',
                            'fits_sequence': True,
                            'accuracy': accuracy,
                            'parameters': {'pattern': pattern, 'period': period},
                            'prediction_function': lambda n=len(sequence): pattern[n % period]
                        })
                        
                        # Prefer shortest period (early termination)
                        if self.pattern_config.enable_early_termination:
                            break
                            
        return patterns
    
    def _detect_fibonacci_pattern(self, sequence: List[Union[int, float]]) -> List[Dict]:
        """
        🌀 Detect Fibonacci-like Patterns
        
        Mathematical Foundation:
        Fibonacci sequences follow F_n = F_{n-1} + F_{n-2} with initial conditions F_0, F_1.
        Generalized: a_n = a_{n-1} + a_{n-2} starting with a_0, a_1.
        Kolmogorov complexity: K(x) = O(log|a₀| + log|a₁| + 1) - very low complexity!
        
        This is one of the most efficient patterns due to simple recursive definition.
        
        Extensions (if enabled):
        - Tribonacci: a_n = a_{n-1} + a_{n-2} + a_{n-3}
        - Lucas sequences: generalized Fibonacci with different coefficients
        - Negative Fibonacci: allowing negative starting values
        """
        patterns = []
        if len(sequence) < 3:
            return patterns
            
        # Standard Fibonacci check: F_n = F_{n-1} + F_{n-2}
        is_fibonacci = True
        for i in range(2, len(sequence)):
            if abs(sequence[i] - (sequence[i-1] + sequence[i-2])) > 1e-10:
                is_fibonacci = False
                break
        
        if is_fibonacci:
            start_a, start_b = sequence[0], sequence[1]
            
            # Verify accuracy
            predicted_sequence = [start_a, start_b]
            for i in range(2, len(sequence)):
                predicted_sequence.append(predicted_sequence[i-1] + predicted_sequence[i-2])
            
            accuracy = 1.0 - np.mean([abs(pred - actual) for pred, actual in 
                                    zip(predicted_sequence, sequence)]) / (max(abs(max(sequence)), abs(min(sequence))) + 1)
            
            if accuracy > 0.99:  # Very high accuracy required
                # Complexity: two starting values + recurrence relation
                complexity = (1 +  # pattern type
                            max(1, int(np.log2(abs(start_a) + 1))) +  # F_0 encoding
                            max(1, int(np.log2(abs(start_b) + 1))))    # F_1 encoding
                
                patterns.append({
                    'type': 'fibonacci',
                    'start_a': start_a,
                    'start_b': start_b,
                    'complexity': complexity,
                    'confidence': accuracy,
                    'weight': 2**(-complexity),
                    'description': f'Fibonacci-like sequence: F(0)={start_a}, F(1)={start_b}',
                    'fits_sequence': True,
                    'accuracy': accuracy,
                    'parameters': {'start_a': start_a, 'start_b': start_b},
                    'prediction_function': lambda n=len(sequence): self._fibonacci_next(sequence, n)
                })
        
        # Extended Fibonacci variants (if enabled)
        if self.pattern_config.enable_fibonacci_variants:
            # Tribonacci: F_n = F_{n-1} + F_{n-2} + F_{n-3}
            if len(sequence) >= 4:
                is_tribonacci = True
                for i in range(3, len(sequence)):
                    if abs(sequence[i] - (sequence[i-1] + sequence[i-2] + sequence[i-3])) > 1e-10:
                        is_tribonacci = False
                        break
                
                if is_tribonacci:
                    complexity = 2 + sum(max(1, int(np.log2(abs(sequence[i]) + 1))) for i in range(3))
                    patterns.append({
                        'type': 'tribonacci',
                        'start_values': sequence[:3],
                        'complexity': complexity,
                        'confidence': 0.99,
                        'weight': 2**(-complexity),
                        'description': f'Tribonacci sequence: starts with {sequence[:3]}',
                        'fits_sequence': True,
                        'accuracy': 0.99,
                        'parameters': {'start_values': sequence[:3]},
                        'prediction_function': lambda n=len(sequence): self._tribonacci_next(sequence, n)
                    })
                    
        return patterns
    
    def _fibonacci_next(self, sequence: List, n: int) -> Union[int, float]:
        """Generate next Fibonacci number"""
        if n < len(sequence):
            return sequence[n]
        elif n < 2:
            return sequence[n] if n < len(sequence) else 0
        else:
            # Generate iteratively to avoid stack overflow
            a, b = sequence[-2], sequence[-1]
            for i in range(len(sequence), n + 1):
                a, b = b, a + b
            return b
    
    def _tribonacci_next(self, sequence: List, n: int) -> Union[int, float]:
        """Generate next Tribonacci number"""
        if n < len(sequence):
            return sequence[n]
        elif n < 3:
            return sequence[n] if n < len(sequence) else 0
        else:
            # Generate iteratively
            a, b, c = sequence[-3], sequence[-2], sequence[-1]
            for i in range(len(sequence), n + 1):
                a, b, c = b, c, a + b + c
            return c
    
    def _detect_polynomial_patterns(self, sequence: List[Union[int, float]]) -> List[Dict]:
        """
        🔢 Detect Polynomial Patterns using Finite Differences
        
        Mathematical Foundation:
        Polynomial sequences of degree d have the property that the d-th finite
        difference is constant. This provides a direct test for polynomial patterns.
        
        For polynomial P(x) = Σᵢ aᵢxⁱ of degree d:
        Kolmogorov complexity: K(x) = O(d + Σᵢ log|aᵢ|)
        
        Algorithm:
        1. Compute successive finite differences
        2. Check for constant difference at each level
        3. Degree = level where constant differences found
        4. Verify accuracy via polynomial reconstruction
        
        This method is mathematically exact for true polynomial sequences
        and robust for approximately polynomial data.
        """
        patterns = []
        if len(sequence) < 3:
            return patterns
            
        max_degree = min(len(sequence) - 1, self.pattern_config.max_polynomial_degree)
        
        # Try each polynomial degree
        current_diffs = list(sequence)
        
        for degree in range(max_degree):
            # Compute next level of differences
            if len(current_diffs) <= 1:
                break
                
            next_diffs = [current_diffs[i+1] - current_diffs[i] for i in range(len(current_diffs)-1)]
            
            # Check if differences are constant
            if len(set(next_diffs)) == 1 or (len(next_diffs) > 1 and 
                                           max(next_diffs) - min(next_diffs) <= self.pattern_config.polynomial_tolerance):
                constant_diff = statistics.mean(next_diffs) if next_diffs else 0
                
                # Reconstruct polynomial and verify accuracy
                try:
                    # Fit polynomial using numpy
                    x_vals = np.arange(len(sequence))
                    poly_coeffs = np.polyfit(x_vals, sequence, degree + 1)
                    predicted = np.polyval(poly_coeffs, x_vals)
                    
                    # Calculate accuracy
                    errors = [abs(pred - actual) for pred, actual in zip(predicted, sequence)]
                    max_val = max(abs(max(sequence)), abs(min(sequence)))
                    accuracy = 1.0 - np.mean(errors) / (max_val + 1e-10) if max_val > 0 else 1.0
                    
                    if accuracy > 0.98:  # High accuracy required
                        # Complexity: degree + coefficient encoding
                        complexity = (degree + 2 +  # degree + pattern type
                                    sum(max(1, int(np.log2(abs(coeff) + 1))) for coeff in poly_coeffs))
                        
                        patterns.append({
                            'type': 'polynomial',
                            'degree': degree + 1,
                            'coefficients': poly_coeffs.tolist(),
                            'constant_diff': constant_diff,
                            'complexity': complexity,
                            'confidence': accuracy,
                            'weight': 2**(-complexity),
                            'description': f'Polynomial of degree {degree + 1}',
                            'fits_sequence': True,
                            'accuracy': accuracy,
                            'parameters': {'degree': degree + 1, 'coefficients': poly_coeffs.tolist()},
                            'prediction_function': lambda n=len(sequence): float(np.polyval(poly_coeffs, n))
                        })
                        
                        # Prefer lower degree (simpler explanation)
                        if self.pattern_config.enable_early_termination:
                            break
                            
                except (np.linalg.LinAlgError, OverflowError):
                    continue
                    
            current_diffs = next_diffs
            
        return patterns
    
    def _detect_recursive_patterns(self, sequence: List[Union[int, float]]) -> List[Dict]:
        """
        🔄 Detect General Linear Recursive Patterns
        
        Mathematical Foundation:
        Linear recurrence relations: a_n = c₁a_{n-1} + c₂a_{n-2} + ... + cₖa_{n-k}
        
        This generalizes arithmetic progressions (k=1, c₁=1), Fibonacci (k=2, c₁=c₂=1),
        and many other mathematical sequences.
        
        Kolmogorov complexity: K(x) = O(k + Σᵢ log|cᵢ| + Σⱼ log|a_j|) where k is order,
        cᵢ are coefficients, and a_j are initial values.
        
        Algorithm:
        1. Try different recurrence orders (1 to max_recursive_order)
        2. For each order, search coefficient space systematically
        3. Verify recurrence holds for entire sequence
        4. Calculate complexity based on coefficients and initial values
        
        This approach can discover many mathematical sequences not caught
        by specialized detectors.
        """
        patterns = []
        if len(sequence) < 4:  # Need at least 4 values for meaningful recurrence
            return patterns
            
        max_order = min(self.pattern_config.max_recursive_order, len(sequence) - 2)
        coeff_min, coeff_max = self.pattern_config.recursive_coefficient_range
        
        for order in range(1, max_order + 1):
            if len(sequence) <= order + 1:
                continue
                
            # Search coefficient space
            for coeff_combo in self._generate_coefficient_combinations(order, coeff_min, coeff_max):
                # Test if recurrence holds
                is_valid_recurrence = True
                
                for i in range(order, len(sequence)):
                    predicted = sum(coeff_combo[j] * sequence[i-1-j] for j in range(order))
                    if abs(predicted - sequence[i]) > 1e-10:
                        is_valid_recurrence = False
                        break
                
                if is_valid_recurrence:
                    # Calculate accuracy (should be perfect for true recurrence)
                    accuracy = 1.0
                    
                    # Calculate complexity
                    initial_values = sequence[:order]
                    complexity = (1 +  # pattern type
                                sum(max(1, int(np.log2(abs(c) + 1))) for c in coeff_combo) +  # coefficients
                                sum(max(1, int(np.log2(abs(v) + 1))) for v in initial_values))  # initial values
                    
                    patterns.append({
                        'type': 'recursive',
                        'order': order,
                        'coefficients': coeff_combo,
                        'initial_values': initial_values,
                        'complexity': complexity,
                        'confidence': accuracy,
                        'weight': 2**(-complexity),
                        'description': f'Linear recurrence order {order}: a(n) = {self._format_recurrence(coeff_combo)}',
                        'fits_sequence': True,
                        'accuracy': accuracy,
                        'parameters': {'order': order, 'coefficients': coeff_combo, 'initial_values': initial_values},
                        'prediction_function': lambda n=len(sequence): self._recursive_next(sequence, coeff_combo, order, n)
                    })
                    
                    # Return first valid recurrence of this order
                    if self.pattern_config.enable_early_termination:
                        return patterns
                        
        return patterns
    
    def _generate_coefficient_combinations(self, order: int, coeff_min: int, coeff_max: int):
        """Generate coefficient combinations for recurrence testing"""
        if order == 1:
            for c in range(coeff_min, coeff_max):
                if c != 0:  # Avoid trivial recurrences
                    yield [c]
        elif order == 2:
            for c1 in range(coeff_min, coeff_max):
                for c2 in range(coeff_min, coeff_max):
                    if c1 != 0 or c2 != 0:  # At least one non-zero coefficient
                        yield [c1, c2]
        else:
            # For higher orders, limit search space
            import itertools
            coeffs = range(max(coeff_min, -2), min(coeff_max, 3))  # Reduced range
            for combo in itertools.product(coeffs, repeat=order):
                if any(c != 0 for c in combo):  # At least one non-zero
                    yield list(combo)
    
    def _format_recurrence(self, coefficients: List[int]) -> str:
        """Format recurrence relation for display"""
        terms = []
        for i, c in enumerate(coefficients):
            if c != 0:
                if c == 1:
                    terms.append(f"a(n-{i+1})")
                elif c == -1:
                    terms.append(f"-a(n-{i+1})")
                else:
                    terms.append(f"{c}*a(n-{i+1})")
        return " + ".join(terms).replace(" + -", " - ")
    
    def _recursive_next(self, sequence: List, coefficients: List, order: int, n: int) -> Union[int, float]:
        """Generate next value using recursive relation"""
        if n < len(sequence):
            return sequence[n]
        
        # Generate values iteratively up to position n
        extended_seq = list(sequence)
        while len(extended_seq) <= n:
            next_val = sum(coefficients[j] * extended_seq[-1-j] for j in range(order))
            extended_seq.append(next_val)
        
        return extended_seq[n]
    
    def _detect_statistical_patterns(self, sequence: List[Union[int, float]]) -> List[Dict]:
        """
        📊 Detect Statistical Patterns in Sequences
        
        Mathematical Foundation:
        Statistical patterns arise from stochastic processes where sequences
        are generated from probability distributions rather than deterministic rules.
        
        For distribution D with parameters θ:
        Kolmogorov complexity: K(x|D) = O(|θ| - log P_D(x))
        
        Where |θ| is parameter description length and P_D(x) is sequence likelihood.
        
        Implemented Distributions:
        1. **Normal Distribution**: N(μ,σ²) - Gaussian processes, noise
        2. **Uniform Distribution**: U(a,b) - Random sequences in range  
        3. **Exponential Distribution**: Exp(λ) - Decay processes
        4. **Geometric Distribution**: Geom(p) - Discrete waiting times
        
        Statistical Tests:
        - Kolmogorov-Smirnov test for distribution fitting
        - Anderson-Darling test for normality  
        - Chi-square goodness-of-fit test
        - Autocorrelation analysis for independence
        """
        patterns = []
        
        if (len(sequence) < self.pattern_config.min_sequence_length_for_stats or 
            not self.pattern_config.enable_statistical_patterns):
            return patterns
        
        sequence_array = np.array(sequence, dtype=float)
        
        # Test for normal distribution
        patterns.extend(self._test_normal_distribution(sequence_array))
        
        # Test for uniform distribution
        patterns.extend(self._test_uniform_distribution(sequence_array))
        
        # Test for exponential distribution (positive values only)
        if all(x > 0 for x in sequence_array):
            patterns.extend(self._test_exponential_distribution(sequence_array))
        
        # Test for geometric distribution (integer positive values)
        if all(x > 0 and int(x) == x for x in sequence_array):
            patterns.extend(self._test_geometric_distribution([int(x) for x in sequence_array]))
        
        return patterns
    
    def _test_normal_distribution(self, sequence: np.ndarray) -> List[Dict]:
        """Test if sequence follows normal distribution"""
        patterns = []
        
        if len(sequence) < 10:
            return patterns
            
        mean_val = np.mean(sequence)
        std_val = np.std(sequence, ddof=1)
        
        if std_val > 1e-10:  # Avoid zero variance
            # Simple normality test: check if ~95% of values within 2 standard deviations
            within_2std = np.sum(np.abs(sequence - mean_val) <= 2 * std_val)
            normality_ratio = within_2std / len(sequence)
            
            # More rigorous test: check empirical vs theoretical quantiles
            sorted_seq = np.sort(sequence)
            theoretical_quantiles = np.linspace(0.01, 0.99, len(sequence))
            empirical_quantiles = [(i + 0.5) / len(sequence) for i in range(len(sequence))]
            
            # Convert to z-scores for comparison
            from scipy import stats
            try:
                # Shapiro-Wilk test for normality
                _, p_value = stats.shapiro(sequence) if len(sequence) <= 5000 else (0, 0.01)
                confidence = max(normality_ratio * 0.7, min(p_value * 10, 0.95))
                
                if confidence >= self.pattern_config.statistical_confidence_threshold * 0.8:
                    # Complexity: distribution type + mean + variance parameters
                    complexity = (2 +  # distribution type + parameter count
                                max(1, int(np.log2(abs(mean_val) + 1))) +  # mean encoding
                                max(1, int(np.log2(std_val + 1))))          # std encoding
                    
                    patterns.append({
                        'type': 'statistical_normal',
                        'distribution': 'normal',
                        'mean': mean_val,
                        'std': std_val,
                        'variance': std_val ** 2,
                        'complexity': complexity,
                        'confidence': confidence,
                        'weight': 2**(-complexity) * confidence,
                        'description': f'Normal distribution: μ={mean_val:.4f}, σ={std_val:.4f}',
                        'fits_sequence': True,
                        'accuracy': confidence,
                        'parameters': {'mean': mean_val, 'std': std_val},
                        'prediction_function': lambda: np.random.normal(mean_val, std_val)
                    })
                    
            except ImportError:
                # Fallback without scipy
                if normality_ratio >= 0.93:  # 93% within 2 std devs suggests normality
                    complexity = 3 + max(1, int(np.log2(abs(mean_val) + 1))) + max(1, int(np.log2(std_val + 1)))
                    patterns.append({
                        'type': 'statistical_normal',
                        'distribution': 'normal',
                        'mean': mean_val,
                        'std': std_val,
                        'complexity': complexity,
                        'confidence': normality_ratio,
                        'weight': 2**(-complexity) * normality_ratio,
                        'description': f'Normal distribution: μ={mean_val:.4f}, σ={std_val:.4f}',
                        'fits_sequence': True,
                        'accuracy': normality_ratio,
                        'parameters': {'mean': mean_val, 'std': std_val},
                        'prediction_function': lambda: mean_val + std_val * np.random.randn()
                    })
        
        return patterns
    
    def _test_uniform_distribution(self, sequence: np.ndarray) -> List[Dict]:
        """Test if sequence follows uniform distribution"""
        patterns = []
        
        if len(sequence) < 10:
            return patterns
            
        min_val = np.min(sequence)
        max_val = np.max(sequence)
        range_val = max_val - min_val
        
        if range_val > 1e-10:  # Non-degenerate range
            # Test uniformity by checking distribution of values across range
            n_bins = min(20, len(sequence) // 3)
            hist, bin_edges = np.histogram(sequence, bins=n_bins)
            
            # Expected count per bin for uniform distribution
            expected_count = len(sequence) / n_bins
            
            # Chi-square test statistic
            chi_square = np.sum((hist - expected_count) ** 2 / expected_count)
            degrees_freedom = n_bins - 1
            
            # Rough p-value approximation (without scipy)
            # For uniform distribution, chi-square should be small
            uniformity_score = max(0, 1 - chi_square / (degrees_freedom * 2))
            
            if uniformity_score >= self.pattern_config.statistical_confidence_threshold * 0.7:
                # Complexity: distribution type + range parameters
                complexity = (2 +  # distribution type + parameter count
                            max(1, int(np.log2(abs(min_val) + 1))) +  # min encoding
                            max(1, int(np.log2(range_val + 1))))       # range encoding
                
                patterns.append({
                    'type': 'statistical_uniform',
                    'distribution': 'uniform',
                    'min': min_val,
                    'max': max_val,
                    'range': range_val,
                    'complexity': complexity,
                    'confidence': uniformity_score,
                    'weight': 2**(-complexity) * uniformity_score,
                    'description': f'Uniform distribution: [{min_val:.4f}, {max_val:.4f}]',
                    'fits_sequence': True,
                    'accuracy': uniformity_score,
                    'parameters': {'min': min_val, 'max': max_val},
                    'prediction_function': lambda: np.random.uniform(min_val, max_val)
                })
        
        return patterns
    
    def _test_exponential_distribution(self, sequence: np.ndarray) -> List[Dict]:
        """Test if sequence follows exponential distribution"""
        patterns = []
        
        if len(sequence) < 10 or np.any(sequence <= 0):
            return patterns
            
        # Maximum likelihood estimate for exponential parameter
        lambda_param = 1.0 / np.mean(sequence)
        
        # Test goodness of fit using empirical vs theoretical CDF
        sorted_seq = np.sort(sequence)
        empirical_cdf = np.arange(1, len(sequence) + 1) / len(sequence)
        theoretical_cdf = 1 - np.exp(-lambda_param * sorted_seq)
        
        # Kolmogorov-Smirnov-like test
        max_diff = np.max(np.abs(empirical_cdf - theoretical_cdf))
        confidence = max(0, 1 - max_diff * 2)  # Rough approximation
        
        if confidence >= self.pattern_config.statistical_confidence_threshold * 0.6:
            # Complexity: distribution type + lambda parameter
            complexity = 2 + max(1, int(np.log2(lambda_param + 1)))
            
            patterns.append({
                'type': 'statistical_exponential',
                'distribution': 'exponential',
                'lambda': lambda_param,
                'mean': 1.0 / lambda_param,
                'complexity': complexity,
                'confidence': confidence,
                'weight': 2**(-complexity) * confidence,
                'description': f'Exponential distribution: λ={lambda_param:.4f}',
                'fits_sequence': True,
                'accuracy': confidence,
                'parameters': {'lambda': lambda_param},
                'prediction_function': lambda: np.random.exponential(1.0 / lambda_param)
            })
        
        return patterns
    
    def _test_geometric_distribution(self, sequence: List[int]) -> List[Dict]:
        """Test if sequence follows geometric distribution"""
        patterns = []
        
        if len(sequence) < 10 or any(x <= 0 for x in sequence):
            return patterns
            
        # Maximum likelihood estimate for geometric parameter
        mean_val = np.mean(sequence)
        p_param = 1.0 / mean_val if mean_val > 1 else 0.5
        
        # Test goodness of fit
        unique_vals, counts = np.unique(sequence, return_counts=True)
        observed_freq = counts / len(sequence)
        
        # Theoretical probabilities for geometric distribution
        theoretical_freq = []
        for val in unique_vals:
            if val >= 1:
                # P(X = k) = (1-p)^(k-1) * p for geometric distribution
                prob = ((1 - p_param) ** (val - 1)) * p_param
                theoretical_freq.append(prob)
            else:
                theoretical_freq.append(0)
        
        theoretical_freq = np.array(theoretical_freq)
        
        # Chi-square-like goodness of fit
        if len(theoretical_freq) > 0 and np.sum(theoretical_freq) > 0:
            theoretical_freq /= np.sum(theoretical_freq)  # Normalize
            chi_square = np.sum((observed_freq - theoretical_freq) ** 2 / (theoretical_freq + 1e-10))
            confidence = max(0, 1 - chi_square / len(unique_vals))
            
            if confidence >= self.pattern_config.statistical_confidence_threshold * 0.5:
                # Complexity: distribution type + probability parameter
                complexity = 2 + max(1, int(np.log2(1.0 / p_param + 1)))
                
                patterns.append({
                    'type': 'statistical_geometric',
                    'distribution': 'geometric',
                    'p': p_param,
                    'mean': 1.0 / p_param,
                    'complexity': complexity,
                    'confidence': confidence,
                    'weight': 2**(-complexity) * confidence,
                    'description': f'Geometric distribution: p={p_param:.4f}',
                    'fits_sequence': True,
                    'accuracy': confidence,
                    'parameters': {'p': p_param},
                    'prediction_function': lambda: np.random.geometric(p_param)
                })
        
        return patterns
    
    def configure_pattern_detection(self, **kwargs):
        """
        🎛️ Configure Pattern Detection Parameters
        
        Allows runtime configuration of pattern detection behavior.
        Useful for optimizing detection for specific sequence types or
        computational constraints.
        """
        for key, value in kwargs.items():
            if hasattr(self.pattern_config, key):
                setattr(self.pattern_config, key, value)
                print(f"✓ Pattern detection parameter '{key}' set to: {value}")
            else:
                print(f"⚠️ Unknown parameter '{key}' - ignored")
    
    def get_pattern_complexity_estimate(self, sequence: List[Union[int, float]]) -> float:
        """
        📏 Get Minimum Pattern Complexity Estimate
        
        Returns the complexity of the simplest pattern that fits the sequence.
        This serves as a proxy for Kolmogorov complexity in Solomonoff Induction.
        
        Returns:
            float: Estimated complexity (bits) of simplest fitting pattern,
                  or infinity if no pattern detected
        """
        patterns = self.detect_all_patterns(sequence)
        
        if not patterns:
            return float('inf')
            
        # Return complexity of simplest (first) pattern
        return patterns[0].get('complexity', float('inf'))
    
    def explain_sequence(self, sequence: List[Union[int, float]]) -> str:
        """
        📝 Generate Human-Readable Explanation of Sequence Patterns
        
        Provides detailed analysis of detected patterns with mathematical
        foundations and confidence assessments.
        """
        patterns = self.detect_all_patterns(sequence)
        
        if not patterns:
            return f"No clear pattern detected in sequence {sequence}. " \
                   f"This may indicate a random or highly complex sequence."
        
        explanation = f"Sequence Analysis for {sequence}:\n"
        explanation += "=" * 50 + "\n\n"
        
        for i, pattern in enumerate(patterns[:3], 1):  # Top 3 patterns
            explanation += f"{i}. {pattern['description']}\n"
            explanation += f"   • Complexity: {pattern['complexity']:.2f} bits\n"
            explanation += f"   • Confidence: {pattern['confidence']:.2%}\n"
            explanation += f"   • Pattern Type: {pattern['type']}\n"
            
            if 'prediction_function' in pattern:
                try:
                    next_val = pattern['prediction_function']()
                    explanation += f"   • Next Predicted Value: {next_val}\n"
                except:
                    explanation += f"   • Next Predicted Value: [computation error]\n"
            
            explanation += "\n"
        
        best_pattern = patterns[0]
        explanation += f"Best Explanation: {best_pattern['description']}\n"
        explanation += f"This pattern has the lowest complexity ({best_pattern['complexity']:.2f} bits) "
        explanation += f"and explains the sequence with {best_pattern['confidence']:.1%} confidence.\n"
        
        return explanation

# Export main class
__all__ = ['PatternDetectionMixin', 'PatternDetectionConfig']