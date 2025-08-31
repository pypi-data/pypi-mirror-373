# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

[![CI](https://github.com/benedictchen/universal-learning/workflows/CI/badge.svg)](https://github.com/benedictchen/universal-learning/actions)
[![PyPI version](https://badge.fury.io/py/universal-learning.svg)](https://badge.fury.io/py/universal-learning)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)

---

# Universal Learning

🧠 AIXI theoretical framework

**Hutter, M. (2005) - "Universal Artificial Intelligence"**

## 📦 Installation

```bash
pip install universal-learning
```

## 🚀 Quick Start

```python
import universal_learning
import numpy as np

# Create universal learner
learner = universal_learning.UniversalLearner(
    alphabet_size=2,
    max_program_length=100
)

# Simple binary sequence learning
sequence = [0, 1, 0, 1, 0, 1]  # Alternating pattern

# Learn from sequence
learner.observe_sequence(sequence)

# Predict next symbols
prediction = learner.predict_next(sequence[-3:])
print(f"✅ Predicted next symbol: {prediction.symbol}")
print(f"✅ Confidence: {prediction.probability:.4f}")

# Use Solomonoff induction directly
inductor = universal_learning.SolomonoffInductor()
inductor.update(sequence)
next_prob = inductor.predict_next()
print(f"✅ Solomonoff prediction probabilities: {next_prob}")
```

## 🎓 About the Implementation

Implemented by **Benedict Chen** - bringing foundational AI research to modern Python.

📧 Contact: benedict@benedictchen.com

## 📖 Citation

If you use this implementation in your research, please cite the original paper:

```bibtex
Hutter, M. (2005) - "Universal Artificial Intelligence"
```

## 📜 License

Custom Non-Commercial License with Donation Requirements - See LICENSE file for details.

---

## 💰 Support This Work - Donation Appreciated!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Your support helps maintain and expand these research implementations! 🙏**