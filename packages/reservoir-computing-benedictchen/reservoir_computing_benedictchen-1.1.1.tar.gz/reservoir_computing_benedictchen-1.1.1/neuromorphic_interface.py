"""
Neuromorphic Reservoir Computing Interface
Based on: Schliebs & Kasabov (2013) "Evolving spiking neural networks" 
and Verstraeten et al. (2007) "An experimental unification of reservoir computing methods"

This module provides interfaces to neuromorphic hardware implementations of
reservoir computing, including spiking neural networks and analog circuits.

Key implementations:
- Spiking neural network reservoirs
- Analog circuit simulation interface
- Hardware-software co-design patterns
- Event-driven processing protocols
- Spike timing dependent plasticity (STDP)
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
import math
import time
from collections import deque, defaultdict
import warnings


class NeuronModel(Enum):
    """Available neuron models for neuromorphic implementation"""
    LEAKY_INTEGRATE_FIRE = "lif"
    ADAPTIVE_EXPONENTIAL = "aex" 
    IZHIKEVICH = "izh"
    HODGKIN_HUXLEY = "hh"


class SynapseModel(Enum):
    """Available synapse models"""
    EXPONENTIAL = "exp"
    ALPHA_FUNCTION = "alpha"
    DUAL_EXPONENTIAL = "dual_exp"
    STDP = "stdp"


@dataclass 
class SpikeEvent:
    """Represents a single spike event"""
    neuron_id: int
    timestamp: float
    amplitude: float = 1.0


@dataclass
class NeuromorphicConfig:
    """Configuration for neuromorphic reservoir"""
    reservoir_size: int
    input_size: int
    output_size: int
    neuron_model: NeuronModel
    synapse_model: SynapseModel
    time_step: float
    membrane_time_constant: float
    refractory_period: float
    threshold_voltage: float
    reset_voltage: float
    resting_potential: float
    synaptic_delay_range: Tuple[float, float]
    connectivity: float


class NeuromorphicReservoir:
    """
    Neuromorphic reservoir computing system using spiking neural networks.
    
    This class implements hardware-inspired reservoir computing with
    biologically plausible spiking dynamics and temporal processing.
    """
    
    def __init__(self, config: NeuromorphicConfig):
        """
        Initialize neuromorphic reservoir.
        
        Args:
            config: Neuromorphic system configuration
        """
        self.config = config
        self.time_step = config.time_step
        self.current_time = 0.0
        
        # Initialize neuron states
        self.membrane_voltages = np.full(config.reservoir_size, config.resting_potential)
        self.refractory_timers = np.zeros(config.reservoir_size)
        self.last_spike_times = np.full(config.reservoir_size, -np.inf)
        
        # Initialize network connectivity
        self._initialize_network()
        
        # Spike history for processing
        self.spike_history = deque(maxlen=int(1.0 / config.time_step))  # 1 second history
        self.input_spikes = deque(maxlen=int(0.1 / config.time_step))   # 100ms input buffer
        
        # Output processing
        self.output_weights = None
        self.state_history = []
        
        # Hardware interface (placeholder for actual hardware)
        self.hardware_interface = None
    
    def _initialize_network(self):
        """Initialize reservoir connectivity and synaptic weights."""
        cfg = self.config
        
        # Reservoir internal connectivity (sparse random)
        reservoir_connections = int(cfg.reservoir_size * cfg.reservoir_size * cfg.connectivity)
        reservoir_i = np.random.randint(0, cfg.reservoir_size, reservoir_connections)
        reservoir_j = np.random.randint(0, cfg.reservoir_size, reservoir_connections)
        
        # Remove self-connections
        mask = reservoir_i != reservoir_j
        reservoir_i = reservoir_i[mask]
        reservoir_j = reservoir_j[mask]
        
        self.reservoir_weights = np.zeros((cfg.reservoir_size, cfg.reservoir_size))
        weights = np.random.normal(0, 1.0, len(reservoir_i))
        self.reservoir_weights[reservoir_i, reservoir_j] = weights
        
        # Input connectivity (dense to promote mixing)
        self.input_weights = np.random.normal(0, 2.0, (cfg.reservoir_size, cfg.input_size))
        
        # Synaptic delays (important for temporal dynamics)
        delay_min, delay_max = cfg.synaptic_delay_range
        self.synaptic_delays = np.random.uniform(
            delay_min, delay_max, 
            (cfg.reservoir_size, cfg.reservoir_size)
        )
        
        # STDP parameters if using plastic synapses
        if cfg.synapse_model == SynapseModel.STDP:
            self.stdp_a_plus = 0.1    # LTP amplitude
            self.stdp_a_minus = 0.12  # LTD amplitude  
            self.stdp_tau_plus = 20.0 # LTP time constant (ms)
            self.stdp_tau_minus = 20.0 # LTD time constant (ms)
    
    def _simulate_neuron_dynamics(self, neuron_idx: int, input_current: float) -> bool:
        """
        Simulate individual neuron dynamics for one time step.
        
        Args:
            neuron_idx: Index of neuron to simulate
            input_current: Input current to the neuron
            
        Returns:
            True if neuron spiked, False otherwise
        """
        cfg = self.config
        dt = self.time_step
        
        # Check refractory period
        if self.refractory_timers[neuron_idx] > 0:
            self.refractory_timers[neuron_idx] -= dt
            return False
        
        current_voltage = self.membrane_voltages[neuron_idx]
        
        if cfg.neuron_model == NeuronModel.LEAKY_INTEGRATE_FIRE:
            # Leaky integrate-and-fire dynamics
            # dV/dt = -(V - V_rest)/tau + I/C
            tau_m = cfg.membrane_time_constant
            v_rest = cfg.resting_potential
            
            dv_dt = -(current_voltage - v_rest) / tau_m + input_current
            new_voltage = current_voltage + dv_dt * dt
            
        elif cfg.neuron_model == NeuronModel.IZHIKEVICH:
            # Simplified Izhikevich model
            # Parameters for regular spiking
            a, b, c, d = 0.02, 0.2, -65.0, 8.0
            
            v = current_voltage
            # Assume recovery variable u is stored separately (simplified here)
            u = getattr(self, '_u_variables', np.zeros(cfg.reservoir_size))[neuron_idx]
            
            dv_dt = 0.04 * v**2 + 5*v + 140 - u + input_current
            du_dt = a * (b * v - u)
            
            new_voltage = v + dv_dt * dt
            new_u = u + du_dt * dt
            
            # Store recovery variable
            if not hasattr(self, '_u_variables'):
                self._u_variables = np.zeros(cfg.reservoir_size)
            self._u_variables[neuron_idx] = new_u
            
        else:
            # Default to simple LIF
            tau_m = cfg.membrane_time_constant
            v_rest = cfg.resting_potential
            dv_dt = -(current_voltage - v_rest) / tau_m + input_current
            new_voltage = current_voltage + dv_dt * dt
        
        self.membrane_voltages[neuron_idx] = new_voltage
        
        # Check for spike
        if new_voltage >= cfg.threshold_voltage:
            # Spike occurred
            self.membrane_voltages[neuron_idx] = cfg.reset_voltage
            self.refractory_timers[neuron_idx] = cfg.refractory_period
            self.last_spike_times[neuron_idx] = self.current_time
            
            # Record spike event
            spike = SpikeEvent(neuron_idx, self.current_time)
            self.spike_history.append(spike)
            
            return True
        
        return False
    
    def _compute_synaptic_current(self, neuron_idx: int) -> float:
        """Compute total synaptic current for a neuron."""
        total_current = 0.0
        
        # Process recent spikes with delays
        for spike in self.spike_history:
            if spike.neuron_id == neuron_idx:
                continue  # No self-connections
            
            # Check if spike should affect this neuron
            delay = self.synaptic_delays[neuron_idx, spike.neuron_id]
            if self.current_time - spike.timestamp >= delay:
                weight = self.reservoir_weights[neuron_idx, spike.neuron_id]
                
                # Apply synaptic dynamics
                time_since_spike = self.current_time - spike.timestamp - delay
                
                if self.config.synapse_model == SynapseModel.EXPONENTIAL:
                    # Exponential decay
                    tau_syn = 5.0  # ms
                    current_contribution = weight * np.exp(-time_since_spike / tau_syn)
                    
                elif self.config.synapse_model == SynapseModel.ALPHA_FUNCTION:
                    # Alpha function
                    tau_syn = 5.0  # ms
                    if time_since_spike >= 0:
                        current_contribution = weight * (time_since_spike / tau_syn) * np.exp(1 - time_since_spike / tau_syn)
                    else:
                        current_contribution = 0.0
                        
                else:
                    # Simple instantaneous
                    current_contribution = weight if time_since_spike < self.time_step else 0.0
                
                total_current += current_contribution
        
        return total_current
    
    def _apply_stdp(self, pre_neuron: int, post_neuron: int, dt_spike: float):
        """Apply spike-timing dependent plasticity rule."""
        if self.config.synapse_model != SynapseModel.STDP:
            return
        
        # STDP learning rule
        if dt_spike > 0:  # Pre before post (LTP)
            weight_change = self.stdp_a_plus * np.exp(-dt_spike / self.stdp_tau_plus)
        else:  # Post before pre (LTD) 
            weight_change = -self.stdp_a_minus * np.exp(dt_spike / self.stdp_tau_minus)
        
        # Apply weight change with bounds
        current_weight = self.reservoir_weights[post_neuron, pre_neuron]
        new_weight = current_weight + weight_change
        self.reservoir_weights[post_neuron, pre_neuron] = np.clip(new_weight, -5.0, 5.0)
    
    def process_input(self, input_data: np.ndarray) -> np.ndarray:
        """
        Process input through neuromorphic reservoir.
        
        Args:
            input_data: Input spike trains or analog values
            
        Returns:
            Reservoir state vector
        """
        # Convert input to spike events if necessary
        if input_data.ndim == 1:
            # Treat as instantaneous rates, convert to Poisson spikes
            input_spikes = self._rate_to_spikes(input_data)
        else:
            # Assume already spike events
            input_spikes = input_data
        
        # Store input spikes
        for i, rate in enumerate(input_spikes.flatten()):
            if rate > np.random.random():  # Poisson process
                spike = SpikeEvent(i, self.current_time)
                self.input_spikes.append(spike)
        
        # Simulate reservoir dynamics for one time step
        spikes_this_step = []
        
        for neuron_idx in range(self.config.reservoir_size):
            # Compute input current from external inputs
            input_current = 0.0
            for spike in self.input_spikes:
                if self.current_time - spike.timestamp < self.time_step:
                    weight = self.input_weights[neuron_idx, spike.neuron_id % self.config.input_size]
                    input_current += weight * spike.amplitude
            
            # Add synaptic current from other reservoir neurons
            synaptic_current = self._compute_synaptic_current(neuron_idx)
            total_current = input_current + synaptic_current
            
            # Simulate neuron dynamics
            spiked = self._simulate_neuron_dynamics(neuron_idx, total_current)
            if spiked:
                spikes_this_step.append(neuron_idx)
        
        # Apply STDP if enabled
        if self.config.synapse_model == SynapseModel.STDP:
            self._update_synaptic_weights(spikes_this_step)
        
        # Generate state vector from recent activity
        state_vector = self._compute_state_vector()
        self.state_history.append(state_vector)
        
        # Advance time
        self.current_time += self.time_step
        
        return state_vector
    
    def _rate_to_spikes(self, rates: np.ndarray) -> np.ndarray:
        """Convert firing rates to Poisson spike probabilities."""
        # Simple rate coding: rate (Hz) * time_step gives spike probability
        max_rate = 100.0  # Hz
        spike_probs = np.clip(rates * self.time_step / 1000.0 * max_rate, 0, 1)
        return spike_probs
    
    def _compute_state_vector(self) -> np.ndarray:
        """Compute reservoir state vector from recent activity."""
        # Multiple encoding methods combined
        
        # 1. Membrane voltage states
        voltage_state = (self.membrane_voltages - self.config.resting_potential) / \
                       (self.config.threshold_voltage - self.config.resting_potential)
        
        # 2. Recent spike counts (temporal window)
        window_size = int(20.0 / self.time_step)  # 20ms window
        recent_spikes = np.zeros(self.config.reservoir_size)
        
        for spike in list(self.spike_history)[-window_size:]:
            if self.current_time - spike.timestamp <= 20.0:  # 20ms
                recent_spikes[spike.neuron_id] += 1
        
        # 3. Time since last spike (normalized)
        time_since_spike = (self.current_time - self.last_spike_times) / 100.0  # Normalize by 100ms
        time_since_spike = np.clip(time_since_spike, 0, 1)
        
        # Combine different state representations
        state_vector = np.concatenate([
            voltage_state,
            recent_spikes / (window_size * self.time_step / 1000.0),  # Normalize spike counts
            1.0 - time_since_spike  # Recency encoding
        ])
        
        return state_vector
    
    def _update_synaptic_weights(self, current_spikes: List[int]):
        """Update synaptic weights using STDP."""
        if self.config.synapse_model != SynapseModel.STDP:
            return
        
        # Find recent spike pairs for STDP
        recent_window = 50.0  # ms
        
        for post_neuron in current_spikes:
            # Look for pre-synaptic spikes within STDP window
            for spike in self.spike_history:
                if self.current_time - spike.timestamp > recent_window:
                    continue
                
                pre_neuron = spike.neuron_id
                if pre_neuron == post_neuron:
                    continue
                
                # Calculate spike timing difference
                dt_spike = spike.timestamp - self.current_time  # Pre - post
                
                # Apply STDP rule
                self._apply_stdp(pre_neuron, post_neuron, dt_spike)
    
    def train_readout(self, target_outputs: np.ndarray, regularization: float = 0.01):
        """
        Train linear readout from reservoir states using ridge regression.
        
        Args:
            target_outputs: Target output sequences
            regularization: L2 regularization parameter
        """
        if len(self.state_history) == 0:
            raise ValueError("No reservoir states available for training")
        
        # Stack state vectors into matrix
        state_matrix = np.array(self.state_history)
        
        # Add bias term
        state_matrix = np.column_stack([state_matrix, np.ones(state_matrix.shape[0])])
        
        # Solve ridge regression
        I = np.eye(state_matrix.shape[1])
        I[-1, -1] = 0  # Don't regularize bias
        
        self.output_weights = np.linalg.solve(
            state_matrix.T @ state_matrix + regularization * I,
            state_matrix.T @ target_outputs
        )
    
    def predict(self, input_sequence: np.ndarray) -> np.ndarray:
        """
        Generate predictions from input sequence.
        
        Args:
            input_sequence: Sequence of input vectors
            
        Returns:
            Predicted output sequence
        """
        if self.output_weights is None:
            raise ValueError("Readout weights not trained")
        
        predictions = []
        
        for input_step in input_sequence:
            # Process input through reservoir
            state = self.process_input(input_step)
            
            # Add bias and compute output
            state_with_bias = np.append(state, 1.0)
            output = state_with_bias @ self.output_weights
            predictions.append(output)
        
        return np.array(predictions)
    
    def reset_state(self):
        """Reset reservoir to initial conditions."""
        self.current_time = 0.0
        self.membrane_voltages.fill(self.config.resting_potential)
        self.refractory_timers.fill(0.0)
        self.last_spike_times.fill(-np.inf)
        self.spike_history.clear()
        self.input_spikes.clear()
        self.state_history.clear()
        
        if hasattr(self, '_u_variables'):
            self._u_variables.fill(0.0)
    
    def get_spike_statistics(self) -> Dict[str, Any]:
        """Get statistics about spike activity."""
        if not self.spike_history:
            return {"total_spikes": 0, "firing_rate": 0.0, "active_neurons": 0}
        
        total_spikes = len(self.spike_history)
        time_window = 1.0  # 1 second window
        recent_spikes = [s for s in self.spike_history 
                        if self.current_time - s.timestamp <= time_window]
        
        firing_rate = len(recent_spikes) / (self.config.reservoir_size * time_window)
        
        active_neurons = len(set(s.neuron_id for s in recent_spikes))
        
        return {
            "total_spikes": total_spikes,
            "recent_spikes": len(recent_spikes),
            "firing_rate": firing_rate,  # Hz
            "active_neurons": active_neurons,
            "activity_ratio": active_neurons / self.config.reservoir_size
        }
    
    def enable_hardware_interface(self, hardware_type: str = "loihi"):
        """
        Enable interface to neuromorphic hardware.
        
        Args:
            hardware_type: Type of hardware ("loihi", "spinnaker", "braindrop")
        """
        # This would interface with actual neuromorphic hardware
        # For now, just a placeholder that logs the interface type
        self.hardware_interface = hardware_type
        print(f"🔌 Neuromorphic interface enabled for {hardware_type}")
        print("⚠️  Hardware interface requires actual hardware drivers")
    
    def benchmark_performance(self, test_sequence: np.ndarray) -> Dict[str, float]:
        """
        Benchmark neuromorphic reservoir performance.
        
        Args:
            test_sequence: Test input sequence
            
        Returns:
            Performance metrics dictionary
        """
        start_time = time.perf_counter()
        
        # Process test sequence
        for input_step in test_sequence:
            self.process_input(input_step)
        
        processing_time = time.perf_counter() - start_time
        
        # Calculate metrics
        steps_per_second = len(test_sequence) / processing_time
        neurons_per_second = steps_per_second * self.config.reservoir_size
        
        stats = self.get_spike_statistics()
        
        return {
            "processing_time": processing_time,
            "steps_per_second": steps_per_second,
            "neurons_per_second": neurons_per_second,
            "average_firing_rate": stats["firing_rate"],
            "network_activity": stats["activity_ratio"],
            "total_spikes": stats["total_spikes"]
        }


def create_neuromorphic_config(reservoir_size: int = 1000,
                             input_size: int = 10,
                             output_size: int = 1,
                             neuron_model: str = "lif",
                             time_step: float = 1.0) -> NeuromorphicConfig:
    """
    Create a default neuromorphic configuration.
    
    Args:
        reservoir_size: Number of neurons in reservoir
        input_size: Number of input channels
        output_size: Number of output channels  
        neuron_model: Type of neuron model
        time_step: Simulation time step in milliseconds
        
    Returns:
        NeuromorphicConfig object
    """
    return NeuromorphicConfig(
        reservoir_size=reservoir_size,
        input_size=input_size,
        output_size=output_size,
        neuron_model=NeuronModel(neuron_model),
        synapse_model=SynapseModel.EXPONENTIAL,
        time_step=time_step,
        membrane_time_constant=20.0,  # ms
        refractory_period=2.0,        # ms
        threshold_voltage=-50.0,      # mV
        reset_voltage=-70.0,          # mV
        resting_potential=-65.0,      # mV
        synaptic_delay_range=(1.0, 10.0),  # ms
        connectivity=0.1              # 10% connectivity
    )


if __name__ == "__main__":
    # Example usage and demonstration
    
    print("🧠 Neuromorphic Reservoir Computing Demo")
    print("=" * 50)
    
    # Create configuration
    config = create_neuromorphic_config(
        reservoir_size=500,
        input_size=5,
        neuron_model="lif",
        time_step=1.0  # 1ms time step
    )
    
    # Create neuromorphic reservoir
    reservoir = NeuromorphicReservoir(config)
    
    print(f"✅ Created neuromorphic reservoir:")
    print(f"   • {config.reservoir_size} neurons ({config.neuron_model.value} model)")
    print(f"   • {config.input_size} input channels")
    print(f"   • {config.time_step}ms time step")
    print(f"   • {config.connectivity:.1%} connectivity")
    
    # Generate test input sequence
    sequence_length = 1000
    test_input = np.random.rand(sequence_length, config.input_size) * 0.5
    
    print(f"\n🔄 Processing {sequence_length} time steps...")
    
    # Process input sequence
    states = []
    for i, input_step in enumerate(test_input):
        state = reservoir.process_input(input_step)
        states.append(state)
        
        if i % 200 == 0:
            stats = reservoir.get_spike_statistics()
            print(f"   Step {i}: {stats['active_neurons']} active neurons, "
                  f"{stats['firing_rate']:.1f} Hz avg firing rate")
    
    # Final statistics
    final_stats = reservoir.get_spike_statistics()
    print(f"\n📊 Final Statistics:")
    print(f"   • Total spikes: {final_stats['total_spikes']}")
    print(f"   • Average firing rate: {final_stats['firing_rate']:.2f} Hz")
    print(f"   • Active neurons: {final_stats['active_neurons']}/{config.reservoir_size}")
    print(f"   • Network activity: {final_stats['activity_ratio']:.1%}")
    
    # Benchmark performance
    print(f"\n⚡ Performance Benchmark:")
    benchmark = reservoir.benchmark_performance(test_input[:100])
    print(f"   • Processing speed: {benchmark['steps_per_second']:.0f} steps/sec")
    print(f"   • Neuron throughput: {benchmark['neurons_per_second']:.0f} neurons/sec")
    print(f"   • Total processing time: {benchmark['processing_time']:.3f} seconds")
    
    # Test training (synthetic target)
    print(f"\n🎯 Testing readout training...")
    target_output = np.sin(np.linspace(0, 4*np.pi, len(states)))[:, None]
    
    try:
        reservoir.train_readout(target_output)
        predictions = reservoir.predict(test_input[:100])
        mse = np.mean((predictions.flatten() - target_output[:100].flatten())**2)
        print(f"   • Training successful: MSE = {mse:.4f}")
    except Exception as e:
        print(f"   • Training error: {e}")
    
    # Hardware interface demo
    print(f"\n🔌 Hardware Interface Demo:")
    reservoir.enable_hardware_interface("loihi")
    
    print(f"\n✅ Neuromorphic reservoir computing demonstration complete!")