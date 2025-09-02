"""
Backward compatibility module for Information Bottleneck
Imports from refactored modules to maintain existing API
"""

# Import the main classes from the refactored modules
from .information_bottleneck_main import InformationBottleneck
from .neural_ib import NeuralInformationBottleneck

# Maintain backward compatibility
__all__ = ["InformationBottleneck", "NeuralInformationBottleneck"]