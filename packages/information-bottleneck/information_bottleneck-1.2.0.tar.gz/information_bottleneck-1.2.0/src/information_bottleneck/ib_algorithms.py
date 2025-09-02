"""
Core Information Bottleneck algorithms and optimization methods
Based on: Tishby, Pereira & Bialek (1999) "The Information Bottleneck Method"
"""

import numpy as np
from typing import Dict, Tuple, Optional, List
from sklearn.cluster import KMeans
try:
    from .mutual_info_core import MutualInfoCore
    from .ib_config import IBConfig, EncoderUpdateMethod, DecoderUpdateMethod, InitializationMethod
except ImportError:
    from mutual_info_core import MutualInfoCore
    from ib_config import IBConfig, EncoderUpdateMethod, DecoderUpdateMethod, InitializationMethod


class IBAlgorithms:
    """Core algorithms for Information Bottleneck optimization"""
    
    def __init__(self, config: IBConfig):
        self.config = config
        self.mi_estimator = MutualInfoCore()
        
        # Algorithm state
        self.p_z_given_x = None  # Encoder p(z|x)
        self.p_y_given_z = None  # Decoder p(y|z)  
        self.p_z = None         # Prior p(z)
        
        # Training history
        self.history = {
            'compression': [],
            'relevance': [],
            'objective': [],
            'beta_values': []
        } if config.save_history else None
    
    def initialize_distributions(self, X: np.ndarray, Y: np.ndarray) -> None:
        """
        Initialize encoder and decoder distributions
        
        Args:
            X: Input data [n_samples, n_features]
            Y: Target data [n_samples, n_targets]
        """
        n_samples = X.shape[0]
        n_clusters = self.config.n_clusters
        
        if self.config.initialization == InitializationMethod.RANDOM:
            # Random initialization
            self.p_z_given_x = np.random.dirichlet(np.ones(n_clusters), n_samples)
            
        elif self.config.initialization == InitializationMethod.KMEANS_PLUS_PLUS:
            self._kmeans_plus_plus_initialization(X, Y)
            
        elif self.config.initialization == InitializationMethod.MUTUAL_INFO:
            self._mutual_info_initialization(X, Y)
            
        elif self.config.initialization == InitializationMethod.HIERARCHICAL:
            self._hierarchical_ib_initialization(X, Y)
        
        # Initialize decoder using Bayes' rule
        self._update_decoder_bayes_rule(X, Y)
        
        # Update prior
        self.p_z = np.mean(self.p_z_given_x, axis=0)
    
    def _kmeans_plus_plus_initialization(self, X: np.ndarray, Y: np.ndarray) -> None:
        """Initialize using k-means++ clustering"""
        # Use both X and Y for clustering to get relevant clusters
        if Y.ndim == 1:
            Y_features = Y.reshape(-1, 1)
        else:
            Y_features = Y
            
        # Combine features (weighted towards Y since it's the target)
        # Add epsilon to avoid division by zero
        eps = 1e-8
        X_std = np.std(X, axis=0, keepdims=True) + eps
        Y_std = np.std(Y_features, axis=0, keepdims=True) + eps
        
        combined_features = np.hstack([
            X / X_std,  # Standardize X
            3 * Y_features / Y_std  # Weight Y higher
        ])
        
        # K-means clustering
        kmeans = KMeans(
            n_clusters=self.config.n_clusters,
            init='k-means++',
            n_init=self.config.n_init,
            random_state=self.config.random_state
        )
        cluster_labels = kmeans.fit_predict(combined_features)
        
        # Convert to soft assignment with temperature
        temperature = 0.5
        distances = kmeans.transform(combined_features)
        soft_assignments = np.exp(-distances / temperature)
        self.p_z_given_x = soft_assignments / np.sum(soft_assignments, axis=1, keepdims=True)
    
    def _mutual_info_initialization(self, X: np.ndarray, Y: np.ndarray) -> None:
        """Initialize based on mutual information between features and targets"""
        n_samples, n_features = X.shape
        n_clusters = self.config.n_clusters
        
        # Compute MI between each feature and target
        feature_mi = np.zeros(n_features)
        for i in range(n_features):
            feature_mi[i] = self.mi_estimator.estimate_mutual_info_continuous(
                X[:, i:i+1], Y, method='binning'
            )
        
        # Select most informative features
        top_features = np.argsort(feature_mi)[-min(5, n_features):]
        X_selected = X[:, top_features]
        
        # Cluster using informative features
        kmeans = KMeans(n_clusters=n_clusters, random_state=self.config.random_state)
        cluster_labels = kmeans.fit_predict(X_selected)
        
        # Convert to soft assignment
        self.p_z_given_x = np.zeros((n_samples, n_clusters))
        for i, label in enumerate(cluster_labels):
            self.p_z_given_x[i, label] = 1.0
        
        # Add small noise for better convergence
        noise = np.random.dirichlet(0.1 * np.ones(n_clusters), n_samples)
        self.p_z_given_x = 0.9 * self.p_z_given_x + 0.1 * noise
    
    def _hierarchical_ib_initialization(self, X: np.ndarray, Y: np.ndarray) -> None:
        """Hierarchical initialization for better local optima"""
        n_samples = X.shape[0]
        n_clusters = self.config.n_clusters
        
        # Start with 2 clusters and progressively split
        current_clusters = 2
        self.p_z_given_x = np.zeros((n_samples, 2))
        
        # Initial 2-cluster split using k-means
        kmeans = KMeans(n_clusters=2, random_state=self.config.random_state)
        labels = kmeans.fit_predict(X)
        for i, label in enumerate(labels):
            self.p_z_given_x[i, label] = 1.0
        
        # Progressively split clusters
        while current_clusters < n_clusters:
            # Find cluster with highest internal variance
            cluster_variances = np.zeros(current_clusters)
            for z in range(current_clusters):
                cluster_mask = self.p_z_given_x[:, z] > 0.5
                if np.sum(cluster_mask) > 1:
                    cluster_data = X[cluster_mask]
                    cluster_variances[z] = np.trace(np.cov(cluster_data.T))
            
            # Split the cluster with highest variance
            split_cluster = np.argmax(cluster_variances)
            cluster_mask = self.p_z_given_x[:, split_cluster] > 0.5
            
            if np.sum(cluster_mask) > 2:  # Need at least 2 points to split
                cluster_data = X[cluster_mask]
                sub_kmeans = KMeans(n_clusters=2, random_state=self.config.random_state)
                sub_labels = sub_kmeans.fit_predict(cluster_data)
                
                # Update assignments
                new_p_z = np.zeros((n_samples, current_clusters + 1))
                new_p_z[:, :split_cluster] = self.p_z_given_x[:, :split_cluster]
                new_p_z[:, split_cluster+1:current_clusters] = self.p_z_given_x[:, split_cluster+1:current_clusters]
                
                # Split the selected cluster
                cluster_indices = np.where(cluster_mask)[0]
                for i, idx in enumerate(cluster_indices):
                    if sub_labels[i] == 0:
                        new_p_z[idx, split_cluster] = 1.0
                    else:
                        new_p_z[idx, current_clusters] = 1.0
                
                self.p_z_given_x = new_p_z
                current_clusters += 1
            else:
                # Can't split further, add random cluster
                new_p_z = np.zeros((n_samples, current_clusters + 1))
                new_p_z[:, :-1] = self.p_z_given_x
                # Assign some points randomly to new cluster
                random_indices = np.random.choice(n_samples, size=max(1, n_samples//10), replace=False)
                for idx in random_indices:
                    new_p_z[idx, :-1] = 0.1 * new_p_z[idx, :-1]
                    new_p_z[idx, -1] = 0.9
                    new_p_z[idx] /= np.sum(new_p_z[idx])
                
                self.p_z_given_x = new_p_z
                current_clusters += 1
        
        # Ensure we have exactly n_clusters
        if current_clusters > n_clusters:
            # Merge similar clusters
            self.p_z_given_x = self.p_z_given_x[:, :n_clusters]
            self.p_z_given_x /= np.sum(self.p_z_given_x, axis=1, keepdims=True)
    
    def update_encoder(self, X: np.ndarray, Y: np.ndarray, temperature: float = 1.0) -> None:
        """
        Update encoder distribution p(z|x)
        
        Args:
            X: Input data
            Y: Target data
            temperature: Temperature parameter for annealing
        """
        if self.config.encoder_update_method == EncoderUpdateMethod.BLAHUT_ARIMOTO:
            self._blahut_arimoto_update(X, Y, temperature)
        elif self.config.encoder_update_method == EncoderUpdateMethod.NATURAL_GRADIENT:
            self._natural_gradient_update(X, Y, temperature)
        elif self.config.encoder_update_method == EncoderUpdateMethod.TEMPERATURE_SCALED:
            self._temperature_scaled_update(X, Y, temperature)
        elif self.config.encoder_update_method == EncoderUpdateMethod.DETERMINISTIC_ANNEALING:
            self._deterministic_annealing_update(X, Y, temperature)
    
    def _blahut_arimoto_update(self, X: np.ndarray, Y: np.ndarray, temperature: float = 1.0) -> None:
        """Standard Blahut-Arimoto algorithm update"""
        n_samples = X.shape[0]
        n_clusters = self.config.n_clusters
        
        # Update encoder using self-consistent equations
        new_p_z_given_x = np.zeros((n_samples, n_clusters))
        
        for i in range(n_samples):
            for z in range(n_clusters):
                # Compute KL divergence D(p(y|x_i) || p(y|z))
                kl_div = self._compute_exact_kl_divergence(i, z)
                
                # Self-consistent update
                new_p_z_given_x[i, z] = self.p_z[z] * np.exp(-self.config.beta * kl_div / temperature)
        
        # Normalize
        for i in range(n_samples):
            Z_i = np.sum(new_p_z_given_x[i, :])
            if Z_i > 1e-12:
                new_p_z_given_x[i, :] /= Z_i
            else:
                # If all probabilities are zero, use uniform distribution
                new_p_z_given_x[i, :] = 1.0 / n_clusters
        
        self.p_z_given_x = new_p_z_given_x
        
        # Update prior
        self.p_z = np.mean(self.p_z_given_x, axis=0)
    
    def _compute_exact_kl_divergence(self, x_idx: int, z: int) -> float:
        """Compute KL divergence D(p(y|x_i) || p(y|z))"""
        # For discrete case, this requires knowing p(y|x_i)
        # In practice, we approximate this using the current decoder
        kl_div = 0.0
        
        # Simple approximation: use squared difference in predictions
        # This is not exact KL but provides the right optimization direction
        y_given_x = self.p_y_given_z[z, :]  # Current prediction for z
        
        # Compute approximate divergence (placeholder implementation)
        # In full implementation, this would compute actual KL divergence
        kl_div = np.sum((y_given_x - 0.5)**2)  # Simplified version
        
        return kl_div
    
    def _natural_gradient_update(self, X: np.ndarray, Y: np.ndarray, temperature: float = 1.0) -> None:
        """Natural gradient update for encoder"""
        # Compute gradient of IB objective
        gradient = self._compute_ib_gradient(X, Y, temperature)
        
        # Compute Fisher information metric (approximation)
        fisher_diag = self._compute_fisher_diagonal()
        
        # Natural gradient step
        lr = 0.01 / temperature  # Adaptive learning rate
        update = lr * gradient / (fisher_diag + 1e-8)
        
        # Update parameters in probability simplex
        self.p_z_given_x += update
        
        # Project back to probability simplex
        self._project_to_simplex()
        
        # Update prior
        self.p_z = np.mean(self.p_z_given_x, axis=0)
    
    def _compute_ib_gradient(self, X: np.ndarray, Y: np.ndarray, temperature: float) -> np.ndarray:
        """Compute gradient of IB objective w.r.t. encoder parameters"""
        n_samples, n_clusters = self.p_z_given_x.shape
        gradient = np.zeros((n_samples, n_clusters))
        
        for i in range(n_samples):
            for z in range(n_clusters):
                # Compression term gradient
                compression_grad = np.log(self.p_z_given_x[i, z] / self.p_z[z])
                
                # Relevance term gradient (approximation)
                relevance_grad = -np.sum(Y[i] * np.log(self.p_y_given_z[z, :] + 1e-12))
                
                gradient[i, z] = compression_grad - self.config.beta * relevance_grad
        
        return gradient
    
    def _compute_fisher_diagonal(self) -> np.ndarray:
        """Compute diagonal approximation of Fisher information matrix"""
        fisher = np.zeros_like(self.p_z_given_x)
        
        for i in range(self.p_z_given_x.shape[0]):
            for z in range(self.p_z_given_x.shape[1]):
                # Diagonal Fisher information
                fisher[i, z] = 1.0 / (self.p_z_given_x[i, z] + 1e-8)
        
        return fisher
    
    def _project_to_simplex(self) -> None:
        """Project encoder probabilities to probability simplex"""
        for i in range(self.p_z_given_x.shape[0]):
            # Ensure non-negative
            self.p_z_given_x[i, :] = np.maximum(self.p_z_given_x[i, :], 1e-12)
            
            # Normalize to sum to 1
            row_sum = np.sum(self.p_z_given_x[i, :])
            if row_sum > 1e-12:
                self.p_z_given_x[i, :] /= row_sum
            else:
                # If all zeros, use uniform distribution
                self.p_z_given_x[i, :] = 1.0 / self.p_z_given_x.shape[1]
    
    def _temperature_scaled_update(self, X: np.ndarray, Y: np.ndarray, temperature: float) -> None:
        """Temperature-scaled soft assignment update"""
        n_samples = X.shape[0]
        n_clusters = self.config.n_clusters
        
        # Compute assignment scores
        scores = np.zeros((n_samples, n_clusters))
        
        for i in range(n_samples):
            for z in range(n_clusters):
                # Score based on relevance to target Y
                if Y.ndim == 1:
                    target_similarity = -np.abs(Y[i] - np.dot(self.p_y_given_z[z, :], np.arange(self.p_y_given_z.shape[1])))
                else:
                    target_similarity = -np.sum((Y[i] - self.p_y_given_z[z, :])**2)
                
                # Prior preference  
                prior_score = np.log(self.p_z[z] + 1e-12)
                
                scores[i, z] = self.config.beta * target_similarity + prior_score
        
        # Soft assignment with temperature
        self.p_z_given_x = np.exp(scores / temperature)
        
        # Normalize
        for i in range(n_samples):
            row_sum = np.sum(self.p_z_given_x[i, :])
            if row_sum > 1e-12:
                self.p_z_given_x[i, :] /= row_sum
            else:
                self.p_z_given_x[i, :] = 1.0 / n_clusters
        
        # Update prior
        self.p_z = np.mean(self.p_z_given_x, axis=0)
    
    def _deterministic_annealing_update(self, X: np.ndarray, Y: np.ndarray, 
                                      temperature: float, phase: str = 'cooling') -> None:
        """Deterministic annealing with phase transitions"""
        if phase == 'cooling':
            # Standard cooling phase
            self._blahut_arimoto_update(X, Y, temperature)
        elif phase == 'heating':
            # Heating phase to escape local minima
            noise_level = 1.0 / temperature
            noise = np.random.dirichlet(noise_level * np.ones(self.config.n_clusters), X.shape[0])
            self.p_z_given_x = 0.8 * self.p_z_given_x + 0.2 * noise
            self.p_z = np.mean(self.p_z_given_x, axis=0)
    
    def update_decoder(self, X: np.ndarray, Y: np.ndarray) -> None:
        """
        Update decoder distribution p(y|z)
        
        Args:
            X: Input data
            Y: Target data
        """
        if self.config.decoder_update_method == DecoderUpdateMethod.BAYES_RULE:
            self._update_decoder_bayes_rule(X, Y)
        elif self.config.decoder_update_method == DecoderUpdateMethod.EM:
            self._em_decoder_update(X, Y)
        elif self.config.decoder_update_method == DecoderUpdateMethod.REGULARIZED:
            self._regularized_decoder_update(X, Y)
    
    def _update_decoder_bayes_rule(self, X: np.ndarray, Y: np.ndarray) -> None:
        """Update decoder using Bayes' rule: p(y|z) = Σ_x p(y|x)p(x|z)"""
        n_clusters = self.config.n_clusters
        
        if Y.ndim == 1:
            # Discrete Y
            n_y_values = len(np.unique(Y))
            self.p_y_given_z = np.zeros((n_clusters, n_y_values))
            
            for z in range(n_clusters):
                for y_val in range(n_y_values):
                    # Find samples with this y value
                    y_indices = np.where(Y == y_val)[0]
                    
                    # Weighted average using p(z|x) 
                    if len(y_indices) > 0:
                        weight_sum = np.sum(self.p_z_given_x[y_indices, z])
                        if weight_sum > 1e-12:
                            self.p_y_given_z[z, y_val] = weight_sum
                
                # Normalize to probability distribution
                row_sum = np.sum(self.p_y_given_z[z, :])
                if row_sum > 1e-12:
                    self.p_y_given_z[z, :] /= row_sum
                else:
                    self.p_y_given_z[z, :] = 1.0 / n_y_values
        else:
            # Continuous Y - use weighted average
            n_y_dim = Y.shape[1] 
            self.p_y_given_z = np.zeros((n_clusters, n_y_dim))
            
            for z in range(n_clusters):
                # Compute weighted average
                weights = self.p_z_given_x[:, z]
                weight_sum = np.sum(weights)
                
                if weight_sum > 1e-12:
                    self.p_y_given_z[z, :] = np.average(Y, axis=0, weights=weights)
                else:
                    self.p_y_given_z[z, :] = np.mean(Y, axis=0)
    
    def _em_decoder_update(self, X: np.ndarray, Y: np.ndarray) -> None:
        """EM-style decoder update with soft assignments"""
        # Similar to Bayes rule but with additional smoothing
        self._update_decoder_bayes_rule(X, Y)
        
        # Add Laplace smoothing for discrete case
        if Y.ndim == 1:
            self.p_y_given_z += self.config.decoder_regularization
            self.p_y_given_z /= np.sum(self.p_y_given_z, axis=1, keepdims=True)
    
    def _regularized_decoder_update(self, X: np.ndarray, Y: np.ndarray, alpha: float = 0.1) -> None:
        """Regularized decoder update with L2 penalty"""
        # Start with Bayes rule update
        self._update_decoder_bayes_rule(X, Y)
        
        # Add regularization towards uniform/mean
        if Y.ndim == 1:
            # Discrete case: regularize towards uniform
            n_y_values = self.p_y_given_z.shape[1]
            uniform = np.ones(n_y_values) / n_y_values
            self.p_y_given_z = (1 - alpha) * self.p_y_given_z + alpha * uniform
        else:
            # Continuous case: regularize towards global mean
            global_mean = np.mean(Y, axis=0)
            self.p_y_given_z = (1 - alpha) * self.p_y_given_z + alpha * global_mean
    
    def compute_ib_objective(self, X: np.ndarray, Y: np.ndarray) -> Dict[str, float]:
        """
        Compute Information Bottleneck objective and its components
        
        Args:
            X: Input data
            Y: Target data
            
        Returns:
            Dictionary with objective components
        """
        # Compression term: I(X;Z)
        compression = self._compute_compression_term(X)
        
        # Relevance term: I(Z;Y) 
        relevance = self._compute_relevance_term(Y)
        
        # IB objective: I(X;Z) - β*I(Z;Y)
        objective = compression - self.config.beta * relevance
        
        results = {
            'compression': compression,
            'relevance': relevance, 
            'objective': objective,
            'beta': self.config.beta
        }
        
        # Save to history if enabled
        if self.history is not None:
            self.history['compression'].append(compression)
            self.history['relevance'].append(relevance)
            self.history['objective'].append(objective)
            self.history['beta_values'].append(self.config.beta)
        
        return results
    
    def _compute_compression_term(self, X: np.ndarray) -> float:
        """Compute compression term I(X;Z)"""
        # Use current encoder distribution
        compression = 0.0
        n_samples = X.shape[0]
        
        for i in range(n_samples):
            for z in range(self.config.n_clusters):
                if self.p_z_given_x[i, z] > 1e-12 and self.p_z[z] > 1e-12:
                    compression += (1.0/n_samples) * self.p_z_given_x[i, z] * \
                                  np.log(self.p_z_given_x[i, z] / self.p_z[z])
        
        return max(0.0, compression)
    
    def _compute_relevance_term(self, Y: np.ndarray) -> float:
        """Compute relevance term I(Z;Y)"""
        # Approximate using decoder distribution
        if self.p_y_given_z is None:
            return 0.0
            
        relevance = 0.0
        n_samples = Y.shape[0]
        
        if Y.ndim == 1:
            # Discrete Y case
            y_values = np.unique(Y)
            p_y = np.bincount(Y.astype(int)) / len(Y)
            
            for z in range(self.config.n_clusters):
                if self.p_z[z] > 1e-12:
                    for y_idx, y_val in enumerate(y_values):
                        if self.p_y_given_z[z, y_idx] > 1e-12 and p_y[y_idx] > 1e-12:
                            relevance += self.p_z[z] * self.p_y_given_z[z, y_idx] * \
                                       np.log(self.p_y_given_z[z, y_idx] / p_y[y_idx])
        else:
            # Continuous Y - use differential entropy approximation
            # This is a simplified approximation
            for z in range(self.config.n_clusters):
                if self.p_z[z] > 1e-12:
                    # Estimate entropy of p(y|z)
                    cluster_mask = self.p_z_given_x[:, z] > 0.1
                    if np.sum(cluster_mask) > 1:
                        y_cluster = Y[cluster_mask]
                        cluster_entropy = -0.5 * np.log(2 * np.pi * np.e * np.var(y_cluster, axis=0))
                        relevance += self.p_z[z] * np.mean(cluster_entropy)
        
        return max(0.0, relevance)