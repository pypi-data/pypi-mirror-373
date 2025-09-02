#!/usr/bin/env python3
"""
Comprehensive test for mutual_info_core.py to achieve 100% coverage
"""

import pytest
import numpy as np
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_mutual_info_core_init():
    """Test MutualInfoCore initialization"""
    
    from mutual_info_core import MutualInfoCore
    
    # Test default initialization
    mic = MutualInfoCore()
    assert mic.method == 'ksg'
    
    # Test initialization with different methods
    mic_binning = MutualInfoCore(method='binning')
    assert mic_binning.method == 'binning'
    
    mic_kernel = MutualInfoCore(method='kernel', kernel='rbf')
    assert mic_kernel.method == 'kernel'

def test_estimate_mutual_info_discrete():
    """Test discrete mutual information estimation"""
    
    from mutual_info_core import MutualInfoCore
    
    mic = MutualInfoCore()
    
    # Test with known joint distribution
    # X=0,Y=0: 0.25, X=0,Y=1: 0.15
    # X=1,Y=0: 0.35, X=1,Y=1: 0.25
    joint_dist = np.array([[0.25, 0.15], [0.35, 0.25]])
    
    mi = mic.estimate_mutual_info_discrete(joint_dist)
    assert isinstance(mi, float)
    assert mi >= 0  # MI is always non-negative
    
    # Test with independent variables (should give low MI)
    p_x = np.array([0.6, 0.4])
    p_y = np.array([0.7, 0.3])
    independent_joint = np.outer(p_x, p_y)
    
    mi_independent = mic.estimate_mutual_info_discrete(independent_joint)
    assert mi_independent >= 0
    assert mi_independent < 0.1  # Should be close to 0 for independent variables

def test_estimate_mutual_info_continuous():
    """Test continuous mutual information estimation"""
    
    from mutual_info_core import MutualInfoCore
    
    mic = MutualInfoCore()
    
    # Test with correlated data
    np.random.seed(42)
    x = np.random.randn(100)
    y = x + 0.1 * np.random.randn(100)  # Strongly correlated
    X = x.reshape(-1, 1)
    Y = y.reshape(-1, 1)
    
    mi_corr = mic.estimate_mutual_info_continuous(X, Y, method='ksg', k=3)
    assert isinstance(mi_corr, float)
    assert mi_corr > 0
    
    # Test with independent data
    x_indep = np.random.randn(100)
    y_indep = np.random.randn(100)
    X_indep = x_indep.reshape(-1, 1)
    Y_indep = y_indep.reshape(-1, 1)
    
    mi_indep = mic.estimate_mutual_info_continuous(X_indep, Y_indep, method='ksg', k=3)
    assert isinstance(mi_indep, float)
    assert mi_corr > mi_indep  # Correlated should have higher MI

def test_ksg_estimator():
    """Test KSG (Kraskov-Grassberger-Stögbauer) estimator"""
    
    from mutual_info_core import MutualInfoCore
    
    mic = MutualInfoCore()
    
    # Generate test data with known dependence
    np.random.seed(42)
    n_samples = 80
    x = np.random.uniform(0, 1, n_samples)
    y = x + 0.2 * np.random.randn(n_samples)  # Noisy dependence
    
    X = x.reshape(-1, 1)
    Y = y.reshape(-1, 1)
    
    # Test with different k values
    for k in [1, 3, 5]:
        mi = mic._ksg_estimator(X, Y, k=k)
        assert isinstance(mi, float)
        assert mi > 0  # Should detect dependence
        
    # Test edge case: identical variables
    mi_identical = mic._ksg_estimator(X, X, k=3)
    assert mi_identical > mi  # Identical should have higher MI

def test_binning_mi_estimator():
    """Test binning-based mutual information estimator"""
    
    from mutual_info_core import MutualInfoCore
    
    mic = MutualInfoCore()
    
    np.random.seed(42)
    X = np.random.randn(100, 1)
    Y = X + 0.5 * np.random.randn(100, 1)
    
    # Test different binning strategies
    bins_options = ['auto', 'fd', 'scott', 10]
    
    for bins in bins_options:
        mi = mic._binning_mi_estimator(X, Y, bins=bins)
        assert isinstance(mi, float)
        assert mi >= 0
    
    # Test uniform binning
    mi_uniform = mic._binning_mi_estimator(X, Y, bins=5, binning_strategy='uniform')
    assert isinstance(mi_uniform, float)
    assert mi_uniform >= 0

def test_kernel_mi_estimator():
    """Test kernel-based mutual information estimator"""
    
    from mutual_info_core import MutualInfoCore
    
    mic = MutualInfoCore()
    
    np.random.seed(42)
    X = np.random.randn(50, 2)
    Y = np.random.randn(50, 1)
    
    # Test different kernels
    kernels = ['rbf', 'polynomial', 'sigmoid']
    
    for kernel in kernels:
        mi = mic._kernel_mi_estimator(X, Y, kernel=kernel)
        assert isinstance(mi, float)
        # Note: Kernel MI can be negative due to approximation
    
    # Test with auto gamma
    mi_auto = mic._kernel_mi_estimator(X, Y, kernel='rbf', gamma='auto')
    assert isinstance(mi_auto, float)

def test_ensemble_mi_estimation():
    """Test ensemble mutual information estimation"""
    
    from mutual_info_core import MutualInfoCore
    
    mic = MutualInfoCore()
    
    np.random.seed(42)
    X = np.random.randn(60, 1)
    Y = X + np.random.randn(60, 1)
    
    # Test with default weights
    mi_ensemble = mic._ensemble_mi_estimation(X, Y)
    assert isinstance(mi_ensemble, float)
    assert mi_ensemble >= 0
    
    # Test with custom weights
    custom_weights = [0.4, 0.4, 0.2]
    mi_custom = mic._ensemble_mi_estimation(X, Y, weights=custom_weights)
    assert isinstance(mi_custom, float)
    assert mi_custom >= 0
    
    # Test with single method weight (should fallback to that method)
    single_weight = [1.0, 0.0, 0.0]
    mi_single = mic._ensemble_mi_estimation(X, Y, weights=single_weight)
    assert isinstance(mi_single, float)

def test_adaptive_mi_estimation():
    """Test adaptive mutual information estimation"""
    
    from mutual_info_core import MutualInfoCore
    
    mic = MutualInfoCore()
    
    # Test with small dataset (should choose binning)
    np.random.seed(42)
    X_small = np.random.randn(20, 1)
    Y_small = np.random.randn(20, 1)
    
    mi_small = mic._adaptive_mi_estimation(X_small, Y_small)
    assert isinstance(mi_small, float)
    assert mi_small >= 0
    
    # Test with medium dataset (should choose KSG)
    X_medium = np.random.randn(100, 2)
    Y_medium = np.random.randn(100, 1)
    
    mi_medium = mic._adaptive_mi_estimation(X_medium, Y_medium)
    assert isinstance(mi_medium, float)
    
    # Test with high-dimensional dataset (should choose kernel)
    X_hd = np.random.randn(80, 15)  # High dimensional
    Y_hd = np.random.randn(80, 1)
    
    mi_hd = mic._adaptive_mi_estimation(X_hd, Y_hd)
    assert isinstance(mi_hd, float)

def test_compute_digamma_approximation():
    """Test digamma function approximation"""
    
    from mutual_info_core import MutualInfoCore
    
    mic = MutualInfoCore()
    
    # Test digamma approximation computation
    k, n_x, n_y, n_samples = 3, 10, 15, 50
    
    digamma_val = mic._compute_digamma_approximation(k, n_x, n_y, n_samples)
    assert isinstance(digamma_val, float)
    
    # Test with different input values
    test_cases = [(1, 5, 8, 20), (5, 20, 25, 100), (2, 3, 4, 30)]
    
    for k, n_x, n_y, n_samples in test_cases:
        digamma_val = mic._compute_digamma_approximation(k, n_x, n_y, n_samples)
        assert isinstance(digamma_val, float)
        # Digamma values can be negative, so just check it's finite
        assert np.isfinite(digamma_val)

def test_method_selection_logic():
    """Test the logic for selecting appropriate MI estimation methods"""
    
    from mutual_info_core import MutualInfoCore
    
    # Test different initialization methods
    methods_to_test = ['ksg', 'binning', 'kernel', 'ensemble', 'adaptive']
    
    for method in methods_to_test:
        mic = MutualInfoCore(method=method)
        assert mic.method == method
        
        # Test that each method can be called
        np.random.seed(42)
        X = np.random.randn(40, 2)
        Y = np.random.randn(40, 1)
        
        if method == 'ksg':
            mi = mic._ksg_estimator(X, Y, k=3)
        elif method == 'binning':
            mi = mic._binning_mi_estimator(X, Y, bins='auto')
        elif method == 'kernel':
            mi = mic._kernel_mi_estimator(X, Y, kernel='rbf')
        elif method == 'ensemble':
            mi = mic._ensemble_mi_estimation(X, Y)
        elif method == 'adaptive':
            mi = mic._adaptive_mi_estimation(X, Y)
            
        assert isinstance(mi, float)

def test_edge_cases_and_error_handling():
    """Test edge cases and error handling"""
    
    from mutual_info_core import MutualInfoCore
    
    mic = MutualInfoCore()
    
    # Test with minimal data
    X_tiny = np.array([[1], [2]])
    Y_tiny = np.array([[3], [4]])
    
    # Should handle small datasets gracefully
    mi_tiny = mic._ksg_estimator(X_tiny, Y_tiny, k=1)
    assert isinstance(mi_tiny, float)
    
    # Test with constant data
    X_const = np.ones((10, 1))
    Y_var = np.random.randn(10, 1)
    
    try:
        mi_const = mic._ksg_estimator(X_const, Y_var, k=3)
        # Some estimators may handle constant data
        assert isinstance(mi_const, float)
    except (ValueError, ZeroDivisionError):
        # Expected for some methods with constant data
        pass
    
    # Test binning with extreme cases
    mi_binning_tiny = mic._binning_mi_estimator(X_tiny, Y_tiny, bins=2)
    assert isinstance(mi_binning_tiny, float)

def test_scipy_integration():
    """Test integration with scipy functions when available"""
    
    from mutual_info_core import MutualInfoCore
    
    mic = MutualInfoCore()
    
    # Test that methods work whether or not scipy is available
    np.random.seed(42)
    X = np.random.randn(50, 1) 
    Y = X + 0.3 * np.random.randn(50, 1)
    
    # Test KSG (uses scipy.spatial if available)
    mi_ksg = mic._ksg_estimator(X, Y, k=3)
    assert isinstance(mi_ksg, float)
    assert mi_ksg > 0  # Should detect correlation
    
    # Test discrete MI (may use scipy.stats)
    joint_dist = np.array([[0.3, 0.2], [0.3, 0.2]])
    mi_discrete = mic.estimate_mutual_info_discrete(joint_dist)
    assert isinstance(mi_discrete, float)
    assert mi_discrete >= 0

def test_performance_with_different_data_sizes():
    """Test performance and accuracy with different data sizes"""
    
    from mutual_info_core import MutualInfoCore
    
    mic = MutualInfoCore()
    
    # Generate data with known relationship
    np.random.seed(42)
    
    data_sizes = [30, 100, 300]
    methods = ['ksg', 'binning', 'ensemble']
    
    for n_samples in data_sizes:
        x = np.random.randn(n_samples)
        y = 0.8 * x + 0.6 * np.random.randn(n_samples)  # Strong correlation
        
        X = x.reshape(-1, 1)
        Y = y.reshape(-1, 1)
        
        for method in methods:
            if method == 'ksg':
                mi = mic._ksg_estimator(X, Y, k=3)
            elif method == 'binning': 
                mi = mic._binning_mi_estimator(X, Y, bins='auto')
            elif method == 'ensemble':
                mi = mic._ensemble_mi_estimation(X, Y)
            
            assert isinstance(mi, float)
            assert mi > 0  # Should detect strong correlation
            
            # Larger datasets should generally give more stable estimates
            # (though this is not a strict requirement for the test)

if __name__ == "__main__":
    test_mutual_info_core_init()
    test_estimate_mutual_info_discrete()
    test_ksg_estimator()
    print("✅ Mutual Info Core comprehensive tests completed!")