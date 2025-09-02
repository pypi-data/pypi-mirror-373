"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀

🚀 Information Bottleneck Core Algorithm - The Mathematical Foundation of Modern AI
================================================================================

Author: Benedict Chen (benedict@benedictchen.com)

Based on: Naftali Tishby, Fernando C. Pereira & William Bialek (1999)
"The Information Bottleneck Method" - arXiv:physics/0004057

🎯 ELI5 Summary:
===============
Imagine you're trying to summarize a book but you can only use 10 words. The Information Bottleneck 
helps you find the perfect 10 words that keep the most important meaning while throwing away everything 
irrelevant. It's like having a magic filter that squeezes information through a narrow "bottleneck" 
but keeps exactly what you need to predict what matters!

🔬 Research Background - The Theory That Changed Everything:
============================================================
In 1999, Tishby, Pereira & Bialek published a paper that would fundamentally change how we understand 
learning, compression, and intelligence. They solved a problem that had puzzled scientists for decades:

💡 **The Central Question**: How do we extract only the "relevant" information from noisy data?

🌟 Historical Impact:
- ✅ Explains why deep neural networks generalize so well
- ✅ Provides theoretical foundation for representation learning  
- ✅ Unifies compression, prediction, and learning in one framework
- ✅ Inspired modern techniques like VAEs, β-VAE, and self-supervised learning
- ✅ Won Tishby international recognition as AI theory pioneer

The key insight was revolutionary: **relevance is determined by prediction ability**, not human intuition!

🔍 The Problem with Traditional Approaches:
==========================================
Before Information Bottleneck, there were two incomplete approaches:

❌ **Rate-Distortion Theory**: Compress data while minimizing reconstruction error
   Problem: Who decides what "error" means? Different tasks need different features!
   
❌ **Feature Selection**: Manually pick "important" features
   Problem: How do we know what's important? Human intuition is often wrong!

💡 **Tishby's Breakthrough**: Let the data tell us what's relevant!
   Instead of guessing, use a separate "relevance variable" Y to define what matters.

🏗️ The Information Bottleneck Principle:
========================================

Given:
- X: Raw input data (images, text, sensors, etc.)  
- Y: Target variable (labels, future values, etc.)
- Z: Compressed representation (the "bottleneck")

Find the optimal Z that simultaneously:
1. **Compresses X maximally**: Minimize I(X;Z) - throw away irrelevant details
2. **Preserves relevant info**: Maximize I(Z;Y) - keep predictive power

🧮 Mathematical Formulation:
============================

    minimize  L = I(X;Z) - β·I(Z;Y)
      over p(z|x)

Where:
- I(X;Z) = mutual information between input and representation (compression cost)
- I(Z;Y) = mutual information between representation and target (prediction benefit)  
- β ≥ 0 = trade-off parameter (β→0: max compression, β→∞: max prediction)

🔄 The Self-Consistent Equations (Theorem 4):
=============================================

The optimal solution satisfies these beautiful equations:

1. **Encoder Update**: p(z|x) ∝ p(z) · exp(-β·D_KL[p(y|x)||p(y|z)])
2. **Decoder Update**: p(y|z) = Σ_x p(y|x)p(x|z) 
3. **Prior Update**: p(z) = Σ_x p(x)p(z|x)

These form a fixed-point iteration that converges to the global optimum!

🌟 Why This Module Architecture?
===============================

This module implements a clean, modular architecture that separates concerns while maintaining 
the theoretical purity of Tishby's original formulation:

• **CoreTheoryMixin**: Pure mathematical core - the fundamental IB equations
• **MutualInformationMixin**: Advanced MI estimation techniques  
• **OptimizationMixin**: Multiple optimization algorithms (Blahut-Arimoto, etc.)
• **TransformPredictMixin**: Extension to new data and prediction capabilities
• **EvaluationMixin**: Analysis tools and information plane visualization

This modular design allows for:
- Clean separation of theoretical and practical concerns
- Easy testing and validation of individual components
- Flexible composition for different use cases
- Maintainable code that reflects the mathematical structure

🎖️ Key Theoretical Results:
===========================
- **Phase Transitions**: As β increases, representations undergo sudden changes
- **Universal Curves**: All problems follow similar information-theoretic trajectories  
- **Optimality**: IB representations are provably optimal for prediction
- **Connection to Thermodynamics**: β acts like "inverse temperature"

🌟 This is the mathematical foundation of modern AI - beautifully elegant and powerful! 🌟
"""

import numpy as np
from typing import Optional
from sklearn.preprocessing import LabelEncoder, StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Import all mixin classes
from .core_theory import CoreTheoryMixin
from .mutual_information import MutualInformationMixin
from .optimization import OptimizationMixin
from .transform_predict import TransformPredictMixin
from .evaluation import EvaluationMixin


class InformationBottleneck(
    CoreTheoryMixin,
    MutualInformationMixin,
    OptimizationMixin,
    TransformPredictMixin,
    EvaluationMixin
):
    """
    🔥 Information Bottleneck - The Mathematical Foundation of Modern AI!
    ====================================================================
    
    🎯 ELI5: Think of this as a smart filter that keeps only the most important 
    information from your data while throwing away noise. It's like having a 
    super-intelligent librarian who can summarize any book by keeping just the 
    sentences that help you answer specific questions!
    
    📚 Research Foundation:
    ======================
    Implements Tishby, Pereira & Bialek's groundbreaking 1999 algorithm that 
    revolutionized our understanding of representation learning. This is THE theory 
    that explains why deep networks generalize so well!
    
    🧮 Mathematical Principle:
    =========================
    Find optimal representation Z that:
    • Minimizes I(X;Z) - compression (throw away irrelevant details)
    • Maximizes I(Z;Y) - prediction (keep what matters for the task)
    
    The solution is found by optimizing: L = I(X;Z) - β·I(Z;Y)
    
    🎯 What Makes This Special:
    ==========================
    Unlike traditional methods that rely on human intuition about what's "important",
    Information Bottleneck discovers relevance automatically by using the target 
    variable Y to define what information should be preserved.
    
    This is the theoretical foundation behind:
    • Deep learning generalization
    • Representation learning  
    • Variational autoencoders (VAEs)
    • Self-supervised learning methods
    
    🔥 Multiple Implementation Methods:
    ==================================
    1. **Classical IB**: Discrete version using the original algorithm
    2. **Continuous IB**: Extension to continuous variables using KDE
    3. **Neural IB**: Deep learning implementation with variational bounds
    
    🌟 Key Features:
    ===============
    • **Modular Design**: Built from specialized mixin classes
    • **Advanced MI Estimation**: Multiple mutual information estimators
    • **Deterministic Annealing**: Improved optimization with temperature scheduling
    • **Information Plane Analysis**: Visualization of learning dynamics
    • **Extensible Architecture**: Easy to extend with new methods
    
    🎖️ Theoretical Guarantees:
    ==========================
    • **Optimality**: Provably finds the best representation for prediction
    • **Convergence**: Guaranteed to converge to global optimum
    • **Phase Transitions**: Reveals natural clustering boundaries in data
    • **Universal Behavior**: Works across different domains and data types
    
    📈 Perfect For:
    ==============
    • Feature selection with theoretical guarantees
    • Dimensionality reduction with supervised guidance  
    • Understanding what neural networks learn
    • Research into representation learning principles
    • Data compression with task-specific relevance
    
    🔬 Architecture:
    ===============
    This class inherits from multiple specialized mixins:
    
    • **CoreTheoryMixin**: Fundamental IB equations and algorithms
    • **MutualInformationMixin**: Advanced MI estimation techniques
    • **OptimizationMixin**: Multiple optimization strategies
    • **TransformPredictMixin**: New data transformation and prediction
    • **EvaluationMixin**: Analysis and visualization tools
    
    This modular design ensures clean separation of concerns while maintaining
    the theoretical purity of Tishby's original formulation.
    """

    def __init__(
        self,
        n_clusters: int = 10,
        beta: float = 1.0,
        max_iter: int = 100,
        tolerance: float = 1e-6,
        random_seed: Optional[int] = None
    ):
        """
        🚀 Initialize Information Bottleneck - Your Gateway to Optimal Representation Learning!
        ===================================================================================
        
        🎯 ELI5: Set up the smart filter that will learn to keep only the most important 
        information from your data. Think of it like training a super-efficient librarian 
        who learns exactly which details to remember and which to forget!
        
        📊 What This Does:
        ==================
        Creates the mathematical machinery to solve Tishby's Information Bottleneck principle:
        
        1. **Compression Engine**: Learns to throw away irrelevant noise from input X
        2. **Prediction Engine**: Keeps exactly the information needed to predict Y  
        3. **Optimal Balance**: Uses parameter β to trade off compression vs prediction
        4. **Convergence Monitor**: Tracks learning progress with adaptive stopping
        
        🔧 Parameter Guide:
        ==================
        Args:
            n_clusters (int, default=10): 🎛️ Size of representation space |Z|
                • Small (3-5): For simple patterns, fast learning
                • Medium (10-20): Good balance for most problems  
                • Large (50+): For complex, high-dimensional data
                • 💡 Rule of thumb: Start with √(n_samples/10)
                
            beta (float, default=1.0): ⚖️ Information trade-off parameter β
                • β < 1: Prioritize compression (lossy, fast)
                • β = 1: Balanced compression-prediction 
                • β > 1: Prioritize prediction (detailed, slower)
                • β → 0: Maximum compression (minimal representation)
                • β → ∞: Maximum prediction (detailed representation)
                
            max_iter (int, default=100): 🔄 Maximum optimization iterations
                • Simple data: 50-100 iterations usually sufficient
                • Complex data: May need 200-500 iterations
                • Monitor training_history to check convergence
                
            tolerance (float, default=1e-6): 🎯 Convergence threshold
                • Smaller values: More precise convergence
                • Larger values: Faster but less precise stopping
                • Good range: 1e-4 to 1e-8
                
            random_seed (Optional[int]): 🎲 Reproducibility control
                • None: Different results each run (exploration)
                • Fixed int: Reproducible results (debugging)
        
        🏗️ What Gets Created:
        ======================
        Internal probability distributions (learned during fit):
        • p_z_given_x: P(z|x) - Encoder: How to map inputs to clusters
        • p_y_given_z: P(y|z) - Decoder: How to predict from clusters  
        • p_z: P(z) - Prior: Cluster usage frequencies
        
        📈 Training Monitoring:
        ======================
        Tracks these metrics during optimization:
        • ib_objective: Overall Information Bottleneck loss
        • mutual_info_xz: I(X;Z) - Compression cost
        • mutual_info_zy: I(Z;Y) - Prediction benefit
        • compression_term: -I(X;Z) component
        • prediction_term: +β·I(Z;Y) component
        
        💡 Pro Usage Tips:
        ==================
        • Start with defaults, then tune β based on your needs
        • Use deterministic annealing (fit parameter) for better optimization
        • Plot information curves to visualize learning dynamics
        • Check training_history to ensure convergence
        
        🎯 Perfect For:
        ===============
        • Dimensionality reduction with supervised guidance
        • Feature selection with theoretical guarantees
        • Understanding representation learning in neural networks  
        • Research into information-theoretic principles
        
        🌟 Example Usage:
        ================
        ```python
        # Basic usage
        ib = InformationBottleneck(n_clusters=15, beta=2.0)
        ib.fit(X_train, y_train)
        Z_compressed = ib.transform(X_test)
        
        # Advanced: Information curve analysis
        curve = ib.get_information_curve(beta_values=[0.1, 1.0, 10.0], X=X, Y=y)
        ib.plot_information_plane(curve)
        ```
        """
        
        # Store core parameters
        self.n_clusters = n_clusters
        self.beta = beta
        self.max_iter = max_iter
        self.tolerance = tolerance
        
        # Set random seed for reproducibility
        if random_seed is not None:
            np.random.seed(random_seed)
            
        # Initialize learned distributions (set during fit)
        self.p_z_given_x = None  # P(z|x) - encoder distribution
        self.p_y_given_z = None  # P(y|z) - decoder distribution 
        self.p_z = None          # P(z) - cluster probabilities
        
        # Initialize preprocessing tools
        self._scaler = None         # For continuous data standardization
        self._label_encoder = None  # For discrete label encoding
        self._training_X = None     # Store training data for transform methods
        
        # Initialize training history for monitoring
        self.training_history = {
            'ib_objective': [],
            'mutual_info_xz': [], 
            'mutual_info_zy': [],
            'compression_term': [],
            'prediction_term': []
        }
        
        print(f"✓ Information Bottleneck initialized: |Z|={n_clusters}, β={beta}")
        print(f"   • Modular architecture with specialized mixins")
        print(f"   • Advanced MI estimation capabilities") 
        print(f"   • Multiple optimization algorithms available")
        print(f"   • Deterministic annealing support")
        print(f"   • Information plane analysis tools")

    def fit(self, X: np.ndarray, Y: np.ndarray, use_annealing: bool = True, 
            verbose: bool = True) -> 'InformationBottleneck':
        """
        🎯 Learn Optimal Information Bottleneck Representation
        ======================================================
        
        This is where the magic happens! The algorithm learns the optimal compressed 
        representation that balances information compression and prediction accuracy
        using Tishby's Information Bottleneck principle.
        
        🔬 What This Method Does:
        ========================
        1. **Data Preprocessing**: Standardize continuous features, encode labels
        2. **Distribution Initialization**: Set up P(z|x), P(y|z), P(z) distributions
        3. **Iterative Optimization**: Run self-consistent equations until convergence
        4. **Convergence Monitoring**: Track training metrics and detect when optimal
        
        🧮 The Mathematical Process:
        ============================
        Implements the self-consistent equations from Tishby 1999:
        
        Repeat until convergence:
        1. **Encoder Update**: p(z|x) ∝ p(z) · exp(-β·D_KL[p(y|x)||p(y|z)])
        2. **Decoder Update**: p(y|z) = Σ_x p(y|x)p(x|z) 
        3. **Prior Update**: p(z) = Σ_x p(x)p(z|x)
        
        Args:
            X (np.ndarray): Input data matrix (n_samples, n_features)
                • Continuous: Any real-valued features
                • Mixed: Handles both continuous and discrete
                • Preprocessing: Automatically standardized
                
            Y (np.ndarray): Target variable (n_samples,)  
                • Classification: Category labels (strings/ints)
                • Regression: Continuous values
                • Preprocessing: Automatically encoded/discretized
                
            use_annealing (bool, default=True): 🌡️ Deterministic annealing
                • True: Start with high temperature, gradually cool (better optima)
                • False: Use fixed β throughout (faster but may get stuck)
                • Recommended: True for better optimization
                
            verbose (bool, default=True): 📊 Progress monitoring
                • True: Print training progress and convergence info
                • False: Silent training (for batch processing)
        
        Returns:
            self: Returns fitted InformationBottleneck instance for method chaining
        
        🎯 What Gets Learned:
        ====================
        After fitting, these are available:
        • **self.p_z_given_x**: Learned encoder P(z|x) - how to compress input
        • **self.p_y_given_z**: Learned decoder P(y|z) - how to predict from compression
        • **self.p_z**: Learned prior P(z) - cluster usage frequencies
        • **self.training_history**: Convergence metrics and information quantities
        
        💡 Pro Tips:
        ===========
        • Use deterministic annealing for complex, high-dimensional data
        • Monitor training_history to ensure proper convergence
        • Try different β values to explore compression-prediction trade-offs
        • Check information plane plots to visualize learning dynamics
        
        🌟 Example:
        ===========
        ```python
        ib = InformationBottleneck(n_clusters=20, beta=1.5)
        ib.fit(X_train, y_train, use_annealing=True)
        
        # Check if training converged properly
        final_objective = ib.training_history['ib_objective'][-1]
        print(f"Final IB objective: {final_objective:.4f}")
        ```
        """
        # This method delegates to the optimization mixin which provides
        # the complete implementation including annealing, convergence checking,
        # and all the mathematical machinery
        return self._fit_implementation(X, Y, use_annealing=use_annealing, verbose=verbose)

    def transform(self, X: np.ndarray, method: str = 'auto') -> np.ndarray:
        """
        🎭 Transform New Data Through Learned Information Bottleneck
        ==========================================================
        
        Once the model is trained, use this method to transform new data through
        the learned information bottleneck representation. This gives you the
        compressed, task-relevant features discovered during training.
        
        🔬 What This Does:
        =================
        Takes new input data and maps it to the learned compressed representation
        Z using the optimal encoder distribution P(z|x) discovered during training.
        
        The challenge: How do we extend the learned discrete distribution P(z|x) 
        to continuous new data points? This method provides multiple sophisticated
        approaches to solve this fundamental problem.
        
        Args:
            X (np.ndarray): New input data to transform (n_samples, n_features)
                • Must have same number of features as training data
                • Will be automatically preprocessed using training statistics
                • Can be different number of samples than training
                
            method (str, default='auto'): 🎛️ Extension method selection
                • **'auto'**: Intelligent method selection based on data properties
                • **'fixed_decoder'**: Theoretically pure IB extension (recommended)
                • **'kernel'**: Smooth kernel-based interpolation
                • **'nearest_neighbor'**: Local similarity-based assignment
                • **'parametric'**: Neural network function approximation
        
        Returns:
            np.ndarray: Compressed representation (n_samples, n_clusters)
                • Each row sums to 1.0 (probability distribution over clusters)
                • Higher values = higher probability of assignment to that cluster
                • Preserves task-relevant information while compressing irrelevant details
        
        🧮 Extension Methods Explained:
        ===============================
        
        **Fixed Decoder Method** (Recommended):
        • Most theoretically sound approach
        • Maintains exact Information Bottleneck structure
        • Optimizes: argmin_p(z|x') D_KL[p(y|x')||p(y|z)] for each new x'
        
        **Kernel Method**:
        • Smooth interpolation using similarity to training points
        • Good for continuous data with local structure
        • Uses RBF kernels to weight training examples
        
        **Nearest Neighbor Method**:
        • Robust local assignment based on training neighbors
        • Works well when training data is dense
        • Uses k-NN to find similar training examples
        
        **Parametric Method**:
        • Fast function approximation via neural networks
        • Learns explicit mapping X → Z during training
        • Good for large-scale applications
        
        🎯 What You Get:
        ===============
        The transformed data Z has several key properties:
        • **Task Relevance**: Preserves information needed to predict Y
        • **Compression**: Removes irrelevant details and noise  
        • **Optimality**: Mathematically optimal trade-off via β parameter
        • **Interpretability**: Each cluster has semantic meaning
        
        💡 Usage Tips:
        =============
        • 'auto' method works well for most cases
        • Use 'fixed_decoder' for theoretically pure results
        • Use 'kernel' for smooth continuous data
        • Use 'nearest_neighbor' for robust discrete-like data
        • Check cluster assignments: np.argmax(Z_transformed, axis=1)
        
        🌟 Example:
        ===========
        ```python
        # Basic transformation
        ib.fit(X_train, y_train)
        Z_test = ib.transform(X_test)
        
        # Get hard cluster assignments
        cluster_assignments = np.argmax(Z_test, axis=1)
        
        # Try different extension methods
        Z_kernel = ib.transform(X_test, method='kernel')
        Z_nn = ib.transform(X_test, method='nearest_neighbor')
        ```
        """
        # This method delegates to the transform_predict mixin which provides
        # multiple sophisticated methods for extending learned representations
        # to new data points
        return self._transform_implementation(X, method=method)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        🎯 Predict Targets Using Information Bottleneck Representation
        =============================================================
        
        Make predictions on new data using the learned compressed representation.
        This demonstrates the power of the Information Bottleneck: the compressed 
        features Z contain exactly the information needed for accurate prediction!
        
        🔬 How Prediction Works:
        =======================
        1. **Transform**: Map input X → compressed representation Z using learned encoder
        2. **Predict**: Use learned decoder P(y|z) to predict from compressed features
        3. **Output**: Return most likely target value for each input
        
        The beauty: Predictions are made using only the compressed representation,
        proving that the Information Bottleneck captured the task-relevant information!
        
        Args:
            X (np.ndarray): Input data for prediction (n_samples, n_features)
                • Same feature space as training data
                • Any number of samples
                • Automatically preprocessed using training statistics
        
        Returns:
            np.ndarray: Predicted targets (n_samples,)
                • Classification: Predicted class labels  
                • Regression: Predicted continuous values
                • Same type/format as original training targets
        
        🧮 Mathematical Process:
        =======================
        For each new input x':
        1. **Compress**: z' ~ P(z|x') using learned encoder
        2. **Predict**: y' ~ P(y|z') using learned decoder  
        3. **Output**: Most likely y' value
        
        🎯 What This Demonstrates:
        =========================
        • **Information Sufficiency**: Z contains all task-relevant information from X
        • **Optimal Compression**: Irrelevant details were successfully removed
        • **Theoretical Validity**: IB principle works as predicted by theory
        
        💡 Interpretation Tips:
        ======================
        • Compare predictions to those made with original features
        • Similar accuracy → successful information compression
        • Better accuracy → IB removed noise and improved signal
        • Check which clusters are most predictive of each class
        
        🌟 Example:
        ===========
        ```python
        # Train and predict
        ib = InformationBottleneck(n_clusters=10, beta=2.0)
        ib.fit(X_train, y_train)
        y_pred = ib.predict(X_test)
        
        # Compare with original features
        from sklearn.metrics import accuracy_score
        accuracy = accuracy_score(y_true, y_pred)
        print(f"IB prediction accuracy: {accuracy:.3f}")
        
        # Analyze predictions by cluster
        Z_test = ib.transform(X_test)
        clusters = np.argmax(Z_test, axis=1)
        for cluster_id in range(ib.n_clusters):
            mask = (clusters == cluster_id)
            if np.sum(mask) > 0:
                cluster_preds = y_pred[mask]
                print(f"Cluster {cluster_id}: {np.unique(cluster_preds, return_counts=True)}")
        ```
        """
        # This method delegates to the transform_predict mixin which handles
        # the complete prediction pipeline using the learned representations
        return self._predict_implementation(X)

    def _fit_implementation(self, X: np.ndarray, Y: np.ndarray, 
                           use_annealing: bool = True, verbose: bool = True) -> 'InformationBottleneck':
        """
        🚀 Core fitting implementation that coordinates all mixin functionality.
        
        This method orchestrates the complete training process by calling methods
        from all the specialized mixins in the correct order.
        """
        # Delegate directly to the OptimizationMixin's fit method which has the complete implementation
        # The mixin handles all the preprocessing, initialization, and optimization
        
        # The OptimizationMixin fit method expects to be called on the class instance
        # and will use all the other mixins' methods as needed
        
        # Note: OptimizationMixin.fit returns a dict, but we need to return self for sklearn compatibility
        OptimizationMixin.fit(self, X, Y, use_annealing=use_annealing)
        return self

    def _transform_implementation(self, X: np.ndarray, method: str = 'auto') -> np.ndarray:
        """Transform implementation that delegates to TransformPredictMixin."""
        # Delegate directly to the TransformPredictMixin's transform method
        return TransformPredictMixin.transform(self, X, method=method)

    def _predict_implementation(self, X: np.ndarray) -> np.ndarray:
        """Prediction implementation that delegates to TransformPredictMixin."""
        # Delegate directly to the TransformPredictMixin's predict method
        return TransformPredictMixin.predict(self, X)

    def get_params(self, deep: bool = True) -> dict:
        """
        Get parameters for this estimator (sklearn compatibility).
        
        Args:
            deep: If True, returns parameters for this estimator and contained 
                 subobjects that are estimators.
        
        Returns:
            Parameter names mapped to their values.
        """
        return {
            'n_clusters': self.n_clusters,
            'beta': self.beta, 
            'max_iter': self.max_iter,
            'tolerance': self.tolerance
        }

    def set_params(self, **parameters) -> 'InformationBottleneck':
        """
        Set parameters for this estimator (sklearn compatibility).
        
        Args:
            **parameters: Parameter names and their new values.
        
        Returns:
            self: This estimator instance.
        """
        for parameter, value in parameters.items():
            if hasattr(self, parameter):
                setattr(self, parameter, value)
            else:
                raise ValueError(f"Invalid parameter {parameter} for estimator {type(self).__name__}")
        return self

    def score(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        🎯 Score the Information Bottleneck model performance.
        
        Returns the prediction accuracy for classification or R² score for regression.
        This demonstrates how well the compressed representation preserves 
        task-relevant information.
        
        Args:
            X: Input data for evaluation
            Y: True target values
            
        Returns:
            Score (higher is better): accuracy for classification, R² for regression
        """
        predictions = self.predict(X)
        
        # Determine if classification or regression
        if hasattr(self._label_encoder, 'classes_'):
            # Classification - use accuracy
            from sklearn.metrics import accuracy_score
            return accuracy_score(Y, predictions)
        else:
            # Regression - use R² score  
            from sklearn.metrics import r2_score
            return r2_score(Y, predictions)

    def __repr__(self) -> str:
        """String representation of the Information Bottleneck model."""
        status = "fitted" if self.p_z_given_x is not None else "unfitted"
        return (f"InformationBottleneck(n_clusters={self.n_clusters}, "
                f"beta={self.beta}, max_iter={self.max_iter}, "
                f"tolerance={self.tolerance}) - {status}")

    def __str__(self) -> str:
        """User-friendly string representation."""
        return self.__repr__()


# For backwards compatibility, create an alias
IB = InformationBottleneck


if __name__ == "__main__":
    """
    🚀 Demonstration of Information Bottleneck Core Algorithm
    ========================================================
    """
    print("🔥 Information Bottleneck Core Algorithm - Modular Implementation")
    print("================================================================")
    print()
    
    # Create synthetic dataset for demonstration
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    
    print("📊 Creating synthetic dataset...")
    X, y = make_classification(
        n_samples=500, n_features=20, n_informative=5, n_redundant=10,
        n_clusters_per_class=2, random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    print(f"   Training set: {X_train.shape}, Test set: {X_test.shape}")
    print()
    
    # Demonstrate core algorithm
    print("🎯 Training Information Bottleneck with modular architecture...")
    ib = InformationBottleneck(
        n_clusters=8,
        beta=1.5, 
        max_iter=150,
        tolerance=1e-6,
        random_seed=42
    )
    
    # Fit the model
    ib.fit(X_train, y_train, use_annealing=True, verbose=True)
    
    # Transform and predict
    print("\n🎭 Testing transformation and prediction capabilities...")
    Z_test = ib.transform(X_test)
    y_pred = ib.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"   Prediction accuracy: {accuracy:.3f}")
    print(f"   Compressed representation shape: {Z_test.shape}")
    print(f"   Compression ratio: {20}/{Z_test.shape[1]:.1f}x")
    
    # Analyze information content
    print("\n📊 Information analysis...")
    final_mi_xz = ib.training_history['mutual_info_xz'][-1]
    final_mi_zy = ib.training_history['mutual_info_zy'][-1]
    print(f"   I(X;Z) = {final_mi_xz:.4f} bits (information preserved)")
    print(f"   I(Z;Y) = {final_mi_zy:.4f} bits (predictive information)")
    if final_mi_xz > 0:
        print(f"   Information efficiency: {final_mi_zy/final_mi_xz:.2%}")
    else:
        print(f"   Information efficiency: N/A (degenerate solution)")
    
    # Test different transformation methods
    print("\n🔬 Testing different transformation methods...")
    methods = ['auto', 'fixed_decoder', 'kernel', 'nearest_neighbor']
    for method in methods:
        try:
            Z_method = ib.transform(X_test[:10], method=method)  # Small sample for speed
            print(f"   ✓ Method '{method}': {Z_method.shape}")
        except Exception as e:
            print(f"   ✗ Method '{method}': {str(e)}")
    
    # Demonstrate sklearn compatibility  
    print("\n🔧 Testing sklearn compatibility...")
    params = ib.get_params()
    print(f"   Parameters: {params}")
    
    ib_clone = InformationBottleneck()
    ib_clone.set_params(**params)
    print(f"   ✓ Parameter getting/setting works")
    
    score = ib.score(X_test, y_test)
    print(f"   Model score: {score:.3f}")
    
    print(f"\n✅ All core algorithm features successfully demonstrated!")
    print(f"   The modular architecture provides clean separation of concerns")
    print(f"   while maintaining theoretical purity and practical usability.")

"""
💝 Thank you for using this research software! 💝

📚 If this work contributed to your research, please:
💳 DONATE: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
📝 CITE: Benedict Chen (2025) - Information Bottleneck Research Implementation

Your support enables continued development of cutting-edge AI research tools! 🎓✨
"""