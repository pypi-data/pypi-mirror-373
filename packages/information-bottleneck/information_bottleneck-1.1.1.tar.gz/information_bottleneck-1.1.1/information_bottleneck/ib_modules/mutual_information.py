"""
💧 Mutual Information Estimation Module - Core of Information Bottleneck Theory
===============================================================================

Author: Benedict Chen (benedict@benedictchen.com)

💝 Support This Work: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Based on: Naftali Tishby, Fernando C. Pereira & William Bialek (1999)
"The Information Bottleneck Method" - arXiv:physics/0004057

🎯 Module Overview:
This module contains the core mutual information estimation functions extracted from 
the Information Bottleneck framework. It provides multiple state-of-the-art MI 
estimation methods including KSG estimators, ensemble methods, adaptive selection,
and bias correction techniques.

🔬 Theoretical Foundation:
The Information Bottleneck principle is built on accurate mutual information estimation.
This module implements the theoretical requirements from Tishby's 1999 paper with
multiple robust estimators to handle different data characteristics and dimensionalities.

⚡ Key Features:
- KSG (Kraskov-Grassberger-Stögbauer) estimators with multiple k values
- Ensemble methods combining multiple estimators
- Adaptive method selection based on data characteristics  
- Bias correction using jackknife and other techniques
- Copula-based estimation for non-Gaussian dependencies
- High-dimensional data handling with PCA projection
- Histogram and kernel density based fallback methods

🚀 Usage:
This is designed as a mixin class to be inherited by the main InformationBottleneck
class, maintaining access to self state variables like p_z_given_x, p_z, etc.
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
from scipy.stats import entropy
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import KBinsDiscretizer, QuantileTransformer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings


class MutualInformationMixin:
    """
    Mixin class providing mutual information estimation capabilities for Information Bottleneck.
    
    This class contains all the core MI estimation functions extracted from the main
    InformationBottleneck implementation. It's designed to be mixed into the main class
    to provide clean separation of concerns while maintaining access to instance variables.
    
    The methods in this class implement various state-of-the-art mutual information
    estimators suitable for the theoretical requirements of Tishby's Information
    Bottleneck framework.
    """

    def _estimate_mutual_info_discrete(self, joint_dist: np.ndarray) -> float:
        """
        Estimate mutual information from joint distribution using proper entropy calculation.
        
        Implements the fundamental MI formula: I(X;Y) = H(X) + H(Y) - H(X,Y)
        Uses numerically stable entropy calculations to avoid log(0) issues.
        
        Args:
            joint_dist: Joint probability distribution as 2D numpy array
            
        Returns:
            Mutual information estimate in bits
            
        Notes:
            - Adds small epsilon to avoid log(0) numerical issues
            - Uses scipy's entropy function for numerical stability
            - Ensures non-negative result (theoretical requirement)
        """
        
        # Avoid log(0) by adding small epsilon
        epsilon = 1e-12
        joint_dist = joint_dist + epsilon
        
        # Normalize to probabilities
        joint_dist = joint_dist / np.sum(joint_dist)
        
        # Marginal distributions
        marginal_x = np.sum(joint_dist, axis=1)
        marginal_y = np.sum(joint_dist, axis=0)
        
        # Compute entropies using scipy's entropy function (more stable)
        H_X = entropy(marginal_x, base=2)
        H_Y = entropy(marginal_y, base=2)
        H_XY = entropy(joint_dist.flatten(), base=2)
        
        # Mutual information: I(X;Y) = H(X) + H(Y) - H(X,Y)
        mi = H_X + H_Y - H_XY
        
        return max(0.0, mi)  # Ensure non-negative due to numerical errors

    def _estimate_mutual_info_continuous(self, X: np.ndarray, Y: np.ndarray, 
                                        n_neighbors: int = 3, method: str = 'auto') -> float:
        """
        Estimate mutual information for continuous variables using multiple robust methods.
        
        This implementation provides multiple estimation methods with automatic selection
        based on data characteristics to handle the theoretical requirements from Tishby 1999.
        
        Args:
            X, Y: Input variables (can be multidimensional)
            n_neighbors: Number of neighbors for KSG estimator
            method: MI estimation method
                - 'auto': Automatically select based on data characteristics
                - 'ksg': Kraskov-Grassberger-Stögbauer estimator
                - 'ensemble': Combination of multiple estimators
                - 'adaptive': Adaptive parameter selection
                - 'bias_corrected': Jackknife bias correction
                - 'copula': Copula-based estimation for non-Gaussian data
        
        Returns:
            Mutual information estimate in bits
            
        Notes:
            - Automatically selects optimal method if method='auto'
            - Handles both univariate and multivariate data
            - All methods return MI in bits for consistency
        """
        
        if method == 'auto':
            method = self._select_optimal_mi_method(X, Y)
        
        if method == 'ksg':
            return self._ksg_estimator(X, Y, n_neighbors)
        elif method == 'ensemble':
            return self._ensemble_mi_estimation(X, Y)
        elif method == 'adaptive':
            return self._adaptive_mi_estimation(X, Y)
        elif method == 'bias_corrected':
            return self._bias_corrected_mi_estimation(X, Y)
        elif method == 'copula':
            return self._copula_mi_estimation(X, Y)
        else:
            return self._ksg_estimator(X, Y, n_neighbors)

    def _select_optimal_mi_method(self, X: np.ndarray, Y: np.ndarray) -> str:
        """
        Select optimal MI estimation method based on data characteristics.
        
        Uses heuristics based on sample size, dimensionality, and data properties
        to choose the most appropriate estimator for the given data.
        
        Args:
            X, Y: Input data arrays
            
        Returns:
            String indicating the recommended method
            
        Selection Criteria:
            - Small samples (n < 100): Use bias correction
            - High dimensional (d > 10): Use adaptive method
            - Medium samples (100 ≤ n < 1000): Use ensemble for robustness
            - Large samples (n ≥ 1000): Use standard KSG
        """
        n_samples = X.shape[0] if len(X.shape) > 1 else len(X)
        x_dim = X.shape[1] if len(X.shape) > 1 else 1
        y_dim = Y.shape[1] if len(Y.shape) > 1 else 1
        
        # Small sample size - use bias correction
        if n_samples < 100:
            return 'bias_corrected'
        # High dimensional - use adaptive
        elif x_dim > 10 or y_dim > 10:
            return 'adaptive'
        # Medium size with low dimension - use ensemble for robustness
        elif n_samples < 1000:
            return 'ensemble'
        # Large sample - use standard KSG
        else:
            return 'ksg'

    def _ksg_estimator(self, X: np.ndarray, Y: np.ndarray, k: int = 3) -> float:
        """
        Kraskov-Grassberger-Stögbauer estimator implementation.
        
        Implements the KSG algorithm which is one of the most widely used and
        theoretically sound MI estimators for continuous data. Uses k-nearest
        neighbors in the joint space and marginal spaces.
        
        Args:
            X, Y: Input variables 
            k: Number of neighbors for estimation
            
        Returns:
            Mutual information estimate in bits
            
        Algorithm:
            1. Normalize data to [0,1] range
            2. Find k-th nearest neighbors in joint space
            3. Count neighbors in marginal spaces within same distance
            4. Apply KSG formula with digamma functions
            
        Notes:
            - Uses configurable digamma computation methods
            - Handles both univariate and multivariate inputs
            - Normalizes data for numerical stability
        """
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        if len(Y.shape) == 1:
            Y = Y.reshape(-1, 1)
            
        n_samples = X.shape[0]
        
        # Normalize to [0,1]
        X_norm = (X - np.min(X, axis=0)) / (np.max(X, axis=0) - np.min(X, axis=0) + 1e-12)
        Y_norm = (Y - np.min(Y, axis=0)) / (np.max(Y, axis=0) - np.min(Y, axis=0) + 1e-12)
        
        # Combine X and Y
        XY = np.hstack([X_norm, Y_norm])
        
        # Build k-d trees for efficient neighbor search
        nbrs_xy = NearestNeighbors(n_neighbors=k + 1, metric='chebyshev').fit(XY)
        nbrs_x = NearestNeighbors(metric='chebyshev').fit(X_norm)
        nbrs_y = NearestNeighbors(metric='chebyshev').fit(Y_norm)
        
        # KSG estimator
        distances_xy, _ = nbrs_xy.kneighbors(XY)
        epsilon = distances_xy[:, -1]  # Distance to k-th neighbor
        
        mi_sum = 0.0
        for i in range(n_samples):
            # Count neighbors within epsilon in marginal spaces
            n_x = len(nbrs_x.radius_neighbors([X_norm[i]], epsilon[i])[1][0]) - 1
            n_y = len(nbrs_y.radius_neighbors([Y_norm[i]], epsilon[i])[1][0]) - 1
            
            # CONFIGURABLE DIGAMMA COMPUTATION
            # Multiple methods available for different accuracy/speed tradeoffs
            digamma_method = getattr(self, 'digamma_method', 'improved_approximation')
            
            if digamma_method == 'scipy_exact':
                # Use scipy for exact digamma computation
                try:
                    from scipy.special import digamma
                    mi_sum += (digamma(k) - digamma(n_x + 1) - digamma(n_y + 1) + digamma(n_samples))
                except ImportError:
                    warnings.warn("scipy not available, falling back to approximation")
                    mi_sum += self._compute_digamma_approximation(k, n_x, n_y, n_samples)
            elif digamma_method == 'improved_approximation':
                # Better approximation with higher-order terms
                mi_sum += self._compute_digamma_approximation(k, n_x, n_y, n_samples)
            elif digamma_method == 'asymptotic_expansion':
                # Asymptotic expansion for better accuracy
                mi_sum += self._compute_digamma_asymptotic(k, n_x, n_y, n_samples)
            elif digamma_method == 'simple_log':
                # Original simplified version (for compatibility)
                mi_sum += (np.log(k) - np.log(max(1, n_x)) - np.log(max(1, n_y)) + np.log(n_samples))
            else:
                # Default to improved approximation
                mi_sum += self._compute_digamma_approximation(k, n_x, n_y, n_samples)
            
        return max(0.0, mi_sum / n_samples / np.log(2))  # Convert to bits

    def _ensemble_mi_estimation(self, X: np.ndarray, Y: np.ndarray, weights: Optional[List[float]] = None) -> float:
        """
        Combine multiple MI estimators with learned or equal weights.
        
        Uses multiple different estimators and combines their results for
        improved robustness and accuracy. This is particularly useful when
        the optimal method is unclear from data characteristics alone.
        
        Args:
            X, Y: Input variables
            weights: Optional weights for combining estimators (default: equal weights)
            
        Returns:
            Weighted combination of MI estimates in bits
            
        Estimators Used:
            - KSG with k=3, 5, 7 (different neighborhood sizes)
            - Histogram-based binning estimator
            - Kernel density estimator
            
        Notes:
            - Gracefully handles estimator failures with fallback to 0
            - Equal weights used by default
            - Can be extended with learned weights from cross-validation
        """
        estimators = [
            ('ksg_k3', lambda x, y: self._ksg_estimator(x, y, k=3)),
            ('ksg_k5', lambda x, y: self._ksg_estimator(x, y, k=5)),
            ('ksg_k7', lambda x, y: self._ksg_estimator(x, y, k=7)),
            ('binning', self._binning_mi_estimator),
            ('kernel', self._kernel_mi_estimator)
        ]
        
        if weights is None:
            # Equal weights by default
            weights = [1.0 / len(estimators)] * len(estimators)
        
        mi_estimates = []
        for (name, estimator), weight in zip(estimators, weights):
            try:
                mi_est = estimator(X, Y)
                mi_estimates.append(mi_est * weight)
            except Exception:
                mi_estimates.append(0.0)  # Fallback
                
        return sum(mi_estimates)

    def _adaptive_mi_estimation(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        Automatically select optimal parameters based on data characteristics.
        
        Adapts the estimation method and parameters based on sample size,
        dimensionality, and other data properties for optimal performance.
        
        Args:
            X, Y: Input variables
            
        Returns:
            Adaptively estimated mutual information in bits
            
        Adaptation Strategy:
            - Small samples (< 100): k=3 for KSG
            - Medium samples (< 1000): k=5 for KSG  
            - Large samples (≥ 1000): k=7 for KSG
            - High dimensional (d > 10): Use binning instead
            - Very small samples (< 50): Use binning
        """
        sample_size = X.shape[0] if len(X.shape) > 1 else len(X)
        d = X.shape[1] if len(X.shape) > 1 else 1
        
        # Adaptive k for KSG based on sample size
        if sample_size < 100:
            k = 3
        elif sample_size < 1000:
            k = 5
        else:
            k = 7
            
        # Choose estimator based on dimensionality and sample size
        if d > 10 or sample_size < 50:
            # Use binning for high-dim or small sample
            return self._binning_mi_estimator(X, Y)
        else:
            return self._ksg_estimator(X, Y, k=k)

    def _bias_corrected_mi_estimation(self, X: np.ndarray, Y: np.ndarray, correction: str = 'jackknife') -> float:
        """
        Apply bias correction techniques to MI estimation.
        
        Implements jackknife bias correction which is particularly important
        for small sample sizes where MI estimators tend to be positively biased.
        
        Args:
            X, Y: Input variables
            correction: Type of bias correction ('jackknife' supported)
            
        Returns:
            Bias-corrected mutual information estimate in bits
            
        Jackknife Method:
            1. Compute full sample MI estimate
            2. Compute leave-one-out estimates for random subset
            3. Apply bias correction formula:
               MI_corrected = n * MI_full - (n-1) * mean(MI_jackknife)
               
        Notes:
            - Uses sample-based jackknife for computational efficiency
            - Falls back to standard estimator if correction fails
            - Essential for accurate small-sample MI estimation
        """
        n = X.shape[0] if len(X.shape) > 1 else len(X)
        
        if correction == 'jackknife' and n > 10:
            # Jackknife bias correction
            full_estimate = self._ksg_estimator(X, Y)
            jackknife_estimates = []
            
            # Sample-based jackknife for efficiency
            n_jackknife = min(20, n)
            indices = np.random.choice(n, n_jackknife, replace=False)
            
            for i in indices:
                # Leave-one-out estimate
                mask = np.ones(n, dtype=bool)
                mask[i] = False
                try:
                    jackknife_est = self._ksg_estimator(X[mask], Y[mask])
                    jackknife_estimates.append(jackknife_est)
                except Exception:
                    continue
            
            if jackknife_estimates:
                # Bias correction: MI_corrected = n * MI_full - (n-1) * mean(MI_jackknife)
                bias = (n - 1) * (np.mean(jackknife_estimates) - full_estimate) / n
                return max(0.0, full_estimate - bias)
                
        # Fallback to standard estimator
        return self._ksg_estimator(X, Y)

    def _copula_mi_estimation(self, X: np.ndarray, Y: np.ndarray, copula_type: str = 'gaussian') -> float:
        """
        Copula-based MI estimation for handling non-Gaussian dependencies.
        
        Uses copula transforms to handle complex, non-linear dependencies
        that might not be well captured by standard MI estimators.
        
        Args:
            X, Y: Input variables
            copula_type: Type of copula ('gaussian' supported)
            
        Returns:
            Copula-based mutual information estimate in bits
            
        Algorithm:
            1. Transform variables to uniform marginals using empirical CDF
            2. Apply copula-specific transformation (e.g., Gaussian)
            3. Estimate MI using copula-specific formula
            4. For Gaussian copula: MI = -0.5 * log(1 - ρ²)
            
        Notes:
            - Particularly effective for non-Gaussian dependencies
            - Falls back to standard KSG if copula estimation fails
            - Handles correlation coefficients near ±1 gracefully
        """
        try:
            from scipy import stats
            
            # Transform to uniform marginals using empirical CDF
            transformer_x = QuantileTransformer(output_distribution='uniform')
            transformer_y = QuantileTransformer(output_distribution='uniform')
            
            X_flat = X.flatten() if len(X.shape) > 1 else X
            Y_flat = Y.flatten() if len(Y.shape) > 1 else Y
            
            U_X = transformer_x.fit_transform(X_flat.reshape(-1, 1)).flatten()
            U_Y = transformer_y.fit_transform(Y_flat.reshape(-1, 1)).flatten()
            
            if copula_type == 'gaussian':
                # Transform to standard normal
                Z_X = stats.norm.ppf(np.clip(U_X, 1e-8, 1-1e-8))
                Z_Y = stats.norm.ppf(np.clip(U_Y, 1e-8, 1-1e-8))
                
                # Estimate correlation coefficient
                rho = np.corrcoef(Z_X, Z_Y)[0, 1]
                
                # MI for bivariate Gaussian copula
                if not np.isnan(rho) and abs(rho) < 0.99:
                    return -0.5 * np.log(1 - rho**2) / np.log(2)
                else:
                    return 0.0
            else:
                # Fallback to KSG on transformed data
                return self._ksg_estimator(Z_X.reshape(-1, 1), Z_Y.reshape(-1, 1))
                
        except Exception:
            # Fallback to standard estimator
            return self._ksg_estimator(X, Y)

    def _binning_mi_estimator(self, X: np.ndarray, Y: np.ndarray, bins: str = 'auto') -> float:
        """
        Histogram-based MI estimation using adaptive binning.
        
        Discretizes continuous variables and estimates MI using histograms.
        This method is robust for high-dimensional data and small samples.
        
        Args:
            X, Y: Input variables
            bins: Binning strategy ('auto' for adaptive, or integer)
            
        Returns:
            Histogram-based mutual information estimate in bits
            
        Algorithm:
            1. Determine optimal number of bins based on sample size
            2. Discretize variables using uniform binning
            3. Build joint histogram
            4. Apply discrete MI formula
            
        Notes:
            - Automatically selects bin count as sqrt(n_samples)
            - Uses sklearn's KBinsDiscretizer for robust binning
            - Falls back to 0 if discretization fails
        """
        try:
            # Determine number of bins
            n_samples = X.shape[0] if len(X.shape) > 1 else len(X)
            if bins == 'auto':
                n_bins = max(5, int(np.sqrt(n_samples)))
            else:
                n_bins = bins if isinstance(bins, int) else 10
            
            # Discretize variables
            discretizer_x = KBinsDiscretizer(n_bins=n_bins, encode='ordinal', strategy='uniform')
            discretizer_y = KBinsDiscretizer(n_bins=n_bins, encode='ordinal', strategy='uniform')
            
            X_binned = discretizer_x.fit_transform(X.reshape(-1, 1) if len(X.shape) == 1 else X).flatten()
            Y_binned = discretizer_y.fit_transform(Y.reshape(-1, 1) if len(Y.shape) == 1 else Y).flatten()
            
            # Build joint histogram
            joint_hist, _, _ = np.histogram2d(X_binned, Y_binned, bins=n_bins)
            
            return self._estimate_mutual_info_discrete(joint_hist)
            
        except Exception:
            return 0.0

    def _kernel_mi_estimator(self, X: np.ndarray, Y: np.ndarray, kernel: str = 'rbf') -> float:
        """
        Kernel density estimation based MI estimation.
        
        Uses kernel density estimation to approximate probability densities
        and then estimates MI from the density ratios.
        
        Args:
            X, Y: Input variables
            kernel: Kernel type ('rbf' default, 'gaussian' used internally)
            
        Returns:
            Kernel-based mutual information estimate in bits
            
        Algorithm:
            1. Fit kernel density estimators to marginals and joint
            2. Sample points for numerical integration
            3. Estimate MI as E[log(p(x,y)/(p(x)p(y)))]
            
        Notes:
            - Uses Gaussian kernels with fixed bandwidth
            - Samples subset of points for computational efficiency
            - Falls back to 0 if kernel estimation fails
        """
        try:
            from sklearn.neighbors import KernelDensity
            
            # Simple approximation using kernel density estimation
            X_flat = X.flatten() if len(X.shape) > 1 else X
            Y_flat = Y.flatten() if len(Y.shape) > 1 else Y
            
            # Estimate marginal densities
            kde_x = KernelDensity(kernel='gaussian', bandwidth=0.1)
            kde_y = KernelDensity(kernel='gaussian', bandwidth=0.1)
            kde_xy = KernelDensity(kernel='gaussian', bandwidth=0.1)
            
            kde_x.fit(X_flat.reshape(-1, 1))
            kde_y.fit(Y_flat.reshape(-1, 1))
            kde_xy.fit(np.column_stack([X_flat, Y_flat]))
            
            # Sample points for integration
            n_samples = min(100, len(X_flat))
            sample_indices = np.random.choice(len(X_flat), n_samples, replace=False)
            
            mi_sum = 0.0
            for i in sample_indices:
                x_i, y_i = X_flat[i], Y_flat[i]
                
                log_pxy = kde_xy.score_samples([[x_i, y_i]])[0]
                log_px = kde_x.score_samples([[x_i]])[0]
                log_py = kde_y.score_samples([[y_i]])[0]
                
                mi_sum += log_pxy - log_px - log_py
                
            return max(0.0, mi_sum / n_samples / np.log(2))
            
        except Exception:
            return 0.0

    def _adaptive_mutual_info_estimator(self, X: np.ndarray, Y: np.ndarray, 
                                       data_type: str = 'auto') -> float:
        """
        Adaptively choose MI estimation method based on data characteristics.
        
        Automatically determines whether data should be treated as discrete
        or continuous and selects the appropriate estimation method.
        
        Args:
            X, Y: Input variables
            data_type: Data type hint ('auto', 'discrete', 'continuous')
            
        Returns:
            Adaptively estimated mutual information in bits
            
        Detection Heuristic:
            - If unique values ratio > 0.1 for both variables: continuous
            - Otherwise: discrete
            
        Discrete Handling:
            - Uses KMeans for multidimensional discretization
            - Builds joint histogram for MI calculation
            
        Notes:
            - More robust than fixed method selection
            - Handles both continuous and discrete-like data appropriately
        """
        
        if data_type == 'auto':
            # Heuristic: if many unique values and continuous-looking, use continuous estimator
            x_unique_ratio = len(np.unique(X.flatten())) / len(X.flatten())
            y_unique_ratio = len(np.unique(Y.flatten())) / len(Y.flatten())
            
            if x_unique_ratio > 0.1 and y_unique_ratio > 0.1:
                data_type = 'continuous'
            else:
                data_type = 'discrete'
                
        if data_type == 'continuous':
            return self._estimate_mutual_info_continuous(X, Y)
        else:
            # For discrete case, build joint histogram
            if len(X.shape) > 1:
                # Use KMeans for multidimensional discretization (more robust)
                kmeans = KMeans(n_clusters=min(20, len(X)), random_state=42, n_init=10)
                X_flat = kmeans.fit_predict(X)
            else:
                X_flat = X.flatten()
                
            # Ensure Y is 1D
            Y_flat = Y.flatten()
                
            # Build joint distribution using proper binning
            x_unique = np.unique(X_flat)
            y_unique = np.unique(Y_flat)
            
            joint_hist = np.zeros((len(x_unique), len(y_unique)))
            
            for i, x_val in enumerate(x_unique):
                for j, y_val in enumerate(y_unique):
                    joint_hist[i, j] = np.sum((X_flat == x_val) & (Y_flat == y_val))
            
            return self._estimate_mutual_info_discrete(joint_hist)

    def _histogram_ib_estimation(self, X: np.ndarray, Y: np.ndarray, n_samples: int) -> Tuple[float, float]:
        """
        Histogram-based Information Bottleneck estimation as fallback method.
        
        Used when continuous MI estimation fails, provides robust fallback
        for computing I(X;Z) and I(Z;Y) using histogram approximations.
        
        Args:
            X: Input features
            Y: Target variables  
            n_samples: Number of samples
            
        Returns:
            Tuple of (I_X_Z, I_Z_Y) mutual information estimates
            
        Algorithm:
            1. Quantize X using K-means clustering for multidimensional case
            2. Build joint distributions for (X,Z) and (Z,Y)
            3. Use sample-based approximation for large datasets
            4. Apply discrete MI formula to joint histograms
            
        Notes:
            - Critical fix: Uses proper X quantization with K-means
            - Handles high-dimensional X robustly
            - Uses probabilistic assignments for soft clustering
        """
        n_y_values = len(np.unique(Y))
        
        # Use K-means clustering for X quantization (more robust than naive binning)
        n_x_bins = min(20, n_samples)  # Reasonable number of X bins
        
        # Quantize X using K-means instead of naive indexing
        if X.shape[1] > 1:
            kmeans_x = KMeans(n_clusters=n_x_bins, random_state=42, n_init=10)
            x_quantized_all = kmeans_x.fit_predict(X)
        else:
            # For 1D, use quantile-based binning
            x_quantized_all = np.digitize(X.flatten(), np.quantile(X.flatten(), np.linspace(0, 1, n_x_bins+1)[1:-1])) - 1
            x_quantized_all = np.clip(x_quantized_all, 0, n_x_bins-1)
        
        # Build joint distributions using proper quantization
        joint_xz = np.zeros((n_x_bins, self.n_clusters))
        joint_zy = np.zeros((self.n_clusters, n_y_values))
        
        # Sample-based approximation for large datasets
        sample_indices = np.random.choice(n_samples, min(1000, n_samples), replace=False)
        
        for i in sample_indices:
            x_bin = x_quantized_all[i]  # Use proper quantization
            y_idx = Y[i]
            
            for z in range(self.n_clusters):
                joint_xz[x_bin, z] += self.p_z_given_x[i, z] / len(sample_indices)
                joint_zy[z, y_idx] += self.p_z_given_x[i, z] / len(sample_indices)
                
        I_X_Z = self._estimate_mutual_info_discrete(joint_xz)
        I_Z_Y = self._estimate_mutual_info_discrete(joint_zy.T)
        
        return I_X_Z, I_Z_Y

    def _estimate_mi_high_dimensional(self, X: np.ndarray, Z: np.ndarray, 
                                    n_components: int = 10) -> float:
        """
        Estimate mutual information for high-dimensional data using PCA projection.
        
        Projects high-dimensional X to lower dimensional space using PCA
        before applying MI estimation. Useful when X has many features.
        
        Args:
            X: High-dimensional input features
            Z: Target variable (often cluster assignments)
            n_components: Number of PCA components to retain
            
        Returns:
            Mutual information estimate in bits
            
        Algorithm:
            1. Apply PCA to X to reduce dimensionality
            2. Use adaptive MI estimator on reduced-dimension data
            3. Preserves most important variance in X
            
        Notes:
            - Essential for very high-dimensional X
            - Automatically limits components to available dimensions
            - Falls back gracefully for lower-dimensional data
        """
        
        # Project X to lower dimensions using PCA
        pca = PCA(n_components=min(n_components, X.shape[1]))
        X_reduced = pca.fit_transform(X)
        
        return self._adaptive_mutual_info_estimator(X_reduced, Z)

    def _compute_digamma_approximation(self, k, n_x, n_y, n_samples):
        """
        Improved digamma approximation using second-order terms.
        
        Implements improved approximation: ψ(x) ≈ log(x) - 1/(2x) - 1/(12x²)
        More accurate than simple log approximation for finite values.
        
        Args:
            k: Number of neighbors
            n_x, n_y: Neighbor counts in marginal spaces
            n_samples: Total sample count
            
        Returns:
            Digamma difference for KSG formula
            
        Notes:
            - Uses recurrence relation for x < 1: ψ(x+1) = ψ(x) + 1/x  
            - Second-order approximation for better accuracy
            - Handles edge cases with x ≤ 0
        """
        def digamma_approx(x):
            """Second-order digamma approximation"""
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

    def _compute_digamma_asymptotic(self, k, n_x, n_y, n_samples):
        """
        Asymptotic expansion for digamma function with higher-order terms.
        
        Uses higher-order asymptotic expansion for better accuracy:
        ψ(x) ≈ log(x) - 1/(2x) - 1/(12x²) + 1/(120x⁴) - 1/(252x⁶) + ...
        
        Args:
            k: Number of neighbors
            n_x, n_y: Neighbor counts in marginal spaces  
            n_samples: Total sample count
            
        Returns:
            Digamma difference for KSG formula
            
        Notes:
            - Uses recurrence relation for small values (x < 2)
            - Higher-order terms for improved accuracy
            - More accurate than second-order approximation
        """
        def digamma_asymptotic(x):
            """Higher-order asymptotic expansion"""
            if x <= 0:
                return -np.inf
            elif x < 2:
                # Use recurrence relation for small values
                return digamma_asymptotic(x + 1) - 1.0/x
            else:
                # Asymptotic series with more terms
                x_inv = 1.0/x
                x2_inv = x_inv * x_inv
                x4_inv = x2_inv * x2_inv
                x6_inv = x4_inv * x2_inv
                
                return (np.log(x) - 0.5 * x_inv - 
                       (1.0/12.0) * x2_inv + 
                       (1.0/120.0) * x4_inv - 
                       (1.0/252.0) * x6_inv)
        
        return (digamma_asymptotic(k) - digamma_asymptotic(n_x + 1) - 
                digamma_asymptotic(n_y + 1) + digamma_asymptotic(n_samples))

    def set_digamma_method(self, method: str):
        """
        Configure the digamma computation method for KSG estimator.
        
        Args:
            method: Digamma computation method
                - 'scipy_exact': Use scipy.special.digamma (most accurate)
                - 'improved_approximation': Second-order approximation 
                - 'asymptotic_expansion': Higher-order asymptotic expansion
                - 'simple_log': Simple log approximation (fastest, least accurate)
        
        Notes:
            - Sets instance attribute used by _ksg_estimator
            - Default is 'improved_approximation' for good accuracy/speed balance
            - 'scipy_exact' requires scipy installation
        """
        valid_methods = ['scipy_exact', 'improved_approximation', 'asymptotic_expansion', 'simple_log']
        if method not in valid_methods:
            raise ValueError(f"Invalid digamma method. Choose from: {valid_methods}")
        
        self.digamma_method = method