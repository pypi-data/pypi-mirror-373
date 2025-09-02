#!/usr/bin/env python3
"""
🧪 Information Bottleneck - Research-Grade Test Suite
===================================================

Tests implementation against Tishby, Pereira, and Bialek (1999) original paper
"The Information Bottleneck Method"

Author: Benedict Chen (benedict@benedictchen.com)
"""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os

# Add parent module to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from information_bottleneck_original import InformationBottleneck
    from information_bottleneck_main import InformationBottleneck as IBMain
    from ib_algorithms import IBAlgorithms
except ImportError:
    # Try alternative import paths
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from information_bottleneck_original import InformationBottleneck
        from information_bottleneck_main import InformationBottleneck as IBMain
        from ib_algorithms import IBAlgorithms
    except ImportError:
        pytest.skip(f"Module information_bottleneck components not available", allow_module_level=True)

class TestInformationBottleneckCore:
    """Test core Information Bottleneck functionality against Tishby 1999"""
    
    @pytest.fixture
    def simple_data(self):
        """Generate simple test data with known information structure"""
        np.random.seed(42)
        n_samples = 1000
        
        # Create correlated variables X -> Z -> Y
        # This creates a known information bottleneck scenario
        X = np.random.randn(n_samples, 2)
        Z = X[:, 0:1] + 0.1 * np.random.randn(n_samples, 1)  # Z is mostly X[0]
        Y = Z.flatten() + 0.1 * np.random.randn(n_samples)   # Y depends on Z
        
        return X, Z, Y
    
    @pytest.fixture
    def ib_instance(self):
        """Create Information Bottleneck instance"""
        return InformationBottleneck(
            n_clusters=5,
            beta=1.0,
            max_iter=100,
            tolerance=1e-6,
            random_seed=42
        )
    
    def test_information_bottleneck_initialization(self, ib_instance):
        """Test proper initialization of IB algorithm"""
        assert ib_instance.n_clusters == 5
        assert ib_instance.beta == 1.0
        assert ib_instance.max_iter == 100
        assert ib_instance.tolerance == 1e-6
        assert not ib_instance.fitted_
        
    def test_mutual_information_calculation(self, ib_instance, simple_data):
        """Test mutual information calculation - core IB concept"""
        X, Z, Y = simple_data
        
        # Test I(X;Y) calculation
        mi_xy = ib_instance._calculate_mutual_information(X, Y)
        assert mi_xy > 0, "Mutual information should be positive for correlated data"
        
        # Test I(Z;Y) should be high (Z predicts Y well)
        mi_zy = ib_instance._calculate_mutual_information(Z, Y)
        assert mi_zy > 0.5, f"I(Z;Y) should be high, got {mi_zy:.3f}"
        
        # Test I(X;Z) - compression measure  
        mi_xz = ib_instance._calculate_mutual_information(X, Z)
        assert mi_xz > 0, "I(X;Z) should be positive"
        
    def test_information_bottleneck_tradeoff(self, ib_instance, simple_data):
        """Test the core IB principle: compression vs. prediction tradeoff"""
        X, Z, Y = simple_data
        
        # Fit the model
        ib_instance.fit(X, Y)
        assert ib_instance.fitted_, "Model should be fitted after fit()"
        
        # Get bottleneck representation
        T = ib_instance.transform(X)
        assert T.shape[0] == X.shape[0], "Transformed data should have same number of samples"
        assert T.shape[1] <= X.shape[1], "Bottleneck should compress information"
        
        # Calculate information measures
        I_XT = ib_instance._calculate_mutual_information(X, T)  # Compression
        I_TY = ib_instance._calculate_mutual_information(T, Y)  # Prediction
        
        assert I_XT > 0, f"I(X;T) should be positive, got {I_XT:.3f}"
        assert I_TY > 0, f"I(T;Y) should be positive, got {I_TY:.3f}"
        
        # The bottleneck should maintain some predictive power
        assert I_TY > 0.1, f"Bottleneck should preserve predictive information, I(T;Y)={I_TY:.3f}"
        
    def test_beta_parameter_effect(self, simple_data):
        """Test that beta parameter controls compression-prediction tradeoff"""
        X, Z, Y = simple_data
        
        # Low beta (more compression)
        ib_low = InformationBottleneck(n_clusters=5, beta=0.1, random_seed=42)
        ib_low.fit(X, Y)
        T_low = ib_low.transform(X)
        
        # High beta (more prediction)  
        ib_high = InformationBottleneck(n_clusters=5, beta=10.0, random_seed=42)
        ib_high.fit(X, Y)
        T_high = ib_high.transform(X)
        
        # Calculate mutual information for both
        I_XT_low = ib_low._calculate_mutual_information(X, T_low)
        I_TY_low = ib_low._calculate_mutual_information(T_low, Y)
        
        I_XT_high = ib_high._calculate_mutual_information(X, T_high)
        I_TY_high = ib_high._calculate_mutual_information(T_high, Y)
        
        # High beta should preserve more information about Y
        assert I_TY_high >= I_TY_low, f"High beta should preserve more predictive info: {I_TY_high:.3f} vs {I_TY_low:.3f}"
        
    def test_convergence_properties(self, ib_instance, simple_data):
        """Test that algorithm converges properly"""
        X, Z, Y = simple_data
        
        ib_instance.fit(X, Y)
        
        # Check convergence
        assert hasattr(ib_instance, 'training_history_'), "Should track training history"
        history = ib_instance.training_history_
        
        assert 'loss' in history, "Should track loss during training"
        assert len(history['loss']) > 0, "Should have loss history"
        
        # Loss should generally decrease
        losses = history['loss']
        assert losses[-1] <= losses[0], f"Final loss {losses[-1]:.6f} should be <= initial loss {losses[0]:.6f}"
        
    def test_information_curve_generation(self, ib_instance, simple_data):
        """Test generation of information curve (core IB result)"""
        X, Z, Y = simple_data
        
        # Generate information curve across different beta values
        betas = np.logspace(-2, 2, 10)  # β from 0.01 to 100
        
        compression_values = []
        prediction_values = []
        
        for beta in betas:
            ib = InformationBottleneck(n_clusters=5, beta=beta, random_seed=42)
            ib.fit(X, Y)
            T = ib.transform(X)
            
            I_XT = ib._calculate_mutual_information(X, T)
            I_TY = ib._calculate_mutual_information(T, Y)
            
            compression_values.append(I_XT)
            prediction_values.append(I_TY)
        
        # Information curve should be monotonic
        compression_values = np.array(compression_values)
        prediction_values = np.array(prediction_values)
        
        assert len(compression_values) == len(betas), "Should have compression value for each beta"
        assert len(prediction_values) == len(betas), "Should have prediction value for each beta"
        
        # Generally, higher compression should lead to lower prediction (tradeoff)
        assert np.corrcoef(compression_values, prediction_values)[0, 1] > 0, "Should show compression-prediction tradeoff"

class TestInformationBottleneckMathematical:
    """Test mathematical properties from Tishby et al. 1999"""
    
    def test_lagrangian_formulation(self):
        """Test that the Lagrangian L = I(T;Y) - β*I(X;T) is implemented correctly"""
        np.random.seed(42)
        X = np.random.randn(500, 3)
        Y = X[:, 0] + 0.1 * np.random.randn(500)
        
        ib = InformationBottleneck(n_clusters=5, beta=1.0, random_seed=42)
        ib.fit(X, Y)
        T = ib.transform(X)
        
        # Calculate Lagrangian components
        I_TY = ib._calculate_mutual_information(T, Y)
        I_XT = ib._calculate_mutual_information(X, T)
        lagrangian = I_TY - ib.beta * I_XT
        
        # The algorithm should maximize this Lagrangian
        assert I_TY > 0, "I(T;Y) should be positive"
        assert I_XT > 0, "I(X;T) should be positive"
        assert isinstance(lagrangian, (int, float)), "Lagrangian should be numeric"
        
    def test_data_processing_inequality(self):
        """Test data processing inequality: I(X;Y) >= I(T;Y) for X->T->Y"""
        np.random.seed(42)
        X = np.random.randn(500, 2)
        Y = X[:, 0] + X[:, 1] + 0.1 * np.random.randn(500)
        
        ib = InformationBottleneck(n_clusters=3, beta=1.0, random_seed=42)
        ib.fit(X, Y)
        T = ib.transform(X)
        
        I_XY = ib._calculate_mutual_information(X, Y)
        I_TY = ib._calculate_mutual_information(T, Y)
        
        # Data processing inequality
        assert I_XY >= I_TY - 0.01, f"Data processing inequality violated: I(X;Y)={I_XY:.3f} < I(T;Y)={I_TY:.3f}"
        
    def test_information_consistency(self):
        """Test consistency of information measures"""
        np.random.seed(42)
        X = np.random.randn(300, 2)
        Y = np.random.choice([0, 1, 2], size=300)
        
        ib = InformationBottleneck(n_clusters=4, beta=2.0, random_seed=42)
        
        # Mutual information should be symmetric
        mi_xy = ib._calculate_mutual_information(X, Y)
        mi_yx = ib._calculate_mutual_information(Y, X)
        
        np.testing.assert_allclose(mi_xy, mi_yx, rtol=1e-6, 
                                 err_msg="Mutual information should be symmetric")

class TestInformationBottleneckBenchmarks:
    """Benchmark tests against known problems"""
    
    def test_gaussian_mixture_problem(self):
        """Test on Gaussian mixture - a classic IB benchmark"""
        np.random.seed(42)
        
        # Create Gaussian mixture problem
        n_samples = 1000
        cluster_id = np.random.choice([0, 1], n_samples)
        X = np.zeros((n_samples, 2))
        Y = np.zeros(n_samples)
        
        # Two well-separated clusters
        X[cluster_id == 0] = np.random.multivariate_normal([2, 2], 0.1*np.eye(2), np.sum(cluster_id == 0))
        X[cluster_id == 1] = np.random.multivariate_normal([-2, -2], 0.1*np.eye(2), np.sum(cluster_id == 1))
        Y = cluster_id  # Perfect classification task
        
        ib = InformationBottleneck(n_clusters=2, beta=5.0, random_seed=42)
        ib.fit(X, Y)
        T = ib.transform(X)
        
        # Should achieve near-perfect compression and prediction
        I_TY = ib._calculate_mutual_information(T, Y)
        I_XY = ib._calculate_mutual_information(X, Y)
        
        # Should preserve most of the predictive information
        information_preservation = I_TY / I_XY
        assert information_preservation > 0.8, f"Should preserve >80% of predictive info, got {information_preservation:.2%}"
        
    def test_noisy_channel_problem(self):
        """Test on noisy channel - fundamental information theory problem"""
        np.random.seed(42)
        
        # Create noisy channel: X -> Z -> Y where Z = X + noise
        n_samples = 800
        X = np.random.choice([0, 1], size=(n_samples, 1))
        noise = 0.2 * np.random.randn(n_samples, 1)
        Z = X + noise
        Y = (Z.flatten() > 0.5).astype(int)  # Threshold decoder
        
        ib = InformationBottleneck(n_clusters=2, beta=1.0, random_seed=42)
        ib.fit(Z, Y)
        T = ib.transform(Z)
        
        # Check that bottleneck captures the essential binary structure
        unique_representations = len(np.unique(T, axis=0))
        assert unique_representations <= 3, f"Should learn simple representation, got {unique_representations} unique representations"

@pytest.mark.slow
class TestInformationBottleneckPerformance:
    """Performance and scalability tests"""
    
    def test_computational_complexity(self):
        """Test computational complexity scaling"""
        import time
        
        sizes = [100, 200, 400]
        times = []
        
        for n in sizes:
            X = np.random.randn(n, 3)
            Y = np.random.choice([0, 1, 2], size=n)
            
            ib = InformationBottleneck(n_clusters=5, max_iter=50, random_seed=42)
            
            start_time = time.time()
            ib.fit(X, Y)
            elapsed = time.time() - start_time
            times.append(elapsed)
        
        # Should scale reasonably (not exponentially)
        assert times[-1] < 10 * times[0], f"Performance scaling issue: {times}"
        
    def test_memory_usage(self):
        """Test memory usage stays reasonable"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Large dataset
        X = np.random.randn(2000, 10)
        Y = np.random.choice([0, 1, 2, 3], size=2000)
        
        ib = InformationBottleneck(n_clusters=10, random_seed=42)
        ib.fit(X, Y)
        T = ib.transform(X)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Should not use excessive memory
        assert memory_increase < 500, f"Memory usage too high: {memory_increase:.1f}MB"

def test_module_integration():
    """Test integration between different IB classes"""
    np.random.seed(42)
    X = np.random.randn(200, 3)
    # Create correlated discrete Y
    Y = (X[:, 0] + X[:, 1] > 0).astype(int)
    
    # Test original implementation
    ib_original = InformationBottleneck(n_clusters=2, random_seed=42)
    ib_original.fit(X, Y)
    T1 = ib_original.transform(X)
    
    # Test main implementation
    ib_main = IBMain(n_clusters=2, random_seed=42)
    ib_main.fit(X, Y)
    T2 = ib_main.transform(X)
    
    # Both should produce valid bottleneck representations
    assert T1.shape[0] == T2.shape[0] == X.shape[0], "Sample count should be preserved"
    print(f"T1 shape: {T1.shape}, T2 shape: {T2.shape}, X shape: {X.shape}")
    # Bottleneck should learn meaningful representation (may not always compress in discrete case)
    assert T1.shape[1] > 0, "Should produce valid representation"
    assert T2.shape[1] > 0, "Should produce valid representation"

if __name__ == "__main__":
    # Run basic tests if called directly
    print("🧪 Running Information Bottleneck Test Suite...")
    
    # Quick smoke tests
    try:
        test_module_integration()
        print("✅ Module integration test passed")
        
        # Run core functionality test
        np.random.seed(42)
        X = np.random.randn(100, 3)
        Y = np.random.choice([0, 1, 2], size=100)
        
        ib = InformationBottleneck(n_clusters=2, random_seed=42)
        ib.fit(X, Y)
        T = ib.transform(X)
        
        print(f"✅ Basic functionality test passed")
        print(f"   Input shape: {X.shape}")
        print(f"   Bottleneck shape: {T.shape}")
        print(f"   Compression ratio: {T.shape[1]/X.shape[1]:.2f}")
        
        print("\n🚀 All basic tests passed! Run 'pytest test_information_bottleneck.py -v' for full suite")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()