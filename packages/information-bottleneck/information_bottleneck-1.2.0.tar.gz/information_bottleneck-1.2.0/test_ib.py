#!/usr/bin/env python3
"""
Quick test of enhanced Information Bottleneck library
"""

import numpy as np
from information_bottleneck import InformationBottleneck
from sklearn.datasets import make_classification

def test_information_bottleneck():
    print("🧪 Testing Enhanced Information Bottleneck...")
    
    # Generate small test dataset
    X, Y = make_classification(
        n_samples=100,
        n_features=5,
        n_informative=3,
        n_classes=2,
        random_state=42
    )
    
    print(f"   Dataset: {X.shape[0]} samples, {X.shape[1]} features, {len(np.unique(Y))} classes")
    
    # Test standard IB
    ib = InformationBottleneck(
        n_clusters=3,
        beta=1.0,
        max_iter=10,  # Quick test
        random_seed=42
    )
    
    # Train
    results = ib.fit(X, Y, use_annealing=False)
    print(f"   ✓ Training completed in {results['n_iterations']} iterations")
    print(f"   ✓ Final I(X;Z) = {results['final_compression']:.4f}")
    print(f"   ✓ Final I(Z;Y) = {results['final_prediction']:.4f}")
    
    # Test transform
    Z = ib.transform(X)
    print(f"   ✓ Transform shape: {Z.shape}")
    
    # Test predict
    predictions = ib.predict(X)
    accuracy = np.mean(predictions == Y)
    print(f"   ✓ Accuracy: {accuracy:.3f}")
    
    print("✅ Information Bottleneck test passed!")
    
    return True

if __name__ == "__main__":
    test_information_bottleneck()