"""
💧 Information Bottleneck Method - The Theory That Explains Deep Learning!
========================================================================

Author: Benedict Chen (benedict@benedictchen.com)

💝 Support This Work: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
Developing high-quality, research-backed software takes countless hours of study, implementation, 
testing, and documentation. Your support - whether a little or a LOT - makes this work possible and is 
deeply appreciated. Please consider donating based on how much this module impacts your life or work!

Based on: Naftali Tishby, Fernando C. Pereira & William Bialek (1999)
"The Information Bottleneck Method" - arXiv:physics/0004057

🎯 ELI5 Summary:
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
- Y: What we want to predict (labels, future values, etc.) 
- Z: Compressed representation (the "bottleneck")

Find the optimal Z that:
1. **Compresses X maximally**: Minimize I(X;Z) - throw away irrelevant details
2. **Preserves relevant info**: Maximize I(Z;Y) - keep predictive power

🧮 Mathematical Formulation:
============================
    
    minimize  L = I(X;Z) - β·I(Z;Y)
      over p(z|x)
    
Where:
- I(X;Z) = compression cost (bits needed to encode Z given X)
- I(Z;Y) = predictive benefit (bits of Y predictable from Z)  
- β = trade-off parameter (β→0: max compression, β→∞: max prediction)

🎨 ASCII Visualization - The Bottleneck:
=======================================

    Raw Data X ──→ │🍳 ENCODER │──→ Z ──→ │🔮 DECODER │──→ Ŷ ≈ Y
    (Complex)       │ Compress  │    ↑      │ Predict   │   (Target)
    🌊📸🎵📝        │  Wisely   │    │      │ Optimally │   
                    └───────────┘    │      └───────────┘
                                     │
                            💧 INFORMATION BOTTLENECK
                         (Keep only what matters for Y!)

🔄 The Self-Consistent Equations:
================================
The optimal solution satisfies these beautiful equations:

1. **Encoder**: p(z|x) = p(z)/Z(x,β) · exp(-β·D_KL[p(y|x)||p(y|z)])
2. **Decoder**: p(y|z) = Σ_x p(y|x)p(x|z)  
3. **Prior**: p(z) = Σ_x p(x)p(z|x)

Where D_KL is the Kullback-Leibler divergence - the "natural distortion measure"
that emerges from the principle (not assumed beforehand!).

🚀 Why This Revolutionized Deep Learning:
==========================================
┌─────────────────────┬────────────────────┬─────────────────────┐
│     Aspect          │   Before IB (1999) │   After IB (2000+)  │
├─────────────────────┼────────────────────┼─────────────────────┤
│ Why networks work   │     "Magic" 🤷     │ Information theory! │
│ Generalization      │   Mysterious       │ IB principle at work│
│ Representation      │   Trial & error    │ Principled approach │
│ Compression         │   Engineering      │ Fundamental theory  │
│ Feature learning    │   Black magic      │ Optimal relevance   │
└─────────────────────┴────────────────────┴─────────────────────┘

🧬 Modern Applications & Extensions:
====================================
- 🤖 **Variational Information Bottleneck**: Neural network implementation
- 🔄 **β-VAE**: Variational autoencoders with controllable disentanglement
- 🧠 **Deep InfoMax**: Contrastive representation learning  
- 📊 **Information-theoretic Regularization**: Better generalization
- 🎯 **Sufficient Dimensionality Reduction**: Optimal feature extraction
- 🔍 **Causal Discovery**: Finding relevant causal variables

💻 Implementation Notes:
=======================
This module provides three approaches:

1. **Classical IB**: Discrete version using the original algorithm
2. **Continuous IB**: Extension to continuous variables using KDE
3. **Neural IB**: Deep learning implementation with variational bounds

🎖️ Key Theoretical Results:
===========================
- **Phase Transitions**: As β increases, representations undergo sudden changes
- **Universal Curves**: All problems follow similar information-theoretic trajectories  
- **Optimality**: IB representations are provably optimal for prediction
- **Connection to Thermodynamics**: β acts like "inverse temperature"

🌟 This is the mathematical foundation of modern AI - beautifully elegant and powerful! 🌟
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple, Optional, Any, Callable, List
from scipy.optimize import minimize
from scipy.spatial.distance import pdist, squareform
from scipy.stats import gaussian_kde, entropy
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
import warnings
warnings.filterwarnings('ignore')


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
        print(f"   • β = {beta}")
        print(f"   • Backend: {'PyTorch' if self._use_pytorch else 'NumPy'}")
        
    def _build_networks(self):
        """Build encoder and decoder networks"""
        
        # Encoder: X → μ, σ (Gaussian latent)
        encoder_layers = []
        for i in range(len(self.encoder_dims) - 1):
            encoder_layers.append(self.nn.Linear(self.encoder_dims[i], self.encoder_dims[i+1]))
            encoder_layers.append(self.nn.ReLU())
            encoder_layers.append(self.nn.Dropout(0.1))
        
        encoder_layers.append(self.nn.Linear(self.encoder_dims[-1], 2 * self.latent_dim))  # μ, log σ
        self.encoder = self.nn.Sequential(*encoder_layers)
        
        # Decoder: Z → Y
        decoder_layers = []
        for i in range(len(self.decoder_dims) - 1):
            decoder_layers.append(self.nn.Linear(self.decoder_dims[i], self.decoder_dims[i+1]))
            if i < len(self.decoder_dims) - 2:  # No activation on output
                decoder_layers.append(self.nn.ReLU())
                decoder_layers.append(self.nn.Dropout(0.1))
        
        self.decoder = self.nn.Sequential(*decoder_layers)
        
    def _build_numpy_networks(self):
        """Build numpy-based neural networks as PyTorch alternative"""
        
        # Initialize encoder weights and biases
        self.encoder_weights = []
        self.encoder_biases = []
        
        # Encoder layers
        for i in range(len(self.encoder_dims) - 1):
            # Xavier initialization
            fan_in, fan_out = self.encoder_dims[i], self.encoder_dims[i+1]
            limit = np.sqrt(6.0 / (fan_in + fan_out))
            
            weight = np.random.uniform(-limit, limit, (fan_in, fan_out))
            bias = np.zeros(fan_out)
            
            self.encoder_weights.append(weight)
            self.encoder_biases.append(bias)
            
        # Final encoder layer for mu and log_var
        fan_in, fan_out = self.encoder_dims[-1], 2 * self.latent_dim
        limit = np.sqrt(6.0 / (fan_in + fan_out))
        
        weight = np.random.uniform(-limit, limit, (fan_in, fan_out))
        bias = np.zeros(fan_out)
        
        self.encoder_weights.append(weight)
        self.encoder_biases.append(bias)
        
        # Initialize decoder weights and biases
        self.decoder_weights = []
        self.decoder_biases = []
        
        # Decoder layers
        for i in range(len(self.decoder_dims) - 1):
            fan_in, fan_out = self.decoder_dims[i], self.decoder_dims[i+1]
            limit = np.sqrt(6.0 / (fan_in + fan_out))
            
            weight = np.random.uniform(-limit, limit, (fan_in, fan_out))
            bias = np.zeros(fan_out)
            
            self.decoder_weights.append(weight)
            self.decoder_biases.append(bias)
            
        print("✅ NumPy neural networks initialized")
        
    def _numpy_relu(self, x):
        """ReLU activation function"""
        return np.maximum(0, x)
        
    def _numpy_sigmoid(self, x):
        """Sigmoid activation function"""
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))
        
    def _numpy_forward_encoder(self, x):
        """Forward pass through numpy encoder"""
        
        hidden = x
        
        # Hidden layers with ReLU activation
        for i in range(len(self.encoder_weights) - 1):
            hidden = np.dot(hidden, self.encoder_weights[i]) + self.encoder_biases[i]
            hidden = self._numpy_relu(hidden)
            
        # Final layer (mu and log_var)
        output = np.dot(hidden, self.encoder_weights[-1]) + self.encoder_biases[-1]
        
        # Split into mu and log_var
        mu = output[:, :self.latent_dim]
        log_var = output[:, self.latent_dim:]
        
        return mu, log_var
        
    def _numpy_forward_decoder(self, z):
        """Forward pass through numpy decoder"""
        
        hidden = z
        
        # Hidden layers with ReLU activation
        for i in range(len(self.decoder_weights) - 1):
            hidden = np.dot(hidden, self.decoder_weights[i]) + self.decoder_biases[i]
            hidden = self._numpy_relu(hidden)
            
        # Final layer
        output = np.dot(hidden, self.decoder_weights[-1]) + self.decoder_biases[-1]
        
        return output
        
    def _numpy_reparameterize(self, mu, log_var):
        """Numpy version of reparameterization trick"""
        std = np.exp(0.5 * log_var)
        eps = np.random.normal(0, 1, mu.shape)
        return mu + eps * std
        
    def _numpy_kl_divergence_gaussian(self, mu, log_var):
        """Numpy version of KL divergence computation"""
        return -0.5 * np.sum(1 + log_var - mu**2 - np.exp(log_var))
        
    def _get_encoder_layer_output(self, X, layer_idx):
        """Get output of specific encoder layer for gradient computation"""
        if layer_idx < 0:
            return X
            
        hidden = X
        for i in range(layer_idx + 1):
            hidden = np.dot(hidden, self.encoder_weights[i]) + self.encoder_biases[i]
            if i < len(self.encoder_weights) - 1:  # Apply ReLU to all but last layer
                hidden = self._numpy_relu(hidden)
        
        return hidden
        
    def _reparameterize(self, mu, log_var):
        """Reparameterization trick for backpropagation through sampling"""
        std = self.torch.exp(0.5 * log_var)
        eps = self.torch.randn_like(std)
        return mu + eps * std
        
    def _kl_divergence_gaussian(self, mu, log_var):
        """KL divergence between encoder distribution and standard normal"""
        return -0.5 * self.torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        
    def fit(self, X: np.ndarray, Y: np.ndarray, epochs: int = 100, lr: float = 0.001):
        """Train Neural Information Bottleneck"""
        
        if self._use_pytorch:
            return self._fit_pytorch(X, Y, epochs, lr)
        else:
            return self._fit_numpy(X, Y, epochs, lr)
            
    def _fit_pytorch(self, X: np.ndarray, Y: np.ndarray, epochs: int, lr: float):
        """PyTorch-based training"""
        
        # Convert to tensors
        X_tensor = self.torch.FloatTensor(X)
        Y_tensor = self.torch.LongTensor(Y) if len(np.unique(Y)) < 50 else self.torch.FloatTensor(Y.reshape(-1, 1))
        
        # Setup optimizer
        optimizer = self.optim.Adam(list(self.encoder.parameters()) + list(self.decoder.parameters()), lr=lr)
        
        # Loss function
        if len(np.unique(Y)) < 50:  # Classification
            criterion = self.nn.CrossEntropyLoss()
        else:  # Regression
            criterion = self.nn.MSELoss()
        
        print(f"🎯 Training Neural IB for {epochs} epochs...")
        
        for epoch in range(epochs):
            optimizer.zero_grad()
            
            # Forward pass
            encoded = self.encoder(X_tensor)
            mu, log_var = encoded[:, :self.latent_dim], encoded[:, self.latent_dim:]
            
            # Sample latent representation
            z = self._reparameterize(mu, log_var)
            
            # Decode
            decoded = self.decoder(z)
            
            # Compute losses
            reconstruction_loss = criterion(decoded, Y_tensor)
            kl_loss = self._kl_divergence_gaussian(mu, log_var) / len(X)
            
            # Information Bottleneck objective
            total_loss = reconstruction_loss + self.beta * kl_loss
            
            # Backward pass
            total_loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 20 == 0:
                print(f"   Epoch {epoch+1}: Total={total_loss:.4f}, Recon={reconstruction_loss:.4f}, KL={kl_loss:.4f}")
        
        print("✅ Neural Information Bottleneck training complete!")
        
    def _fit_numpy(self, X: np.ndarray, Y: np.ndarray, epochs: int, lr: float):
        """NumPy-based training with gradient descent"""
        
        print(f"🎯 Training NumPy Neural IB for {epochs} epochs...")
        
        n_samples = X.shape[0]
        
        for epoch in range(epochs):
            # Forward pass
            mu, log_var = self._numpy_forward_encoder(X)
            z = self._numpy_reparameterize(mu, log_var)
            y_pred = self._numpy_forward_decoder(z)
            
            # Compute losses
            if len(np.unique(Y)) < 50:  # Classification - use cross-entropy
                # Softmax
                exp_scores = np.exp(y_pred - np.max(y_pred, axis=1, keepdims=True))
                probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)
                
                # Cross-entropy loss
                Y_one_hot = np.eye(y_pred.shape[1])[Y.astype(int)]
                reconstruction_loss = -np.sum(Y_one_hot * np.log(probs + 1e-10)) / n_samples
            else:  # Regression - use MSE
                reconstruction_loss = np.mean((y_pred - Y.reshape(-1, 1))**2)
                
            kl_loss = self._numpy_kl_divergence_gaussian(mu, log_var) / n_samples
            
            # Information Bottleneck objective
            total_loss = reconstruction_loss + self.beta * kl_loss
            
            # FIXME: FAKE CODE REPLACED - This was just demo code with no actual learning!
            # Real gradient computation and backpropagation for numpy neural network
            
            # Compute gradients manually for each layer (real implementation)
            batch_size = X.shape[0]
            
            # === BACKWARD PASS - DECODER GRADIENTS ===
            if len(np.unique(Y)) < 50:  # Classification
                # Gradient of cross-entropy loss w.r.t. decoder output
                Y_one_hot = np.eye(y_pred.shape[1])[Y.astype(int)]
                grad_output = (probs - Y_one_hot) / batch_size
            else:  # Regression 
                grad_output = 2 * (y_pred - Y.reshape(-1, 1)) / batch_size
            
            # Backpropagate through decoder layers
            grad_z = grad_output
            for i in reversed(range(len(self.decoder_weights))):
                if i == len(self.decoder_weights) - 1:
                    # Output layer
                    grad_w = np.dot(z.T, grad_z)
                    grad_b = np.sum(grad_z, axis=0)
                    next_grad = np.dot(grad_z, self.decoder_weights[i].T)
                else:
                    # Hidden layer with ReLU
                    hidden_layer = np.dot(z, self.decoder_weights[i]) + self.decoder_biases[i]
                    relu_mask = (hidden_layer > 0).astype(float)
                    grad_z = grad_z * relu_mask
                    
                    grad_w = np.dot(z.T, grad_z)
                    grad_b = np.sum(grad_z, axis=0)
                    if i > 0:
                        next_grad = np.dot(grad_z, self.decoder_weights[i].T)
                
                # Update decoder weights with gradient descent
                self.decoder_weights[i] -= lr * grad_w
                self.decoder_biases[i] -= lr * grad_b
                
                if i > 0:
                    grad_z = next_grad
            
            # === BACKWARD PASS - ENCODER GRADIENTS ===
            # Gradient from reconstruction loss (through z)
            grad_z_recon = next_grad if 'next_grad' in locals() else np.dot(grad_output, self.decoder_weights[0].T)
            
            # Gradient from KL divergence
            grad_mu_kl = mu * self.beta / batch_size
            grad_logvar_kl = (np.exp(log_var) - 1) * self.beta / (2 * batch_size)
            
            # Total gradients for latent variables
            grad_mu = grad_z_recon + grad_mu_kl
            grad_logvar = grad_logvar_kl
            
            # Combine mu and log_var gradients
            grad_encoder_output = np.concatenate([grad_mu, grad_logvar], axis=1)
            
            # Backpropagate through encoder layers
            grad_hidden = grad_encoder_output
            for i in reversed(range(len(self.encoder_weights))):
                if i == len(self.encoder_weights) - 1:
                    # Final encoder layer (no activation)
                    prev_layer = self._get_encoder_layer_output(X, i-1) if i > 0 else X
                    grad_w = np.dot(prev_layer.T, grad_hidden)
                    grad_b = np.sum(grad_hidden, axis=0)
                    if i > 0:
                        next_grad = np.dot(grad_hidden, self.encoder_weights[i].T)
                else:
                    # Hidden layers with ReLU
                    prev_layer = self._get_encoder_layer_output(X, i-1) if i > 0 else X
                    current_layer = np.dot(prev_layer, self.encoder_weights[i]) + self.encoder_biases[i]
                    relu_mask = (current_layer > 0).astype(float)
                    grad_hidden = grad_hidden * relu_mask
                    
                    grad_w = np.dot(prev_layer.T, grad_hidden)
                    grad_b = np.sum(grad_hidden, axis=0)
                    if i > 0:
                        next_grad = np.dot(grad_hidden, self.encoder_weights[i].T)
                
                # Update encoder weights
                self.encoder_weights[i] -= lr * grad_w
                self.encoder_biases[i] -= lr * grad_b
                
                if i > 0:
                    grad_hidden = next_grad
            
            if (epoch + 1) % 20 == 0:
                print(f"   Epoch {epoch+1}: Total={total_loss:.4f}, Recon={reconstruction_loss:.4f}, KL={kl_loss:.4f}")
                
        print("✅ NumPy Information Bottleneck training complete!")
        
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform data to latent representation"""
        
        if self._use_pytorch:
            return self._transform_pytorch(X)
        else:
            return self._transform_numpy(X)
            
    def _transform_pytorch(self, X: np.ndarray) -> np.ndarray:
        """PyTorch-based transformation"""
        with self.torch.no_grad():
            X_tensor = self.torch.FloatTensor(X)
            encoded = self.encoder(X_tensor)
            mu = encoded[:, :self.latent_dim]
            return mu.numpy()
            
    def _transform_numpy(self, X: np.ndarray) -> np.ndarray:
        """NumPy-based transformation"""
        mu, log_var = self._numpy_forward_encoder(X)
        return mu  # Return mean of latent distribution
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        z = self.transform(X)
        
        if self._use_pytorch:
            with self.torch.no_grad():
                z_tensor = self.torch.FloatTensor(z)
                predictions = self.decoder(z_tensor)
                return predictions.numpy()
        else:
            return self._numpy_forward_decoder(z)


