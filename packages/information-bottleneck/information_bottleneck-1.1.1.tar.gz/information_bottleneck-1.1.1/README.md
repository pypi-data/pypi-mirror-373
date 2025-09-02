# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

<div align="center">

**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)** | **[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

</div>

[![CI](https://github.com/benedictchen/information-bottleneck/workflows/CI/badge.svg)](https://github.com/benedictchen/information-bottleneck/actions)
[![PyPI version](https://badge.fury.io/py/information-bottleneck.svg)](https://badge.fury.io/py/information-bottleneck)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)
[![Research Accurate](https://img.shields.io/badge/research-accurate-brightgreen.svg)](RESEARCH_FOUNDATION.md)

---

# Information Bottleneck

🌟 **Find optimal compression-prediction tradeoffs for principled feature extraction and representation learning**

The Information Bottleneck principle provides a theoretical framework for learning representations that are maximally informative about targets while being maximally compressed. This implementation faithfully reproduces Tishby's groundbreaking information-theoretic approach to learning.

**Research Foundation**: Tishby, N., Pereira, F. C., & Bialek, W. (1999) - *"The Information Bottleneck Method"*

## 🚀 Quick Start

### Installation

```bash
pip install information-bottleneck
```

**Requirements**: Python 3.9+, NumPy, SciPy, scikit-learn, matplotlib

### Basic Information Bottleneck

```python
from information_bottleneck import InformationBottleneckClassifier
import numpy as np
from sklearn.datasets import make_classification

# Create sample data
X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)

# Basic IB for feature selection
ib_classifier = InformationBottleneckClassifier(
    beta=0.1,  # Compression-prediction tradeoff
    max_iter=1000,
    algorithm='tishby_original'
)

# Learn optimal compressed representation
print("Learning optimal information bottleneck...")
X_compressed = ib_classifier.fit_transform(X, y)
print(f"Original features: {X.shape[1]} → Compressed: {X_compressed.shape[1]}")

# Evaluate compression quality
mutual_info_xy = ib_classifier.mutual_information(X, y)
mutual_info_ty = ib_classifier.mutual_information(X_compressed, y)
compression_ratio = ib_classifier.compression_ratio()

print(f"I(X;Y): {mutual_info_xy:.3f}")
print(f"I(T;Y): {mutual_info_ty:.3f}")  
print(f"Compression ratio: {compression_ratio:.2%}")
```

### Neural Information Bottleneck

```python
from information_bottleneck import NeuralInformationBottleneck
from information_bottleneck.ib_modules import MINEEstimator
import torch

# Advanced: Neural Information Bottleneck
neural_ib = NeuralInformationBottleneck(
    encoder_layers=[512, 256, 128, 64],
    decoder_layers=[64, 128, 256, 512],
    beta_schedule='annealed',  # β increases during training
    kl_estimation='mine',      # Mutual Information Neural Estimation
    variational=True
)

# Train neural network with IB objective
neural_ib.fit(X_train, y_train, 
             validation_data=(X_val, y_val),
             epochs=100,
             batch_size=128)

# Extract learned representations
representations = neural_ib.encode(X_test)
reconstructions = neural_ib.decode(representations)

# Analyze information-theoretic properties
info_analysis = neural_ib.analyze_information_flow()
print(f"Encoder I(X;T): {info_analysis['encoder_mutual_info']:.3f}")
print(f"Decoder I(T;Y): {info_analysis['decoder_mutual_info']:.3f}")
```

### Information-Theoretic Feature Selection

```python
from information_bottleneck import IBFeatureSelector
from information_bottleneck.ib_modules import MutualInformationEstimator

# Use IB principle for feature selection
feature_selector = IBFeatureSelector(
    selection_method='information_bottleneck',
    beta_range=np.logspace(-3, 1, 20),  # Explore β values
    mi_estimator=MutualInformationEstimator(method='kraskov')
)

# Select optimal features
selected_features = feature_selector.fit_transform(X, y)
feature_importance = feature_selector.feature_importance_

print(f"Selected {selected_features.shape[1]} most informative features")
print("Top 5 features by IB importance:")
for i, importance in enumerate(feature_importance[:5]):
    print(f"  Feature {i}: {importance:.4f}")

# Visualize information-compression tradeoff
feature_selector.plot_information_curve()
```

## 🧬 Advanced Features

### Modular Architecture

```python
# Access individual IB components
from information_bottleneck.ib_modules import (
    CoreAlgorithm,              # Core IB mathematics
    CoreTheory,                 # Information-theoretic foundations
    Evaluation,                 # Performance assessment methods
    MutualInformation,          # MI estimation techniques
    NeuralInformationBottleneck, # Deep learning IB
    Optimization,               # IB optimization algorithms
    TransformPredict,           # Representation learning
    Utilities                   # Helper functions
)

# Custom IB configuration
custom_ib = CoreAlgorithm(
    compression_method='variational',
    prediction_method='deterministic',
    mi_estimation='neural',
    optimization='alternating'
)
```

### Multi-Beta Analysis

```python
from information_bottleneck import InformationBottleneckAnalysis

# Analyze IB behavior across β values
ib_analysis = InformationBottleneckAnalysis(
    beta_values=np.logspace(-4, 2, 50),
    n_repeats=10,  # Multiple random initializations
    parallel=True
)

# Generate complete IB curve
ib_curve = ib_analysis.generate_information_curve(X, y)

# Find critical β values
phase_transitions = ib_analysis.detect_phase_transitions()
optimal_beta = ib_analysis.find_optimal_beta(criterion='elbow')

print(f"Detected {len(phase_transitions)} phase transitions")
print(f"Optimal β: {optimal_beta:.4f}")

# Visualize complete analysis
ib_analysis.plot_phase_diagram()
ib_analysis.plot_representational_similarity()
```

### Deep Variational Information Bottleneck

```python
from information_bottleneck import DeepVariationalIB
import torch.nn as nn

# Create custom encoder-decoder architecture
encoder = nn.Sequential(
    nn.Linear(784, 512), nn.ReLU(),
    nn.Linear(512, 256), nn.ReLU(),
    nn.Linear(256, 128), nn.ReLU(),
    nn.Linear(128, 64)  # Bottleneck layer
)

decoder = nn.Sequential(
    nn.Linear(64, 128), nn.ReLU(),
    nn.Linear(128, 256), nn.ReLU(), 
    nn.Linear(256, 10)  # Classification head
)

# Deep VIB with custom architecture
deep_vib = DeepVariationalIB(
    encoder=encoder,
    decoder=decoder,
    latent_dim=64,
    beta=0.01,  # Start with low compression
    beta_scheduler='polynomial',
    kl_annealing=True
)

# Train with information-theoretic objective
deep_vib.fit(train_loader, val_loader, epochs=200)

# Analyze learned representations
latent_analysis = deep_vib.analyze_latent_space(test_data)
print(f"Latent space utilization: {latent_analysis['active_units']:.1%}")
print(f"Disentanglement score: {latent_analysis['disentanglement']:.3f}")
```

## 🔬 Research Foundation

### Scientific Accuracy

This implementation provides **research-accurate** reproductions of fundamental IB algorithms:

- **Mathematical Fidelity**: Exact implementation of IB Lagrangian optimization
- **Information Theory**: Rigorous mutual information estimation methods
- **Convergence Properties**: Faithful reproduction of algorithm dynamics
- **Modern Extensions**: Neural and variational IB variants

### Key Research Contributions

- **Optimal Representations**: Find representations that balance compression and prediction
- **Information-Theoretic Learning**: Principled approach to feature learning
- **Phase Transitions**: Discovery of critical points in representation learning
- **Universal Approximation**: IB as a general framework for learning

### Original Research Papers

- **Tishby, N., Pereira, F. C., & Bialek, W. (1999)**. "The Information Bottleneck Method." *Proceedings of the 37th Annual Allerton Conference*.
- **Tishby, N., & Zaslavsky, N. (2015)**. "Deep learning and the information bottleneck principle." *Information Theory Workshop (ITW)*.
- **Alemi, A., et al. (2016)**. "Deep Variational Information Bottleneck." *arXiv preprint arXiv:1612.00410*.

## 📊 Implementation Highlights

### Information-Theoretic Methods

- **MI Estimation**: KSG, MINE, binning, and kernel-based estimators
- **Optimization**: Alternating minimization, neural optimization, variational methods
- **Scalability**: Efficient algorithms for high-dimensional data
- **Convergence**: Guaranteed convergence for convex cases

### Code Quality

- **Research Accurate**: 100% faithful to original mathematical formulations
- **Modular Design**: Clean separation of estimation, optimization, and evaluation
- **Extensively Tested**: Validated against theoretical results and published benchmarks
- **Educational Value**: Clear mathematical exposition in code documentation

## 🧮 Mathematical Foundation

### Information Bottleneck Lagrangian

The IB method optimizes the following objective:

```
L = I(T;Y) - β I(T;X)
```

Where:
- `T`: Compressed representation of input `X`
- `Y`: Target variable to predict
- `β`: Lagrange multiplier controlling compression-prediction tradeoff
- `I(A;B)`: Mutual information between random variables A and B

### Self-Consistent Equations

The optimal solution satisfies:

```
p(t|x) = p(t) / Z(x,β) * exp(-β DKL[p(y|t)||p(y|x)])
p(t) = Σₓ p(x)p(t|x)  
p(y|t) = Σₓ p(y|x)p(x|t)
```

Where `DKL` is the Kullback-Leibler divergence and `Z(x,β)` is the normalization constant.

## 🎯 Use Cases & Applications

### Machine Learning Applications
- **Feature Selection**: Principled dimensionality reduction
- **Representation Learning**: Learn compressed yet predictive features  
- **Model Compression**: Reduce neural network complexity while maintaining performance
- **Transfer Learning**: Extract transferable representations across domains

### Information Theory Research
- **Rate-Distortion Theory**: Study fundamental compression limits
- **Minimal Sufficient Statistics**: Find most compressed sufficient representations
- **Phase Transitions**: Investigate critical phenomena in learning
- **Information Geometry**: Analyze geometry of probability distributions

### Neuroscience Applications  
- **Efficient Coding**: Model neural information processing principles
- **Sensory Systems**: Understand retinal and cortical processing
- **Memory Formation**: Model hippocampal compression mechanisms
- **Attention Mechanisms**: Information-theoretic models of selective attention

## 📖 Documentation & Tutorials

- 📚 **[Complete Documentation](https://information-bottleneck.readthedocs.io/)**
- 🎓 **[Tutorial Notebooks](https://github.com/benedictchen/information-bottleneck/tree/main/tutorials)**
- 🔬 **[Research Foundation](RESEARCH_FOUNDATION.md)**
- 🎯 **[Advanced Examples](https://github.com/benedictchen/information-bottleneck/tree/main/examples)**
- 🐛 **[Issue Tracker](https://github.com/benedictchen/information-bottleneck/issues)**

## 🤝 Contributing

We welcome contributions! Please see:

- **[Contributing Guidelines](CONTRIBUTING.md)**
- **[Development Setup](docs/development.md)**  
- **[Code of Conduct](CODE_OF_CONDUCT.md)**

### Development Installation

```bash
git clone https://github.com/benedictchen/information-bottleneck.git
cd information-bottleneck
pip install -e ".[test,dev]"
pytest tests/
```

## 📜 Citation

If you use this implementation in academic work, please cite:

```bibtex
@software{information_bottleneck_benedictchen,
    title={Information Bottleneck: Research-Accurate Implementation of Tishby's Framework},
    author={Benedict Chen},
    year={2025},
    url={https://github.com/benedictchen/information-bottleneck},
    version={1.1.0}
}

@inproceedings{tishby1999information,
    title={The information bottleneck method},
    author={Tishby, Naftali and Pereira, Fernando C and Bialek, William},
    booktitle={Proceedings of the 37th Annual Allerton Conference on Communication, Control, and Computing},
    pages={368--377},
    year={1999}
}
```

## 📋 License

**Custom Non-Commercial License with Donation Requirements** - See [LICENSE](LICENSE) file for details.

## 🎓 About the Implementation

**Implemented by Benedict Chen** - Bringing foundational AI research to modern Python.

📧 **Contact**: benedict@benedictchen.com  
🐙 **GitHub**: [@benedictchen](https://github.com/benedictchen)

---

## 💰 Support This Work - Choose Your Adventure!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

### 🎯 Donation Tier Goals (With Information-Theoretic Humor)

**☕ $5 - Buy Benedict Coffee**  
*"Caffeine increases my mutual information with good code! I(Benedict;Code|Coffee) > I(Benedict;Code)."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🍕 $25 - Pizza Fund**  
*"Optimal compression-nutrition tradeoff! Pizza maximizes I(Benedict;Happiness) while minimizing cooking effort."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🏠 $500,000 - Buy Benedict a House**  
*"With a whiteboard wall for drawing information-theoretic equations! My neighbors will love the entropy calculations."*  
💳 [PayPal Challenge](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**🚀 $10,000,000,000 - Space Program**  
*"To test information bottlenecks in zero gravity! Does mutual information behave differently without gravity?"*  
💳 [PayPal Cosmic](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Galactic](https://github.com/sponsors/benedictchen)

### 🎪 Monthly Subscription Tiers (GitHub Sponsors)

**🧮 Information Theorist ($10/month)** - *"Monthly support for maximum mutual information with my research!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**🤖 Neural Optimizer ($50/month)** - *"Help me optimize the β parameter of my life!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

<div align="center">

**One-time donation?**  
**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Ongoing support?**  
**[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

**Can't decide?**  
**Why not both?** 🤷‍♂️

</div>

**Every contribution maximizes I(Benedict;Motivation) while minimizing H(Financial Stress)! 🚀**

*P.S. - If you donate enough for that whiteboard wall, I'll derive the information bottleneck equations in your honor!*

---

<div align="center">

## 🌟 What the Community is Saying

</div>

---

> **@DataCompressionGuru** (847K followers) • *4 hours ago* • *(parody)*
> 
> *"OK SO HEAR ME OUT - this information bottleneck thing is basically Marie Kondo for data! 🧹 It keeps what sparks joy (the important stuff) and yeets everything else, but make it mathematical perfection! Tishby really understood the assignment when he figured out optimal compression. This is literally why your phone can recognize your face even when you look crusty in the morning - it learned the essential 'you' features while ignoring the chaos. Currently applying this to my dating app photos and the results are sending me! Quality over quantity bestie! 💅"*
> 
> **76.1K ❤️ • 12.3K 🔄 • 3.8K 💯**