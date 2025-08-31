"""
Kolmogorov Complexity Estimation Library
Based on: Li & Vitányi (1997) "An Introduction to Kolmogorov Complexity and Its Applications"

This module provides practical approximations to Kolmogorov complexity using
compression algorithms, algorithmic probability, and minimum description length principles.

Key implementations:
- Compression-based complexity estimation
- Normalized compression distance (NCD)
- Minimum description length (MDL) 
- Approximations to algorithmic probability
- Context-free grammar induction for complexity bounds
"""

import numpy as np
import zlib
import bz2
import gzip
import lzma
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
import math
import re
from collections import defaultdict, Counter
import pickle
import json


class CompressionMethod(Enum):
    """Available compression methods for complexity estimation"""
    ZLIB = "zlib"
    BZ2 = "bz2"
    GZIP = "gzip"
    LZMA = "lzma"


@dataclass
class ComplexityEstimate:
    """Result of complexity estimation"""
    raw_complexity: float
    normalized_complexity: float
    compression_ratio: float
    method: str
    original_size: int
    compressed_size: int
    confidence: float


@dataclass
class NCDResult:
    """Normalized Compression Distance result"""
    distance: float
    complexity_x: float
    complexity_y: float
    complexity_xy: float
    method: str


class KolmogorovComplexityEstimator:
    """
    Practical Kolmogorov complexity estimation using compression methods.
    
    While true Kolmogorov complexity is uncomputable, we can approximate it
    using practical compression algorithms that approach the theoretical limits.
    """
    
    def __init__(self, default_method: CompressionMethod = CompressionMethod.LZMA):
        """
        Initialize complexity estimator.
        
        Args:
            default_method: Default compression method to use
        """
        self.default_method = default_method
        self.compression_functions = {
            CompressionMethod.ZLIB: zlib.compress,
            CompressionMethod.BZ2: bz2.compress,
            CompressionMethod.GZIP: gzip.compress,
            CompressionMethod.LZMA: lzma.compress
        }
        
        # Cache for complexity computations
        self._complexity_cache = {}
    
    def estimate_complexity(self, 
                          data: Union[str, bytes, np.ndarray], 
                          method: Optional[CompressionMethod] = None,
                          normalize: bool = True) -> ComplexityEstimate:
        """
        Estimate Kolmogorov complexity of data using compression.
        
        Args:
            data: Input data (string, bytes, or array)
            method: Compression method to use
            normalize: Whether to normalize by original size
            
        Returns:
            ComplexityEstimate with compression-based complexity
        """
        if method is None:
            method = self.default_method
        
        # Convert data to bytes
        data_bytes = self._to_bytes(data)
        original_size = len(data_bytes)
        
        # Check cache
        cache_key = (hash(data_bytes), method)
        if cache_key in self._complexity_cache:
            return self._complexity_cache[cache_key]
        
        # Compress data
        compress_func = self.compression_functions[method]
        try:
            compressed = compress_func(data_bytes)
            compressed_size = len(compressed)
        except Exception as e:
            # Fallback to simpler method
            compressed = zlib.compress(data_bytes)
            compressed_size = len(compressed)
            method = CompressionMethod.ZLIB
        
        # Calculate complexity measures
        raw_complexity = compressed_size
        compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
        normalized_complexity = compression_ratio if normalize else raw_complexity
        
        # Estimate confidence based on compression effectiveness
        # Better compression (lower ratio) usually means higher confidence
        confidence = 1.0 - min(compression_ratio, 1.0)
        
        result = ComplexityEstimate(
            raw_complexity=raw_complexity,
            normalized_complexity=normalized_complexity,
            compression_ratio=compression_ratio,
            method=method.value,
            original_size=original_size,
            compressed_size=compressed_size,
            confidence=confidence
        )
        
        # Cache result
        self._complexity_cache[cache_key] = result
        return result
    
    def normalized_compression_distance(self,
                                      x: Union[str, bytes, np.ndarray],
                                      y: Union[str, bytes, np.ndarray],
                                      method: Optional[CompressionMethod] = None) -> NCDResult:
        """
        Calculate Normalized Compression Distance between two objects.
        
        NCD(x,y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
        
        Where C(x) is the compressed size of x, and xy is concatenation of x and y.
        NCD approximates the normalized information distance.
        
        Args:
            x: First object
            y: Second object  
            method: Compression method to use
            
        Returns:
            NCDResult with distance and component complexities
        """
        if method is None:
            method = self.default_method
        
        # Convert to bytes
        x_bytes = self._to_bytes(x)
        y_bytes = self._to_bytes(y)
        xy_bytes = x_bytes + y_bytes
        
        # Get complexities
        cx = self.estimate_complexity(x_bytes, method, normalize=False).raw_complexity
        cy = self.estimate_complexity(y_bytes, method, normalize=False).raw_complexity
        cxy = self.estimate_complexity(xy_bytes, method, normalize=False).raw_complexity
        
        # Calculate NCD
        min_c = min(cx, cy)
        max_c = max(cx, cy)
        
        if max_c == 0:
            distance = 0.0
        else:
            distance = (cxy - min_c) / max_c
            # Clamp to [0, 1] range
            distance = max(0.0, min(1.0, distance))
        
        return NCDResult(
            distance=distance,
            complexity_x=cx,
            complexity_y=cy,
            complexity_xy=cxy,
            method=method.value
        )
    
    def mutual_information_estimate(self,
                                  x: Union[str, bytes, np.ndarray],
                                  y: Union[str, bytes, np.ndarray],
                                  method: Optional[CompressionMethod] = None) -> float:
        """
        Estimate mutual information using compression.
        
        MI(X;Y) ≈ C(X) + C(Y) - C(XY)
        
        Args:
            x: First random variable data
            y: Second random variable data
            method: Compression method
            
        Returns:
            Estimated mutual information in bits
        """
        if method is None:
            method = self.default_method
        
        x_bytes = self._to_bytes(x)
        y_bytes = self._to_bytes(y)
        xy_bytes = x_bytes + y_bytes
        
        cx = self.estimate_complexity(x_bytes, method, normalize=False).raw_complexity
        cy = self.estimate_complexity(y_bytes, method, normalize=False).raw_complexity
        cxy = self.estimate_complexity(xy_bytes, method, normalize=False).raw_complexity
        
        # Convert bytes to bits
        mutual_info_bits = (cx + cy - cxy) * 8
        return max(0.0, mutual_info_bits)  # MI must be non-negative
    
    def conditional_complexity(self,
                             x: Union[str, bytes, np.ndarray],
                             y: Union[str, bytes, np.ndarray],
                             method: Optional[CompressionMethod] = None) -> float:
        """
        Estimate conditional Kolmogorov complexity K(x|y).
        
        K(x|y) ≈ C(xy) - C(y)
        
        Args:
            x: Target data
            y: Conditioning data
            method: Compression method
            
        Returns:
            Estimated conditional complexity
        """
        if method is None:
            method = self.default_method
        
        x_bytes = self._to_bytes(x)
        y_bytes = self._to_bytes(y)
        xy_bytes = x_bytes + y_bytes
        
        cy = self.estimate_complexity(y_bytes, method, normalize=False).raw_complexity
        cxy = self.estimate_complexity(xy_bytes, method, normalize=False).raw_complexity
        
        return max(0.0, cxy - cy)
    
    def randomness_deficiency(self,
                             data: Union[str, bytes, np.ndarray],
                             method: Optional[CompressionMethod] = None) -> float:
        """
        Estimate randomness deficiency: how far data is from maximum entropy.
        
        δ(x) = n - K(x) where n is the length of x
        
        Args:
            data: Input data
            method: Compression method
            
        Returns:
            Randomness deficiency (higher = more structured/predictable)
        """
        if method is None:
            method = self.default_method
        
        data_bytes = self._to_bytes(data)
        original_size = len(data_bytes)
        
        complexity_est = self.estimate_complexity(data_bytes, method, normalize=False)
        complexity_bits = complexity_est.raw_complexity * 8  # Convert to bits
        
        max_entropy_bits = original_size * 8  # Maximum possible entropy
        deficiency = max_entropy_bits - complexity_bits
        
        return max(0.0, deficiency)
    
    def logical_depth_estimate(self,
                             data: Union[str, bytes, np.ndarray],
                             method: Optional[CompressionMethod] = None) -> Tuple[float, float]:
        """
        Estimate logical depth: computation time of shortest program.
        
        We approximate this by measuring compression time as a proxy for
        the computational complexity of the shortest description.
        
        Args:
            data: Input data
            method: Compression method
            
        Returns:
            Tuple of (time_estimate, complexity_estimate)
        """
        import time
        
        if method is None:
            method = self.default_method
        
        data_bytes = self._to_bytes(data)
        compress_func = self.compression_functions[method]
        
        # Measure compression time
        start_time = time.perf_counter()
        compressed = compress_func(data_bytes)
        compression_time = time.perf_counter() - start_time
        
        # Get complexity estimate
        complexity = len(compressed)
        
        # Normalize time by data size (depth per byte)
        normalized_time = compression_time / len(data_bytes) if len(data_bytes) > 0 else 0.0
        
        return (normalized_time, complexity)
    
    def minimum_description_length(self,
                                 data: List[Any],
                                 model_class: str = "histogram",
                                 precision: float = 0.01) -> Dict[str, Any]:
        """
        Apply Minimum Description Length principle for model selection.
        
        MDL chooses the model that minimizes: L(model) + L(data|model)
        where L(x) is the description length of x.
        
        Args:
            data: Training data
            model_class: Type of model to fit ("histogram", "gaussian", "uniform")
            precision: Precision for discretization
            
        Returns:
            Dictionary with model parameters and description length
        """
        if model_class == "histogram":
            return self._mdl_histogram(data, precision)
        elif model_class == "gaussian":
            return self._mdl_gaussian(data)
        elif model_class == "uniform":
            return self._mdl_uniform(data)
        else:
            raise ValueError(f"Unknown model class: {model_class}")
    
    def algorithmic_probability_estimate(self,
                                       data: Union[str, bytes, np.ndarray],
                                       method: Optional[CompressionMethod] = None) -> float:
        """
        Estimate algorithmic probability P(x) ≈ 2^(-K(x)).
        
        Args:
            data: Input data
            method: Compression method
            
        Returns:
            Estimated algorithmic probability
        """
        if method is None:
            method = self.default_method
        
        complexity = self.estimate_complexity(data, method, normalize=False)
        complexity_bits = complexity.raw_complexity * 8
        
        # P(x) ≈ 2^(-K(x))
        # Use log space to avoid numerical underflow
        log_prob = -complexity_bits * math.log(2)
        probability = math.exp(log_prob)
        
        return probability
    
    def grammar_based_complexity(self, text: str) -> Dict[str, Any]:
        """
        Estimate complexity using context-free grammar induction.
        
        This approximates Kolmogorov complexity by finding the shortest
        context-free grammar that generates the input string.
        
        Args:
            text: Input text string
            
        Returns:
            Dictionary with grammar complexity metrics
        """
        # Simple grammar induction using repeated substring patterns
        patterns = self._extract_repeated_patterns(text)
        
        # Calculate original size
        original_size = len(text)
        
        # Estimate compressed size using patterns
        grammar_rules = []
        remaining_text = text
        rule_id = 0
        
        # Replace patterns with shorter symbols
        for pattern, count in sorted(patterns.items(), 
                                   key=lambda x: len(x[0]) * x[1], 
                                   reverse=True):
            if len(pattern) > 2 and count > 1:
                rule_symbol = f"R{rule_id}"
                rule_id += 1
                grammar_rules.append((rule_symbol, pattern))
                remaining_text = remaining_text.replace(pattern, rule_symbol)
        
        # Calculate grammar description length
        grammar_length = sum(len(rule[0]) + len(rule[1]) + 3 for rule in grammar_rules)  # +3 for " -> "
        compressed_text_length = len(remaining_text)
        total_compressed_length = grammar_length + compressed_text_length
        
        compression_ratio = total_compressed_length / original_size if original_size > 0 else 1.0
        
        return {
            "original_size": original_size,
            "compressed_size": total_compressed_length,
            "compression_ratio": compression_ratio,
            "grammar_rules": len(grammar_rules),
            "patterns_found": len(patterns),
            "complexity_estimate": total_compressed_length
        }
    
    def compare_complexities(self,
                           datasets: List[Tuple[str, Union[str, bytes, np.ndarray]]],
                           method: Optional[CompressionMethod] = None) -> Dict[str, ComplexityEstimate]:
        """
        Compare complexities of multiple datasets.
        
        Args:
            datasets: List of (name, data) tuples
            method: Compression method to use
            
        Returns:
            Dictionary mapping names to complexity estimates
        """
        results = {}
        
        for name, data in datasets:
            results[name] = self.estimate_complexity(data, method)
        
        return results
    
    def _to_bytes(self, data: Union[str, bytes, np.ndarray]) -> bytes:
        """Convert various data types to bytes for compression."""
        if isinstance(data, bytes):
            return data
        elif isinstance(data, str):
            return data.encode('utf-8')
        elif isinstance(data, np.ndarray):
            return data.tobytes()
        elif hasattr(data, '__iter__'):
            # Try to serialize as JSON
            try:
                json_str = json.dumps(list(data), separators=(',', ':'))
                return json_str.encode('utf-8')
            except:
                # Fallback to pickle
                return pickle.dumps(data)
        else:
            # Try to pickle arbitrary objects
            return pickle.dumps(data)
    
    def _extract_repeated_patterns(self, text: str, min_length: int = 2) -> Dict[str, int]:
        """Extract repeated substrings and their counts."""
        patterns = defaultdict(int)
        
        # Extract all substrings of various lengths
        for length in range(min_length, min(len(text) // 2 + 1, 50)):
            for i in range(len(text) - length + 1):
                pattern = text[i:i+length]
                if len(set(pattern)) > 1:  # Skip patterns with single character
                    patterns[pattern] += 1
        
        # Filter to only repeated patterns
        repeated_patterns = {p: c for p, c in patterns.items() if c > 1}
        
        return repeated_patterns
    
    def _mdl_histogram(self, data: List[float], precision: float) -> Dict[str, Any]:
        """MDL for histogram model."""
        # Discretize data
        min_val, max_val = min(data), max(data)
        bins = max(1, int((max_val - min_val) / precision))
        
        # Count frequencies
        counts = Counter()
        for x in data:
            bin_idx = min(bins - 1, int((x - min_val) / precision))
            counts[bin_idx] += 1
        
        # Model description length (parameters)
        model_length = math.log2(bins) + bins * math.log2(len(data))
        
        # Data description length given model
        data_length = 0
        total_count = len(data)
        for count in counts.values():
            if count > 0:
                prob = count / total_count
                data_length -= count * math.log2(prob)
        
        total_length = model_length + data_length
        
        return {
            "model": "histogram",
            "bins": bins,
            "model_length": model_length,
            "data_length": data_length,
            "total_length": total_length,
            "parameters": {"bins": bins, "precision": precision}
        }
    
    def _mdl_gaussian(self, data: List[float]) -> Dict[str, Any]:
        """MDL for Gaussian model."""
        data_array = np.array(data)
        mean = np.mean(data_array)
        std = np.std(data_array)
        
        # Model description length (2 parameters: mean, std)
        precision_bits = 32  # Assume 32-bit precision for parameters
        model_length = 2 * precision_bits
        
        # Data description length given model
        data_length = 0
        for x in data:
            # Negative log likelihood
            data_length += 0.5 * ((x - mean) / std) ** 2 + 0.5 * math.log(2 * math.pi * std ** 2)
        
        # Convert to bits
        data_length *= math.log2(math.e)
        total_length = model_length + data_length
        
        return {
            "model": "gaussian",
            "mean": mean,
            "std": std,
            "model_length": model_length,
            "data_length": data_length,
            "total_length": total_length,
            "parameters": {"mean": mean, "std": std}
        }
    
    def _mdl_uniform(self, data: List[float]) -> Dict[str, Any]:
        """MDL for uniform model."""
        min_val, max_val = min(data), max(data)
        
        # Model description length (2 parameters: min, max)
        precision_bits = 32
        model_length = 2 * precision_bits
        
        # Data description length given model
        if max_val > min_val:
            data_length = len(data) * math.log2(max_val - min_val)
        else:
            data_length = 0  # All data points identical
        
        total_length = model_length + data_length
        
        return {
            "model": "uniform",
            "min": min_val,
            "max": max_val,
            "model_length": model_length,
            "data_length": data_length,
            "total_length": total_length,
            "parameters": {"min": min_val, "max": max_val}
        }


def estimate_kolmogorov_complexity(data: Union[str, bytes, np.ndarray],
                                 method: str = "lzma",
                                 normalize: bool = True) -> float:
    """
    Convenience function to estimate Kolmogorov complexity.
    
    Args:
        data: Input data
        method: Compression method ("zlib", "bz2", "gzip", "lzma")
        normalize: Whether to normalize by data size
        
    Returns:
        Estimated complexity value
    """
    estimator = KolmogorovComplexityEstimator(CompressionMethod(method))
    result = estimator.estimate_complexity(data, normalize=normalize)
    return result.normalized_complexity if normalize else result.raw_complexity


def compression_distance(x: Union[str, bytes, np.ndarray],
                        y: Union[str, bytes, np.ndarray],
                        method: str = "lzma") -> float:
    """
    Convenience function to calculate normalized compression distance.
    
    Args:
        x: First object
        y: Second object
        method: Compression method
        
    Returns:
        Normalized compression distance (0 = identical, 1 = maximally different)
    """
    estimator = KolmogorovComplexityEstimator(CompressionMethod(method))
    result = estimator.normalized_compression_distance(x, y)
    return result.distance


if __name__ == "__main__":
    # Example usage and demonstrations
    
    print("🔬 Kolmogorov Complexity Estimation Library Demo")
    print("=" * 60)
    
    # Create estimator
    estimator = KolmogorovComplexityEstimator()
    
    # Test data with different complexity levels
    test_strings = [
        ("Random", "xkjvbqwer12348asdflkj2903847alksjdf"),
        ("Structured", "abcabcabcabcabcabcabc"),
        ("Repetitive", "aaaaaaaaaaaaaaaaaaaaaa"),
        ("Complex", "The quick brown fox jumps over the lazy dog")
    ]
    
    print("\n📊 Complexity Estimates:")
    for name, text in test_strings:
        est = estimator.estimate_complexity(text)
        print(f"{name:12}: {est.normalized_complexity:.3f} "
              f"(ratio: {est.compression_ratio:.3f}, "
              f"confidence: {est.confidence:.3f})")
    
    # Test NCD between strings
    print("\n📏 Normalized Compression Distances:")
    for i, (name1, text1) in enumerate(test_strings):
        for name2, text2 in test_strings[i+1:]:
            ncd = estimator.normalized_compression_distance(text1, text2)
            print(f"{name1} ↔ {name2}: {ncd.distance:.3f}")
    
    # Test mutual information
    print("\n🔗 Mutual Information Estimates:")
    x = "hello world hello"
    y = "hello universe hello"
    mi = estimator.mutual_information_estimate(x, y)
    print(f"MI between '{x}' and '{y}': {mi:.1f} bits")
    
    # Test grammar-based complexity
    print("\n📝 Grammar-based Complexity:")
    text = "the cat sat on the mat and the cat was fat"
    grammar_result = estimator.grammar_based_complexity(text)
    print(f"Original: {grammar_result['original_size']} chars")
    print(f"Grammar compressed: {grammar_result['compressed_size']} chars")
    print(f"Compression ratio: {grammar_result['compression_ratio']:.3f}")
    print(f"Grammar rules: {grammar_result['grammar_rules']}")
    
    # Test algorithmic probability
    print("\n🎲 Algorithmic Probability Estimates:")
    for name, text in test_strings[:3]:
        prob = estimator.algorithmic_probability_estimate(text)
        print(f"{name}: {prob:.2e}")
    
    print("\n✅ Kolmogorov complexity estimation complete!")