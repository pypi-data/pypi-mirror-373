"""
Information Bottleneck Library
Based on: Tishby, Pereira & Bialek (1999) "The Information Bottleneck Method"

This library implements the information-theoretic principle that explains
why deep learning works and provides principled methods for representation learning.
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🔍 Information Bottleneck Library - Made possible by Benedict Chen")
        print("   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\")
        print("   Support his work: \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\🍺 Buy him a beer\033]8;;\033\\")
    except:
        print("\n🔍 Information Bottleneck Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("   Support: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")

# Import unified implementation with all functionality
from .information_bottleneck import (
    InformationBottleneck,
    NeuralInformationBottleneck,
    create_information_bottleneck,
    run_ib_benchmark_suite,
    IBConfig,
    NeuralIBConfig,
    IBMethod,
    InitializationMethod
)

# Import additional modular components
from .mutual_info_estimator import MutualInfoEstimator
from .ib_optimizer import IBOptimizer

# Try to import optional components
try:
    from .deep_ib import DeepInformationBottleneck
except ImportError:
    DeepInformationBottleneck = None

# Backward compatibility factory functions  
from .information_bottleneck_main import create_discrete_ib, create_neural_ib, create_continuous_ib

# Show attribution on library import
_print_attribution()

__version__ = "1.0.0"
__authors__ = ["Based on Tishby, Pereira & Bialek (1999)"]

__all__ = [
    # Core unified classes
    "InformationBottleneck",
    "NeuralInformationBottleneck",
    
    # Configuration
    "IBConfig",
    "NeuralIBConfig", 
    "IBMethod",
    "InitializationMethod",
    
    # Factory functions
    "create_information_bottleneck",
    "create_discrete_ib",
    "create_neural_ib", 
    "create_continuous_ib",
    
    # Utility functions
    "run_ib_benchmark_suite",
    
    # Additional components
    "MutualInfoEstimator",
    "IBOptimizer",
    "DeepInformationBottleneck"  # May be None if not available
]