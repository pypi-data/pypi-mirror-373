"""
Information Bottleneck Optimizer
Based on: Tishby, Pereira & Bialek (1999) "The Information Bottleneck Method"

Implements optimization algorithms for finding optimal representations
that maximize I(T; Y) while minimizing I(X; T) subject to constraints.
"""

import numpy as np
from scipy.optimize import minimize
from typing import Callable, Dict, Any, Optional, Tuple, Union
import warnings
from .mutual_info_estimator import MutualInfoEstimator

class IBOptimizer:
    """
    Information Bottleneck optimization algorithms
    
    Finds representations T that solve:
    min_{p(t|x)} I(X; T) - β * I(T; Y)
    
    Where β controls the trade-off between compression and prediction.
    """
    
    def __init__(self, 
                 mi_estimator: Optional[MutualInfoEstimator] = None,
                 beta: float = 1.0,
                 method: str = "alternating_minimization"):
        """
        Initialize IB optimizer
        
        Args:
            mi_estimator: Mutual information estimator
            beta: Trade-off parameter (higher β = more compression)
            method: Optimization method - "alternating_minimization", "gradient_descent", "em"
        """
        self.mi_estimator = mi_estimator or MutualInfoEstimator()
        self.beta = beta
        self.method = method
        
        if method not in ["alternating_minimization", "gradient_descent", "em"]:
            raise ValueError(f"Unknown optimization method: {method}")
            
    def optimize(self, 
                 X: np.ndarray, 
                 Y: np.ndarray,
                 n_clusters: int = 10,
                 max_iterations: int = 100,
                 tolerance: float = 1e-6) -> Dict[str, Any]:
        """
        Optimize Information Bottleneck objective
        
        Args:
            X: Input data, shape (n_samples, n_features)
            Y: Target data, shape (n_samples, n_targets)  
            n_clusters: Number of clusters in representation T
            max_iterations: Maximum optimization iterations
            tolerance: Convergence tolerance
            
        Returns:
            Dictionary containing optimized representation and statistics
        """
        if self.method == "alternating_minimization":
            return self._alternating_minimization(X, Y, n_clusters, max_iterations, tolerance)
        elif self.method == "gradient_descent":
            return self._gradient_descent(X, Y, n_clusters, max_iterations, tolerance)
        elif self.method == "em":
            return self._expectation_maximization(X, Y, n_clusters, max_iterations, tolerance)
        else:
            raise ValueError(f"Method {self.method} not implemented")
    
    def _alternating_minimization(self, 
                                 X: np.ndarray, 
                                 Y: np.ndarray,
                                 n_clusters: int,
                                 max_iterations: int,
                                 tolerance: float) -> Dict[str, Any]:
        """
        Alternating minimization algorithm for IB
        
        Alternates between:
        1. Updating p(t|x) given p(y|t)
        2. Updating p(y|t) given p(t|x)
        """
        n_samples, n_features = X.shape
        n_targets = Y.shape[1] if Y.ndim > 1 else 1
        
        # Initialize random cluster assignments
        T = np.random.randint(0, n_clusters, n_samples)
        
        # Initialize probability matrices
        p_t_given_x = np.zeros((n_samples, n_clusters))  # p(t|x)
        p_y_given_t = np.zeros((n_clusters, n_targets))   # p(y|t)
        p_t = np.zeros(n_clusters)                        # p(t)
        
        objective_history = []
        
        for iteration in range(max_iterations):
            # E-step: Update p(t|x) using current p(y|t)
            for i in range(n_samples):
                for t in range(n_clusters):
                    # Calculate p(t|x_i) ∝ p(t) * exp(-β * D_KL[p(y|x_i) || p(y|t)])
                    if p_t[t] > 0:
                        # Simplified: use exponential of negative distance
                        y_i = Y[i] if Y.ndim > 1 else Y[i:i+1]
                        distance = np.linalg.norm(y_i - p_y_given_t[t])
                        p_t_given_x[i, t] = p_t[t] * np.exp(-self.beta * distance)
                    else:
                        p_t_given_x[i, t] = 1e-10
                        
                # Normalize p(t|x_i)
                p_t_given_x[i, :] /= np.sum(p_t_given_x[i, :])
            
            # M-step: Update p(y|t) and p(t) using current p(t|x)
            # Update p(t)
            p_t = np.mean(p_t_given_x, axis=0)
            
            # Update p(y|t) 
            for t in range(n_clusters):
                if p_t[t] > 0:
                    # Weighted average of Y values assigned to cluster t
                    weights = p_t_given_x[:, t] / p_t[t]
                    if Y.ndim > 1:
                        p_y_given_t[t, :] = np.average(Y, axis=0, weights=weights)
                    else:
                        p_y_given_t[t, 0] = np.average(Y, weights=weights)
            
            # Calculate objective function
            try:
                # Get hard assignments for MI estimation
                T_hard = np.argmax(p_t_given_x, axis=1).reshape(-1, 1)
                
                mi_xt = self.mi_estimator.estimate(X, T_hard)
                mi_ty = self.mi_estimator.estimate(T_hard, Y.reshape(-1, 1) if Y.ndim == 1 else Y)
                
                objective = mi_ty - self.beta * mi_xt
                objective_history.append(objective)
                
                # Check convergence
                if len(objective_history) > 1:
                    if abs(objective_history[-1] - objective_history[-2]) < tolerance:
                        print(f"Converged after {iteration + 1} iterations")
                        break
                        
            except Exception as e:
                warnings.warn(f"Error calculating objective at iteration {iteration}: {e}")
                objective = float('nan')
                objective_history.append(objective)
        
        # Final hard assignment
        T_final = np.argmax(p_t_given_x, axis=1)
        
        return {
            "representation": T_final,
            "soft_assignment": p_t_given_x,
            "cluster_centers": p_y_given_t,
            "cluster_probs": p_t,
            "objective_history": objective_history,
            "final_objective": objective_history[-1] if objective_history else float('nan'),
            "n_iterations": len(objective_history),
            "converged": len(objective_history) < max_iterations
        }
    
    def _gradient_descent(self,
                         X: np.ndarray,
                         Y: np.ndarray, 
                         n_clusters: int,
                         max_iterations: int,
                         tolerance: float) -> Dict[str, Any]:
        """
        Gradient descent optimization for IB
        
        Uses continuous relaxation of the discrete clustering problem.
        """
        n_samples, n_features = X.shape
        
        # Initialize soft assignments (logits)
        logits = np.random.randn(n_samples, n_clusters)
        
        learning_rate = 0.01
        objective_history = []
        
        for iteration in range(max_iterations):
            # Convert logits to probabilities
            p_t_given_x = np.exp(logits) / np.sum(np.exp(logits), axis=1, keepdims=True)
            
            # Get expected representation
            T_soft = p_t_given_x @ np.arange(n_clusters).reshape(-1, 1)
            
            try:
                # Calculate MI terms
                mi_xt = self.mi_estimator.estimate(X, T_soft)
                mi_ty = self.mi_estimator.estimate(T_soft, Y.reshape(-1, 1) if Y.ndim == 1 else Y)
                
                objective = mi_ty - self.beta * mi_xt
                objective_history.append(objective)
                
                # Simple finite difference gradient approximation
                eps = 1e-4
                gradients = np.zeros_like(logits)
                
                for i in range(n_samples):
                    for t in range(n_clusters):
                        # Perturb logit
                        logits_plus = logits.copy()
                        logits_plus[i, t] += eps
                        
                        p_plus = np.exp(logits_plus) / np.sum(np.exp(logits_plus), axis=1, keepdims=True)
                        T_plus = p_plus @ np.arange(n_clusters).reshape(-1, 1)
                        
                        mi_xt_plus = self.mi_estimator.estimate(X, T_plus)
                        mi_ty_plus = self.mi_estimator.estimate(T_plus, Y.reshape(-1, 1) if Y.ndim == 1 else Y)
                        obj_plus = mi_ty_plus - self.beta * mi_xt_plus
                        
                        gradients[i, t] = (obj_plus - objective) / eps
                
                # Update logits
                logits += learning_rate * gradients
                
                # Check convergence
                if len(objective_history) > 1:
                    if abs(objective_history[-1] - objective_history[-2]) < tolerance:
                        print(f"Converged after {iteration + 1} iterations")
                        break
                        
            except Exception as e:
                warnings.warn(f"Error in gradient descent at iteration {iteration}: {e}")
                break
        
        # Final assignments
        p_t_given_x_final = np.exp(logits) / np.sum(np.exp(logits), axis=1, keepdims=True)
        T_final = np.argmax(p_t_given_x_final, axis=1)
        
        return {
            "representation": T_final,
            "soft_assignment": p_t_given_x_final,
            "objective_history": objective_history,
            "final_objective": objective_history[-1] if objective_history else float('nan'),
            "n_iterations": len(objective_history)
        }
    
    def _expectation_maximization(self,
                                 X: np.ndarray,
                                 Y: np.ndarray,
                                 n_clusters: int, 
                                 max_iterations: int,
                                 tolerance: float) -> Dict[str, Any]:
        """
        EM algorithm for Information Bottleneck
        
        Treats IB as a special case of clustering with information constraints.
        """
        n_samples, n_features = X.shape
        
        # Initialize cluster parameters
        np.random.seed(42)  # For reproducibility
        
        # Initialize means as random samples
        cluster_means_x = X[np.random.choice(n_samples, n_clusters, replace=False)]
        if Y.ndim == 1:
            cluster_means_y = Y[np.random.choice(n_samples, n_clusters, replace=False)]
        else:
            cluster_means_y = Y[np.random.choice(n_samples, n_clusters, replace=False)]
            
        cluster_weights = np.ones(n_clusters) / n_clusters
        
        # Covariance matrices (simplified as scalar variances)
        cluster_vars = np.ones(n_clusters)
        
        responsibilities = np.zeros((n_samples, n_clusters))
        log_likelihood_history = []
        
        for iteration in range(max_iterations):
            # E-step: Calculate responsibilities
            for k in range(n_clusters):
                # Gaussian likelihood for X given cluster k
                diff_x = X - cluster_means_x[k]
                likelihood_x = np.exp(-0.5 * np.sum(diff_x**2, axis=1) / cluster_vars[k])
                
                # Gaussian likelihood for Y given cluster k  
                if Y.ndim == 1:
                    diff_y = Y - cluster_means_y[k]
                    likelihood_y = np.exp(-0.5 * diff_y**2 / cluster_vars[k])
                else:
                    diff_y = Y - cluster_means_y[k]
                    likelihood_y = np.exp(-0.5 * np.sum(diff_y**2, axis=1) / cluster_vars[k])
                
                # Combined likelihood with IB weighting
                responsibilities[:, k] = cluster_weights[k] * likelihood_x * (likelihood_y ** self.beta)
            
            # Normalize responsibilities
            responsibilities /= np.sum(responsibilities, axis=1, keepdims=True)
            
            # M-step: Update parameters
            N_k = np.sum(responsibilities, axis=0)
            
            # Update cluster weights
            cluster_weights = N_k / n_samples
            
            # Update means
            for k in range(n_clusters):
                if N_k[k] > 0:
                    cluster_means_x[k] = np.sum(responsibilities[:, k].reshape(-1, 1) * X, axis=0) / N_k[k]
                    if Y.ndim == 1:
                        cluster_means_y[k] = np.sum(responsibilities[:, k] * Y) / N_k[k]
                    else:
                        cluster_means_y[k] = np.sum(responsibilities[:, k].reshape(-1, 1) * Y, axis=0) / N_k[k]
            
            # Update variances (simplified)
            for k in range(n_clusters):
                if N_k[k] > 0:
                    diff_x = X - cluster_means_x[k]
                    var_x = np.sum(responsibilities[:, k].reshape(-1, 1) * diff_x**2) / N_k[k]
                    cluster_vars[k] = max(var_x / n_features, 1e-6)  # Prevent zero variance
            
            # Calculate log-likelihood
            log_likelihood = 0
            for i in range(n_samples):
                likelihood_i = 0
                for k in range(n_clusters):
                    diff_x = X[i] - cluster_means_x[k]
                    gauss_x = np.exp(-0.5 * np.sum(diff_x**2) / cluster_vars[k])
                    
                    if Y.ndim == 1:
                        diff_y = Y[i] - cluster_means_y[k]
                        gauss_y = np.exp(-0.5 * diff_y**2 / cluster_vars[k])
                    else:
                        diff_y = Y[i] - cluster_means_y[k]
                        gauss_y = np.exp(-0.5 * np.sum(diff_y**2) / cluster_vars[k])
                    
                    likelihood_i += cluster_weights[k] * gauss_x * (gauss_y ** self.beta)
                
                if likelihood_i > 0:
                    log_likelihood += np.log(likelihood_i)
            
            log_likelihood_history.append(log_likelihood)
            
            # Check convergence
            if len(log_likelihood_history) > 1:
                if abs(log_likelihood_history[-1] - log_likelihood_history[-2]) < tolerance:
                    print(f"EM converged after {iteration + 1} iterations")
                    break
        
        # Final cluster assignments
        T_final = np.argmax(responsibilities, axis=1)
        
        return {
            "representation": T_final,
            "soft_assignment": responsibilities,
            "cluster_means_x": cluster_means_x,
            "cluster_means_y": cluster_means_y,
            "cluster_weights": cluster_weights,
            "cluster_vars": cluster_vars,
            "log_likelihood_history": log_likelihood_history,
            "final_log_likelihood": log_likelihood_history[-1] if log_likelihood_history else float('nan'),
            "n_iterations": len(log_likelihood_history)
        }
    
    def information_curve(self,
                         X: np.ndarray,
                         Y: np.ndarray, 
                         beta_range: np.ndarray,
                         n_clusters: int = 10) -> Dict[str, np.ndarray]:
        """
        Compute Information Bottleneck curve for range of β values
        
        Creates the characteristic IB curve showing trade-off between
        compression I(X;T) and prediction I(T;Y).
        
        Args:
            X: Input data
            Y: Target data
            beta_range: Array of β values to test
            n_clusters: Number of clusters for each β
            
        Returns:
            Dictionary with I(X;T), I(T;Y) arrays for each β
        """
        mi_xt_values = []
        mi_ty_values = []
        objectives = []
        
        original_beta = self.beta
        
        for beta in beta_range:
            print(f"Computing IB for β = {beta:.3f}")
            self.beta = beta
            
            try:
                result = self.optimize(X, Y, n_clusters=n_clusters, max_iterations=50)
                T = result["representation"].reshape(-1, 1)
                
                mi_xt = self.mi_estimator.estimate(X, T)
                mi_ty = self.mi_estimator.estimate(T, Y.reshape(-1, 1) if Y.ndim == 1 else Y)
                
                mi_xt_values.append(mi_xt)
                mi_ty_values.append(mi_ty)
                objectives.append(mi_ty - beta * mi_xt)
                
            except Exception as e:
                warnings.warn(f"Failed for β = {beta}: {e}")
                mi_xt_values.append(np.nan)
                mi_ty_values.append(np.nan)
                objectives.append(np.nan)
        
        # Restore original beta
        self.beta = original_beta
        
        return {
            "beta_values": beta_range,
            "I_XT": np.array(mi_xt_values),
            "I_TY": np.array(mi_ty_values),
            "objectives": np.array(objectives)
        }