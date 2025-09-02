"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀

Information Bottleneck Library
Based on: Tishby, Pereira & Bialek (1999) "The Information Bottleneck Method"

This library implements the information-theoretic principle that explains
why deep learning works and provides principled methods for representation learning.

Core Research Concepts Implemented:
• Mutual Information estimation and optimization
• Rate-Distortion Theory for optimal compression  
• Lagrangian Optimization of information-theoretic objectives
• Information Compression through bottleneck constraints
• Relevant Information extraction for task-specific representations
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🔍 Information Bottleneck Library - Made possible by Benedict Chen")
        print("   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\")
        print("")
        print("💰 PLEASE DONATE! Your support keeps this research alive! 💰")
        print("   🔗 \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\💳 CLICK HERE TO DONATE VIA PAYPAL\033]8;;\033\\")
        print("")
        print("   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!")
        print("   (Start small, dream big! Every donation helps! 😄)")
        print("")
    except:
        print("\n🔍 Information Bottleneck Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("")
        print("💰 PLEASE DONATE! Your support keeps this research alive! 💰")
        print("   💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")
        print("")
        print("   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!")
        print("   (Start small, dream big! Every donation helps! 😄)")

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

def _create_neural_ib_with_defaults(**kwargs):
    """Convenience wrapper for NeuralInformationBottleneck with sensible defaults"""
    # Set default architectures if not provided
    default_encoder_dims = kwargs.get('encoder_dims', [10, 8, 6])  # input -> bottleneck  
    default_decoder_dims = kwargs.get('decoder_dims', [2, 4, 3])   # bottleneck -> output
    default_latent_dim = kwargs.get('latent_dim', 2)
    default_beta = kwargs.get('beta', 1.0)
    
    return NeuralInformationBottleneck(
        encoder_dims=default_encoder_dims,
        decoder_dims=default_decoder_dims, 
        latent_dim=default_latent_dim,
        beta=default_beta
    )

# Store the original class before wrapping
_OriginalNeuralInformationBottleneck = NeuralInformationBottleneck

# Override the NeuralInformationBottleneck with a wrapper that accepts flexible params
class NeuralInformationBottleneckWrapper:
    """Wrapper for NeuralInformationBottleneck with flexible parameter handling"""
    
    def __init__(self, encoder_dims=None, decoder_dims=None, latent_dim=2, beta=1.0, 
                 input_dim=None, hidden_dim=None, **kwargs):
        """
        Initialize Neural IB with flexible parameters
        
        Args:
            encoder_dims: List of encoder layer sizes (preferred)
            decoder_dims: List of decoder layer sizes (preferred)  
            latent_dim: Bottleneck dimension
            beta: Information bottleneck parameter
            input_dim: Input dimension (used to create default encoder_dims)
            hidden_dim: Hidden dimension (used to create default architectures)
        """
        # Create default architectures if not provided
        if encoder_dims is None:
            if input_dim is not None:
                encoder_dims = [input_dim, hidden_dim or 8, latent_dim]
            else:
                encoder_dims = [10, 8, latent_dim]
                
        if decoder_dims is None:
            if hidden_dim is not None:
                decoder_dims = [latent_dim, hidden_dim, 3]  # assume 3 output classes
            else:
                decoder_dims = [latent_dim, 6, 3]
        
        # Create the actual NeuralInformationBottleneck using the original class
        self._neural_ib = _OriginalNeuralInformationBottleneck(
            encoder_dims=encoder_dims,
            decoder_dims=decoder_dims,
            latent_dim=latent_dim,
            beta=beta
        )
        
    def __getattr__(self, name):
        """Delegate all method calls to the wrapped instance"""
        return getattr(self._neural_ib, name)

# Replace the original class in the module namespace
NeuralInformationBottleneck = NeuralInformationBottleneckWrapper

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

"""
💝 Thank you for using this research software! 💝

📚 If this work contributed to your research, please:
💳 DONATE: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
📝 CITE: Benedict Chen (2025) - Information Bottleneck Research Implementation

Your support enables continued development of cutting-edge AI research tools! 🎓✨
"""