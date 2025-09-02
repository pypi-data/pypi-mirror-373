"""
Mutual Information Estimator for Information Bottleneck Method
Based on: Tishby, Pereira & Bialek (1999) "The Information Bottleneck Method"

Implements various methods for estimating mutual information I(X;Y) from data samples.
"""

import numpy as np
from scipy.special import digamma, gamma
from scipy.spatial.distance import pdist, squareform
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from typing import Union, Optional, Dict, Any, Tuple
import warnings

class MutualInfoEstimator:
    """
    Mutual Information estimator with multiple methods
    
    Critical for Information Bottleneck method which requires estimating:
    I(X; T) - mutual information between input and representation  
    I(T; Y) - mutual information between representation and target
    """
    
    def __init__(self, method: str = "ksg", k: int = 3, base: float = np.e):
        """
        Initialize MI estimator
        
        Args:
            method: Estimation method - "ksg", "binning", "kde", "mine", "sklearn"
            k: Number of neighbors for KSG estimator
            base: Logarithm base (np.e for nats, 2 for bits)
        """
        self.method = method
        self.k = k
        self.base = base
        
        if method not in ["ksg", "binning", "kde", "mine", "sklearn"]:
            raise ValueError(f"Unknown method: {method}")
            
    def estimate(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        Estimate mutual information I(X; Y)
        
        Args:
            X: First random variable samples, shape (n_samples, n_features_x)
            Y: Second random variable samples, shape (n_samples, n_features_y)
            
        Returns:
            Estimated mutual information in specified base units
        """
        X = np.atleast_2d(X)
        Y = np.atleast_2d(Y)
        
        if X.shape[0] != Y.shape[0]:
            raise ValueError("X and Y must have same number of samples")
            
        if self.method == "ksg":
            return self._ksg_estimator(X.T, Y.T)
        elif self.method == "binning":
            return self._binning_estimator(X, Y)
        elif self.method == "kde":
            return self._kde_estimator(X, Y)
        elif self.method == "mine":
            return self._mine_estimator(X, Y)
        elif self.method == "sklearn":
            return self._sklearn_estimator(X, Y)
        else:
            raise ValueError(f"Method {self.method} not implemented")
    
    def _ksg_estimator(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        Kraskov-Stögbauer-Grassberger (KSG) estimator
        
        Gold standard for continuous MI estimation.
        Paper: Kraskov et al. (2004) "Estimating mutual information"
        """
        n_samples, dx = X.shape
        _, dy = Y.shape
        
        # Combine X and Y
        XY = np.concatenate([X, Y], axis=1)
        
        # Build k-NN trees
        nn_xy = NearestNeighbors(n_neighbors=self.k + 1, metric='chebyshev')
        nn_x = NearestNeighbors(metric='chebyshev')  
        nn_y = NearestNeighbors(metric='chebyshev')
        
        nn_xy.fit(XY)
        nn_x.fit(X)
        nn_y.fit(Y)
        
        # For each point, find k-th nearest neighbor distance
        distances_xy, _ = nn_xy.kneighbors(XY)
        epsilon = distances_xy[:, self.k]  # k-th neighbor distance
        
        # Count neighbors within epsilon in marginal spaces
        nx = np.zeros(n_samples)
        ny = np.zeros(n_samples)
        
        for i in range(n_samples):
            # Count X neighbors within epsilon[i] 
            neighbors_x = nn_x.radius_neighbors([X[i]], epsilon[i])[1][0]
            nx[i] = len(neighbors_x) - 1  # Exclude self
            
            # Count Y neighbors within epsilon[i]
            neighbors_y = nn_y.radius_neighbors([Y[i]], epsilon[i])[1][0] 
            ny[i] = len(neighbors_y) - 1  # Exclude self
            
        # KSG estimator formula
        mi = (digamma(self.k) + digamma(n_samples) - 
              np.mean(digamma(nx + 1) + digamma(ny + 1)))
              
        return mi / np.log(self.base)
    
    def _binning_estimator(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        Histogram-based MI estimation using binning
        
        Simple but often biased for continuous variables.
        """
        n_samples = X.shape[0]
        
        # Determine number of bins (Freedman-Diaconis rule)
        def freedman_diaconis_bins(data):
            q75, q25 = np.percentile(data, [75, 25])
            iqr = q75 - q25
            h = 2 * iqr / (len(data) ** (1/3))
            return max(1, int((data.max() - data.min()) / h))
        
        # Flatten for univariate case
        if X.shape[1] == 1:
            X_flat = X.flatten()
            bins_x = freedman_diaconis_bins(X_flat)
        else:
            bins_x = max(5, int(np.sqrt(n_samples)))
            X_flat = X
            
        if Y.shape[1] == 1:
            Y_flat = Y.flatten()
            bins_y = freedman_diaconis_bins(Y_flat)
        else:
            bins_y = max(5, int(np.sqrt(n_samples)))
            Y_flat = Y
            
        # Create joint histogram
        try:
            if X.shape[1] == 1 and Y.shape[1] == 1:
                hist_xy, x_edges, y_edges = np.histogram2d(X_flat, Y_flat, 
                                                          bins=[bins_x, bins_y])
                hist_x, _ = np.histogram(X_flat, bins=x_edges)
                hist_y, _ = np.histogram(Y_flat, bins=y_edges)
            else:
                # For multivariate, use adaptive binning
                bins_xy = max(5, int(n_samples ** (1 / (X.shape[1] + Y.shape[1] + 2))))
                hist_xy = np.histogramdd(np.column_stack([X_flat, Y_flat]), bins=bins_xy)[0]
                hist_x = np.histogramdd(X_flat, bins=bins_xy)[0] 
                hist_y = np.histogramdd(Y_flat, bins=bins_xy)[0]
        except ValueError:
            # Fallback to fixed bins
            hist_xy, _, _ = np.histogram2d(X.flatten(), Y.flatten(), bins=10)
            hist_x, _ = np.histogram(X.flatten(), bins=10)
            hist_y, _ = np.histogram(Y.flatten(), bins=10)
        
        # Convert to probabilities
        p_xy = hist_xy / n_samples
        p_x = hist_x / n_samples  
        p_y = hist_y / n_samples
        
        # Calculate MI avoiding log(0)
        mi = 0.0
        for i in range(len(p_x)):
            for j in range(len(p_y)):
                if p_xy[i, j] > 0 and p_x[i] > 0 and p_y[j] > 0:
                    mi += p_xy[i, j] * np.log(p_xy[i, j] / (p_x[i] * p_y[j]))
                    
        return mi / np.log(self.base)
    
    def _kde_estimator(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        Kernel Density Estimation based MI
        
        Uses Gaussian kernels to estimate probability densities.
        """
        from scipy.stats import gaussian_kde
        
        n_samples = X.shape[0]
        
        # Handle dimensionality
        if X.shape[1] == 1:
            X_data = X.flatten()
        else:
            X_data = X.T
            
        if Y.shape[1] == 1:
            Y_data = Y.flatten()
        else:
            Y_data = Y.T
            
        # Joint data
        XY_data = np.vstack([X.T, Y.T])
        
        # Fit KDEs
        try:
            kde_xy = gaussian_kde(XY_data)
            kde_x = gaussian_kde(X_data)
            kde_y = gaussian_kde(Y_data)
        except np.linalg.LinAlgError:
            # Fallback to binning if KDE fails
            warnings.warn("KDE failed, falling back to binning")
            return self._binning_estimator(X, Y)
        
        # Evaluate densities at sample points
        p_xy = kde_xy(XY_data)
        p_x = kde_x(X_data)
        p_y = kde_y(Y_data)
        
        # Calculate MI
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            log_ratios = np.log(p_xy / (p_x * p_y))
            log_ratios = log_ratios[np.isfinite(log_ratios)]
            
        mi = np.mean(log_ratios) if len(log_ratios) > 0 else 0.0
        return mi / np.log(self.base)
    
    def _mine_estimator(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        MINE (Mutual Information Neural Estimation)
        
        Uses neural networks to estimate MI through dual representation.
        Simplified implementation without full neural network training.
        """
        # Enhanced MINE implementation using neural network approximation
        try:
            # Try to import neural network dependencies
            import torch
            import torch.nn as nn
            import torch.optim as optim
            
            # Simple neural network for MINE estimation
            class MINENetwork(nn.Module):
                def __init__(self, x_dim, y_dim, hidden_size=128):
                    super().__init__()
                    self.net = nn.Sequential(
                        nn.Linear(x_dim + y_dim, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, hidden_size),
                        nn.ReLU(),
                        nn.Linear(hidden_size, 1)
                    )
                
                def forward(self, x, y):
                    return self.net(torch.cat([x, y], dim=1))
            
            # Quick MINE training (simplified)
            x_dim, y_dim = X.shape[1], Y.shape[1]
            network = MINENetwork(x_dim, y_dim)
            optimizer = optim.Adam(network.parameters(), lr=0.01)
            
            X_torch = torch.FloatTensor(X)
            Y_torch = torch.FloatTensor(Y)
            
            # Train for limited epochs
            for epoch in range(50):  # Reduced for speed
                # Sample joint and marginal distributions
                batch_size = min(256, len(X))
                indices = torch.randperm(len(X))[:batch_size]
                
                x_sample = X_torch[indices]
                y_sample = Y_torch[indices]
                y_marginal = Y_torch[torch.randperm(len(Y))[:batch_size]]
                
                # MINE objective
                joint_scores = network(x_sample, y_sample)
                marginal_scores = network(x_sample, y_marginal)
                
                # DV representation: MI = E[T] - log(E[exp(T)])
                mi_estimate = joint_scores.mean() - torch.logsumexp(marginal_scores, 0) + np.log(len(marginal_scores))
                loss = -mi_estimate
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            
            # Final MI estimate
            with torch.no_grad():
                joint_scores = network(X_torch, Y_torch)
                marginal_scores = network(X_torch, Y_torch[torch.randperm(len(Y_torch))])
                mi_final = joint_scores.mean() - torch.logsumexp(marginal_scores, 0) + np.log(len(marginal_scores))
                return float(mi_final.item())
                
        except ImportError:
            # Fallback to KSG if PyTorch not available
            warnings.warn("PyTorch not available for MINE, using KSG")
            return self._ksg_estimator(X.T, Y.T)
        except Exception as e:
            warnings.warn(f"MINE estimation failed: {e}, using KSG")
            return self._ksg_estimator(X.T, Y.T)
    
    def _sklearn_estimator(self, X: np.ndarray, Y: np.ndarray) -> float:
        """
        Scikit-learn based MI estimation
        
        Uses sklearn's built-in MI estimators.
        """
        # Flatten Y for sklearn compatibility
        if Y.shape[1] == 1:
            y = Y.flatten()
            # Use regression or classification based on Y characteristics
            if len(np.unique(y)) < 20:  # Assume discrete/classification
                mi = mutual_info_classif(X, y.astype(int))[0]
            else:  # Continuous/regression
                mi = mutual_info_regression(X, y)[0]
        else:
            # For multivariate Y, use first component
            y = Y[:, 0]
            mi = mutual_info_regression(X, y)[0]
            
        return mi / np.log(self.base)
    
    def conditional_mutual_info(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray) -> float:
        """
        Estimate conditional mutual information I(X; Y | Z)
        
        Uses the identity: I(X; Y | Z) = I(X; Y, Z) - I(X; Z)
        """
        # I(X; Y, Z) 
        YZ = np.column_stack([Y, Z])
        mi_xyz = self.estimate(X, YZ)
        
        # I(X; Z)
        mi_xz = self.estimate(X, Z)
        
        return mi_xyz - mi_xz
    
    def information_bottleneck_quantities(self, X: np.ndarray, T: np.ndarray, Y: np.ndarray) -> Dict[str, float]:
        """
        Compute all quantities needed for Information Bottleneck method
        
        Args:
            X: Input data
            T: Intermediate representation  
            Y: Target data
            
        Returns:
            Dictionary with I(X;T), I(T;Y), I(X;Y), and IB Lagrangian
        """
        mi_xt = self.estimate(X, T)
        mi_ty = self.estimate(T, Y) 
        mi_xy = self.estimate(X, Y)
        
        # Information Bottleneck Lagrangian: I(T; Y) - β * I(X; T)
        # Common β values are around 0.1 to 10
        beta = 1.0  
        ib_lagrangian = mi_ty - beta * mi_xt
        
        return {
            "I(X;T)": mi_xt,
            "I(T;Y)": mi_ty, 
            "I(X;Y)": mi_xy,
            "IB_Lagrangian": ib_lagrangian,
            "beta": beta
        }