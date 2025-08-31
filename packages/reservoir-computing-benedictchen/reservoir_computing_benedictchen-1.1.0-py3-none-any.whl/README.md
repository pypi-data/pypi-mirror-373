# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

[![CI](https://github.com/benedictchen/reservoir-computing-benedictchen/workflows/CI/badge.svg)](https://github.com/benedictchen/reservoir-computing-benedictchen/actions)
[![PyPI version](https://badge.fury.io/py/reservoir-computing-benedictchen.svg)](https://badge.fury.io/py/reservoir-computing-benedictchen)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)

---

# Reservoir Computing

🌊 Echo State Networks & Liquid State Machines

**Jaeger, H. (2001) & Maass, W. (2002) - Reservoir Computing foundations**

## 📦 Installation

```bash
pip install reservoir-computing-benedictchen
```

## 🚀 Quick Start

```python
import reservoir_computing_benedictchen
import numpy as np

# Create Echo State Network
esn = reservoir_computing_benedictchen.EchoStateNetwork(
    reservoir_size=100,
    input_size=3,
    output_size=1,
    spectral_radius=0.95
)

# Generate sample temporal data
time_steps = 1000
X = np.random.randn(time_steps, 3)  # Input sequences
y = np.sin(np.arange(time_steps) * 0.1)[:, np.newaxis]  # Target

# Train the network
esn.train(X, y)

# Make predictions
predictions = esn.predict(X[:100])
print(f"✅ ESN prediction shape: {predictions.shape}")

# Create Liquid State Machine  
lsm = reservoir_computing_benedictchen.create_lsm_with_presets(
    'temporal_pattern_recognition'
)

# Process spike trains
spike_train = np.random.poisson(0.1, (100, 50))  # 100 time steps, 50 inputs
liquid_states = lsm.process(spike_train)
print(f"✅ LSM liquid states: {liquid_states.shape}")
```

## 🎓 About the Implementation

Implemented by **Benedict Chen** - bringing foundational AI research to modern Python.

📧 Contact: benedict@benedictchen.com

## 📖 Citation

If you use this implementation in your research, please cite the original paper:

```bibtex
Jaeger, H. (2001) & Maass, W. (2002) - Reservoir Computing foundations
```

## 📜 License

Custom Non-Commercial License with Donation Requirements - See LICENSE file for details.

---

## 💰 Support This Work - Donation Appreciated!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Your support helps maintain and expand these research implementations! 🙏**