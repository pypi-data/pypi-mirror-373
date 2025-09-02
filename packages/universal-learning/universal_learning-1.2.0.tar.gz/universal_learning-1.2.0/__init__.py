"""
Universal Learning Library
Based on: Solomonoff (1964) "A Formal Theory of Inductive Inference" and Hutter (2005) "Universal Artificial Intelligence"

This library implements optimal learning through algorithmic information theory and universal priors,
providing the theoretical foundation for optimal prediction and learning in any computable environment.
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🌌 Universal Learning Library - Made possible by Benedict Chen")
        print("   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\")
        print("   Support his work: \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\🍺 Buy him a beer\033]8;;\033\\")
    except:
        print("\n🌌 Universal Learning Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("   Support: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")

from .universal_learning import UniversalLearner, HypothesisProgram, Prediction
from .solomonoff_induction import SolomonoffInductor
from .aixi import AIXIAgent
from .kolmogorov_complexity import KolmogorovComplexityEstimator

# Show attribution on library import
_print_attribution()

__version__ = "1.0.0"
__authors__ = ["Based on Solomonoff (1964), Hutter (2005)"]

__all__ = [
    "UniversalLearner",
    "HypothesisProgram", 
    "Prediction",
    "SolomonoffInductor",
    "AIXIAgent",
    "KolmogorovComplexityEstimator"
]