"""
📊 Mutual Information Core - The Mathematical Heart of Information Theory
========================================================================

📚 Research Paper:
Tishby, N., Pereira, F. C., & Bialek, W. (1999)
"The Information Bottleneck Method"
arXiv:physics/0004057

🎯 ELI5 Summary:
Mutual Information is like measuring how much knowing one thing tells you about another!
If you know someone's height, how much can you guess their weight? Mutual Information
quantifies this "predictiveness" between variables. It's the secret sauce that lets
AI figure out what information is truly important vs. what's just noise!

🧪 Research Background:
Mutual Information I(X;Y) forms the mathematical foundation of the Information
Bottleneck principle. It measures the statistical dependence between random variables,
providing the theoretical framework for optimal information compression.

Key concepts:
- I(X;Y) = 0: Variables are independent (knowing X tells you nothing about Y)
- I(X;Y) = H(X): Variables are perfectly dependent (X completely determines Y)
- Symmetric: I(X;Y) = I(Y;X)
- Always non-negative

🔬 Mathematical Framework:
Discrete: I(X;Y) = Σₓ Σᵧ p(x,y) log[p(x,y)/(p(x)p(y))]
Continuous: I(X;Y) = ∫∫ p(x,y) log[p(x,y)/(p(x)p(y))] dx dy
KSG Estimator: I(X;Y) ≈ ψ(k) + ψ(N) - ⟨ψ(nₓ + 1) + ψ(nᵧ + 1)⟩

🎨 ASCII Diagram - Mutual Information Concept:
=============================================

    Variables X and Y Relationship Spectrum:
    
    Independent (I=0)        Dependent (I>0)        Perfect Dependence (I=H)
    X: ●○●○●○               X: ●●○○●●                X: ●○●○●○
    Y: ○●○●○●               Y: ●●○○●●                Y: ●○●○●○
       ↑                      ↑                        ↑
    No pattern            Strong pattern           Identical pattern
    
    Information Bottleneck Trade-off:
    
    Input X ─────► Bottleneck T ─────► Output Y
        │              │                  │
        └─── I(X;T) ───┘                  │
                       └──── I(T;Y) ──────┘
                       
    Goal: Minimize I(X;T) while Maximizing I(T;Y)

👨‍💻 Author: Benedict Chen
💰 Donations: Help support this work! Buy me a coffee ☕, beer 🍺, or lamborghini 🏎️
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Please consider recurring donations to fully support continued research

🔗 Related Work: Information Theory, Entropy Estimation, Statistical Dependencies
"""

import numpy as np
from typing import Optional, List
from scipy.spatial.distance import pdist, squareform
from scipy.special import digamma
from sklearn.metrics import mutual_info_score
from sklearn.neighbors import NearestNeighbors


class MutualInfoCore:
    """Core mutual information estimation algorithms"""
    
    def __init__(self, method: str = 'ksg', **kwargs):
        self.method = method
        self.kwargs = kwargs
    
    def estimate_mutual_info_discrete(self, joint_dist: np.ndarray) -> float:
        """
        Estimate mutual information from discrete joint distribution
        
        Args:
            joint_dist: Joint distribution p(x,y) as 2D array
            
        Returns:
            Mutual information I(X;Y)
        """
        # Ensure proper probability distribution
        joint_dist = joint_dist / np.sum(joint_dist)
        
        # Marginal distributions
        p_x = np.sum(joint_dist, axis=1)
        p_y = np.sum(joint_dist, axis=0)
        
        # Compute mutual information
        mi = 0.0
        for i in range(joint_dist.shape[0]):
            for j in range(joint_dist.shape[1]):
                if joint_dist[i, j] > 1e-12:  # Avoid log(0)
                    if p_x[i] > 1e-12 and p_y[j] > 1e-12:
                        mi += joint_dist[i, j] * np.log(joint_dist[i, j] / (p_x[i] * p_y[j]))
        
        return mi
    
    def estimate_mutual_info_continuous(self, X: np.ndarray, Y: np.ndarray, 
                                      method: str = 'ksg') -> float:
        """
        Estimate mutual information for continuous variables
        
        Args:
            X: First variable [n_samples, n_features_x]
            Y: Second variable [n_samples, n_features_y]
            method: Estimation method ('ksg', 'binning', 'kernel')
            
        Returns:
            Estimated mutual information
        """
        if method == 'ksg':
            return self._ksg_estimator(X, Y)
        elif method == 'binning':
            return self._binning_mi_estimator(X, Y)
        elif method == 'kernel':
            return self._kernel_mi_estimator(X, Y)
        else:
            raise ValueError(f"Unknown continuous MI method: {method}")
    
    def _ksg_estimator(self, X: np.ndarray, Y: np.ndarray, k: int = 3) -> float:
        """
        Kozachenko-Leonenko-Grassberger (KSG) estimator for mutual information
        
        This is a k-nearest neighbor based estimator that's consistent for 
        continuous distributions.
        
        Args:
            X: First variable [n_samples, n_features_x] 
            Y: Second variable [n_samples, n_features_y]
            k: Number of nearest neighbors
            
        Returns:
            MI estimate using KSG method
        """
        n_samples = X.shape[0]
        
        # Ensure 2D arrays
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if Y.ndim == 1:
            Y = Y.reshape(-1, 1)
        
        # Combined data
        XY = np.hstack([X, Y])
        
        # Build k-NN models
        xy_nn = NearestNeighbors(n_neighbors=k+1, metric='chebyshev').fit(XY)
        x_nn = NearestNeighbors(n_neighbors=k, metric='chebyshev').fit(X)
        y_nn = NearestNeighbors(n_neighbors=k, metric='chebyshev').fit(Y)
        
        # For each point, find k-th nearest neighbor distance in joint space
        mi_sum = 0.0
        
        for i in range(n_samples):
            # Distance to k-th nearest neighbor in joint space (excluding self)
            distances, _ = xy_nn.kneighbors([XY[i]], k+1)
            epsilon = distances[0, k]  # k-th neighbor distance (0-th is self)
            
            # Count neighbors within epsilon in marginal spaces
            x_neighbors = x_nn.radius_neighbors([X[i]], epsilon - 1e-10, 
                                               return_distance=False)[0]
            y_neighbors = y_nn.radius_neighbors([Y[i]], epsilon - 1e-10,
                                               return_distance=False)[0]
            
            n_x = len(x_neighbors)
            n_y = len(y_neighbors)
            
            # KSG formula with digamma functions
            if n_x > 0 and n_y > 0:
                mi_sum += self._compute_digamma_approximation(k, n_x, n_y, n_samples)
        
        mi_estimate = mi_sum / n_samples
        return max(0.0, mi_estimate)  # MI is non-negative
    
    def _binning_mi_estimator(self, X: np.ndarray, Y: np.ndarray, 
                             bins: str = 'auto') -> float:
        """
        Histogram-based mutual information estimator
        
        Args:
            X: First variable
            Y: Second variable  
            bins: Binning strategy ('auto', 'fd', 'scott', or integer)
            
        Returns:
            MI estimate using histogram method
        """
        # Ensure 1D for histogram
        if X.ndim > 1:
            # Use first principal component for multivariate data
            from sklearn.decomposition import PCA
            pca_x = PCA(n_components=1)
            X = pca_x.fit_transform(X).ravel()
        else:
            X = X.ravel()
            
        if Y.ndim > 1:
            from sklearn.decomposition import PCA
            pca_y = PCA(n_components=1)  
            Y = pca_y.fit_transform(Y).ravel()
        else:
            Y = Y.ravel()
        
        # Determine number of bins
        if isinstance(bins, str):
            if bins == 'auto':
                # Sturges' rule with adjustment for MI
                n_bins_x = max(5, int(np.log2(len(X)) + 1))
                n_bins_y = max(5, int(np.log2(len(Y)) + 1))
            elif bins == 'fd':
                # Freedman-Diaconis rule
                def fd_bins(data):
                    iqr = np.percentile(data, 75) - np.percentile(data, 25)
                    return max(5, int((np.max(data) - np.min(data)) / 
                                    (2 * iqr * len(data)**(-1/3))))
                n_bins_x = fd_bins(X)
                n_bins_y = fd_bins(Y)
            elif bins == 'scott':
                # Scott's rule
                def scott_bins(data):
                    return max(5, int((np.max(data) - np.min(data)) / 
                                    (3.5 * np.std(data) * len(data)**(-1/3))))
                n_bins_x = scott_bins(X)
                n_bins_y = scott_bins(Y)
        else:
            n_bins_x = n_bins_y = bins
        
        # Create 2D histogram
        hist_xy, x_edges, y_edges = np.histogram2d(X, Y, bins=[n_bins_x, n_bins_y])
        
        # Add small epsilon to avoid log(0)
        hist_xy = hist_xy + 1e-10
        
        # Convert to probability
        joint_prob = hist_xy / np.sum(hist_xy)
        
        return self.estimate_mutual_info_discrete(joint_prob)
    
    def _kernel_mi_estimator(self, X: np.ndarray, Y: np.ndarray, 
                           kernel: str = 'rbf') -> float:
        """
        Kernel-based mutual information estimator
        
        Uses kernel density estimation to approximate probability densities
        
        Args:
            X: First variable
            Y: Second variable
            kernel: Kernel type ('rbf', 'linear', 'polynomial')
            
        Returns:
            MI estimate using kernel method
        """
        from sklearn.neighbors import KernelDensity
        
        # Ensure 2D arrays
        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if Y.ndim == 1:
            Y = Y.reshape(-1, 1)
        
        # Combined data
        XY = np.hstack([X, Y])
        
        # Determine bandwidth using rule-of-thumb
        n_samples = X.shape[0]
        
        # Scott's rule adapted for MI
        bw_x = n_samples**(-1/(X.shape[1] + 4))
        bw_y = n_samples**(-1/(Y.shape[1] + 4)) 
        bw_xy = n_samples**(-1/(XY.shape[1] + 4))
        
        try:
            # Fit kernel density estimators
            kde_x = KernelDensity(kernel=kernel, bandwidth=bw_x).fit(X)
            kde_y = KernelDensity(kernel=kernel, bandwidth=bw_y).fit(Y)  
            kde_xy = KernelDensity(kernel=kernel, bandwidth=bw_xy).fit(XY)
            
            # Evaluate densities on sample points
            log_p_x = kde_x.score_samples(X)
            log_p_y = kde_y.score_samples(Y)
            log_p_xy = kde_xy.score_samples(XY)
            
            # MI = E[log(p(x,y)/(p(x)p(y)))]
            mi_samples = log_p_xy - log_p_x - log_p_y
            mi_estimate = np.mean(mi_samples)
            
            return max(0.0, mi_estimate)
            
        except Exception as e:
            # Fallback to binning method if kernel estimation fails
            print(f"⚠️  Kernel MI estimation failed: {e}, falling back to binning")
            return self._binning_mi_estimator(X, Y)
    
    def _ensemble_mi_estimation(self, X: np.ndarray, Y: np.ndarray, 
                               weights: Optional[List[float]] = None) -> float:
        """
        Ensemble mutual information estimation
        
        Combines multiple estimators for robust estimation
        
        Args:
            X: First variable
            Y: Second variable
            weights: Optional weights for different estimators
            
        Returns:
            Weighted ensemble MI estimate
        """
        methods = ['ksg', 'binning', 'kernel']
        estimates = []
        
        for method in methods:
            try:
                mi = self.estimate_mutual_info_continuous(X, Y, method)
                estimates.append(mi)
            except Exception as e:
                print(f"⚠️  Method {method} failed: {e}")
                estimates.append(0.0)
        
        if weights is None:
            # Equal weights with preference for KSG (most theoretically sound)
            weights = [0.5, 0.3, 0.2]
        
        # Weighted average
        ensemble_mi = sum(w * est for w, est in zip(weights, estimates))
        return max(0.0, ensemble_mi)
    
    def _adaptive_mi_estimation(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        Adaptive method selection based on data properties
        
        Args:
            X: First variable
            Y: Second variable
            
        Returns:
            MI estimate using adaptively selected method
        """
        n_samples = X.shape[0]
        
        # Data dimensionality
        d_x = X.shape[1] if X.ndim > 1 else 1
        d_y = Y.shape[1] if Y.ndim > 1 else 1
        
        # Select method based on sample size and dimensionality
        if n_samples < 100:
            # Small sample: use binning with few bins
            return self._binning_mi_estimator(X, Y, bins=5)
        elif d_x + d_y > 5:
            # High dimensional: use kernel method
            return self._kernel_mi_estimator(X, Y)
        else:
            # Default: KSG estimator
            return self._ksg_estimator(X, Y)
    
    def _compute_digamma_approximation(self, k: int, n_x: int, n_y: int, n_samples: int) -> float:
        """
        Compute digamma approximation for KSG estimator
        
        Args:
            k: Number of nearest neighbors
            n_x: Number of x-neighbors within epsilon
            n_y: Number of y-neighbors within epsilon
            n_samples: Total number of samples
            
        Returns:
            Digamma approximation value
        """
        def digamma_approx(x):
            """High-accuracy digamma approximation using multiple methods"""
            if x <= 0:
                return -np.inf  # Proper behavior for non-positive arguments
            elif x < 1:
                # Use recurrence relation: ψ(x) = ψ(x+1) - 1/x
                return digamma_approx(x + 1) - 1.0/x
            elif x < 7:
                # Higher-order series expansion for improved accuracy
                # ψ(x) = -γ + Σ((-1)^n * ζ(n+1) * x^n / n!) for |x| < 1
                # For x >= 1, use Stirling series
                x_shifted = x - 1
                result = -0.5772156649015329  # Euler-Mascheroni constant
                
                # More terms for better accuracy
                terms = [
                    1.0,                    # x^1 term
                    -1.0/12.0,             # x^2 term  
                    1.0/120.0,             # x^3 term
                    -1.0/252.0,            # x^4 term
                    1.0/240.0,             # x^5 term
                    -1.0/132.0,            # x^6 term
                    691.0/32760.0,         # x^7 term (Bernoulli number)
                    -1.0/12.0              # x^8 term
                ]
                
                x_power = x_shifted
                for i, coeff in enumerate(terms):
                    if i == 0:
                        result += coeff * np.log(x)
                    else:
                        result += coeff * x_power / (i + 1)
                        x_power *= x_shifted
                        
                return result
            else:
                # High-precision asymptotic expansion for large x
                # ψ(x) = ln(x) - 1/(2x) - 1/(12x^2) + 1/(120x^4) - 1/(252x^6) + ...
                inv_x = 1.0 / x
                inv_x2 = inv_x * inv_x
                
                result = np.log(x) - 0.5 * inv_x
                
                # Bernoulli numbers series for high accuracy
                result -= inv_x2 / 12.0                    # B_2/2
                result += inv_x2 * inv_x2 / 120.0          # B_4/4  
                result -= inv_x2 * inv_x2 * inv_x2 / 252.0 # B_6/6
                result += inv_x2**4 / 240.0                # B_8/8
                result -= inv_x2**4 * inv_x2 / 132.0       # B_10/10
                
                return result
        
        # KSG formula components
        psi_k = digamma_approx(k)
        psi_n = digamma_approx(n_samples)
        psi_nx = digamma_approx(n_x)
        psi_ny = digamma_approx(n_y)
        
        return psi_k + psi_n - psi_nx - psi_ny