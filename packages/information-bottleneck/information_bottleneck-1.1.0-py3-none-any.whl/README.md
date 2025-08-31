# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

[![CI](https://github.com/benedictchen/information-bottleneck/workflows/CI/badge.svg)](https://github.com/benedictchen/information-bottleneck/actions)
[![PyPI version](https://badge.fury.io/py/information-bottleneck.svg)](https://badge.fury.io/py/information-bottleneck)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)

---

# Information Bottleneck

🌟 Optimal compression-prediction tradeoffs for principled feature extraction

**Tishby, N., Pereira, F. C., & Bialek, W. (1999) - "The Information Bottleneck Method"**

## 📦 Installation

```bash
pip install information-bottleneck
```

## 🚀 Quick Start

```python
import information_bottleneck
import numpy as np

# Create sample data
X = np.random.randn(1000, 20)  # Input data
Y = np.random.randint(0, 3, 1000)  # Target labels

# Create Information Bottleneck
ib = information_bottleneck.create_information_bottleneck(
    method='discrete',
    beta=1.0
)

# Fit the model
ib.fit(X, Y)

# Get compressed representations
compressed = ib.transform(X)
print(f"✅ Compressed {X.shape} → {compressed.shape}")
```

## 🎓 About the Implementation

Implemented by **Benedict Chen** - bringing foundational AI research to modern Python.

📧 Contact: benedict@benedictchen.com

## 📖 Citation

If you use this implementation in your research, please cite the original paper:

```bibtex
Tishby, N., Pereira, F. C., & Bialek, W. (1999) - "The Information Bottleneck Method"
```

## 📜 License

Custom Non-Commercial License with Donation Requirements - See LICENSE file for details.

---

## 💰 Support This Work - Donation Appreciated!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Your support helps maintain and expand these research implementations! 🙏**