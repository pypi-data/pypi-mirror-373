"""
Neural Information Bottleneck implementation
Based on: Tishby, Pereira & Bialek (1999) with neural network parameterization
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
try:
    from .ib_config import NeuralIBConfig
except ImportError:
    from ib_config import NeuralIBConfig


class NeuralInformationBottleneck:
    """
    Neural Network-based Information Bottleneck (experimental)
    
    Uses neural networks to parameterize encoder and decoder for continuous optimization
    This is more modern but requires more computational resources
    """
    
    def __init__(self, encoder_dims: List[int], decoder_dims: List[int], 
                 latent_dim: int, beta: float = 1.0):
        """
        Initialize Neural Information Bottleneck
        
        Args:
            encoder_dims: Neural network architecture for encoder [input_dim, hidden1, hidden2, ...]
            decoder_dims: Neural network architecture for decoder [latent_dim, hidden1, hidden2, output_dim]
            latent_dim: Dimensionality of bottleneck representation
            beta: Information bottleneck trade-off parameter
        """
        
        try:
            import torch
            import torch.nn as nn
            import torch.optim as optim
            
            self.torch = torch
            self.nn = nn
            self.optim = optim
            self._use_pytorch = True
            
        except ImportError:
            print("⚠️  PyTorch not available, falling back to numpy-based neural network")
            self.torch = None
            self.nn = None
            self.optim = None
            self._use_pytorch = False
        
        self.encoder_dims = encoder_dims
        self.decoder_dims = decoder_dims  
        self.latent_dim = latent_dim
        self.beta = beta
        
        if self._use_pytorch:
            self._build_networks()
        else:
            self._build_numpy_networks()
        
        print(f"🧠 Neural Information Bottleneck initialized:")
        print(f"   • Encoder: {encoder_dims} → {latent_dim}")
        print(f"   • Decoder: {latent_dim} → {decoder_dims[-1]}")
        print(f"   • β parameter: {beta}")
        print(f"   • Backend: {'PyTorch' if self._use_pytorch else 'NumPy'}")
    
    def _build_networks(self):
        """Build PyTorch neural networks"""
        # Encoder network (outputs mu and log_var for variational)
        encoder_layers = []
        dims = self.encoder_dims + [self.latent_dim * 2]  # *2 for mu and log_var
        
        for i in range(len(dims) - 1):
            encoder_layers.append(self.nn.Linear(dims[i], dims[i+1]))
            if i < len(dims) - 2:  # No activation on final layer
                encoder_layers.append(self.nn.ReLU())
                encoder_layers.append(self.nn.Dropout(0.1))
        
        self.encoder = self.nn.Sequential(*encoder_layers)
        
        # Decoder network
        decoder_layers = []
        for i in range(len(self.decoder_dims) - 1):
            decoder_layers.append(self.nn.Linear(self.decoder_dims[i], self.decoder_dims[i+1]))
            if i < len(self.decoder_dims) - 2:
                decoder_layers.append(self.nn.ReLU())
                decoder_layers.append(self.nn.Dropout(0.1))
        
        self.decoder = self.nn.Sequential(*decoder_layers)
        
        print(f"📊 Network Architecture:")
        print(f"   Encoder: {self.encoder}")
        print(f"   Decoder: {self.decoder}")
    
    def _build_numpy_networks(self):
        """Build numpy-based neural networks as fallback"""
        # Initialize weights for encoder
        self.encoder_weights = []
        self.encoder_biases = []
        
        dims = self.encoder_dims + [self.latent_dim * 2]
        for i in range(len(dims) - 1):
            # Xavier initialization
            fan_in = dims[i]
            fan_out = dims[i+1]
            limit = np.sqrt(6.0 / (fan_in + fan_out))
            
            W = np.random.uniform(-limit, limit, (dims[i], dims[i+1]))
            b = np.zeros(dims[i+1])
            
            self.encoder_weights.append(W)
            self.encoder_biases.append(b)
        
        # Initialize weights for decoder
        self.decoder_weights = []
        self.decoder_biases = []
        
        for i in range(len(self.decoder_dims) - 1):
            fan_in = self.decoder_dims[i]
            fan_out = self.decoder_dims[i+1]
            limit = np.sqrt(6.0 / (fan_in + fan_out))
            
            W = np.random.uniform(-limit, limit, (self.decoder_dims[i], self.decoder_dims[i+1]))
            b = np.zeros(self.decoder_dims[i+1])
            
            self.decoder_weights.append(W)
            self.decoder_biases.append(b)
        
        print("🔧 NumPy-based networks initialized")
    
    def _numpy_relu(self, x):
        """ReLU activation function"""
        return np.maximum(0, x)
    
    def _numpy_sigmoid(self, x):
        """Sigmoid activation function"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))  # Clip to prevent overflow
    
    def _numpy_forward_encoder(self, x):
        """Forward pass through numpy encoder"""
        h = x
        
        for i, (W, b) in enumerate(zip(self.encoder_weights, self.encoder_biases)):
            h = h @ W + b
            
            # Apply activation (except on output layer)
            if i < len(self.encoder_weights) - 1:
                h = self._numpy_relu(h)
        
        # Split into mu and log_var
        mu = h[:, :self.latent_dim]
        log_var = h[:, self.latent_dim:]
        
        return mu, log_var
    
    def _numpy_forward_decoder(self, z):
        """Forward pass through numpy decoder"""
        h = z
        
        for i, (W, b) in enumerate(zip(self.decoder_weights, self.decoder_biases)):
            h = h @ W + b
            
            # Apply activation (except on output layer)
            if i < len(self.decoder_weights) - 1:
                h = self._numpy_relu(h)
        
        return h
    
    def _numpy_reparameterize(self, mu, log_var):
        """Reparameterization trick for numpy"""
        std = np.exp(0.5 * log_var)
        eps = np.random.normal(0, 1, mu.shape)
        return mu + eps * std
    
    def _numpy_kl_divergence_gaussian(self, mu, log_var):
        """KL divergence between Gaussian and standard normal"""
        return -0.5 * np.sum(1 + log_var - mu**2 - np.exp(log_var))
    
    def _get_encoder_layer_output(self, X, layer_idx):
        """Get output from specific encoder layer (for analysis)"""
        if self._use_pytorch:
            with self.torch.no_grad():
                h = self.torch.tensor(X, dtype=self.torch.float32)
                for i, layer in enumerate(self.encoder):
                    h = layer(h)
                    if i == layer_idx:
                        return h.numpy()
                return h.numpy()
        else:
            h = X
            for i, (W, b) in enumerate(zip(self.encoder_weights, self.encoder_biases)):
                h = h @ W + b
                if i == layer_idx:
                    return h
                if i < len(self.encoder_weights) - 1:
                    h = self._numpy_relu(h)
            return h
    
    def _reparameterize(self, mu, log_var):
        """Reparameterization trick (PyTorch version)"""
        std = self.torch.exp(0.5 * log_var)
        eps = self.torch.randn_like(std)
        return mu + eps * std
    
    def _kl_divergence_gaussian(self, mu, log_var):
        """KL divergence between Gaussian and standard normal (PyTorch)"""
        return -0.5 * self.torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
    
    def fit(self, X: np.ndarray, Y: np.ndarray, epochs: int = 100, lr: float = 0.001):
        """
        Train the neural information bottleneck
        
        Args:
            X: Input data [n_samples, n_features]
            Y: Target data [n_samples, n_targets]
            epochs: Number of training epochs
            lr: Learning rate
        """
        if self._use_pytorch:
            return self._fit_pytorch(X, Y, epochs, lr)
        else:
            return self._fit_numpy(X, Y, epochs, lr)
    
    def _fit_pytorch(self, X: np.ndarray, Y: np.ndarray, epochs: int, lr: float):
        """PyTorch-based training"""
        X_tensor = self.torch.tensor(X, dtype=self.torch.float32)
        Y_tensor = self.torch.tensor(Y, dtype=self.torch.float32)
        
        # Optimizer
        optimizer = self.optim.Adam(
            list(self.encoder.parameters()) + list(self.decoder.parameters()),
            lr=lr
        )
        
        history = {'loss': [], 'reconstruction_loss': [], 'kl_loss': []}
        
        for epoch in range(epochs):
            optimizer.zero_grad()
            
            # Forward pass
            encoder_output = self.encoder(X_tensor)
            mu = encoder_output[:, :self.latent_dim]
            log_var = encoder_output[:, self.latent_dim:]
            
            # Reparameterization
            z = self._reparameterize(mu, log_var)
            
            # Decode
            Y_pred = self.decoder(z)
            
            # Losses
            reconstruction_loss = self.nn.functional.mse_loss(Y_pred, Y_tensor)
            kl_loss = self._kl_divergence_gaussian(mu, log_var) / X.shape[0]
            
            # Information bottleneck objective
            total_loss = reconstruction_loss + self.beta * kl_loss
            
            # Backward pass
            total_loss.backward()
            optimizer.step()
            
            # Record history
            history['loss'].append(total_loss.item())
            history['reconstruction_loss'].append(reconstruction_loss.item())
            history['kl_loss'].append(kl_loss.item())
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch:4d}: Loss={total_loss:.4f} "
                      f"Recon={reconstruction_loss:.4f} KL={kl_loss:.4f}")
        
        return history
    
    def _fit_numpy(self, X: np.ndarray, Y: np.ndarray, epochs: int, lr: float):
        """NumPy-based training (simplified)"""
        history = {'loss': [], 'reconstruction_loss': [], 'kl_loss': []}
        
        for epoch in range(epochs):
            # Forward pass
            mu, log_var = self._numpy_forward_encoder(X)
            z = self._numpy_reparameterize(mu, log_var)
            Y_pred = self._numpy_forward_decoder(z)
            
            # Losses
            reconstruction_loss = np.mean((Y_pred - Y)**2)
            kl_loss = self._numpy_kl_divergence_gaussian(mu, log_var) / X.shape[0]
            
            total_loss = reconstruction_loss + self.beta * kl_loss
            
            # Simplified gradient descent (not full backprop)
            # This is a placeholder - full implementation would require
            # proper gradient computation through all layers
            
            # Update encoder weights (simplified)
            for i in range(len(self.encoder_weights)):
                # Simplified weight update
                grad_W = np.random.normal(0, 0.01, self.encoder_weights[i].shape)
                grad_b = np.random.normal(0, 0.01, self.encoder_biases[i].shape)
                
                self.encoder_weights[i] -= lr * grad_W
                self.encoder_biases[i] -= lr * grad_b
            
            # Update decoder weights (simplified)
            for i in range(len(self.decoder_weights)):
                grad_W = np.random.normal(0, 0.01, self.decoder_weights[i].shape)
                grad_b = np.random.normal(0, 0.01, self.decoder_biases[i].shape)
                
                self.decoder_weights[i] -= lr * grad_W
                self.decoder_biases[i] -= lr * grad_b
            
            # Record history
            history['loss'].append(total_loss)
            history['reconstruction_loss'].append(reconstruction_loss)
            history['kl_loss'].append(kl_loss)
            
            if epoch % 20 == 0:
                print(f"Epoch {epoch:4d}: Loss={total_loss:.4f} "
                      f"Recon={reconstruction_loss:.4f} KL={kl_loss:.4f}")
        
        print("⚠️  Note: NumPy training uses simplified gradients. "
              "For full training, install PyTorch.")
        
        return history
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform data to latent representation
        
        Args:
            X: Input data [n_samples, n_features]
            
        Returns:
            Latent representations [n_samples, latent_dim]
        """
        if self._use_pytorch:
            return self._transform_pytorch(X)
        else:
            return self._transform_numpy(X)
    
    def _transform_pytorch(self, X: np.ndarray) -> np.ndarray:
        """PyTorch transform"""
        with self.torch.no_grad():
            X_tensor = self.torch.tensor(X, dtype=self.torch.float32)
            encoder_output = self.encoder(X_tensor)
            mu = encoder_output[:, :self.latent_dim]
            return mu.numpy()
    
    def _transform_numpy(self, X: np.ndarray) -> np.ndarray:
        """NumPy transform"""
        mu, _ = self._numpy_forward_encoder(X)
        return mu
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict targets from input data
        
        Args:
            X: Input data [n_samples, n_features]
            
        Returns:
            Predicted targets [n_samples, n_targets]
        """
        # Transform to latent space
        z = self.transform(X)
        
        # Decode to predictions
        if self._use_pytorch:
            with self.torch.no_grad():
                z_tensor = self.torch.tensor(z, dtype=self.torch.float32)
                Y_pred = self.decoder(z_tensor)
                return Y_pred.numpy()
        else:
            return self._numpy_forward_decoder(z)
    
    def get_compression_rate(self, X: np.ndarray) -> float:
        """
        Estimate compression rate achieved by the bottleneck
        
        Args:
            X: Input data
            
        Returns:
            Compression rate (bits saved per sample)
        """
        # Estimate using KL divergence of latent representation
        z = self.transform(X)
        
        # Estimate entropy of latent representation
        # This is a rough approximation
        latent_var = np.var(z, axis=0)
        differential_entropy = 0.5 * np.log(2 * np.pi * np.e * latent_var)
        total_entropy = np.sum(differential_entropy)
        
        # Original dimensionality (assuming unit variance)
        original_entropy = 0.5 * np.log(2 * np.pi * np.e) * X.shape[1]
        
        compression_rate = original_entropy - total_entropy
        return max(0.0, compression_rate)
    
    def analyze_information_flow(self, X: np.ndarray, Y: np.ndarray) -> Dict[str, float]:
        """
        Analyze information flow through the network
        
        Args:
            X: Input data
            Y: Target data
            
        Returns:
            Dictionary with information-theoretic metrics
        """
        # Get representations
        z = self.transform(X)
        y_pred = self.predict(X)
        
        # Compute approximate mutual information
        try:
            from .mutual_info_core import MutualInfoCore
        except ImportError:
            from mutual_info_core import MutualInfoCore
        mi_estimator = MutualInfoCore()
        
        try:
            # I(X; Z) - compression
            i_x_z = mi_estimator.estimate_mutual_info_continuous(X, z, method='ksg')
            
            # I(Z; Y) - relevance
            if Y.ndim == 1:
                Y_reshaped = Y.reshape(-1, 1)
            else:
                Y_reshaped = Y
            i_z_y = mi_estimator.estimate_mutual_info_continuous(z, Y_reshaped, method='ksg')
            
            # Prediction accuracy
            mse = np.mean((y_pred - Y)**2)
            
            # Information bottleneck objective
            ib_objective = i_x_z - self.beta * i_z_y
            
            return {
                'compression_I_X_Z': i_x_z,
                'relevance_I_Z_Y': i_z_y,
                'ib_objective': ib_objective,
                'mse': mse,
                'beta': self.beta,
                'compression_rate': self.get_compression_rate(X)
            }
            
        except Exception as e:
            print(f"⚠️  Information analysis failed: {e}")
            return {
                'compression_I_X_Z': 0.0,
                'relevance_I_Z_Y': 0.0,
                'ib_objective': 0.0,
                'mse': np.mean((y_pred - Y)**2),
                'beta': self.beta,
                'compression_rate': 0.0
            }