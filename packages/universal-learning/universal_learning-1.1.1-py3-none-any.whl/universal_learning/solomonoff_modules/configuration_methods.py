"""
🎛️ CONFIGURATION METHODS MODULE - Solomonoff Induction Configuration & Optimization
=================================================================================

This module provides comprehensive configuration and parameter optimization
capabilities for Solomonoff Induction implementations, allowing users to fine-tune
algorithms for specific data types and computational constraints.

Features:
- Dynamic algorithm configuration
- Performance optimization for different data types
- Parameter validation and constraints
- Configuration profiles for common use cases
- Automatic parameter tuning based on data characteristics

Based on Solomonoff (1964) with modern optimization techniques.
Author: Benedict Chen
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import warnings
from collections import defaultdict


@dataclass
class ConfigProfile:
    """Predefined configuration profile for specific use cases"""
    name: str
    description: str
    complexity_method: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    performance_characteristics: Dict[str, str] = field(default_factory=dict)


@dataclass
class OptimizationResult:
    """Result of parameter optimization"""
    best_parameters: Dict[str, Any]
    performance_score: float
    optimization_time: float
    iterations: int
    convergence_info: Dict[str, Any]


class ConfigurationMethodsMixin:
    """
    🎛️ Configuration and parameter optimization for Solomonoff Induction
    
    Provides comprehensive control over algorithm behavior, including:
    - Method selection and weighting
    - Performance tuning for specific data types
    - Automatic parameter optimization
    - Configuration validation and constraints
    - Preset profiles for common scenarios
    
    The configuration system balances theoretical soundness with practical
    computational constraints, allowing users to optimize the universal
    prediction approach for their specific needs.
    """
    
    def __init__(self):
        """Initialize configuration system"""
        # Configuration profiles
        self._config_profiles = self._initialize_config_profiles()
        
        # Optimization history
        self._optimization_history = []
        
        # Performance metrics tracking
        self._performance_metrics = {}

    def set_program_generation_method(self, method: str):
        """
        Configure program generation method for maximum user control
        
        Args:
            method: One of 'utm_approximation', 'compression_based', 
                   'context_trees', 'enhanced_patterns', 'basic'
        """
        valid_methods = [
            'utm_approximation', 
            'compression_based', 
            'context_trees', 
            'enhanced_patterns', 
            'basic'
        ]
        
        if method in valid_methods:
            self.program_generation_method = method
            print(f"Program generation method set to: {method}")
        else:
            raise ValueError(f"Invalid method. Choose from: {valid_methods}")

    def configure_utm_parameters(self, max_length: int = 8, 
                                max_programs_per_length: int = 100, 
                                max_steps: int = 1000, 
                                instruction_set: Optional[str] = None):
        """
        Configure Universal Turing Machine approximation parameters
        
        Args:
            max_length: Maximum program length to search
            max_programs_per_length: Max programs to test per length
            max_steps: Maximum execution steps per program
            instruction_set: UTM instruction set ('brainfuck', 'lambda', 'binary')
        """
        # Validate parameters
        if max_length < 1 or max_length > 30:
            warnings.warn(f"max_length={max_length} may be inefficient. Recommended: 8-20")
        
        if max_programs_per_length < 10:
            warnings.warn(f"max_programs_per_length={max_programs_per_length} may miss patterns")
        
        self.utm_max_length = max_length
        self.utm_max_programs_per_length = max_programs_per_length
        self.utm_max_steps = max_steps
        
        if instruction_set:
            valid_sets = ['brainfuck', 'lambda', 'binary']
            if instruction_set in valid_sets:
                self.utm_instruction_set = instruction_set
            else:
                raise ValueError(f"Invalid instruction set. Choose from: {valid_sets}")
        
        print("UTM parameters configured")

    def configure_compression_methods(self, methods: List[str]):
        """
        Configure compression methods for complexity estimation
        
        Args:
            methods: List of compression methods to use
                    Options: 'zlib', 'lz77_sim', 'rle', 'lzma', 'bzip2'
        """
        valid_methods = ['zlib', 'lz77_sim', 'rle', 'lzma', 'bzip2']
        
        if not all(m in valid_methods for m in methods):
            invalid = [m for m in methods if m not in valid_methods]
            raise ValueError(f"Invalid methods {invalid}. Choose from: {valid_methods}")
        
        if len(methods) == 0:
            raise ValueError("At least one compression method must be specified")
            
        self.compression_methods = methods
        print(f"Compression methods set to: {methods}")

    def configure_pattern_types(self, pattern_types: List[str]):
        """
        Configure enhanced pattern detection types
        
        Args:
            pattern_types: List of pattern types to detect
                          Options: 'constant', 'arithmetic', 'geometric', 
                                  'periodic', 'fibonacci', 'polynomial', 
                                  'recursive', 'statistical'
        """
        valid_types = [
            'constant', 'arithmetic', 'geometric', 'periodic', 
            'fibonacci', 'polynomial', 'recursive', 'statistical'
        ]
        
        if not all(p in valid_types for p in pattern_types):
            invalid = [p for p in pattern_types if p not in valid_types]
            raise ValueError(f"Invalid pattern types {invalid}. Choose from: {valid_types}")
        
        if len(pattern_types) == 0:
            warnings.warn("No pattern types specified. Using default set.")
            pattern_types = ['constant', 'arithmetic', 'periodic']
            
        self.enhanced_pattern_types = pattern_types
        print(f"Pattern types set to: {pattern_types}")

    def configure_ensemble_weights(self, method_weights: Dict[str, float]):
        """
        Configure weights for ensemble method combination
        
        Args:
            method_weights: Dictionary mapping method names to weights
                           Methods: 'BASIC_PATTERNS', 'COMPRESSION_BASED',
                                   'UNIVERSAL_TURING', 'CONTEXT_TREE'
        """
        valid_methods = ['BASIC_PATTERNS', 'COMPRESSION_BASED', 'UNIVERSAL_TURING', 'CONTEXT_TREE']
        
        # Validate method names
        invalid_methods = [m for m in method_weights.keys() if m not in valid_methods]
        if invalid_methods:
            raise ValueError(f"Invalid methods {invalid_methods}. Valid: {valid_methods}")
        
        # Validate weights are positive
        if not all(w > 0 for w in method_weights.values()):
            raise ValueError("All weights must be positive")
        
        # Normalize weights to sum to 1
        total_weight = sum(method_weights.values())
        normalized_weights = {method: weight/total_weight 
                            for method, weight in method_weights.items()}
        
        self.ensemble_method_weights = normalized_weights
        print(f"Ensemble weights configured: {normalized_weights}")

    def configure_performance_settings(self, enable_caching: bool = True,
                                     enable_parallel: bool = False,
                                     max_cache_size: int = 1000,
                                     memory_limit_mb: Optional[int] = None):
        """
        Configure performance and resource usage settings
        
        Args:
            enable_caching: Enable complexity calculation caching
            enable_parallel: Enable parallel processing (where available)
            max_cache_size: Maximum number of cached complexity calculations
            memory_limit_mb: Memory limit in MB (None = no limit)
        """
        self.enable_caching = enable_caching
        self.enable_parallel = enable_parallel
        self.max_cache_size = max_cache_size
        
        if memory_limit_mb is not None and memory_limit_mb < 100:
            warnings.warn("Memory limit < 100MB may severely impact performance")
        
        self.memory_limit_mb = memory_limit_mb
        
        # Initialize or clear cache based on settings
        if enable_caching:
            if not hasattr(self, 'complexity_cache'):
                self.complexity_cache = {}
            # Trim cache if needed
            if len(self.complexity_cache) > max_cache_size:
                # Keep most recent entries
                items = list(self.complexity_cache.items())
                self.complexity_cache = dict(items[-max_cache_size:])
        else:
            self.complexity_cache = None
        
        print(f"Performance settings: caching={enable_caching}, "
              f"parallel={enable_parallel}, cache_size={max_cache_size}")

    def load_config_profile(self, profile_name: str):
        """
        Load a predefined configuration profile
        
        Args:
            profile_name: Name of profile to load
                         Options: 'fast', 'balanced', 'accurate', 'time_series',
                                 'text_data', 'binary_data', 'scientific'
        """
        if profile_name not in self._config_profiles:
            available = list(self._config_profiles.keys())
            raise ValueError(f"Profile '{profile_name}' not found. Available: {available}")
        
        profile = self._config_profiles[profile_name]
        
        # Apply profile settings
        if hasattr(self, 'config') and self.config is not None:
            # Update config object
            for param, value in profile.parameters.items():
                if hasattr(self.config, param):
                    setattr(self.config, param, value)
        
        # Apply direct settings
        for param, value in profile.parameters.items():
            if hasattr(self, param):
                setattr(self, param, value)
        
        print(f"Loaded config profile: {profile.name}")
        print(f"Description: {profile.description}")

    def optimize_parameters_for_data(self, sample_sequences: List[List[int]], 
                                   optimization_target: str = 'prediction_accuracy',
                                   max_iterations: int = 50,
                                   validation_split: float = 0.2) -> OptimizationResult:
        """
        Automatically optimize parameters for specific data
        
        Uses sample sequences to find optimal parameter settings
        by testing different configurations and measuring performance.
        
        Args:
            sample_sequences: List of representative sequences for optimization
            optimization_target: 'prediction_accuracy', 'speed', 'complexity_estimate'
            max_iterations: Maximum optimization iterations
            validation_split: Fraction of data to use for validation
        
        Returns:
            OptimizationResult with best parameters and performance metrics
        """
        if not sample_sequences:
            raise ValueError("At least one sample sequence required")
        
        start_time = time.time()
        
        # Split data
        n_validation = max(1, int(len(sample_sequences) * validation_split))
        train_sequences = sample_sequences[:-n_validation]
        val_sequences = sample_sequences[-n_validation:]
        
        # Define parameter search space
        parameter_space = self._get_parameter_search_space()
        
        # Track best configuration
        best_score = float('-inf') if optimization_target == 'prediction_accuracy' else float('inf')
        best_params = {}
        
        # Optimization loop
        for iteration in range(max_iterations):
            # Sample parameter configuration
            current_params = self._sample_parameter_configuration(parameter_space)
            
            # Apply parameters temporarily
            original_params = self._backup_current_parameters()
            self._apply_parameter_configuration(current_params)
            
            try:
                # Evaluate configuration
                score = self._evaluate_configuration(train_sequences, val_sequences, optimization_target)
                
                # Update best if improved
                is_better = (score > best_score if optimization_target == 'prediction_accuracy' 
                           else score < best_score)
                
                if is_better:
                    best_score = score
                    best_params = current_params.copy()
                
            except Exception as e:
                print(f"Configuration failed: {e}")
                score = float('-inf') if optimization_target == 'prediction_accuracy' else float('inf')
            
            # Restore original parameters
            self._restore_parameters(original_params)
            
            if iteration % 10 == 0:
                print(f"Optimization iteration {iteration}: best_score={best_score:.4f}")
        
        # Apply best parameters
        self._apply_parameter_configuration(best_params)
        
        optimization_time = time.time() - start_time
        
        result = OptimizationResult(
            best_parameters=best_params,
            performance_score=best_score,
            optimization_time=optimization_time,
            iterations=max_iterations,
            convergence_info={'target': optimization_target, 'final_score': best_score}
        )
        
        self._optimization_history.append(result)
        
        print(f"Parameter optimization completed in {optimization_time:.2f}s")
        print(f"Best {optimization_target}: {best_score:.4f}")
        
        return result

    def get_configuration_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of current configuration
        
        Returns:
            Dictionary with all configuration settings and their values
        """
        summary = {}
        
        # Core settings
        summary['complexity_method'] = getattr(self, 'config', {})
        if hasattr(self.config, 'complexity_method'):
            summary['complexity_method'] = self.config.complexity_method
        
        # Program generation
        summary['program_generation_method'] = getattr(self, 'program_generation_method', 'not_set')
        
        # UTM settings
        summary['utm_settings'] = {
            'max_length': getattr(self, 'utm_max_length', 'not_set'),
            'max_programs_per_length': getattr(self, 'utm_max_programs_per_length', 'not_set'),
            'max_steps': getattr(self, 'utm_max_steps', 'not_set'),
            'instruction_set': getattr(self, 'utm_instruction_set', 'not_set')
        }
        
        # Compression settings
        summary['compression_methods'] = getattr(self, 'compression_methods', 'not_set')
        
        # Pattern settings
        summary['pattern_types'] = getattr(self, 'enhanced_pattern_types', 'not_set')
        
        # Performance settings
        summary['performance_settings'] = {
            'caching_enabled': getattr(self, 'enable_caching', 'not_set'),
            'parallel_enabled': getattr(self, 'enable_parallel', 'not_set'),
            'cache_size': getattr(self, 'max_cache_size', 'not_set'),
            'memory_limit_mb': getattr(self, 'memory_limit_mb', 'not_set')
        }
        
        # Ensemble weights
        summary['ensemble_weights'] = getattr(self, 'ensemble_method_weights', 'not_set')
        
        return summary

    def validate_configuration(self) -> List[str]:
        """
        Validate current configuration and return warnings/issues
        
        Returns:
            List of warning messages for configuration issues
        """
        warnings = []
        
        # Check UTM parameters
        if hasattr(self, 'utm_max_length'):
            if self.utm_max_length > 20:
                warnings.append("UTM max_length > 20 may cause slow performance")
            if self.utm_max_length < 5:
                warnings.append("UTM max_length < 5 may miss complex patterns")
        
        # Check compression methods
        if hasattr(self, 'compression_methods'):
            if 'bzip2' in self.compression_methods:
                warnings.append("BZIP2 compression is very slow for real-time applications")
        
        # Check cache settings
        if hasattr(self, 'max_cache_size') and self.max_cache_size > 10000:
            warnings.append("Large cache size may consume significant memory")
        
        # Check ensemble weights
        if hasattr(self, 'ensemble_method_weights'):
            if len(self.ensemble_method_weights) < 2:
                warnings.append("Ensemble with <2 methods may not provide robustness benefits")
        
        return warnings

    def reset_to_defaults(self):
        """Reset all configuration to default values"""
        # Core defaults
        self.program_generation_method = 'enhanced_patterns'
        
        # UTM defaults
        self.utm_max_length = 8
        self.utm_max_programs_per_length = 100
        self.utm_max_steps = 1000
        self.utm_instruction_set = 'brainfuck'
        
        # Compression defaults
        self.compression_methods = ['zlib', 'lz77_sim']
        
        # Pattern defaults
        self.enhanced_pattern_types = ['constant', 'arithmetic', 'geometric', 'periodic']
        
        # Performance defaults
        self.enable_caching = True
        self.enable_parallel = False
        self.max_cache_size = 1000
        self.memory_limit_mb = None
        
        # Clear cache
        if hasattr(self, 'complexity_cache'):
            self.complexity_cache = {}
        
        print("Configuration reset to defaults")

    # Private helper methods
    
    def _initialize_config_profiles(self) -> Dict[str, ConfigProfile]:
        """Initialize predefined configuration profiles"""
        profiles = {}
        
        # Fast profile - minimal computation
        profiles['fast'] = ConfigProfile(
            name="Fast",
            description="Optimized for speed with basic pattern recognition",
            complexity_method="BASIC_PATTERNS",
            parameters={
                'program_generation_method': 'basic',
                'utm_max_length': 6,
                'utm_max_programs_per_length': 50,
                'compression_methods': ['zlib'],
                'enhanced_pattern_types': ['constant', 'arithmetic', 'periodic'],
                'enable_caching': True,
                'max_cache_size': 500
            },
            performance_characteristics={
                'speed': 'very_fast',
                'accuracy': 'moderate',
                'memory_usage': 'low'
            }
        )
        
        # Balanced profile - good speed/accuracy trade-off
        profiles['balanced'] = ConfigProfile(
            name="Balanced",
            description="Balanced speed and accuracy for general use",
            complexity_method="HYBRID",
            parameters={
                'program_generation_method': 'enhanced_patterns',
                'utm_max_length': 10,
                'utm_max_programs_per_length': 100,
                'compression_methods': ['zlib', 'lz77_sim'],
                'enhanced_pattern_types': ['constant', 'arithmetic', 'geometric', 'periodic', 'fibonacci'],
                'enable_caching': True,
                'max_cache_size': 1000
            },
            performance_characteristics={
                'speed': 'fast',
                'accuracy': 'good',
                'memory_usage': 'moderate'
            }
        )
        
        # Accurate profile - maximum accuracy
        profiles['accurate'] = ConfigProfile(
            name="Accurate",
            description="Maximum accuracy with comprehensive methods",
            complexity_method="HYBRID",
            parameters={
                'program_generation_method': 'utm_approximation',
                'utm_max_length': 15,
                'utm_max_programs_per_length': 200,
                'compression_methods': ['zlib', 'lzma', 'lz77_sim', 'rle'],
                'enhanced_pattern_types': ['constant', 'arithmetic', 'geometric', 'periodic', 
                                         'fibonacci', 'polynomial', 'recursive', 'statistical'],
                'enable_caching': True,
                'max_cache_size': 2000
            },
            performance_characteristics={
                'speed': 'slow',
                'accuracy': 'excellent',
                'memory_usage': 'high'
            }
        )
        
        # Time series profile
        profiles['time_series'] = ConfigProfile(
            name="Time Series",
            description="Optimized for temporal data and forecasting",
            complexity_method="CONTEXT_TREE",
            parameters={
                'program_generation_method': 'context_trees',
                'enhanced_pattern_types': ['arithmetic', 'periodic', 'polynomial', 'recursive'],
                'compression_methods': ['lz77_sim', 'rle'],
                'enable_caching': True
            },
            performance_characteristics={
                'speed': 'fast',
                'accuracy': 'good_for_temporal',
                'memory_usage': 'moderate'
            }
        )
        
        return profiles
    
    def _get_parameter_search_space(self) -> Dict[str, List[Any]]:
        """Define search space for parameter optimization"""
        return {
            'utm_max_length': [6, 8, 10, 12, 15],
            'utm_max_programs_per_length': [50, 100, 200],
            'compression_methods': [
                ['zlib'],
                ['zlib', 'lz77_sim'],
                ['zlib', 'lzma'],
                ['zlib', 'lz77_sim', 'rle']
            ],
            'enhanced_pattern_types': [
                ['constant', 'arithmetic', 'periodic'],
                ['constant', 'arithmetic', 'geometric', 'periodic'],
                ['constant', 'arithmetic', 'geometric', 'periodic', 'fibonacci'],
                ['constant', 'arithmetic', 'geometric', 'periodic', 'fibonacci', 'polynomial']
            ],
            'max_cache_size': [500, 1000, 2000]
        }
    
    def _sample_parameter_configuration(self, parameter_space: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Sample a random parameter configuration from search space"""
        config = {}
        for param, options in parameter_space.items():
            config[param] = np.random.choice(len(options))
            config[param] = options[config[param]]
        return config
    
    def _backup_current_parameters(self) -> Dict[str, Any]:
        """Backup current parameter values"""
        backup = {}
        params = ['utm_max_length', 'utm_max_programs_per_length', 'compression_methods',
                 'enhanced_pattern_types', 'max_cache_size']
        
        for param in params:
            if hasattr(self, param):
                backup[param] = getattr(self, param)
        
        return backup
    
    def _apply_parameter_configuration(self, config: Dict[str, Any]):
        """Apply parameter configuration"""
        for param, value in config.items():
            if hasattr(self, param) or param in ['utm_max_length', 'utm_max_programs_per_length',
                                                'compression_methods', 'enhanced_pattern_types',
                                                'max_cache_size']:
                setattr(self, param, value)
    
    def _restore_parameters(self, backup: Dict[str, Any]):
        """Restore parameters from backup"""
        for param, value in backup.items():
            setattr(self, param, value)
    
    def _evaluate_configuration(self, train_sequences: List[List[int]], 
                              val_sequences: List[List[int]], 
                              target: str) -> float:
        """Evaluate a parameter configuration"""
        if target == 'prediction_accuracy':
            return self._evaluate_prediction_accuracy(train_sequences, val_sequences)
        elif target == 'speed':
            return self._evaluate_speed(train_sequences)
        elif target == 'complexity_estimate':
            return self._evaluate_complexity_estimation(train_sequences)
        else:
            raise ValueError(f"Unknown optimization target: {target}")
    
    def _evaluate_prediction_accuracy(self, train_sequences: List[List[int]], 
                                    val_sequences: List[List[int]]) -> float:
        """Evaluate prediction accuracy on validation sequences"""
        accuracies = []
        
        for seq in val_sequences:
            if len(seq) < 2:
                continue
                
            try:
                # Use most of sequence for training, last element for testing
                train_part = seq[:-1]
                true_next = seq[-1]
                
                predictions = self.predict_next(train_part)
                predicted_next = max(predictions.keys(), key=lambda k: predictions[k])
                
                accuracy = 1.0 if predicted_next == true_next else 0.0
                accuracies.append(accuracy)
                
            except Exception:
                continue
        
        return np.mean(accuracies) if accuracies else 0.0
    
    def _evaluate_speed(self, sequences: List[List[int]]) -> float:
        """Evaluate processing speed (lower is better)"""
        start_time = time.time()
        
        for seq in sequences[:min(5, len(sequences))]:  # Test on subset
            try:
                self.predict_next(seq)
            except Exception:
                continue
        
        elapsed_time = time.time() - start_time
        return elapsed_time  # Lower is better
    
    def _evaluate_complexity_estimation(self, sequences: List[List[int]]) -> float:
        """Evaluate quality of complexity estimation"""
        complexities = []
        
        for seq in sequences:
            try:
                complexity = self.get_complexity_estimate(seq)
                if complexity != float('inf'):
                    complexities.append(complexity)
            except Exception:
                continue
        
        if not complexities:
            return float('inf')
        
        # Return negative mean complexity (lower complexity is better)
        return -np.mean(complexities)