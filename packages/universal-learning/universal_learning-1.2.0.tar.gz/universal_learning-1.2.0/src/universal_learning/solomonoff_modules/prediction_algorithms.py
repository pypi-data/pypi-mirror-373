"""
🎯 PREDICTION ALGORITHMS MODULE - Solomonoff Induction Core Predictions
====================================================================

This module implements the core prediction algorithms for Solomonoff Induction,
including the universal prior calculation, algorithmic probability computation,
and Bayesian prediction updating.

Based on Solomonoff (1964) "A Formal Theory of Inductive Inference"
Mathematical foundation: P(x_n+1 | x_1...x_n) = Σ_{p: U(p) extends x_1...x_n} 2^(-|p|)

Key Features:
- Universal prior implementation (2^(-K(p)))  
- Algorithmic probability calculation
- Bayesian updating with program weights
- Ensemble prediction from multiple complexity methods
- Configurable prediction confidence thresholds

Author: Benedict Chen
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
import heapq
import statistics
from enum import Enum


class PredictionAlgorithmsMixin:
    """
    🎯 Core prediction algorithms for Solomonoff Induction
    
    Implements the mathematical heart of universal prediction:
    finding the most likely next symbol given a sequence by weighting
    all possible explanations (programs) by their simplicity.
    
    The key insight: simpler explanations get exponentially higher weight
    via the universal prior 2^(-|program|), implementing Occam's Razor
    in a mathematically principled way.
    """
    
    def predict_next(self, sequence: List[int]) -> Dict[int, float]:
        """
        🎯 Predict Next Symbol Using Universal Induction
        
        ELI5: Give me a sequence like [1,1,2,3,5,8] and I'll tell you what's most 
        likely to come next! I do this by finding all possible "rules" that could 
        explain your sequence, then voting based on how simple each rule is.
        
        Technical Implementation:
        ========================
        Computes the Solomonoff prediction distribution:
        
        P(xₙ₊₁ = s | x₁...xₙ) = Σ_{p: U(p) extends x₁...xₙ with s} 2^(-|p|) 
                                 / Σ_{p: U(p) extends x₁...xₙ} 2^(-|p|)
        
        Where:
        • p ranges over all programs that generate sequences starting with x₁...xₙ
        • U(p) is the output of program p on a Universal Turing Machine
        • |p| is the program length (Kolmogorov complexity approximation)
        • 2^(-|p|) implements the universal prior (Occam's razor)
        
        Algorithm Steps:
        ===============
        1. 🔍 PROGRAM GENERATION: Find all candidate programs that fit the sequence
           Using configured method: UTM enumeration, compression, context trees, or patterns
           
        2. 📏 COMPLEXITY ESTIMATION: Estimate K(p) ≈ |p| for each program p
           Different methods provide different approximations to true Kolmogorov complexity
           
        3. ⚖️  WEIGHT CALCULATION: Compute w_p = 2^(-K(p)) for each fitting program
           Implements universal prior: simpler explanations get exponentially more weight
           
        4. 🗳️  PREDICTION VOTING: Each program votes for its predicted next symbol
           Weight of vote proportional to 2^(-complexity)
           
        5. 📊 NORMALIZATION: Convert to proper probability distribution
           Ensures Σ P(xₙ₊₁ = s) = 1 across all possible next symbols
        
        Args:
            sequence (List[int]): Observed sequence of symbols from alphabet {0, 1, ..., alphabet_size-1}
                Length should be ≥ 1 for meaningful predictions.
                Longer sequences generally yield more confident predictions.
                Examples: [1,1,2,3,5,8,13] (Fibonacci), [1,4,9,16,25] (perfect squares)
        
        Returns:
            Dict[int, float]: Probability distribution over next symbols {0, 1, ..., alphabet_size-1}
                Key = symbol, Value = probability of that symbol occurring next
                Probabilities sum to 1.0 and are ≥ 0.0
                Higher probability indicates stronger confidence in prediction
                
        Complexity Analysis:
        ===================
        • Time: O(|sequence| × 2^max_program_length) for exhaustive program search
                O(|sequence| × poly(length)) for compression/heuristic approximations  
        • Space: O(2^max_program_length) for program storage + O(cache_size) for memoization
        
        Convergence Properties:
        ======================
        • For computable sequences: Prediction error → 0 as sequence length → ∞
        • Rate: Exponential convergence in true Kolmogorov complexity of source
        • Optimality: Dominates any other computable prediction algorithm
        
        Example Usage:
        =============
        # Fibonacci sequence prediction
        inductor = SolomonoffInductor()
        probs = inductor.predict_next([1, 1, 2, 3, 5, 8, 13])
        next_symbol = max(probs, key=probs.get)  # Most likely = 21
        confidence = probs[next_symbol]          # How confident we are
        
        # Get full distribution
        for symbol, prob in probs.items():
            print(f"P(next = {symbol}) = {prob:.3f}")
        
        Edge Cases:
        ==========
        • Empty sequence: Returns uniform distribution (no information)
        • Random sequence: Approaches uniform distribution (no pattern detectable)
        • Single symbol: May predict continuation or pattern depending on method
        • Very long sequences: May exceed memory/time limits with deep program search
        
        Performance Tips:
        ================
        • Enable caching for repeated predictions on similar sequences
        • Use BASIC_PATTERNS method for fastest results on simple data
        • Use HYBRID method for best accuracy/speed trade-off
        • Reduce max_program_length if predictions are too slow
        """
        
        # Generate candidate programs using configured method
        programs = self._generate_programs_configurable(sequence)
        
        # Calculate prediction probabilities
        predictions = {i: 0.0 for i in range(self.alphabet_size)}
        total_weight = 0.0
        
        for program in programs:
            if program['fits_sequence']:
                weight = 2 ** (-program['complexity'])  # Universal prior using complexity estimate
                
                # Get program's prediction
                next_pred = program.get('next_prediction', 0)
                predictions[next_pred] += weight
                total_weight += weight
                
        # Normalize
        if total_weight > 0:
            for symbol in predictions:
                predictions[symbol] /= total_weight
        else:
            # Uniform prior
            for symbol in predictions:
                predictions[symbol] = 1.0 / self.alphabet_size
                
        return predictions

    def predict_next_with_confidence(self, sequence: List[int]) -> Tuple[int, float, Dict[int, float]]:
        """
        🎯 Predict with confidence measure
        
        Returns the most likely next symbol along with confidence score
        and full probability distribution.
        
        Args:
            sequence: Input sequence for prediction
            
        Returns:
            Tuple of (most_likely_symbol, confidence_score, full_distribution)
            confidence_score ∈ [0,1] where 1 = completely certain, 0 = no pattern
        """
        predictions = self.predict_next(sequence)
        
        if not predictions:
            return 0, 0.0, predictions
            
        # Most likely prediction
        best_symbol = max(predictions.keys(), key=lambda k: predictions[k])
        best_prob = predictions[best_symbol]
        
        # Confidence = entropy-based measure
        # High confidence when distribution is concentrated (low entropy)
        # Low confidence when distribution is uniform (high entropy)
        entropy = -sum(p * np.log2(p + 1e-10) for p in predictions.values() if p > 0)
        max_entropy = np.log2(len(predictions))
        confidence = 1 - (entropy / max_entropy) if max_entropy > 0 else 0.0
        
        return best_symbol, confidence, predictions

    def predict_sequence_continuation(self, sequence: List[int], num_predictions: int = 5) -> List[Tuple[int, float]]:
        """
        🔮 Predict multiple future symbols
        
        Uses iterative prediction: predict next symbol, add to sequence,
        predict again, etc. Confidence generally decreases with distance.
        
        Args:
            sequence: Input sequence
            num_predictions: Number of future symbols to predict
            
        Returns:
            List of (predicted_symbol, confidence) pairs
        """
        if num_predictions <= 0:
            return []
            
        predictions = []
        current_sequence = sequence.copy()
        
        for i in range(num_predictions):
            next_symbol, confidence, _ = self.predict_next_with_confidence(current_sequence)
            predictions.append((next_symbol, confidence))
            
            # Add prediction to sequence for next iteration
            current_sequence.append(next_symbol)
            
            # Stop if confidence gets too low (pattern breaking down)
            if confidence < getattr(self, 'min_prediction_confidence', 0.1):
                break
                
        return predictions

    def algorithmic_probability(self, sequence: List[int]) -> float:
        """
        📊 Calculate algorithmic probability P(sequence)
        
        Implements the Solomonoff universal distribution:
        P(x) = Σ_{p: U(p) = x} 2^(-|p|)
        
        This is the probability that a universal Turing machine
        produces the given sequence when fed a random program.
        
        Args:
            sequence: Input sequence to evaluate
            
        Returns:
            Algorithmic probability ∈ [0, 1]
            Higher values indicate simpler/more likely sequences
        """
        programs = self._generate_programs_configurable(sequence)
        fitting_programs = [p for p in programs if p['fits_sequence']]
        
        if not fitting_programs:
            return 1.0 / (2 ** len(sequence))  # Fallback: uniform over all sequences of this length
            
        # Sum weights of all programs that generate this sequence
        total_probability = sum(2 ** (-p['complexity']) for p in fitting_programs)
        
        return total_probability

    def solomonoff_complexity(self, sequence: List[int]) -> float:
        """
        📏 Estimate Solomonoff complexity (negative log probability)
        
        K_S(x) = -log₂(P(x)) where P(x) is the algorithmic probability.
        This approximates the true Kolmogorov complexity.
        
        Args:
            sequence: Input sequence
            
        Returns:
            Estimated complexity in bits
            Lower values indicate simpler/more compressible sequences
        """
        prob = self.algorithmic_probability(sequence)
        if prob <= 0:
            return float('inf')
        return -np.log2(prob)

    def bayes_update_predictions(self, prior_predictions: Dict[int, float], 
                                observed_symbol: int) -> Dict[int, float]:
        """
        🔄 Bayesian update of predictions after observing new symbol
        
        Updates our belief about future predictions based on what we just observed.
        Programs that successfully predicted the observed symbol get higher weight.
        
        Args:
            prior_predictions: Previous prediction distribution
            observed_symbol: The symbol that actually occurred
            
        Returns:
            Updated prediction distribution incorporating the observation
        """
        # This is a simplified Bayesian update
        # In full Solomonoff induction, we'd recompute all program weights
        
        updated_predictions = prior_predictions.copy()
        
        # Boost confidence in prediction that was correct
        if observed_symbol in updated_predictions:
            # Reward correct prediction
            boost_factor = getattr(self, 'bayes_boost_factor', 1.1)
            updated_predictions[observed_symbol] *= boost_factor
            
            # Renormalize
            total = sum(updated_predictions.values())
            if total > 0:
                for symbol in updated_predictions:
                    updated_predictions[symbol] /= total
                    
        return updated_predictions

    def ensemble_prediction(self, sequence: List[int], methods: List[str] = None) -> Dict[int, float]:
        """
        🎭 Ensemble prediction combining multiple complexity methods
        
        Combines predictions from different approximation methods
        (compression, patterns, UTM, etc.) for more robust results.
        
        Args:
            sequence: Input sequence
            methods: List of method names to ensemble. If None, uses all available.
            
        Returns:
            Combined prediction distribution
        """
        if methods is None:
            methods = ['BASIC_PATTERNS', 'COMPRESSION_BASED', 'CONTEXT_TREE']
            
        ensemble_predictions = {i: 0.0 for i in range(self.alphabet_size)}
        method_weights = {}
        total_weight = 0.0
        
        # Save current method
        original_method = getattr(self.config, 'complexity_method', 'BASIC_PATTERNS')
        
        try:
            for method in methods:
                # Temporarily switch to this method
                self.config.complexity_method = method
                
                # Get predictions from this method
                method_predictions = self.predict_next(sequence)
                
                # Weight this method based on its confidence/performance
                method_confidence = self._evaluate_method_confidence(sequence, method)
                method_weights[method] = method_confidence
                total_weight += method_confidence
                
                # Add weighted predictions
                for symbol in ensemble_predictions:
                    ensemble_predictions[symbol] += method_predictions[symbol] * method_confidence
                    
        finally:
            # Restore original method
            self.config.complexity_method = original_method
            
        # Normalize ensemble predictions
        if total_weight > 0:
            for symbol in ensemble_predictions:
                ensemble_predictions[symbol] /= total_weight
        else:
            # Fallback to uniform
            for symbol in ensemble_predictions:
                ensemble_predictions[symbol] = 1.0 / self.alphabet_size
                
        return ensemble_predictions

    def _evaluate_method_confidence(self, sequence: List[int], method: str) -> float:
        """
        📊 Evaluate confidence/reliability of a complexity method
        
        Measures how well a method performs on this type of sequence.
        Methods that find simpler explanations get higher confidence.
        
        Args:
            sequence: Test sequence
            method: Method name to evaluate
            
        Returns:
            Confidence score ∈ [0, 1]
        """
        try:
            # Generate programs using this method
            original_method = getattr(self.config, 'complexity_method', 'BASIC_PATTERNS')
            self.config.complexity_method = method
            
            programs = self._generate_programs_configurable(sequence)
            fitting_programs = [p for p in programs if p['fits_sequence']]
            
            # Restore original method
            self.config.complexity_method = original_method
            
            if not fitting_programs:
                return 0.1  # Low confidence if no programs found
                
            # Confidence based on best complexity found
            best_complexity = min(p['complexity'] for p in fitting_programs)
            
            # Convert to confidence score (lower complexity = higher confidence)
            confidence = np.exp(-best_complexity / 10.0)  # Exponential decay
            
            return max(0.1, min(1.0, confidence))  # Clamp to [0.1, 1.0]
            
        except Exception:
            return 0.1  # Low confidence on error

    def get_prediction_explanations(self, sequence: List[int], top_k: int = 3) -> List[Dict]:
        """
        🔍 Get explanations for predictions
        
        Returns the top-k most influential programs/patterns that contribute
        to the prediction, along with their descriptions and weights.
        
        Args:
            sequence: Input sequence
            top_k: Number of top explanations to return
            
        Returns:
            List of explanation dictionaries with 'description', 'weight', 'prediction', etc.
        """
        programs = self._generate_programs_configurable(sequence)
        fitting_programs = [p for p in programs if p['fits_sequence']]
        
        if not fitting_programs:
            return []
            
        # Sort by weight (complexity-based)
        for program in fitting_programs:
            program['weight'] = 2 ** (-program['complexity'])
            
        # Get top-k programs
        top_programs = heapq.nlargest(top_k, fitting_programs, key=lambda p: p['weight'])
        
        explanations = []
        for program in top_programs:
            explanation = {
                'description': program.get('description', f"Pattern type: {program.get('type', 'unknown')}"),
                'weight': program['weight'],
                'complexity': program['complexity'],
                'next_prediction': program.get('next_prediction', 0),
                'program_type': program.get('type', 'unknown'),
                'confidence': program['weight']  # Weight as confidence proxy
            }
            explanations.append(explanation)
            
        return explanations

    def prediction_stability_analysis(self, sequence: List[int], perturbation_size: int = 1) -> Dict:
        """
        🔬 Analyze prediction stability under small perturbations
        
        Tests how sensitive predictions are to small changes in the input sequence.
        Stable predictions indicate robust pattern detection.
        
        Args:
            sequence: Base sequence
            perturbation_size: Size of perturbations to test
            
        Returns:
            Dictionary with stability metrics
        """
        if len(sequence) < 2:
            return {'stability_score': 0.0, 'details': 'Sequence too short'}
            
        # Get baseline prediction
        baseline_prediction = self.predict_next(sequence)
        baseline_symbol = max(baseline_prediction.keys(), key=lambda k: baseline_prediction[k])
        
        stability_scores = []
        perturbation_count = 0
        
        # Test perturbations
        for i in range(max(1, len(sequence) - 5), len(sequence)):  # Test last few positions
            original_val = sequence[i]
            
            for delta in range(-perturbation_size, perturbation_size + 1):
                if delta == 0:
                    continue
                    
                new_val = (original_val + delta) % self.alphabet_size
                if new_val == original_val:
                    continue
                    
                # Create perturbed sequence
                perturbed_sequence = sequence.copy()
                perturbed_sequence[i] = new_val
                
                try:
                    # Get prediction on perturbed sequence
                    perturbed_prediction = self.predict_next(perturbed_sequence)
                    perturbed_symbol = max(perturbed_prediction.keys(), 
                                         key=lambda k: perturbed_prediction[k])
                    
                    # Measure stability (same prediction = stable)
                    stability = 1.0 if perturbed_symbol == baseline_symbol else 0.0
                    stability_scores.append(stability)
                    perturbation_count += 1
                    
                except Exception:
                    continue
                    
        # Calculate overall stability
        if stability_scores:
            mean_stability = np.mean(stability_scores)
            stability_std = np.std(stability_scores)
        else:
            mean_stability = 0.0
            stability_std = 0.0
            
        return {
            'stability_score': mean_stability,
            'stability_std': stability_std,
            'perturbations_tested': perturbation_count,
            'baseline_prediction': baseline_symbol,
            'baseline_confidence': baseline_prediction[baseline_symbol]
        }

    def adaptive_prediction_threshold(self, sequence: List[int]) -> float:
        """
        🎚️ Adaptively determine prediction confidence threshold
        
        Automatically sets a confidence threshold based on sequence characteristics.
        More regular sequences allow lower thresholds; random sequences need higher thresholds.
        
        Args:
            sequence: Input sequence to analyze
            
        Returns:
            Recommended confidence threshold ∈ [0, 1]
        """
        if len(sequence) < 2:
            return 0.5  # Default threshold
            
        # Analyze sequence characteristics
        sequence_complexity = self.get_complexity_estimate(sequence)
        sequence_length = len(sequence)
        
        # Estimate sequence entropy (randomness)
        from collections import Counter
        symbol_counts = Counter(sequence)
        total = len(sequence)
        entropy = -sum((count/total) * np.log2(count/total) for count in symbol_counts.values())
        max_entropy = np.log2(self.alphabet_size)
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 1.0
        
        # Adaptive threshold based on complexity and entropy
        # Simple sequences: lower threshold (easier to predict)
        # Complex sequences: higher threshold (harder to predict reliably)
        
        base_threshold = 0.3
        complexity_factor = min(sequence_complexity / sequence_length, 2.0) * 0.2
        entropy_factor = normalized_entropy * 0.3
        
        adaptive_threshold = base_threshold + complexity_factor + entropy_factor
        
        return max(0.1, min(0.9, adaptive_threshold))