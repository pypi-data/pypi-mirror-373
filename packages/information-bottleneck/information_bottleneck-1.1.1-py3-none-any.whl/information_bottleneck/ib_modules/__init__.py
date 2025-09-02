"""
Information Bottleneck Modular Components
==========================================

This module provides all functionality from the original 2478-line monolithic
information_bottleneck_core.py file, now broken down into focused, maintainable 
modules while preserving 100% research accuracy.

🏗️ Modular Architecture:
- core_algorithm.py      : Main InformationBottleneck class
- core_theory.py         : Fundamental IB equations and theory
- mutual_information.py  : MI estimation methods (KSG, ensemble, etc.)
- optimization.py        : Blahut-Arimoto, deterministic annealing
- transform_predict.py   : Data transformation and prediction  
- evaluation.py          : Information curves and visualization
- utilities.py           : Mathematical utilities and helpers

Based on: Tishby, Pereira & Bialek (1999) "The Information Bottleneck Method"
"""

# Import the new modular InformationBottleneck implementation
from .core_algorithm import InformationBottleneck

# Import individual mixin classes for advanced usage
from .core_theory import CoreTheoryMixin
from .mutual_information import MutualInformationMixin
from .optimization import OptimizationMixin
from .transform_predict import TransformPredictMixin
from .evaluation import EvaluationMixin

# Import utilities for direct use
from .utilities import (
    compute_digamma_approximation,
    compute_digamma_asymptotic,
    set_digamma_method,
    benchmark_digamma_methods,
    safe_log,
    project_to_simplex,
    entropy_discrete,
    kl_divergence_discrete
)

# Import neural implementation if available
try:
    from .neural_information_bottleneck import NeuralInformationBottleneck
    _has_neural = True
except ImportError:
    _has_neural = False

# Re-export main classes for backward compatibility
__all__ = [
    # Main class
    'InformationBottleneck',
    
    # Mixin classes for advanced usage
    'CoreTheoryMixin',
    'MutualInformationMixin', 
    'OptimizationMixin',
    'TransformPredictMixin',
    'EvaluationMixin',
    
    # Utility functions
    'compute_digamma_approximation',
    'compute_digamma_asymptotic', 
    'set_digamma_method',
    'benchmark_digamma_methods',
    'safe_log',
    'project_to_simplex',
    'entropy_discrete',
    'kl_divergence_discrete'
]

# Add neural implementation if available
if _has_neural:
    __all__.append('NeuralInformationBottleneck')

# Module metadata
__version__ = "2.1.0"  # Incremented for modular architecture
__authors__ = ["Benedict Chen", "Based on Tishby, Pereira & Bialek (1999)"]

def get_module_info():
    """
    Get information about the Information Bottleneck module architecture.
    
    Returns
    -------
    dict
        Dictionary containing module information and architecture details.
    """
    return {
        'version': __version__,
        'architecture': 'modular',
        'modules': [
            'core_algorithm',
            'core_theory',
            'mutual_information',
            'optimization', 
            'transform_predict',
            'evaluation',
            'utilities'
        ],
        'research_basis': 'Tishby, Pereira & Bialek (1999)',
        'total_lines_modularized': 2478,
        'backward_compatible': True,
        'has_neural_implementation': _has_neural
    }