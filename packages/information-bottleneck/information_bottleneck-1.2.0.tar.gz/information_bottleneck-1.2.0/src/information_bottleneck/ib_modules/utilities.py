"""
Utility Functions for Information Bottleneck Implementation
=========================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module contains numerical utility functions extracted from the main
Information Bottleneck implementation. These functions focus on mathematical
computations, numerical stability, and performance optimization for the
Information Bottleneck method based on Tishby et al. (1999).

The utilities include:
- Digamma function approximations for continuous mutual information estimation
- Numerical stability functions for KL divergence computation
- Performance benchmarking tools for method selection

Mathematical Background:
The digamma function ψ(x) = d/dx log Γ(x) is central to continuous mutual
information estimation in the Kraskov-Grassberger-Stögbauer (KGS) method.
Multiple approximation methods are provided to balance accuracy vs. computational cost.
"""

import numpy as np
from typing import List, Optional, Dict, Any
import time
import warnings


def compute_digamma_approximation(k: int, n_x: int, n_y: int, n_samples: int) -> float:
    """
    Improved digamma approximation using second-order asymptotic expansion.
    
    This function computes the digamma difference required for the KGS mutual
    information estimator: ψ(k) - ψ(n_x + 1) - ψ(n_y + 1) + ψ(n_samples).
    
    Uses second-order approximation: ψ(x) ≈ log(x) - 1/(2x) - 1/(12x²)
    This provides better accuracy than simple log approximation while remaining
    computationally efficient.
    
    Mathematical Foundation:
    The digamma function has the asymptotic expansion:
    ψ(x) = log(x) - 1/(2x) - 1/(12x²) + 1/(120x⁴) - 1/(252x⁶) + O(x⁻⁸)
    
    For the KGS estimator, we need:
    I(X;Y) = ψ(k) - ψ(n_x + 1) - ψ(n_y + 1) + ψ(N)
    where k is the k-th nearest neighbor count.
    
    Args:
        k: Number of k-th nearest neighbors (positive integer)
        n_x: Number of neighbors in X-marginal space (positive integer)
        n_y: Number of neighbors in Y-marginal space (positive integer) 
        n_samples: Total number of samples (positive integer)
        
    Returns:
        float: Digamma difference for mutual information estimation
        
    References:
        Kraskov, A., Stögbauer, H., & Grassberger, P. (2004).
        "Estimating mutual information." Physical review E 69.6: 066138.
    """
    def digamma_approx(x: float) -> float:
        """Second-order digamma approximation with recurrence relation"""
        if x <= 0:
            return -np.inf
        elif x < 1:
            # Use recurrence relation: ψ(x+1) = ψ(x) + 1/x
            return digamma_approx(x + 1) - 1.0/x
        else:
            # Second-order approximation for x >= 1
            return np.log(x) - 1.0/(2*x) - 1.0/(12*x*x)
    
    return (digamma_approx(k) - digamma_approx(n_x + 1) - 
            digamma_approx(n_y + 1) + digamma_approx(n_samples))


def compute_digamma_asymptotic(k: int, n_x: int, n_y: int, n_samples: int) -> float:
    """
    High-precision digamma approximation using higher-order asymptotic expansion.
    
    This function provides the most accurate pure-Python digamma approximation
    by including more terms in the asymptotic series. Recommended when scipy
    is not available but high precision is required.
    
    Uses expansion: ψ(x) ≈ log(x) - 1/(2x) - 1/(12x²) + 1/(120x⁴) - 1/(252x⁶)
    
    Mathematical Background:
    The full asymptotic expansion of the digamma function is:
    ψ(x) = log(x) - 1/(2x) - Σ(n=1 to ∞) B₂ₙ/(2n·x^(2n))
    where B₂ₙ are Bernoulli numbers: B₂=1/6, B₄=-1/30, B₆=1/42, ...
    
    This implementation includes terms up to x⁻⁶, providing excellent accuracy
    for x ≥ 2 and reasonable accuracy for smaller values via recurrence.
    
    Args:
        k: Number of k-th nearest neighbors (positive integer)
        n_x: Number of neighbors in X-marginal space (positive integer)
        n_y: Number of neighbors in Y-marginal space (positive integer)
        n_samples: Total number of samples (positive integer)
        
    Returns:
        float: High-precision digamma difference for mutual information estimation
        
    References:
        Abramowitz, M., & Stegun, I. A. (1972). Handbook of Mathematical Functions.
        National Bureau of Standards Applied Mathematics Series 55.
    """
    def digamma_asymptotic(x: float) -> float:
        """Higher-order asymptotic expansion with recurrence for small values"""
        if x <= 0:
            return -np.inf
        elif x < 2:
            # Use recurrence relation for small values
            return digamma_asymptotic(x + 1) - 1.0/x
        else:
            # Asymptotic series with Bernoulli number coefficients
            x_inv = 1.0/x
            x2_inv = x_inv * x_inv
            x4_inv = x2_inv * x2_inv
            x6_inv = x4_inv * x2_inv
            
            return (np.log(x) - 0.5 * x_inv - 
                   (1.0/12.0) * x2_inv +      # B₂/(2·2) = 1/6 / 4 = 1/12
                   (1.0/120.0) * x4_inv -     # B₄/(2·4) = -1/30 / 8 = -1/240, but we want +1/120
                   (1.0/252.0) * x6_inv)      # B₆/(2·6) = 1/42 / 12 = 1/504, but we want -1/252
    
    return (digamma_asymptotic(k) - digamma_asymptotic(n_x + 1) - 
            digamma_asymptotic(n_y + 1) + digamma_asymptotic(n_samples))


def compute_exact_kl_divergence(p_y_given_z: np.ndarray, z: int, y_i: int, 
                               min_prob: float = 1e-8) -> float:
    """
    Compute exact KL divergence D_KL[p(y|x)||p(y|z)] for discrete labels.
    
    For discrete Y with delta function p(y|x_i), the KL divergence simplifies to
    -log p(y_i|z). This function includes numerical stability measures to prevent
    mathematical collapse when probabilities approach zero.
    
    Mathematical Background:
    For a discrete random variable Y and point x_i with label y_i:
    p(y|x_i) = δ(y - y_i)  (Dirac delta)
    
    The KL divergence becomes:
    D_KL[p(y|x_i)||p(y|z)] = Σ_y p(y|x_i) log[p(y|x_i)/p(y|z)]
                            = log[δ(y_i - y_i)/p(y_i|z)]
                            = -log p(y_i|z)
    
    Args:
        p_y_given_z: Probability matrix p(y|z) of shape (n_clusters, n_classes)
        z: Cluster index (0 to n_clusters-1)
        y_i: True label for sample i (0 to n_classes-1)
        min_prob: Minimum probability to prevent log(0) (default: 1e-8)
        
    Returns:
        float: KL divergence value, always non-negative
        
    References:
        Tishby, N., Pereira, F. C., & Bialek, W. (1999).
        "The information bottleneck method." arXiv preprint physics/0004057.
    """
    # Extract probability with numerical stability
    prob = max(p_y_given_z[z, y_i], min_prob)
    return -np.log(prob)


def set_digamma_method(method: str, valid_methods: Optional[List[str]] = None) -> str:
    """
    Validate and return digamma computation method for maximum user control.
    
    This function provides a centralized way to validate digamma method selection,
    ensuring compatibility with available dependencies and user preferences.
    
    Args:
        method: Requested digamma method name
        valid_methods: List of valid method names (optional)
        
    Returns:
        str: Validated method name
        
    Raises:
        ValueError: If method is not in valid_methods list
        
    Available Methods:
        - 'scipy_exact': Use scipy.special.digamma (most accurate, requires scipy)
        - 'asymptotic_expansion': High-order pure Python approximation
        - 'improved_approximation': Second-order pure Python approximation  
        - 'simple_log': Basic log(x) approximation (fastest, least accurate)
    """
    if valid_methods is None:
        valid_methods = ['scipy_exact', 'improved_approximation', 
                        'asymptotic_expansion', 'simple_log']
    
    if method not in valid_methods:
        raise ValueError(f"Invalid method '{method}'. Choose from: {valid_methods}")
    
    return method


def benchmark_digamma_methods(test_values: Optional[List[float]] = None, 
                             verbose: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    Benchmark different digamma methods for accuracy and performance.
    
    This comprehensive benchmarking function helps users choose the optimal
    digamma computation method for their specific use case, balancing accuracy
    against computational cost and dependency requirements.
    
    The benchmark evaluates:
    1. Numerical accuracy vs. scipy.special.digamma (when available)
    2. Computational performance via timing
    3. Dependency requirements and availability
    4. Recommendations based on use case
    
    Args:
        test_values: List of test points for evaluation (default: [1,2,5,10,50,100,1000])
        verbose: Whether to print detailed results table (default: True)
        
    Returns:
        dict: Comprehensive benchmark results with structure:
            {
                'results': Dict[method_name, List[float]],  # Computed values
                'errors': Dict[method_name, List[float]],   # Errors vs scipy
                'timings': Dict[method_name, float],        # Execution times
                'recommendations': List[str],               # Usage recommendations
                'scipy_available': bool                     # Scipy availability
            }
            
    Example Usage:
        >>> results = benchmark_digamma_methods([1, 10, 100])
        >>> best_method = min(results['errors']['asymptotic_expansion'])
        >>> print(f"Best pure Python method: asymptotic_expansion")
        
    References:
        Performance comparison methodology follows numerical analysis best practices
        from Numerical Recipes and Handbook of Mathematical Functions.
    """
    if test_values is None:
        test_values = [1, 2, 5, 10, 50, 100, 1000]
    
    if verbose:
        print("\n🔬 Digamma Method Benchmark")
        print("=" * 50)
    
    # Check scipy availability and get reference values
    try:
        from scipy.special import digamma as scipy_digamma
        has_scipy = True
        reference = [scipy_digamma(x) for x in test_values]
    except ImportError:
        has_scipy = False
        reference = None
        if verbose:
            print("⚠️  Scipy not available - using asymptotic_expansion as reference")
    
    # Define methods to test
    methods = ['simple_log', 'improved_approximation', 'asymptotic_expansion']
    if has_scipy:
        methods.insert(0, 'scipy_exact')
    
    # Initialize results storage
    results = {method: [] for method in methods}
    timings = {method: 0.0 for method in methods}
    errors = {method: [] for method in methods}
    
    # Benchmark each method
    for method in methods:
        start_time = time.time()
        
        for x in test_values:
            if method == 'scipy_exact' and has_scipy:
                val = scipy_digamma(x)
            elif method == 'simple_log':
                val = np.log(x) if x > 0 else -np.inf
            elif method == 'improved_approximation':
                if x <= 0:
                    val = -np.inf
                elif x < 1:
                    val = np.log(x + 1) - 1.0/x - 1.0/(2*(x+1)) - 1.0/(12*(x+1)**2)
                else:
                    val = np.log(x) - 1.0/(2*x) - 1.0/(12*x*x)
            elif method == 'asymptotic_expansion':
                if x <= 0:
                    val = -np.inf
                elif x < 2:
                    # Simplified recurrence for benchmark
                    val = np.log(x + 1) - 1.0/x - 0.5/(x+1) - 1.0/(12*(x+1)**2)
                else:
                    x_inv = 1.0/x
                    x2_inv = x_inv * x_inv
                    x4_inv = x2_inv * x2_inv 
                    x6_inv = x4_inv * x2_inv
                    val = (np.log(x) - 0.5 * x_inv - (1.0/12.0) * x2_inv + 
                          (1.0/120.0) * x4_inv - (1.0/252.0) * x6_inv)
            
            results[method].append(val)
        
        timings[method] = time.time() - start_time
    
    # Compute errors against reference
    if has_scipy and reference:
        ref_method = 'scipy_exact'
    else:
        ref_method = 'asymptotic_expansion'  # Use best pure Python as reference
        reference = results[ref_method]
    
    for method in methods:
        if method != ref_method:
            method_errors = []
            for i, val in enumerate(results[method]):
                if not np.isinf(val) and not np.isinf(reference[i]):
                    error = abs(val - reference[i])
                    method_errors.append(error)
                else:
                    method_errors.append(float('inf'))
            errors[method] = method_errors
        else:
            errors[method] = [0.0] * len(test_values)  # Reference has zero error
    
    # Display results table
    if verbose:
        print(f"{'x':<8} ", end="")
        for method in methods:
            print(f"{method:<20} ", end="")
        if len(methods) > 1:
            print("Max Error")
        print()
        
        for i, x in enumerate(test_values):
            print(f"{x:<8.0f} ", end="")
            for method in methods:
                print(f"{results[method][i]:<20.6f} ", end="")
            
            # Show maximum error for this test value
            if len(methods) > 1:
                max_error = max(errors[m][i] for m in methods if m != ref_method)
                print(f"{max_error:<12.2e} ", end="")
            print()
        
        # Performance summary
        print(f"\n⏱️  Execution Times (for {len(test_values)} evaluations):")
        for method in methods:
            print(f"   • {method:<25}: {timings[method]:.6f} seconds")
        
        # Generate recommendations
        recommendations = []
        if has_scipy:
            recommendations.append("scipy_exact: Most accurate, requires scipy dependency")
        
        # Find best pure Python method based on average error
        if len(methods) > 1:
            pure_methods = [m for m in methods if m != 'scipy_exact']
            if pure_methods:
                avg_errors = {m: np.mean(errors[m]) for m in pure_methods}
                best_pure = min(avg_errors.keys(), key=lambda k: avg_errors[k])
                recommendations.append(f"{best_pure}: Best pure Python accuracy")
        
        recommendations.extend([
            "improved_approximation: Good balance of speed and accuracy",
            "simple_log: Fastest but least accurate, use only for rough estimates"
        ])
        
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   • {rec}")
        
        if not has_scipy:
            print(f"\n📦 Install scipy for highest accuracy: pip install scipy")
    
    return {
        'results': results,
        'errors': errors, 
        'timings': timings,
        'recommendations': recommendations,
        'scipy_available': has_scipy,
        'reference_method': ref_method
    }


def safe_log(x: np.ndarray, min_val: float = 1e-12) -> np.ndarray:
    """
    Numerically stable logarithm computation.
    
    Prevents log(0) errors by clipping input values to a minimum threshold.
    Essential for Information Bottleneck computations involving probabilities.
    
    Args:
        x: Input array or scalar
        min_val: Minimum value threshold (default: 1e-12)
        
    Returns:
        np.ndarray: Safe logarithm values
    """
    x_safe = np.maximum(x, min_val)
    return np.log(x_safe)


def project_to_simplex(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Project array onto probability simplex.
    
    Ensures that each row/column sums to 1 and all entries are non-negative.
    Used to maintain probability constraints in Information Bottleneck updates.
    
    Args:
        x: Input array to project
        axis: Axis along which to normalize (default: -1, last axis)
        
    Returns:
        np.ndarray: Projected array on probability simplex
    """
    # Clip negative values
    x_pos = np.maximum(x, 0.0)
    
    # Normalize to sum to 1 along specified axis
    sums = np.sum(x_pos, axis=axis, keepdims=True)
    sums = np.maximum(sums, 1e-12)  # Prevent division by zero
    
    return x_pos / sums


def entropy_discrete(p: np.ndarray, base: float = np.e, axis: int = -1) -> np.ndarray:
    """
    Compute entropy of discrete probability distribution.
    
    H(X) = -Σ p(x) log p(x)
    
    Args:
        p: Probability distribution array
        base: Logarithm base (e for nats, 2 for bits)
        axis: Axis along which to compute entropy
        
    Returns:
        np.ndarray: Entropy values
    """
    # Ensure probabilities are positive and normalized
    p_safe = project_to_simplex(p, axis=axis)
    
    # Compute entropy with safe logarithm
    if base == np.e:
        log_p = safe_log(p_safe)
    else:
        log_p = safe_log(p_safe) / np.log(base)
    
    return -np.sum(p_safe * log_p, axis=axis)


def kl_divergence_discrete(p: np.ndarray, q: np.ndarray, 
                          axis: int = -1, epsilon: float = 1e-12) -> np.ndarray:
    """
    Compute KL divergence between discrete probability distributions.
    
    D_KL(P||Q) = Σ p(x) log[p(x)/q(x)]
    
    Args:
        p: First probability distribution
        q: Second probability distribution  
        axis: Axis along which to compute KL divergence
        epsilon: Minimum probability to prevent log(0)
        
    Returns:
        np.ndarray: KL divergence values
    """
    # Ensure inputs are valid probability distributions
    p_safe = np.maximum(p, epsilon)
    q_safe = np.maximum(q, epsilon)
    
    # Normalize to ensure they sum to 1
    p_norm = project_to_simplex(p_safe, axis=axis)
    q_norm = project_to_simplex(q_safe, axis=axis)
    
    # Compute KL divergence
    ratio = p_norm / q_norm
    log_ratio = safe_log(ratio)
    
    return np.sum(p_norm * log_ratio, axis=axis)


# Global digamma method configuration
_DIGAMMA_METHOD = 'asymptotic_expansion'  # Default method

def get_digamma_method() -> str:
    """Get current global digamma method."""
    return _DIGAMMA_METHOD


def set_global_digamma_method(method: str) -> None:
    """Set global digamma method."""
    global _DIGAMMA_METHOD
    _DIGAMMA_METHOD = set_digamma_method(method)
    print(f"Global digamma method set to: {_DIGAMMA_METHOD}")