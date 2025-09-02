"""
🧮 THEORETICAL ANALYSIS MODULE - Solomonoff Induction Theory & Analysis
====================================================================

This module implements the theoretical foundations and analysis capabilities
for Solomonoff Induction, including Kolmogorov complexity estimation,
information-theoretic analysis, and convergence properties.

Based on the mathematical foundations from:
- Solomonoff (1964) "A Formal Theory of Inductive Inference"
- Li & Vitányi (2019) "An Introduction to Kolmogorov Complexity"
- Hutter (2005) "Universal Artificial Intelligence"

Key Features:
- Kolmogorov complexity estimation and bounds
- Information-theoretic sequence analysis
- Universal prior computation and validation
- Convergence rate analysis
- Theoretical performance guarantees
- Sequence entropy and compressibility analysis

Author: Benedict Chen
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum


@dataclass
class SequenceAnalysisResult:
    """Result of theoretical sequence analysis"""
    sequence_length: int
    estimated_complexity: float
    complexity_bounds: Tuple[float, float]  # (lower, upper)
    information_content: float
    entropy_rate: float
    compressibility_score: float
    convergence_estimate: float
    theoretical_confidence: float
    analysis_details: Dict[str, Any]


@dataclass
class ComplexityBounds:
    """Theoretical bounds on Kolmogorov complexity"""
    lower_bound: float
    upper_bound: float
    tight_bound: Optional[float]
    confidence: float
    method_used: str


class TheoreticalAnalysisMixin:
    """
    🧮 Theoretical analysis and foundations for Solomonoff Induction
    
    This mixin provides the mathematical and theoretical backbone for
    universal induction, including complexity analysis, information theory,
    and convergence guarantees.
    
    The theoretical foundation rests on Kolmogorov complexity K(x) and
    the universal distribution P(x) = Σ_{p: U(p)=x} 2^(-|p|).
    """
    
    def analyze_sequence(self, sequence: List[int]) -> SequenceAnalysisResult:
        """
        🔬 Comprehensive theoretical analysis of a sequence
        
        Provides deep theoretical insights into sequence properties:
        - Kolmogorov complexity estimates and bounds
        - Information-theoretic measures (entropy, compressibility)
        - Convergence properties for prediction
        - Theoretical performance guarantees
        
        Args:
            sequence: Input sequence to analyze
            
        Returns:
            SequenceAnalysisResult with comprehensive theoretical metrics
        """
        if not sequence:
            return SequenceAnalysisResult(
                sequence_length=0,
                estimated_complexity=0.0,
                complexity_bounds=(0.0, 0.0),
                information_content=0.0,
                entropy_rate=0.0,
                compressibility_score=0.0,
                convergence_estimate=0.0,
                theoretical_confidence=0.0,
                analysis_details={}
            )
        
        # Core complexity estimation
        estimated_complexity = self.get_complexity_estimate(sequence)
        complexity_bounds = self._compute_complexity_bounds(sequence)
        
        # Information-theoretic analysis
        information_content = self._compute_information_content(sequence)
        entropy_rate = self._compute_entropy_rate(sequence)
        
        # Compressibility analysis
        compressibility_score = self._analyze_compressibility(sequence)
        
        # Convergence analysis
        convergence_estimate = self._estimate_convergence_rate(sequence)
        
        # Overall theoretical confidence
        theoretical_confidence = self._compute_theoretical_confidence(sequence)
        
        # Detailed analysis
        analysis_details = {
            'universal_prior_mass': self._compute_universal_prior_mass(sequence),
            'algorithmic_probability': self._compute_algorithmic_probability(sequence),
            'minimum_description_length': self._compute_mdl(sequence),
            'symmetry_analysis': self._analyze_symmetries(sequence),
            'pattern_complexity_breakdown': self._analyze_pattern_complexity(sequence),
            'theoretical_prediction_error': self._estimate_prediction_error_bound(sequence),
            'solomonoff_complexity': self._compute_solomonoff_complexity(sequence)
        }
        
        return SequenceAnalysisResult(
            sequence_length=len(sequence),
            estimated_complexity=estimated_complexity,
            complexity_bounds=(complexity_bounds.lower_bound, complexity_bounds.upper_bound),
            information_content=information_content,
            entropy_rate=entropy_rate,
            compressibility_score=compressibility_score,
            convergence_estimate=convergence_estimate,
            theoretical_confidence=theoretical_confidence,
            analysis_details=analysis_details
        )

    def get_complexity_estimate(self, sequence: List[int]) -> float:
        """
        📏 Estimate Kolmogorov complexity using configured method
        
        Implements K(x) ≈ min{|p| : U(p) = x} where U is universal TM.
        Uses the best available approximation method.
        
        Args:
            sequence: Input sequence
            
        Returns:
            Estimated Kolmogorov complexity in bits
        """
        # Check cache first
        if hasattr(self, 'complexity_cache') and self.complexity_cache is not None:
            seq_key = tuple(sequence)
            if seq_key in self.complexity_cache:
                return self.complexity_cache[seq_key]
        
        programs = self._generate_programs_configurable(sequence)
        fitting_programs = [p for p in programs if p['fits_sequence']]
        
        if not fitting_programs:
            complexity = float('inf')  # No program found
        else:
            # Return complexity of shortest program (lowest complexity estimate)
            complexity = min(p.get('complexity', p.get('length', float('inf'))) for p in fitting_programs)
        
        # Cache result
        if hasattr(self, 'complexity_cache') and self.complexity_cache is not None:
            if len(self.complexity_cache) < getattr(self.config, 'max_cache_size', 1000):
                seq_key = tuple(sequence)
                self.complexity_cache[seq_key] = complexity
                
        return complexity

    def _compute_complexity_bounds(self, sequence: List[int]) -> ComplexityBounds:
        """
        📐 Compute theoretical bounds on Kolmogorov complexity
        
        Uses various theoretical results to bound K(x):
        - Information-theoretic lower bounds (entropy)
        - Compression-based upper bounds
        - Counting arguments for specific pattern classes
        
        Args:
            sequence: Input sequence
            
        Returns:
            ComplexityBounds object with lower/upper bounds and confidence
        """
        n = len(sequence)
        
        # Lower bound: Shannon entropy (information-theoretic)
        entropy_bound = self._compute_shannon_entropy(sequence)
        
        # Lower bound: Pattern analysis
        pattern_bound = self._compute_pattern_lower_bound(sequence)
        lower_bound = max(entropy_bound, pattern_bound)
        
        # Upper bound: Naive encoding (log₂(alphabet_size) × length)
        naive_upper = n * math.log2(self.alphabet_size) if hasattr(self, 'alphabet_size') else n * math.log2(256)
        
        # Upper bound: Best compression achieved
        compression_upper = self._compute_compression_upper_bound(sequence)
        upper_bound = min(naive_upper, compression_upper)
        
        # Tight bound: Best estimate from program generation
        estimated_complexity = self.get_complexity_estimate(sequence)
        tight_bound = estimated_complexity if estimated_complexity != float('inf') else None
        
        # Confidence based on bound tightness
        if tight_bound is not None:
            gap = upper_bound - lower_bound
            confidence = 1.0 / (1.0 + gap / n) if gap > 0 else 1.0
        else:
            confidence = 0.5  # Default confidence when no tight bound available
        
        return ComplexityBounds(
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            tight_bound=tight_bound,
            confidence=confidence,
            method_used="information_theoretic_and_compression"
        )

    def _compute_information_content(self, sequence: List[int]) -> float:
        """
        ℹ️ Compute information content I(x) = -log₂(P(x))
        
        Uses the universal distribution to estimate information content.
        Higher information content indicates more surprising/complex sequences.
        
        Args:
            sequence: Input sequence
            
        Returns:
            Information content in bits
        """
        try:
            prob = self._compute_algorithmic_probability(sequence)
            if prob <= 0:
                return float('inf')
            return -math.log2(prob)
        except Exception:
            # Fallback: use empirical probability
            return self._compute_shannon_entropy(sequence)

    def _compute_entropy_rate(self, sequence: List[int]) -> float:
        """
        📊 Compute entropy rate h = lim_{n→∞} H(X₁...Xₙ)/n
        
        Estimates the per-symbol entropy rate using various window sizes.
        Fundamental quantity for understanding sequence complexity growth.
        
        Args:
            sequence: Input sequence
            
        Returns:
            Estimated entropy rate in bits per symbol
        """
        if len(sequence) <= 1:
            return 0.0
            
        # Compute entropy for different block lengths
        entropies = []
        max_block_length = min(8, len(sequence) // 2)
        
        for block_length in range(1, max_block_length + 1):
            blocks = []
            for i in range(len(sequence) - block_length + 1):
                block = tuple(sequence[i:i+block_length])
                blocks.append(block)
            
            if blocks:
                block_counts = Counter(blocks)
                total_blocks = len(blocks)
                entropy = -sum((count/total_blocks) * math.log2(count/total_blocks) 
                             for count in block_counts.values())
                entropies.append(entropy / block_length)
        
        # Return entropy rate estimate (typically converges for large blocks)
        return entropies[-1] if entropies else 0.0

    def _analyze_compressibility(self, sequence: List[int]) -> float:
        """
        🗜️ Analyze sequence compressibility
        
        Compressibility score ∈ [0,1] where:
        - 0 = completely incompressible (random)
        - 1 = perfectly compressible (simple pattern)
        
        Args:
            sequence: Input sequence
            
        Returns:
            Compressibility score ∈ [0,1]
        """
        if len(sequence) <= 1:
            return 1.0  # Trivially compressible
            
        # Maximum possible information (uniform random)
        max_info = len(sequence) * math.log2(self.alphabet_size) if hasattr(self, 'alphabet_size') else len(sequence) * 8
        
        # Actual complexity estimate
        actual_complexity = self.get_complexity_estimate(sequence)
        
        if actual_complexity == float('inf'):
            return 0.0  # Incompressible
            
        # Compressibility as 1 - (actual_complexity / max_possible_complexity)
        compressibility = 1.0 - min(1.0, actual_complexity / max_info)
        
        return max(0.0, compressibility)

    def _estimate_convergence_rate(self, sequence: List[int]) -> float:
        """
        📈 Estimate convergence rate for Solomonoff prediction
        
        Theoretical result: prediction error decreases as O(2^(-K(source)/2))
        where K(source) is the complexity of the true generating process.
        
        Args:
            sequence: Input sequence (representing observed data from source)
            
        Returns:
            Estimated convergence rate (higher = faster convergence)
        """
        # Estimate source complexity from observed sequence
        source_complexity_estimate = self.get_complexity_estimate(sequence)
        
        if source_complexity_estimate == float('inf'):
            return 0.0  # No convergence if no pattern found
            
        # Convergence rate based on theoretical bound
        # Rate ∝ 2^(-K/2) where K is source complexity
        convergence_rate = 2 ** (-source_complexity_estimate / 2)
        
        # Adjust for sequence length (more data = better convergence)
        length_factor = min(1.0, len(sequence) / 100.0)  # Normalize to [0,1]
        
        return convergence_rate * length_factor

    def _compute_theoretical_confidence(self, sequence: List[int]) -> float:
        """
        🎯 Compute theoretical confidence in analysis
        
        Combines multiple theoretical indicators to assess reliability:
        - Complexity bound tightness
        - Pattern consistency
        - Convergence indicators
        - Data sufficiency
        
        Args:
            sequence: Input sequence
            
        Returns:
            Theoretical confidence ∈ [0,1]
        """
        if len(sequence) < 3:
            return 0.1  # Very low confidence for short sequences
            
        # Factor 1: Complexity bound tightness
        bounds = self._compute_complexity_bounds(sequence)
        bound_tightness = 1.0 / (1.0 + (bounds.upper_bound - bounds.lower_bound) / len(sequence))
        
        # Factor 2: Pattern consistency across methods
        consistency_score = self._evaluate_pattern_consistency(sequence)
        
        # Factor 3: Convergence indicators
        convergence_factor = min(1.0, self._estimate_convergence_rate(sequence) * 10)
        
        # Factor 4: Data sufficiency (more data = higher confidence)
        data_sufficiency = min(1.0, len(sequence) / 50.0)
        
        # Combine factors (geometric mean for balanced weighting)
        confidence = (bound_tightness * consistency_score * convergence_factor * data_sufficiency) ** 0.25
        
        return max(0.1, min(1.0, confidence))

    def _compute_universal_prior_mass(self, sequence: List[int]) -> float:
        """
        🌍 Compute universal prior mass P(x) = Σ_{p: U(p)=x} 2^(-|p|)
        
        The universal prior assigns probability mass to sequences
        based on the total weight of all programs that generate them.
        
        Args:
            sequence: Input sequence
            
        Returns:
            Universal prior mass (approximated)
        """
        programs = self._generate_programs_configurable(sequence)
        fitting_programs = [p for p in programs if p['fits_sequence']]
        
        if not fitting_programs:
            # Fallback: uniform over sequences of this length
            return 1.0 / (self.alphabet_size ** len(sequence)) if hasattr(self, 'alphabet_size') else 1e-10
            
        # Sum weights of all fitting programs
        total_mass = sum(2 ** (-p['complexity']) for p in fitting_programs)
        
        return total_mass

    def _compute_algorithmic_probability(self, sequence: List[int]) -> float:
        """
        🔢 Compute algorithmic probability
        
        Same as universal prior mass - the probability that a universal
        Turing machine outputs this sequence on random input.
        
        Args:
            sequence: Input sequence
            
        Returns:
            Algorithmic probability
        """
        return self._compute_universal_prior_mass(sequence)

    def _compute_mdl(self, sequence: List[int]) -> float:
        """
        📦 Compute Minimum Description Length (MDL)
        
        MDL principle: best model minimizes description length
        = model_complexity + data_given_model_complexity
        
        Args:
            sequence: Input sequence
            
        Returns:
            Estimated MDL in bits
        """
        programs = self._generate_programs_configurable(sequence)
        fitting_programs = [p for p in programs if p['fits_sequence']]
        
        if not fitting_programs:
            # Fallback: naive encoding
            return len(sequence) * math.log2(self.alphabet_size) if hasattr(self, 'alphabet_size') else len(sequence) * 8
            
        # MDL = shortest program that explains the data
        return min(p['complexity'] for p in fitting_programs)

    def _analyze_symmetries(self, sequence: List[int]) -> Dict[str, Any]:
        """
        🔄 Analyze symmetries and invariances in sequence
        
        Identifies structural regularities that could reduce complexity:
        - Translation symmetry (periodic patterns)
        - Reflection symmetry (palindromes)
        - Scaling symmetry (self-similar structures)
        
        Args:
            sequence: Input sequence
            
        Returns:
            Dictionary of symmetry analysis results
        """
        analysis = {}
        
        # Periodicity analysis
        periods_found = []
        for period in range(1, min(len(sequence) // 2, 20)):
            is_periodic = all(sequence[i] == sequence[i % period] for i in range(len(sequence)))
            if is_periodic:
                periods_found.append(period)
        
        analysis['periods'] = periods_found
        analysis['is_periodic'] = len(periods_found) > 0
        analysis['shortest_period'] = min(periods_found) if periods_found else None
        
        # Palindrome analysis
        is_palindrome = sequence == sequence[::-1]
        analysis['is_palindrome'] = is_palindrome
        
        # Self-similarity (simple version)
        analysis['self_similarity_score'] = self._compute_self_similarity(sequence)
        
        return analysis

    def _analyze_pattern_complexity(self, sequence: List[int]) -> Dict[str, float]:
        """
        🧩 Break down complexity by pattern types
        
        Analyzes how much complexity comes from different pattern types:
        constant, arithmetic, geometric, recursive, etc.
        
        Args:
            sequence: Input sequence
            
        Returns:
            Dictionary mapping pattern types to their complexity contributions
        """
        complexity_breakdown = {}
        
        programs = self._generate_programs_configurable(sequence)
        fitting_programs = [p for p in programs if p['fits_sequence']]
        
        # Group by program type
        type_complexities = defaultdict(list)
        for program in fitting_programs:
            prog_type = program.get('type', 'unknown')
            type_complexities[prog_type].append(program['complexity'])
        
        # Compute best complexity for each type
        for prog_type, complexities in type_complexities.items():
            complexity_breakdown[prog_type] = min(complexities) if complexities else float('inf')
        
        return complexity_breakdown

    def _estimate_prediction_error_bound(self, sequence: List[int]) -> float:
        """
        📊 Estimate theoretical prediction error bound
        
        Uses Solomonoff's convergence theorem to bound prediction error
        based on sequence complexity and length.
        
        Args:
            sequence: Input sequence
            
        Returns:
            Theoretical upper bound on prediction error
        """
        if len(sequence) < 2:
            return 1.0  # Maximum error for insufficient data
            
        # Theoretical bound: error ≤ K(source) / n + O(√(log n / n))
        source_complexity = self.get_complexity_estimate(sequence)
        n = len(sequence)
        
        if source_complexity == float('inf'):
            return 1.0  # No bound available
            
        # Main term: complexity divided by sequence length
        main_term = source_complexity / n
        
        # Logarithmic correction term
        log_term = math.sqrt(math.log2(n + 1) / n) if n > 1 else 1.0
        
        error_bound = main_term + 0.5 * log_term  # 0.5 is empirical constant
        
        return min(1.0, error_bound)

    def _compute_solomonoff_complexity(self, sequence: List[int]) -> float:
        """
        🧮 Compute Solomonoff complexity K_S(x) = -log₂(P(x))
        
        Solomonoff complexity is the negative log of algorithmic probability.
        It approximates Kolmogorov complexity from an information-theoretic perspective.
        
        Args:
            sequence: Input sequence
            
        Returns:
            Solomonoff complexity in bits
        """
        prob = self._compute_algorithmic_probability(sequence)
        if prob <= 0:
            return float('inf')
        return -math.log2(prob)

    # Helper methods for theoretical analysis
    
    def _compute_shannon_entropy(self, sequence: List[int]) -> float:
        """Compute Shannon entropy H(X) = -Σ p(x) log₂(p(x))"""
        if not sequence:
            return 0.0
            
        counts = Counter(sequence)
        total = len(sequence)
        entropy = -sum((count/total) * math.log2(count/total) for count in counts.values())
        
        return entropy

    def _compute_pattern_lower_bound(self, sequence: List[int]) -> float:
        """Compute lower bound based on pattern analysis"""
        # Simple heuristic: if we detect a pattern, complexity is at least pattern description length
        programs = self._generate_programs_configurable(sequence)
        fitting_programs = [p for p in programs if p['fits_sequence']]
        
        if fitting_programs:
            return min(p['complexity'] for p in fitting_programs)
        else:
            return self._compute_shannon_entropy(sequence)

    def _compute_compression_upper_bound(self, sequence: List[int]) -> float:
        """Compute upper bound using compression"""
        try:
            import zlib
            seq_bytes = bytes(sequence) if all(0 <= x <= 255 for x in sequence) else str(sequence).encode()
            compressed = zlib.compress(seq_bytes, level=9)
            return len(compressed) * 8  # Convert to bits
        except Exception:
            # Fallback: simple run-length encoding estimate
            return len(sequence) * math.log2(len(set(sequence)) + 1)

    def _evaluate_pattern_consistency(self, sequence: List[int]) -> float:
        """Evaluate consistency of pattern detection across methods"""
        # Generate programs using different methods and see if they agree
        methods = ['BASIC_PATTERNS', 'COMPRESSION_BASED']
        agreements = 0
        total_comparisons = 0
        
        try:
            results = {}
            original_method = getattr(self.config, 'complexity_method', 'BASIC_PATTERNS')
            
            for method in methods:
                self.config.complexity_method = method
                programs = self._generate_programs_configurable(sequence)
                fitting_programs = [p for p in programs if p['fits_sequence']]
                if fitting_programs:
                    results[method] = min(p['complexity'] for p in fitting_programs)
            
            # Restore original method
            self.config.complexity_method = original_method
            
            # Check agreement between methods
            if len(results) >= 2:
                complexities = list(results.values())
                max_complexity = max(complexities)
                min_complexity = min(complexities)
                
                if max_complexity > 0:
                    agreement_score = min_complexity / max_complexity
                    return agreement_score
                    
        except Exception:
            pass
            
        return 0.5  # Default moderate consistency

    def _compute_self_similarity(self, sequence: List[int]) -> float:
        """Compute self-similarity score using fractal-like analysis"""
        if len(sequence) < 4:
            return 0.0
            
        # Compare sequence with scaled/shifted versions of itself
        similarities = []
        
        for scale in [2, 3, 4]:
            if len(sequence) >= scale:
                downsampled = sequence[::scale]
                
                # Compare with original prefix
                min_len = min(len(sequence), len(downsampled))
                if min_len > 0:
                    matches = sum(1 for i in range(min_len) if sequence[i] == downsampled[i])
                    similarity = matches / min_len
                    similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0