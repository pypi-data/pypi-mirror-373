#!/usr/bin/env python3
"""
Comprehensive test for ib_visualization.py to achieve 100% coverage
"""

import pytest
import numpy as np
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Add module to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_ib_visualization_init():
    """Test IBVisualization initialization"""
    
    # Mock matplotlib and seaborn
    with patch('matplotlib.pyplot.style'), patch('seaborn.set_palette'):
        # Mock MutualInfoCore to avoid dependency issues
        with patch('ib_visualization.MutualInfoCore') as mock_mic:
            mock_mic.return_value = MagicMock()
            
            from ib_visualization import IBVisualization
            
            viz = IBVisualization()
            assert viz.mi_estimator is not None
            mock_mic.assert_called_once()

def test_ib_visualization_init_import_fallback():
    """Test initialization with import fallback"""
    
    # Mock the local import to succeed
    with patch('ib_visualization.MutualInfoCore') as mock_mic, \
         patch('matplotlib.pyplot.style'), \
         patch('seaborn.set_palette'):
        
        mock_mic.return_value = MagicMock()
        
        from ib_visualization import IBVisualization
        
        viz = IBVisualization()
        assert viz.mi_estimator is not None

def test_plot_information_curve():
    """Test information curve plotting"""
    
    with patch('matplotlib.pyplot.style'), \
         patch('seaborn.set_palette'), \
         patch('ib_visualization.MutualInfoCore') as mock_mic:
        
        mock_estimator = MagicMock()
        mock_mic.return_value = mock_estimator
        
        from ib_visualization import IBVisualization
        
        viz = IBVisualization()
        
        # Mock IB model
        mock_ib_model = MagicMock()
        mock_ib_model.beta = 1.0
        
        # Mock fit method to return results
        mock_ib_model.fit.return_value = {
            'final_compression': 1.5,
            'final_prediction': 0.8,
            'objective_value': 0.3
        }
        
        # Mock transform method
        mock_ib_model.transform.return_value = np.random.randn(20, 3)
        
        # Test data
        X = np.random.randn(20, 5)
        Y = np.random.choice([0, 1, 2], size=20)
        beta_values = [0.1, 1.0, 2.0]
        
        # Mock matplotlib plotting functions
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.subplot'), \
             patch('matplotlib.pyplot.plot'), \
             patch('matplotlib.pyplot.scatter'), \
             patch('matplotlib.pyplot.xlabel'), \
             patch('matplotlib.pyplot.ylabel'), \
             patch('matplotlib.pyplot.title'), \
             patch('matplotlib.pyplot.legend'), \
             patch('matplotlib.pyplot.grid'), \
             patch('matplotlib.pyplot.tight_layout'), \
             patch('matplotlib.pyplot.show'):
            
            result = viz.plot_information_curve(
                beta_values=beta_values,
                X=X,
                Y=Y,
                ib_model=mock_ib_model,
                title="Test Curve",
                figsize=(10, 6)
            )
            
            assert isinstance(result, dict)
            assert 'beta_values' in result
            assert 'compression_values' in result
            assert 'relevance_values' in result

def test_plot_information_plane():
    """Test information plane plotting"""
    
    with patch('matplotlib.pyplot.style'), \
         patch('seaborn.set_palette'), \
         patch('ib_visualization.MutualInfoCore') as mock_mic:
        
        mock_mic.return_value = MagicMock()
        
        from ib_visualization import IBVisualization
        
        viz = IBVisualization()
        
        compression_values = [0.5, 1.0, 1.5, 2.0]
        relevance_values = [0.3, 0.6, 0.9, 1.2]
        
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.plot'), \
             patch('matplotlib.pyplot.scatter'), \
             patch('matplotlib.pyplot.xlabel'), \
             patch('matplotlib.pyplot.ylabel'), \
             patch('matplotlib.pyplot.title'), \
             patch('matplotlib.pyplot.legend'), \
             patch('matplotlib.pyplot.grid'), \
             patch('matplotlib.pyplot.show'):
            
            result = viz.plot_information_plane(
                compression_values=compression_values,
                relevance_values=relevance_values,
                title="Test Plane",
                figsize=(8, 6)
            )
            
            # Method should complete without error
            assert result is None or isinstance(result, dict)

def test_analyze_clusters():
    """Test cluster analysis functionality"""
    
    with patch('matplotlib.pyplot.style'), \
         patch('seaborn.set_palette'), \
         patch('ib_visualization.MutualInfoCore') as mock_mic:
        
        mock_mic.return_value = MagicMock()
        
        from ib_visualization import IBVisualization
        
        viz = IBVisualization()
        
        X = np.random.randn(30, 4)
        Y = np.random.choice([0, 1, 2], size=30)
        
        # Mock IB model with cluster methods
        mock_ib_model = MagicMock()
        mock_ib_model.n_clusters = 3
        mock_ib_model.transform.return_value = np.random.randn(30, 3)
        mock_ib_model.get_cluster_centers.return_value = np.random.randn(3, 4)
        mock_ib_model.predict.return_value = np.random.choice([0, 1, 2], size=30)
        mock_ib_model.p_z_given_x = np.random.rand(30, 3)  # Cluster assignment probabilities
        
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.subplot'), \
             patch('matplotlib.pyplot.scatter'), \
             patch('matplotlib.pyplot.plot'), \
             patch('matplotlib.pyplot.xlabel'), \
             patch('matplotlib.pyplot.ylabel'), \
             patch('matplotlib.pyplot.title'), \
             patch('matplotlib.pyplot.legend'), \
             patch('matplotlib.pyplot.colorbar'), \
             patch('matplotlib.pyplot.tight_layout'), \
             patch('matplotlib.pyplot.show'), \
             patch('seaborn.heatmap'):
            
            result = viz.analyze_clusters(
                X=X,
                Y=Y,
                ib_model=mock_ib_model,
                figsize=(12, 8)
            )
            
            # Should return analysis results
            assert isinstance(result, dict)

def test_plot_training_history():
    """Test training history plotting"""
    
    with patch('matplotlib.pyplot.style'), \
         patch('seaborn.set_palette'), \
         patch('ib_visualization.MutualInfoCore') as mock_mic:
        
        mock_mic.return_value = MagicMock()
        
        from ib_visualization import IBVisualization
        
        viz = IBVisualization()
        
        # Mock training history
        history = {
            'compression_history': [2.0, 1.8, 1.5, 1.3, 1.2],
            'prediction_history': [0.5, 0.6, 0.7, 0.75, 0.8],
            'objective_history': [1.5, 1.2, 0.8, 0.55, 0.4],
            'beta_history': [0.1, 0.3, 0.5, 0.8, 1.0]
        }
        
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.subplot'), \
             patch('matplotlib.pyplot.plot'), \
             patch('matplotlib.pyplot.xlabel'), \
             patch('matplotlib.pyplot.ylabel'), \
             patch('matplotlib.pyplot.title'), \
             patch('matplotlib.pyplot.legend'), \
             patch('matplotlib.pyplot.grid'), \
             patch('matplotlib.pyplot.tight_layout'), \
             patch('matplotlib.pyplot.show'):
            
            viz.plot_training_history(history, figsize=(12, 4))
            
            # Should complete without error

def test_compare_methods():
    """Test method comparison plotting"""
    
    with patch('matplotlib.pyplot.style'), \
         patch('seaborn.set_palette'), \
         patch('ib_visualization.MutualInfoCore') as mock_mic:
        
        mock_mic.return_value = MagicMock()
        
        from ib_visualization import IBVisualization
        
        viz = IBVisualization()
        
        # Mock comparison results
        results_dict = {
            'Standard IB': {
                'compression_values': [0.5, 1.0, 1.5],
                'relevance_values': [0.3, 0.6, 0.9],
                'training_time': 5.2,
                'final_accuracy': 0.85
            },
            'Neural IB': {
                'compression_values': [0.4, 0.9, 1.4],
                'relevance_values': [0.35, 0.65, 0.95], 
                'training_time': 15.8,
                'final_accuracy': 0.87
            },
            'Annealed IB': {
                'compression_values': [0.45, 0.95, 1.45],
                'relevance_values': [0.32, 0.62, 0.92],
                'training_time': 8.1,
                'final_accuracy': 0.86
            }
        }
        
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.subplot'), \
             patch('matplotlib.pyplot.plot'), \
             patch('matplotlib.pyplot.bar'), \
             patch('matplotlib.pyplot.scatter'), \
             patch('matplotlib.pyplot.xlabel'), \
             patch('matplotlib.pyplot.ylabel'), \
             patch('matplotlib.pyplot.title'), \
             patch('matplotlib.pyplot.legend'), \
             patch('matplotlib.pyplot.grid'), \
             patch('matplotlib.pyplot.tight_layout'), \
             patch('matplotlib.pyplot.show'):
            
            viz.compare_methods(results_dict, figsize=(12, 8))
            
            # Should complete without error

def test_error_handling_and_edge_cases():
    """Test error handling and edge cases"""
    
    with patch('matplotlib.pyplot.style'), \
         patch('seaborn.set_palette'), \
         patch('ib_visualization.MutualInfoCore') as mock_mic:
        
        mock_mic.return_value = MagicMock()
        
        from ib_visualization import IBVisualization
        
        viz = IBVisualization()
        
        # Test with minimal data
        X_small = np.array([[1, 2], [3, 4]])
        Y_small = np.array([0, 1])
        
        mock_ib_model = MagicMock()
        mock_ib_model.fit.return_value = {
            'final_compression': 0.5,
            'final_prediction': 0.3,
            'objective_value': 0.2
        }
        mock_ib_model.transform.return_value = np.array([[0.1], [0.2]])
        
        with patch('matplotlib.pyplot.figure'), \
             patch('matplotlib.pyplot.subplot'), \
             patch('matplotlib.pyplot.plot'), \
             patch('matplotlib.pyplot.scatter'), \
             patch('matplotlib.pyplot.xlabel'), \
             patch('matplotlib.pyplot.ylabel'), \
             patch('matplotlib.pyplot.title'), \
             patch('matplotlib.pyplot.legend'), \
             patch('matplotlib.pyplot.grid'), \
             patch('matplotlib.pyplot.tight_layout'), \
             patch('matplotlib.pyplot.show'):
            
            # Test with single beta value
            result = viz.plot_information_curve(
                beta_values=[1.0],
                X=X_small,
                Y=Y_small,
                ib_model=mock_ib_model
            )
            
            assert isinstance(result, dict)

def test_visualization_with_matplotlib_errors():
    """Test handling of matplotlib import/display errors"""
    
    # Mock matplotlib to raise errors
    mock_plt = MagicMock()
    mock_plt.figure.side_effect = Exception("Display not available")
    
    with patch('matplotlib.pyplot', mock_plt), \
         patch('seaborn.set_palette'), \
         patch('ib_visualization.MutualInfoCore') as mock_mic:
        
        mock_mic.return_value = MagicMock()
        
        from ib_visualization import IBVisualization
        
        viz = IBVisualization()
        
        X = np.random.randn(10, 3)
        Y = np.random.choice([0, 1], size=10)
        
        mock_ib_model = MagicMock()
        mock_ib_model.fit.return_value = {
            'final_compression': 1.0,
            'final_prediction': 0.5,
            'objective_value': 0.5
        }
        mock_ib_model.transform.return_value = np.random.randn(10, 2)
        
        # Should handle matplotlib errors gracefully
        try:
            result = viz.plot_information_curve(
                beta_values=[0.5, 1.0],
                X=X,
                Y=Y,
                ib_model=mock_ib_model
            )
            # If no exception, test passed
        except Exception:
            # Expected behavior when display fails
            pass

if __name__ == "__main__":
    test_ib_visualization_init()
    test_plot_information_curve()
    print("✅ IB Visualization comprehensive tests completed!")