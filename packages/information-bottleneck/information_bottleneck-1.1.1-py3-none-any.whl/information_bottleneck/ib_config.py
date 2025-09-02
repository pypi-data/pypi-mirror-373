"""
Configuration classes for Information Bottleneck Method
Based on: Tishby, Pereira & Bialek (1999) "The Information Bottleneck Method"
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Union


class IBMethod(Enum):
    """Available Information Bottleneck methods"""
    DISCRETE = "discrete"  # Classical discrete IB algorithm
    NEURAL = "neural"  # Neural network-based IB
    CONTINUOUS = "continuous"  # Continuous variable approach


class MutualInfoEstimator(Enum):
    """Mutual information estimation methods"""
    KSG = "ksg"  # Kozachenko-Leonenko-Grassberger
    BINNING = "binning"  # Histogram-based
    KERNEL = "kernel"  # Kernel-based estimation  
    ENSEMBLE = "ensemble"  # Ensemble of estimators
    ADAPTIVE = "adaptive"  # Adaptive method selection
    COPULA = "copula"  # Copula-based estimation


class InitializationMethod(Enum):
    """Initialization strategies for IB algorithm"""
    RANDOM = "random"
    KMEANS_PLUS_PLUS = "kmeans++"
    MUTUAL_INFO = "mutual_info"
    HIERARCHICAL = "hierarchical"


class EncoderUpdateMethod(Enum):
    """Methods for updating encoder distribution"""
    BLAHUT_ARIMOTO = "blahut_arimoto"
    NATURAL_GRADIENT = "natural_gradient"
    TEMPERATURE_SCALED = "temperature_scaled"
    DETERMINISTIC_ANNEALING = "deterministic_annealing"


class DecoderUpdateMethod(Enum):
    """Methods for updating decoder distribution"""
    BAYES_RULE = "bayes_rule"
    EM = "em"
    REGULARIZED = "regularized"


@dataclass
class IBConfig:
    """
    Configuration for Information Bottleneck algorithm
    
    Controls all aspects of the IB optimization process
    """
    # Core parameters
    n_clusters: int = 10
    
    def __post_init__(self):
        """Validate configuration parameters"""
        if self.n_clusters <= 0:
            raise ValueError(f"n_clusters must be positive, got {self.n_clusters}")
        if self.beta < 0:
            raise ValueError(f"beta must be non-negative, got {self.beta}")
        if self.max_iterations <= 0:
            raise ValueError(f"max_iterations must be positive, got {self.max_iterations}")
    beta: float = 1.0
    max_iterations: int = 100
    tolerance: float = 1e-6
    
    # Method selection
    method: IBMethod = IBMethod.DISCRETE
    mi_estimator: MutualInfoEstimator = MutualInfoEstimator.KSG
    
    # Initialization
    initialization: InitializationMethod = InitializationMethod.KMEANS_PLUS_PLUS
    n_init: int = 10
    random_state: Optional[int] = None
    
    # Algorithm parameters
    encoder_update_method: EncoderUpdateMethod = EncoderUpdateMethod.BLAHUT_ARIMOTO
    decoder_update_method: DecoderUpdateMethod = DecoderUpdateMethod.BAYES_RULE
    
    # Annealing schedule
    use_annealing: bool = True
    beta_start: float = 0.001
    beta_end: float = 10.0
    annealing_steps: int = 20
    annealing_method: str = "exponential"  # "linear", "exponential", "power"
    
    # Convergence criteria
    check_convergence_every: int = 10
    patience: int = 10
    min_improvement: float = 1e-6
    
    # Mutual information estimation
    mi_k_neighbors: int = 3
    mi_bins: Union[int, str] = "auto"
    mi_kernel: str = "rbf"
    mi_ensemble_weights: Optional[List[float]] = None
    
    # Regularization
    encoder_regularization: float = 0.0
    decoder_regularization: float = 0.1
    
    # Advanced options
    verbose: bool = True
    debug: bool = False
    save_history: bool = True


@dataclass
class NeuralIBConfig:
    """
    Configuration for Neural Information Bottleneck
    
    Neural network-based IB implementation
    """
    # Network architecture
    encoder_dims: List[int] = None  # Will default to [784, 512, 256]
    decoder_dims: List[int] = None  # Will default to [latent_dim, 256, 10]
    latent_dim: int = 20
    
    # Training parameters
    beta: float = 1.0
    learning_rate: float = 0.001
    batch_size: int = 128
    epochs: int = 100
    
    # Network configuration
    activation: str = "relu"
    dropout_rate: float = 0.1
    use_batch_norm: bool = True
    
    # Optimizer settings
    optimizer: str = "adam"  # "adam", "sgd", "rmsprop"
    weight_decay: float = 1e-4
    lr_scheduler: Optional[str] = "step"  # None, "step", "cosine", "exponential"
    
    # Variational parameters
    use_variational: bool = True
    kl_weight: float = 1.0
    reconstruction_loss: str = "mse"  # "mse", "cross_entropy"
    
    # Device and precision
    device: str = "auto"  # "auto", "cpu", "cuda"
    mixed_precision: bool = False
    
    # Monitoring
    log_interval: int = 10
    save_checkpoints: bool = False
    checkpoint_dir: Optional[str] = None
    
    def __post_init__(self):
        """Set default architectures if not provided"""
        if self.encoder_dims is None:
            self.encoder_dims = [784, 512, 256]
        if self.decoder_dims is None:
            self.decoder_dims = [self.latent_dim, 256, 10]