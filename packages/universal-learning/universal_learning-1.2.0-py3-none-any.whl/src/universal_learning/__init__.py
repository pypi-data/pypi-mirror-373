"""
Universal Learning Package
=========================

This package contains implementations of universal learning algorithms
including Solomonoff Induction, AIXI, and related methods.

The package provides both monolithic and modular implementations:
- solomonoff_core: Modular Solomonoff Induction with clean separation of concerns
- solomonoff_induction: Original monolithic implementation (legacy)
"""

__version__ = "1.0.0"
__author__ = "Benedict Chen"

# Export main classes
from .solomonoff_core import SolomonoffInductor, SolomonoffConfig, ComplexityMethod, CompressionAlgorithm
from .solomonoff_core import create_fast_inductor, create_accurate_inductor, create_research_inductor

__all__ = [
    'SolomonoffInductor', 'SolomonoffConfig', 'ComplexityMethod', 'CompressionAlgorithm',
    'create_fast_inductor', 'create_accurate_inductor', 'create_research_inductor'
]