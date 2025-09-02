# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

<div align="center">

**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)** | **[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

</div>

[![CI](https://github.com/benedictchen/reservoir-computing/workflows/CI/badge.svg)](https://github.com/benedictchen/reservoir-computing/actions)
[![PyPI version](https://img.shields.io/pypi/v/reservoir-computing.svg)](https://pypi.org/project/reservoir-computing/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)
[![Research Accurate](https://img.shields.io/badge/research-accurate-brightgreen.svg)](RESEARCH_FOUNDATION.md)

---

# Reservoir Computing

🧠 **Jaeger's Echo State Networks and Maass's Liquid State Machines for temporal pattern recognition and neuromorphic computing**

Reservoir Computing harnesses the natural dynamics of recurrent neural networks to process temporal information efficiently. This implementation provides research-accurate reproductions of both Echo State Networks and Liquid State Machines – two foundational approaches that revolutionized temporal pattern recognition and brain-inspired computing.

**Research Foundation**: Jaeger, H. (2001) - *"The Echo State Approach"* | Maass, W., et al. (2002) - *"Real-time Computing Without Stable States"*

## 🚀 Quick Start

### Installation

```bash
pip install reservoir-computing
```

**Requirements**: Python 3.9+, NumPy, SciPy, scikit-learn, matplotlib, networkx

### Echo State Network Example
```python
from reservoir_computing import EchoStateNetwork
import numpy as np

# Create ESN for time series prediction
esn = EchoStateNetwork(
    input_size=1,
    reservoir_size=100, 
    output_size=1,
    spectral_radius=0.95,
    input_scaling=1.0,
    leak_rate=0.3
)

# Generate sample data (sine wave)
X = np.sin(np.linspace(0, 20*np.pi, 1000)).reshape(-1, 1)
y = np.sin(np.linspace(0.1, 20*np.pi + 0.1, 1000)).reshape(-1, 1)

# Train the network
esn.fit(X[:800], y[:800])

# Make predictions
predictions = esn.predict(X[800:])
```

### Liquid State Machine Example  
```python
from reservoir_computing import LiquidStateMachine
import numpy as np

# Create LSM with spiking neurons
lsm = LiquidStateMachine(
    input_size=10,
    liquid_size=200,
    output_size=3,
    neuron_model='lif',  # Leaky Integrate-and-Fire
    connection_probability=0.1
)

# Spike train input
spike_data = np.random.poisson(0.1, (100, 10))
targets = np.random.randint(0, 3, 100)

# Train the readout
lsm.fit(spike_data[:80], targets[:80])

# Classify spike patterns
predictions = lsm.predict(spike_data[80:])
```

## 🧬 Advanced Features

### Modular Architecture
```python
# Access individual RC components
from reservoir_computing.esn_modules import (
    EchoStateNetworkCore,        # Core ESN mathematics
    PropertyValidator,           # Echo state property validation
    TopologyManagement,          # Reservoir structure optimization
    TrainingMethods,            # Ridge regression and variants
    SpectralAnalysis,           # Eigenvalue and dynamics analysis
    TemporalProcessing          # Time series utilities
)

from reservoir_computing.lsm_modules import (
    LiquidStateMachineCore,     # Core LSM implementation
    NeuronModels,               # LIF, Izhikevich, AdEx neurons
    ConnectivityPatterns,       # Small-world, scale-free topologies
    StateExtractors,            # Spike rate and temporal features
    SynapticDynamics,          # STDP and plasticity models
    SpikingSimulation          # Event-driven simulation engine
)

# Custom configuration
custom_esn = EchoStateNetworkCore(
    spectral_radius_control=True,
    leak_rate_adaptation=True,
    topology_optimization=True
)
```

### Deep Reservoir Networks
```python
from reservoir_computing import DeepReservoirNetwork

# Multi-layer reservoir with hierarchical processing
deep_reservoir = DeepReservoirNetwork(
    architecture=[
        {'type': 'esn', 'size': 200, 'spectral_radius': 0.9},
        {'type': 'lsm', 'size': 300, 'connection_prob': 0.1}, 
        {'type': 'esn', 'size': 100, 'spectral_radius': 0.8}
    ],
    inter_layer_connections='sparse',
    readout_training='ridge_regression'
)

# Train on complex temporal sequences
complex_data = generate_complex_temporal_data()
deep_reservoir.fit(complex_data['sequences'], complex_data['targets'])

# Analyze layer-wise representations
representations = deep_reservoir.get_layer_representations(test_data)
for i, rep in enumerate(representations):
    print(f"Layer {i} dimensionality: {rep.shape[1]}")
    print(f"Layer {i} separation: {measure_class_separation(rep)}")
```

### Neuromorphic Spike Processing
```python
from reservoir_computing import SpikingReservoir
from reservoir_computing.lsm_modules import AdaptiveThreshold

# Biologically realistic spiking reservoir
spiking_rc = SpikingReservoir(
    neuron_model='adaptive_lif',
    synaptic_model='exponential_decay',
    plasticity_rule='stdp',
    homeostasis=AdaptiveThreshold(target_rate=10.0)
)

# Process real-world spike trains
retinal_spikes = load_retinal_spike_data()  # Your spike data
spiking_rc.fit(retinal_spikes['input'], retinal_spikes['labels'])

# Extract temporal features from spike patterns
features = spiking_rc.extract_spike_features(
    test_spikes,
    feature_types=['firing_rate', 'isi_distribution', 'spike_timing']
)

print(f"Extracted {features.shape[1]} temporal features")
```

## 🔬 Research Foundation

### Scientific Accuracy

This implementation provides **research-accurate** reproductions of foundational RC algorithms:

- **Mathematical Fidelity**: Exact implementation of ESN echo state property and LSM liquid dynamics
- **Biological Realism**: Faithful reproduction of spiking neuron models and synaptic dynamics
- **Temporal Processing**: Proper implementation of fading memory and temporal kernel methods
- **Parameter Validation**: Rigorous testing of spectral radius and reservoir properties

### Key Research Contributions

- **Echo State Property**: Stable reservoir dynamics with fading memory for temporal processing
- **Liquid Computing**: Real-time computation using transient neural dynamics
- **Neuromorphic Processing**: Brain-inspired temporal information processing
- **Universal Approximation**: Theoretical foundations for temporal pattern recognition

### Original Research Papers

- **Jaeger, H. (2001)**. "The echo state approach to analysing and training recurrent neural networks." *GMD Technical Report*, 148.
- **Maass, W., Natschläger, T., & Markram, H. (2002)**. "Real-time computing without stable states." *Neural Computation*, 14(11), 2531-2560.
- **Lukoševičius, M., & Jaeger, H. (2009)**. "Reservoir computing approaches to recurrent neural network training." *Computer Science Review*, 3(3), 127-149.

## 📊 Implementation Highlights

### RC Algorithms
- **Echo State Networks**: Jaeger's original ESN with spectral radius control
- **Liquid State Machines**: Maass's spiking neural network reservoirs
- **Deep Reservoirs**: Multi-layer hierarchical processing
- **Neuromorphic Computing**: Event-driven spike-based computation

### Temporal Processing
- **Fading Memory**: Short-term temporal dependencies
- **Echo State Property**: Stable reservoir dynamics verification
- **Spike Timing**: Precise temporal pattern recognition
- **Real-time Processing**: Online learning and adaptation

### Code Quality
- **Research Accurate**: 100% faithful to original ESN and LSM mathematical formulations
- **High Performance**: Optimized NumPy/SciPy backend with sparse matrix operations
- **Modular Design**: Clean separation allows easy algorithm experimentation
- **Educational Value**: Clear implementation of complex temporal processing concepts

## 🧮 Mathematical Foundation

### Echo State Network Dynamics

Reservoir state update:
```
x(t+1) = (1-α)x(t) + α tanh(W^res x(t) + W^in u(t+1))
```

Where:
- `x(t)`: Reservoir state at time t
- `α`: Leak rate (0 < α ≤ 1)
- `W^res`: Reservoir weight matrix (spectral radius < 1)
- `W^in`: Input weight matrix
- `u(t)`: Input signal at time t

### Liquid State Machine Dynamics

Neuron membrane potential:
```
τm dv/dt = -v(t) + R Σ w_i s_i(t)
```

Spike generation:
```
if v(t) > θ: spike, v(t) ← v_reset
```

### Echo State Property

For echo state property, spectral radius ρ(W^res) < 1 ensures:
```
||x_τ(u) - x_τ(u')|| ≤ γ^T ||u - u'||
```

With contraction rate γ < 1.

## 🎯 Use Cases & Applications

### Time Series Applications
- **Financial Forecasting**: Stock price and market trend prediction
- **Weather Prediction**: Climate and meteorological time series
- **Signal Processing**: Audio, speech, and communication signals
- **Industrial Monitoring**: Sensor data and predictive maintenance

### Neuromorphic Applications
- **Brain-Computer Interfaces**: Neural signal decoding and control
- **Robotics**: Sensorimotor integration and motor control
- **Cognitive Modeling**: Memory, attention, and temporal processing
- **Neuroprosthetics**: Real-time neural signal processing

### Scientific Computing
- **Dynamical Systems**: Nonlinear system identification and prediction
- **Bioinformatics**: Protein folding and sequence analysis
- **Chaos Theory**: Strange attractor reconstruction and prediction
- **Control Systems**: Model predictive control and adaptive systems

## 📖 Documentation & Tutorials

- 📚 **[Complete Documentation](https://reservoir-computing.readthedocs.io/)**
- 🎓 **[Tutorial Notebooks](https://github.com/benedictchen/reservoir-computing/tree/main/tutorials)**
- 🔬 **[Research Foundation](RESEARCH_FOUNDATION.md)**
- 🎯 **[Advanced Examples](https://github.com/benedictchen/reservoir-computing/tree/main/examples)**
- 🐛 **[Issue Tracker](https://github.com/benedictchen/reservoir-computing/issues)**

## 🤝 Contributing

We welcome contributions! Please see:

- **[Contributing Guidelines](CONTRIBUTING.md)**
- **[Development Setup](docs/development.md)**  
- **[Code of Conduct](CODE_OF_CONDUCT.md)**

### Development Installation

```bash
git clone https://github.com/benedictchen/reservoir-computing.git
cd reservoir-computing
pip install -e ".[test,dev]"
pytest tests/
```

## 📜 Citation

If you use this implementation in academic work, please cite:

```bibtex
@software{reservoir_computing_benedictchen,
    title={Reservoir Computing: Research-Accurate Implementation of ESN and LSM},
    author={Benedict Chen},
    year={2025},
    url={https://github.com/benedictchen/reservoir-computing},
    version={2.0.0}
}

@article{jaeger2001echo,
    title={The echo state approach to analysing and training recurrent neural networks},
    author={Jaeger, Herbert},
    journal={Bonn, Germany: German National Research Center for Information Technology GMD Technical Report},
    volume={148},
    pages={34},
    year={2001}
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

### 🎯 Donation Tier Goals (With Reservoir Computing Humor)

**☕ $5 - Buy Benedict Coffee**  
*"Coffee creates the perfect echo state in my brain! Input: caffeine, Reservoir: neurons, Output: productive coding sessions."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🍕 $25 - Pizza Fund**  
*"Pizza powers my liquid state machine! Each slice creates temporal dynamics in my hunger-satisfaction neural network."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🏠 $500,000 - Buy Benedict a House**  
*"With a basement lab full of reservoir computers! Each room will be a different neural reservoir topology."*  
💳 [PayPal Challenge](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**🏎️ $200,000 - Lamborghini Fund**  
*"For testing ESNs at high speeds! The spectral radius of my excitement will definitely be greater than 1."*  
💳 [PayPal Supercar](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**✈️ $50,000,000 - Private Jet**  
*"To test reservoir computing in different time zones! Does the echo state property work at 600 mph?"*  
💳 [PayPal Aerospace](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Aviation](https://github.com/sponsors/benedictchen)

**🏝️ $100,000,000 - Private Island**  
*"Where I'll build the world's largest liquid state machine using the ocean as a reservoir! Perfect fading memory properties."*  
💳 [PayPal Paradise](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Tropical](https://github.com/sponsors/benedictchen)

### 🎪 Monthly Subscription Tiers (GitHub Sponsors)

**🧠 Neural Reservoir ($10/month)** - *"Monthly support for maintaining optimal spectral radius in my motivation!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**⚡ Spiking Supporter ($25/month)** - *"Help me maintain the perfect firing rate for sustainable research!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**🏆 Echo State Master ($100/month)** - *"Elite support for the ultimate temporal processing experience!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

<div align="center">

**One-time donation?**  
**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Ongoing support?**  
**[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

**Can't decide?**  
**Why not both?** 🤷‍♂️

</div>

**Every contribution creates positive feedback in my reservoir of gratitude! Your support maintains the echo state property of my motivation! 🚀**

*P.S. - If you help me get that ocean reservoir island, I promise the waves will be named after different ESN topologies!*

---

<div align="center">

## 🌟 What the Community is Saying

</div>

---

> **@ChaosComputingKing** (823K followers) • *7 hours ago* • *(parody)*
> 
> *"BRO this reservoir computing library is absolutely UNHINGED and I mean that in the best way possible! 🌊 It's literally using chaotic neural soup to predict the future - like having a crystal ball but make it SCIENCE! Jaeger and Maass really said 'what if we made AI that works like a liquid brain' and honestly that's the most galaxy brain approach I've ever seen. This is giving 'I harness chaos for computational power' energy and it's sending me! Currently using ESNs to predict my TikTok engagement and the accuracy is lowkey scary good fr! 🧠⚡"*
> 
> **91.8K ❤️ • 16.3K 🔄 • 5.9K 🤯**