"""
⚖️ Information Bottleneck Evaluation Metrics: Measuring Compression-Prediction Trade-offs
=======================================================================================

Comprehensive evaluation framework for Information Bottleneck methods, measuring the 
fundamental trade-off between data compression and predictive performance.

📚 **Key Research Citations:**
• Tishby, N., Pereira, F.C., & Bialek, W. (1999). "The information bottleneck method."
  Proceedings of the 37th Annual Allerton Conference on Communication, Control, and Computing.
  → Original Information Bottleneck principle with theoretical foundations
  
• Tishby, N. & Zaslavsky, N. (2015). "Deep learning and the information bottleneck principle."
  Proceedings of the IEEE Information Theory Workshop.
  → Modern applications to deep learning with evaluation methodologies
  
• Alemi, A.A., Fischer, I., Dillon, J.V., & Murphy, K. (2017). "Deep variational information bottleneck."
  International Conference on Learning Representations.
  → Practical evaluation metrics for variational information bottleneck
  
• Kolchinsky, A., Tracey, B.D., & Wolpert, D.H. (2019). "Nonlinear information bottleneck."
  Entropy, 21(12), 1181.
  → Comprehensive evaluation framework for nonlinear information bottleneck methods

📖 **Historical Context:**
Information Bottleneck evaluation emerged from information theory's quest to quantify
the fundamental trade-off between compression and prediction. Tishby's 1999 work established
that optimal representations should compress irrelevant information while preserving
task-relevant structure. Evaluation metrics evolved to capture this dual objective,
measuring both information-theoretic properties and downstream task performance.

🎯 **ELI5 Explanation:**
Think of an Information Bottleneck like a skilled news editor 📰

A newspaper receives thousands of stories daily, but can only print a few pages. The
editor's job is to compress all this information while keeping the most important parts.
Our evaluation metrics are like different ways to judge the editor's performance:

1. 📊 **Compression Score**: How much did you reduce the information?
   - Like measuring how many stories were cut from 1000 to 50

2. 🎯 **Prediction Score**: Can readers still understand what's happening?
   - Like testing if people can answer questions about current events

3. ⚖️ **Trade-off Balance**: Did you find the sweet spot?
   - Like checking if cutting too much made news incomprehensible
   
4. 📈 **Information Curve**: How does compression quality change?
   - Like plotting performance vs. space constraints

The perfect editor finds the optimal balance - maximum compression with minimal
information loss for the task at hand!

🏗️ **Evaluation Architecture:**
```
📊 Original Data X → [Information Bottleneck] → 📉 Compressed T → [Prediction] → 🎯 Target Y
     ↓                        ↓                        ↓                   ↓
🔍 Evaluation Metrics:
     
📊 Compression Metrics:
   • I(X;T) - Information preserved
   • H(T) - Representation complexity  
   • β-weighted compression loss
   
🎯 Prediction Metrics:
   • I(T;Y) - Predictive information
   • Prediction accuracy/error
   • Task-specific performance
   
⚖️ Trade-off Analysis:
   • Information Plane: I(X;T) vs I(T;Y)
   • β-curves: Performance vs compression
   • Pareto frontier analysis
   
🔬 Theoretical Bounds:
   • Data Processing Inequality limits
   • Rate-distortion boundaries
   • Optimal β selection criteria
```

📊 **Core Evaluation Metrics:**

**🗜️ Compression Measures**
Quantify how much the original data X is compressed into representation T:

• **Mutual Information I(X;T)**: Measures information preserved about input
• **Entropy H(T)**: Complexity of learned representation
• **Compression Ratio**: |T| / |X| for discrete representations
• **Rate**: Average bits needed to encode representation

**🎯 Prediction Measures**  
Evaluate how well compressed representation T predicts target Y:

• **Mutual Information I(T;Y)**: Information about target in representation
• **Prediction Accuracy**: Classification/regression performance
• **Cross-Entropy Loss**: Probabilistic prediction quality
• **Task-Specific Metrics**: F1, AUC, BLEU, etc.

**⚖️ Trade-off Analysis**
Assess the fundamental compression-prediction balance:

• **β-Curves**: Performance vs compression parameter β
• **Information Plane**: 2D plot of I(X;T) vs I(T;Y)  
• **Pareto Efficiency**: Frontier of optimal trade-offs
• **Rate-Distortion**: Theoretical compression limits

🔬 **Advanced Evaluation Methods:**

**📈 Information Dynamics**
Track how information flows during training:
- Phase transitions in information plane
- Compression vs. generalization phases  
- Learning trajectory analysis
- Convergence pattern identification

**🎲 Statistical Significance**
Ensure robust evaluation through:
- Bootstrap confidence intervals
- Multiple random seed validation
- Cross-validation for stability
- Hypothesis testing for improvements

**🧠 Representation Quality**
Analyze learned representations:
- Disentanglement measures
- Interpretability scores
- Robustness to perturbations
- Transfer learning performance

**⚡ Computational Efficiency**
Practical considerations:
- Training time vs. performance
- Memory usage scaling
- Inference speed analysis
- Hardware utilization metrics

🚀 **Real-World Applications:**

**Deep Learning Architecture Design** 🤖
- Evaluate neural network bottleneck layers
- Compare autoencoder architectures
- Optimize model compression for deployment
- Balance accuracy vs. model size

**Natural Language Processing** 📝
- Sentence embedding evaluation
- Document summarization quality
- Machine translation compression
- Text classification with compressed features

**Computer Vision** 👁️
- Image representation learning assessment
- Feature extraction quality measurement
- Object detection with compressed features
- Medical imaging analysis optimization

**Neuroscience Research** 🧠
- Neural coding efficiency analysis
- Brain-inspired architecture evaluation
- Sensory processing bottleneck modeling
- Cognitive load measurement frameworks

**Financial Analytics** 💰
- Portfolio compression strategies
- Risk factor extraction evaluation
- High-frequency trading feature selection
- Market prediction with compressed signals

💡 **Evaluation Insights:**

**🎯 Optimal β Selection**
The compression parameter β determines the trade-off balance:
- Low β: Minimal compression, high prediction accuracy
- High β: Maximum compression, potential information loss
- Optimal β: Best balance for specific task requirements

**📊 Information Plane Analysis**
The I(X;T) vs I(T;Y) plot reveals:
- Fitting phase: Both quantities increase
- Compression phase: I(X;T) decreases while I(T;Y) stabilizes
- Generalization quality from trajectory shape

**⚖️ Task-Dependent Trade-offs**
Different tasks require different evaluation emphasis:
- Classification: Focus on decision boundary preservation
- Regression: Emphasize continuous value accuracy
- Generation: Balance fidelity with diversity
- Compression: Optimize rate-distortion trade-off

**🔍 Representation Diagnostics**
Quality representations show:
- Smooth information curves without sharp drops
- Stable performance across multiple runs
- Meaningful clusters in representation space
- Good transfer to related tasks

---
💰 **Support This Research:** https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Developing comprehensive evaluation frameworks for information-theoretic methods requires
deep understanding of both theoretical foundations and practical considerations. Your
support helps advance these fundamental measurement techniques.

💡 **Support Impact:**
• ☕ $5-15: Fuel for mathematical derivation sessions
• 🍺 $20-50: Celebration of completed evaluation frameworks
• 🏎️ $100-500: Serious commitment to information theory advancement
• ✈️ $1000+: Enable conference presentations and research collaboration

Every contribution helps ensure these powerful evaluation methods remain available
for current and future information bottleneck research!

---
👨‍💻 **Author:** Benedict Chen (benedict@benedictchen.com)
🔗 **Related:** Information Theory, Representation Learning, Model Evaluation, Compression Theory
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from dataclasses import dataclass
from scipy.stats import entropy
from sklearn.metrics import mutual_info_score, accuracy_score, mean_squared_error
from sklearn.model_selection import cross_val_score
import warnings


@dataclass
class EvaluationConfig:
    """Configuration for information bottleneck evaluation"""
    n_bins: int = 20  # For mutual information estimation
    n_bootstrap: int = 100  # Bootstrap samples for confidence intervals
    confidence_level: float = 0.95  # Confidence level for intervals
    normalize_mi: bool = True  # Normalize mutual information
    random_state: Optional[int] = None


class InformationBottleneckEvaluator:
    """
    Comprehensive evaluation framework for Information Bottleneck methods
    
    Implements standard metrics for measuring compression-prediction trade-offs
    including mutual information estimates, performance curves, and statistical
    significance testing.
    """
    
    def __init__(self, config: Optional[EvaluationConfig] = None):
        """
        Initialize evaluator with configuration
        
        Args:
            config: Evaluation configuration parameters
        """
        self.config = config or EvaluationConfig()
        self.results_cache = {}
        
        if self.config.random_state is not None:
            np.random.seed(self.config.random_state)
    
    def compute_mutual_information(self, X: np.ndarray, Y: np.ndarray, 
                                 method: str = 'histogram') -> float:
        """
        Compute mutual information between two variables
        
        Args:
            X: First variable
            Y: Second variable  
            method: Estimation method ('histogram', 'ksg', 'gaussian')
            
        Returns:
            Mutual information estimate
        """
        if method == 'histogram':
            return self._mutual_info_histogram(X, Y)
        elif method == 'ksg':
            return self._mutual_info_ksg(X, Y)
        elif method == 'gaussian':
            return self._mutual_info_gaussian(X, Y)
        else:
            raise ValueError(f"Unknown MI estimation method: {method}")
    
    def _mutual_info_histogram(self, X: np.ndarray, Y: np.ndarray) -> float:
        """Histogram-based mutual information estimation"""
        # Discretize continuous variables
        if X.ndim > 1:
            X_discrete = self._discretize_multivariate(X)
        else:
            X_discrete = self._discretize_univariate(X)
            
        if Y.ndim > 1:
            Y_discrete = self._discretize_multivariate(Y)
        else:
            Y_discrete = self._discretize_univariate(Y)
        
        # Compute mutual information
        mi = mutual_info_score(X_discrete, Y_discrete)
        
        if self.config.normalize_mi:
            # Normalize by geometric mean of entropies
            h_x = entropy(np.bincount(X_discrete) + 1e-10)
            h_y = entropy(np.bincount(Y_discrete) + 1e-10)
            mi = mi / np.sqrt(h_x * h_y) if h_x * h_y > 0 else 0
            
        return mi
    
    def _discretize_univariate(self, x: np.ndarray) -> np.ndarray:
        """Discretize univariate data using equal-frequency binning"""
        quantiles = np.linspace(0, 1, self.config.n_bins + 1)
        bin_edges = np.quantile(x, quantiles)
        bin_edges[-1] += 1e-10  # Ensure all data fits
        return np.digitize(x, bin_edges) - 1
    
    def _discretize_multivariate(self, X: np.ndarray) -> np.ndarray:
        """Discretize multivariate data using independent binning per dimension"""
        X_discrete = np.zeros(X.shape[0], dtype=int)
        
        for i in range(X.shape[1]):
            x_discrete = self._discretize_univariate(X[:, i])
            X_discrete += x_discrete * (self.config.n_bins ** i)
            
        return X_discrete
    
    def _mutual_info_ksg(self, X: np.ndarray, Y: np.ndarray) -> float:
        """KSG mutual information estimator (simplified implementation)"""
        # This is a placeholder - full KSG implementation is complex
        warnings.warn("KSG estimator not fully implemented, using histogram method")
        return self._mutual_info_histogram(X, Y)
    
    def _mutual_info_gaussian(self, X: np.ndarray, Y: np.ndarray) -> float:
        """Gaussian mutual information estimator"""
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if Y.ndim == 1:
            Y = Y.reshape(-1, 1)
            
        XY = np.hstack([X, Y])
        
        # Compute covariance matrices
        cov_x = np.cov(X.T)
        cov_y = np.cov(Y.T)  
        cov_xy = np.cov(XY.T)
        
        # Handle scalar case
        if X.shape[1] == 1:
            cov_x = float(cov_x)
        if Y.shape[1] == 1:
            cov_y = float(cov_y)
            
        # Compute mutual information using determinants
        det_x = np.linalg.det(cov_x) if X.shape[1] > 1 else cov_x
        det_y = np.linalg.det(cov_y) if Y.shape[1] > 1 else cov_y
        det_xy = np.linalg.det(cov_xy)
        
        mi = 0.5 * np.log(det_x * det_y / det_xy) if det_xy > 0 else 0
        
        return max(0, mi)  # MI should be non-negative
    
    def evaluate_compression_prediction(self, X: np.ndarray, T: np.ndarray, 
                                      Y: np.ndarray, 
                                      predictor: Optional[Callable] = None) -> Dict[str, float]:
        """
        Evaluate compression-prediction trade-off
        
        Args:
            X: Original input data
            T: Compressed representation  
            Y: Target variable
            predictor: Optional predictor function T -> Y
            
        Returns:
            Dictionary of evaluation metrics
        """
        results = {}
        
        # Compression metrics
        results['I_X_T'] = self.compute_mutual_information(X, T)
        results['H_T'] = self.compute_entropy(T)
        results['compression_ratio'] = T.shape[1] / X.shape[1] if X.ndim > 1 else 1.0
        
        # Prediction metrics  
        results['I_T_Y'] = self.compute_mutual_information(T, Y)
        
        if predictor is not None:
            Y_pred = predictor(T)
            if self._is_classification_task(Y):
                results['accuracy'] = accuracy_score(Y, Y_pred)
                results['prediction_loss'] = -np.mean(Y == Y_pred)
            else:
                results['mse'] = mean_squared_error(Y, Y_pred)
                results['prediction_loss'] = np.sqrt(results['mse'])
        
        # Trade-off metrics
        results['information_efficiency'] = results['I_T_Y'] / (results['I_X_T'] + 1e-10)
        results['compression_loss'] = results['I_X_T'] - results['H_T']
        
        return results
    
    def compute_entropy(self, X: np.ndarray) -> float:
        """Compute entropy of variable"""
        if X.ndim > 1:
            # For multivariate, use discretization
            X_discrete = self._discretize_multivariate(X)
        else:
            X_discrete = self._discretize_univariate(X)
            
        counts = np.bincount(X_discrete)
        probabilities = counts / np.sum(counts)
        
        return entropy(probabilities)
    
    def _is_classification_task(self, Y: np.ndarray) -> bool:
        """Determine if task is classification based on target variable"""
        unique_vals = np.unique(Y)
        return len(unique_vals) < 20 and np.all(unique_vals == np.round(unique_vals))
    
    def compute_beta_curve(self, evaluation_results: List[Dict[str, float]], 
                          beta_values: List[float]) -> Dict[str, List[float]]:
        """
        Compute β-curve showing compression-prediction trade-off
        
        Args:
            evaluation_results: List of evaluation results for different β
            beta_values: Corresponding β parameter values
            
        Returns:
            Dictionary with β-curve data
        """
        curve_data = {
            'beta': beta_values,
            'I_X_T': [r['I_X_T'] for r in evaluation_results],
            'I_T_Y': [r['I_T_Y'] for r in evaluation_results],
            'compression_ratio': [r['compression_ratio'] for r in evaluation_results],
        }
        
        # Add prediction metrics if available
        if 'accuracy' in evaluation_results[0]:
            curve_data['accuracy'] = [r['accuracy'] for r in evaluation_results]
        if 'mse' in evaluation_results[0]:
            curve_data['mse'] = [r['mse'] for r in evaluation_results]
            
        return curve_data
    
    def bootstrap_confidence_intervals(self, X: np.ndarray, T: np.ndarray, 
                                     Y: np.ndarray, 
                                     metric_func: Callable) -> Tuple[float, float, float]:
        """
        Compute bootstrap confidence intervals for evaluation metrics
        
        Args:
            X: Original input data
            T: Compressed representation
            Y: Target variable
            metric_func: Function to compute metric
            
        Returns:
            Tuple of (mean, lower_bound, upper_bound)
        """
        n_samples = X.shape[0]
        bootstrap_values = []
        
        for _ in range(self.config.n_bootstrap):
            # Bootstrap sample
            indices = np.random.choice(n_samples, size=n_samples, replace=True)
            X_boot = X[indices]
            T_boot = T[indices]  
            Y_boot = Y[indices]
            
            # Compute metric
            metric_value = metric_func(X_boot, T_boot, Y_boot)
            bootstrap_values.append(metric_value)
        
        bootstrap_values = np.array(bootstrap_values)
        
        # Compute confidence intervals
        alpha = 1 - self.config.confidence_level
        lower_percentile = 100 * (alpha / 2)
        upper_percentile = 100 * (1 - alpha / 2)
        
        mean_val = np.mean(bootstrap_values)
        lower_bound = np.percentile(bootstrap_values, lower_percentile)
        upper_bound = np.percentile(bootstrap_values, upper_percentile)
        
        return mean_val, lower_bound, upper_bound
    
    def plot_information_plane(self, evaluation_results: List[Dict[str, float]], 
                              beta_values: List[float],
                              figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
        """
        Plot information plane: I(X;T) vs I(T;Y)
        
        Args:
            evaluation_results: List of evaluation results
            beta_values: Corresponding β values
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        I_X_T = [r['I_X_T'] for r in evaluation_results]
        I_T_Y = [r['I_T_Y'] for r in evaluation_results]
        
        # Plot trajectory
        scatter = ax.scatter(I_X_T, I_T_Y, c=beta_values, cmap='viridis', s=50)
        ax.plot(I_X_T, I_T_Y, 'k--', alpha=0.5, linewidth=1)
        
        # Add colorbar
        plt.colorbar(scatter, ax=ax, label='β value')
        
        # Labels and formatting
        ax.set_xlabel('I(X;T) - Information about Input')
        ax.set_ylabel('I(T;Y) - Information about Target')
        ax.set_title('Information Plane: Compression-Prediction Trade-off')
        ax.grid(True, alpha=0.3)
        
        # Add arrow showing β direction
        if len(I_X_T) > 1:
            ax.annotate('', xy=(I_X_T[0], I_T_Y[0]), xytext=(I_X_T[1], I_T_Y[1]),
                       arrowprops=dict(arrowstyle='->', color='red', lw=2))
            ax.text(I_X_T[0], I_T_Y[0], 'Low β', fontsize=10, color='red')
            ax.text(I_X_T[-1], I_T_Y[-1], 'High β', fontsize=10, color='red')
        
        plt.tight_layout()
        return fig
    
    def plot_beta_curves(self, curve_data: Dict[str, List[float]], 
                        figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
        """
        Plot β-curves showing various metrics vs β parameter
        
        Args:
            curve_data: β-curve data from compute_beta_curve
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        metrics = [k for k in curve_data.keys() if k != 'beta']
        n_metrics = len(metrics)
        
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        beta_values = curve_data['beta']
        
        for i, metric in enumerate(metrics[:4]):  # Plot up to 4 metrics
            if i >= 4:
                break
                
            ax = axes[i]
            values = curve_data[metric]
            
            ax.plot(beta_values, values, 'o-', linewidth=2, markersize=6)
            ax.set_xlabel('β parameter')
            ax.set_ylabel(metric.replace('_', ' ').title())
            ax.set_title(f'{metric.replace("_", " ").title()} vs β')
            ax.grid(True, alpha=0.3)
            
            # Log scale for β if values span multiple orders of magnitude
            if max(beta_values) / min(beta_values) > 100:
                ax.set_xscale('log')
        
        # Hide unused subplots
        for i in range(n_metrics, 4):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def compute_rate_distortion_bound(self, X: np.ndarray, Y: np.ndarray, 
                                    rates: List[float]) -> List[float]:
        """
        Compute theoretical rate-distortion bound
        
        Args:
            X: Input data
            Y: Target data  
            rates: List of compression rates
            
        Returns:
            List of minimal distortions for each rate
        """
        # This is a simplified implementation
        # Full rate-distortion theory requires more sophisticated analysis
        
        max_mi = self.compute_mutual_information(X, Y)
        distortions = []
        
        for rate in rates:
            # Simple approximation: exponential decay from max MI
            distortion = max_mi * np.exp(-rate)
            distortions.append(distortion)
        
        return distortions
    
    def generate_evaluation_report(self, results: Dict[str, Any]) -> str:
        """
        Generate comprehensive evaluation report
        
        Args:
            results: Dictionary of evaluation results
            
        Returns:
            Formatted evaluation report string
        """
        report = []
        report.append("=" * 60)
        report.append("INFORMATION BOTTLENECK EVALUATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Basic metrics
        if 'I_X_T' in results:
            report.append(f"Information Preserved (I(X;T)): {results['I_X_T']:.4f}")
        if 'I_T_Y' in results:
            report.append(f"Predictive Information (I(T;Y)): {results['I_T_Y']:.4f}")
        if 'H_T' in results:
            report.append(f"Representation Entropy (H(T)): {results['H_T']:.4f}")
        
        report.append("")
        
        # Performance metrics
        if 'accuracy' in results:
            report.append(f"Classification Accuracy: {results['accuracy']:.4f}")
        if 'mse' in results:
            report.append(f"Regression MSE: {results['mse']:.4f}")
        
        # Compression metrics
        if 'compression_ratio' in results:
            report.append(f"Compression Ratio: {results['compression_ratio']:.4f}")
        if 'information_efficiency' in results:
            report.append(f"Information Efficiency: {results['information_efficiency']:.4f}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def demo_evaluation():
    """
    Demonstrate Information Bottleneck evaluation on synthetic data
    """
    print("🔍 Information Bottleneck Evaluation Demo")
    print("=" * 50)
    
    # Generate synthetic data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    n_components = 5
    
    # Original data
    X = np.random.randn(n_samples, n_features)
    
    # Compressed representation (simulated)
    compression_matrix = np.random.randn(n_features, n_components)
    T = X @ compression_matrix
    
    # Target variable (classification)
    Y = (np.sum(X[:, :3], axis=1) > 0).astype(int)
    
    # Initialize evaluator
    evaluator = InformationBottleneckEvaluator()
    
    # Basic evaluation
    results = evaluator.evaluate_compression_prediction(X, T, Y)
    
    print("\n📊 Basic Evaluation Results:")
    for metric, value in results.items():
        print(f"  {metric}: {value:.4f}")
    
    # Generate different β values
    beta_values = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
    evaluation_results = []
    
    for beta in beta_values:
        # Simulate different compression levels
        noise_level = 1.0 / beta  # Higher β = less noise = more compression
        T_beta = T + np.random.randn(*T.shape) * noise_level
        
        result = evaluator.evaluate_compression_prediction(X, T_beta, Y)
        evaluation_results.append(result)
    
    # Compute β-curve
    curve_data = evaluator.compute_beta_curve(evaluation_results, beta_values)
    
    print("\n📈 β-Curve Analysis:")
    for i, beta in enumerate(beta_values):
        print(f"  β={beta:4.1f}: I(X;T)={curve_data['I_X_T'][i]:.4f}, "
              f"I(T;Y)={curve_data['I_T_Y'][i]:.4f}")
    
    # Plot information plane
    fig1 = evaluator.plot_information_plane(evaluation_results, beta_values)
    fig1.savefig('information_plane_demo.png', dpi=150, bbox_inches='tight')
    print("\n📊 Information plane plot saved as 'information_plane_demo.png'")
    
    # Plot β-curves  
    fig2 = evaluator.plot_beta_curves(curve_data)
    fig2.savefig('beta_curves_demo.png', dpi=150, bbox_inches='tight')
    print("📊 β-curves plot saved as 'beta_curves_demo.png'")
    
    # Generate report
    report = evaluator.generate_evaluation_report(results)
    print("\n" + report)
    
    print("\n✅ Information Bottleneck evaluation demo completed!")


if __name__ == "__main__":
    demo_evaluation()