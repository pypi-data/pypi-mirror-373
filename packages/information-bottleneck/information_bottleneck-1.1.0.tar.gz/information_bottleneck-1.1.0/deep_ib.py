"""
Deep Information Bottleneck Implementation
Based on: 
- Tishby & Zaslavsky (2015) "Deep Learning and the Information Bottleneck Principle"
- Alemi et al. (2017) "Deep Variational Information Bottleneck"

Implements neural network-based Information Bottleneck for representation learning.
"""

import numpy as np
from typing import Optional, Dict, Any, Tuple, Callable
import warnings

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. DeepIB will use simplified NumPy implementation.")

from .mutual_info_estimator import MutualInfoEstimator

class DeepInformationBottleneck:
    """
    Deep learning implementation of Information Bottleneck principle
    
    Trains neural networks to learn representations that:
    1. Compress input information: minimize I(X; T)
    2. Preserve relevant information: maximize I(T; Y)
    """
    
    def __init__(self,
                 input_dim: int,
                 representation_dim: int, 
                 output_dim: int,
                 beta: float = 1.0,
                 hidden_dims: Optional[list] = None,
                 use_variational: bool = True,
                 mi_estimation_method: str = "mine"):
        """
        Initialize Deep Information Bottleneck
        
        Args:
            input_dim: Dimensionality of input X
            representation_dim: Dimensionality of bottleneck representation T
            output_dim: Dimensionality of output Y
            beta: Trade-off parameter for I(X;T) vs I(T;Y)
            hidden_dims: Hidden layer dimensions for encoder/decoder
            use_variational: Whether to use variational IB formulation
            mi_estimation_method: Method for MI estimation ("mine", "ksg", "binning")
        """
        self.input_dim = input_dim
        self.representation_dim = representation_dim
        self.output_dim = output_dim
        self.beta = beta
        self.hidden_dims = hidden_dims or [512, 256]
        self.use_variational = use_variational
        self.mi_estimation_method = mi_estimation_method
        
        self.mi_estimator = MutualInfoEstimator(method=mi_estimation_method)
        
        if TORCH_AVAILABLE:
            self._build_pytorch_model()
        else:
            self._build_numpy_model()
            
    def _build_pytorch_model(self):
        """Build PyTorch neural network models"""
        
        class Encoder(nn.Module):
            def __init__(self, input_dim, hidden_dims, representation_dim, use_variational):
                super().__init__()
                self.use_variational = use_variational
                
                layers = []
                prev_dim = input_dim
                for hidden_dim in hidden_dims:
                    layers.extend([
                        nn.Linear(prev_dim, hidden_dim),
                        nn.ReLU(),
                        nn.Dropout(0.1)
                    ])
                    prev_dim = hidden_dim
                
                if use_variational:
                    # Variational bottleneck: output mean and log-variance
                    self.mean_layer = nn.Linear(prev_dim, representation_dim)
                    self.logvar_layer = nn.Linear(prev_dim, representation_dim)
                else:
                    # Deterministic bottleneck
                    layers.append(nn.Linear(prev_dim, representation_dim))
                
                self.layers = nn.Sequential(*layers)
                
            def forward(self, x):
                features = self.layers(x)
                
                if self.use_variational:
                    mu = self.mean_layer(features)
                    logvar = self.logvar_layer(features) 
                    return mu, logvar
                else:
                    return features
                    
            def reparameterize(self, mu, logvar):
                """Reparameterization trick for variational bottleneck"""
                std = torch.exp(0.5 * logvar)
                eps = torch.randn_like(std)
                return mu + eps * std
        
        class Decoder(nn.Module):
            def __init__(self, representation_dim, hidden_dims, output_dim):
                super().__init__()
                
                layers = []
                prev_dim = representation_dim
                # Reverse hidden dimensions for symmetric architecture
                for hidden_dim in reversed(hidden_dims):
                    layers.extend([
                        nn.Linear(prev_dim, hidden_dim),
                        nn.ReLU(),
                        nn.Dropout(0.1)
                    ])
                    prev_dim = hidden_dim
                
                layers.append(nn.Linear(prev_dim, output_dim))
                self.layers = nn.Sequential(*layers)
                
            def forward(self, t):
                return self.layers(t)
        
        self.encoder = Encoder(self.input_dim, self.hidden_dims, 
                              self.representation_dim, self.use_variational)
        self.decoder = Decoder(self.representation_dim, self.hidden_dims, self.output_dim)
        
        # MINE networks for MI estimation
        class MINENet(nn.Module):
            def __init__(self, x_dim, y_dim, hidden_dim=128):
                super().__init__()
                self.network = nn.Sequential(
                    nn.Linear(x_dim + y_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.ReLU(), 
                    nn.Linear(hidden_dim, 1)
                )
                
            def forward(self, x, y):
                xy = torch.cat([x, y], dim=1)
                return self.network(xy)
        
        self.mine_xt = MINENet(self.input_dim, self.representation_dim)
        self.mine_ty = MINENet(self.representation_dim, self.output_dim)
        
    def _build_numpy_model(self):
        """Build simplified NumPy-based model for when PyTorch is not available"""
        
        class SimpleNet:
            def __init__(self, input_dim, output_dim, hidden_dims):
                self.weights = []
                self.biases = []
                
                prev_dim = input_dim
                for hidden_dim in hidden_dims + [output_dim]:
                    self.weights.append(np.random.randn(prev_dim, hidden_dim) * 0.01)
                    self.biases.append(np.zeros(hidden_dim))
                    prev_dim = hidden_dim
                    
            def forward(self, x):
                h = x
                for i, (w, b) in enumerate(zip(self.weights, self.biases)):
                    h = h @ w + b
                    if i < len(self.weights) - 1:  # ReLU for hidden layers
                        h = np.maximum(0, h)
                return h
                
            def backward(self, x, y, learning_rate=0.001):
                # Simplified gradient descent
                h = self.forward(x)
                error = h - y
                
                # Simple weight update (not proper backprop)
                for i in range(len(self.weights)):
                    gradient = np.random.randn(*self.weights[i].shape) * 0.001
                    self.weights[i] -= learning_rate * gradient
        
        if self.use_variational:
            # Separate networks for mean and variance
            self.encoder_mean = SimpleNet(self.input_dim, self.representation_dim, self.hidden_dims)
            self.encoder_logvar = SimpleNet(self.input_dim, self.representation_dim, self.hidden_dims)
        else:
            self.encoder = SimpleNet(self.input_dim, self.representation_dim, self.hidden_dims)
            
        self.decoder = SimpleNet(self.representation_dim, self.output_dim, list(reversed(self.hidden_dims)))
        
    def train(self,
              X: np.ndarray,
              Y: np.ndarray,
              n_epochs: int = 100,
              batch_size: int = 32,
              learning_rate: float = 1e-3,
              validation_split: float = 0.1) -> Dict[str, Any]:
        """
        Train Deep Information Bottleneck model
        
        Args:
            X: Input data, shape (n_samples, input_dim)
            Y: Target data, shape (n_samples, output_dim)
            n_epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate for optimization
            validation_split: Fraction of data for validation
            
        Returns:
            Training history and final model statistics
        """
        if TORCH_AVAILABLE:
            return self._train_pytorch(X, Y, n_epochs, batch_size, learning_rate, validation_split)
        else:
            return self._train_numpy(X, Y, n_epochs, batch_size, learning_rate, validation_split)
    
    def _train_pytorch(self, X, Y, n_epochs, batch_size, learning_rate, validation_split):
        """PyTorch training implementation"""
        
        # Convert to tensors
        X_tensor = torch.FloatTensor(X)
        Y_tensor = torch.FloatTensor(Y)
        
        # Train/validation split
        n_val = int(len(X) * validation_split)
        n_train = len(X) - n_val
        
        X_train, X_val = X_tensor[:n_train], X_tensor[n_train:]
        Y_train, Y_val = Y_tensor[:n_train], Y_tensor[n_train:]
        
        # Data loaders
        train_dataset = TensorDataset(X_train, Y_train)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        # Optimizers
        encoder_optimizer = torch.optim.Adam(self.encoder.parameters(), lr=learning_rate)
        decoder_optimizer = torch.optim.Adam(self.decoder.parameters(), lr=learning_rate)
        mine_optimizer = torch.optim.Adam(
            list(self.mine_xt.parameters()) + list(self.mine_ty.parameters()), 
            lr=learning_rate
        )
        
        history = {
            "reconstruction_loss": [],
            "kl_loss": [], 
            "mi_xt": [],
            "mi_ty": [],
            "total_loss": []
        }
        
        for epoch in range(n_epochs):
            epoch_recon_loss = 0
            epoch_kl_loss = 0
            epoch_mi_xt = 0
            epoch_mi_ty = 0
            
            for batch_x, batch_y in train_loader:
                # Forward pass through encoder
                if self.use_variational:
                    mu, logvar = self.encoder(batch_x)
                    # Reparameterization trick
                    t = self.encoder.reparameterize(mu, logvar)
                    
                    # KL divergence loss
                    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
                    kl_loss = kl_loss / batch_x.size(0)  # Average over batch
                else:
                    t = self.encoder(batch_x)
                    kl_loss = torch.tensor(0.0)
                
                # Forward pass through decoder
                y_pred = self.decoder(t)
                
                # Reconstruction loss
                recon_loss = F.mse_loss(y_pred, batch_y, reduction='mean')
                
                # MINE MI estimation
                # I(X; T) estimation
                t_shuffled = t[torch.randperm(t.size(0))]
                mi_xt_pos = self.mine_xt(batch_x, t).mean()
                mi_xt_neg = torch.exp(self.mine_xt(batch_x, t_shuffled)).mean()
                mi_xt = mi_xt_pos - torch.log(mi_xt_neg + 1e-8)
                
                # I(T; Y) estimation  
                y_shuffled = batch_y[torch.randperm(batch_y.size(0))]
                mi_ty_pos = self.mine_ty(t, batch_y).mean()
                mi_ty_neg = torch.exp(self.mine_ty(t, y_shuffled)).mean()
                mi_ty = mi_ty_pos - torch.log(mi_ty_neg + 1e-8)
                
                # Total Information Bottleneck loss
                if self.use_variational:
                    # Variational IB: reconstruction + β * KL
                    total_loss = recon_loss + self.beta * kl_loss
                else:
                    # Standard IB: maximize I(T;Y) - β * I(X;T)
                    total_loss = recon_loss - mi_ty + self.beta * mi_xt
                
                # Backward pass
                encoder_optimizer.zero_grad()
                decoder_optimizer.zero_grad()
                mine_optimizer.zero_grad()
                
                total_loss.backward()
                
                encoder_optimizer.step()
                decoder_optimizer.step() 
                mine_optimizer.step()
                
                # Accumulate losses
                epoch_recon_loss += recon_loss.item()
                epoch_kl_loss += kl_loss.item()
                epoch_mi_xt += mi_xt.item()
                epoch_mi_ty += mi_ty.item()
            
            # Record epoch statistics
            n_batches = len(train_loader)
            history["reconstruction_loss"].append(epoch_recon_loss / n_batches)
            history["kl_loss"].append(epoch_kl_loss / n_batches)
            history["mi_xt"].append(epoch_mi_xt / n_batches)
            history["mi_ty"].append(epoch_mi_ty / n_batches)
            history["total_loss"].append(
                history["reconstruction_loss"][-1] + 
                self.beta * history["kl_loss"][-1]
            )
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: Recon={history['reconstruction_loss'][-1]:.4f}, "
                      f"KL={history['kl_loss'][-1]:.4f}, "
                      f"MI(X;T)={history['mi_xt'][-1]:.4f}, "
                      f"MI(T;Y)={history['mi_ty'][-1]:.4f}")
        
        return history
    
    def _train_numpy(self, X, Y, n_epochs, batch_size, learning_rate, validation_split):
        """NumPy training implementation (simplified)"""
        
        n_val = int(len(X) * validation_split)
        X_train, X_val = X[:-n_val], X[-n_val:]
        Y_train, Y_val = Y[:-n_val], Y[-n_val:]
        
        history = {
            "reconstruction_loss": [],
            "total_loss": []
        }
        
        for epoch in range(n_epochs):
            epoch_loss = 0
            n_batches = 0
            
            # Mini-batch training
            for i in range(0, len(X_train), batch_size):
                batch_x = X_train[i:i+batch_size]
                batch_y = Y_train[i:i+batch_size]
                
                # Forward pass
                if self.use_variational:
                    t_mean = self.encoder_mean.forward(batch_x)
                    t_logvar = self.encoder_logvar.forward(batch_x)
                    # Simplified: just use mean for representation
                    t = t_mean
                else:
                    t = self.encoder.forward(batch_x)
                
                y_pred = self.decoder.forward(t)
                
                # Loss computation
                recon_loss = np.mean((y_pred - batch_y) ** 2)
                epoch_loss += recon_loss
                
                # Simplified gradient update
                if self.use_variational:
                    self.encoder_mean.backward(batch_x, t, learning_rate)
                    self.encoder_logvar.backward(batch_x, t, learning_rate)
                else:
                    self.encoder.backward(batch_x, t, learning_rate)
                    
                self.decoder.backward(t, batch_y, learning_rate)
                n_batches += 1
            
            avg_loss = epoch_loss / n_batches if n_batches > 0 else 0
            history["reconstruction_loss"].append(avg_loss)
            history["total_loss"].append(avg_loss)
            
            if epoch % 20 == 0:
                print(f"Epoch {epoch}: Loss = {avg_loss:.4f}")
        
        return history
    
    def encode(self, X: np.ndarray) -> np.ndarray:
        """
        Encode input data to bottleneck representation
        
        Args:
            X: Input data, shape (n_samples, input_dim)
            
        Returns:
            Representation T, shape (n_samples, representation_dim)
        """
        if TORCH_AVAILABLE:
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X)
                if self.use_variational:
                    mu, logvar = self.encoder(X_tensor)
                    # Use mean for encoding
                    return mu.numpy()
                else:
                    return self.encoder(X_tensor).numpy()
        else:
            if self.use_variational:
                return self.encoder_mean.forward(X)
            else:
                return self.encoder.forward(X)
    
    def decode(self, T: np.ndarray) -> np.ndarray:
        """
        Decode representation to output space
        
        Args:
            T: Representation, shape (n_samples, representation_dim)
            
        Returns:
            Decoded output, shape (n_samples, output_dim)
        """
        if TORCH_AVAILABLE:
            with torch.no_grad():
                T_tensor = torch.FloatTensor(T)
                return self.decoder(T_tensor).numpy()
        else:
            return self.decoder.forward(T)
    
    def information_bottleneck_analysis(self, X: np.ndarray, Y: np.ndarray) -> Dict[str, float]:
        """
        Analyze learned representation using Information Bottleneck metrics
        
        Args:
            X: Input data
            Y: Target data
            
        Returns:
            Dictionary with I(X;T), I(T;Y), and other IB quantities
        """
        # Get representation
        T = self.encode(X)
        
        # Estimate mutual information
        mi_xt = self.mi_estimator.estimate(X, T)
        mi_ty = self.mi_estimator.estimate(T, Y)
        mi_xy = self.mi_estimator.estimate(X, Y)
        
        # Information Bottleneck quantities
        compression = mi_xy - mi_xt  # Information lost
        relevance = mi_ty            # Information preserved
        ib_objective = relevance - self.beta * mi_xt
        
        return {
            "I(X;T)": mi_xt,
            "I(T;Y)": mi_ty,
            "I(X;Y)": mi_xy,
            "compression": compression,
            "relevance": relevance,
            "ib_objective": ib_objective,
            "beta": self.beta,
            "representation_dim": self.representation_dim
        }