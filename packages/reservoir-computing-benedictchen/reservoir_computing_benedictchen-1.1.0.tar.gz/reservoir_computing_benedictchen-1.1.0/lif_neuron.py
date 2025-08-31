"""
Leaky Integrate-and-Fire Neuron Implementation
Based on: Maass, Natschläger & Markram (2002) "Real-Time Computing Without Stable States"
"""

import numpy as np
from typing import Optional
from .lsm_config import LIFNeuronConfig, NeuronModelType


class LIFNeuron:
    """
    Configurable Leaky Integrate-and-Fire Neuron Model
    
    Now supports multiple implementation options including paper-accurate Maass 2002 parameters
    """
    
    def __init__(self, config: LIFNeuronConfig, neuron_type: str = 'E', position: Optional[np.ndarray] = None):
        self.config = config
        self.neuron_type = neuron_type
        self.position = position if position is not None else np.zeros(3)
        
        # Adjust parameters based on neuron type
        self.tau_m = config.tau_m
        if neuron_type == 'I' and config.model_type == NeuronModelType.MAASS_2002_LIF:
            self.tau_m = 20.0  # Inhibitory neurons have faster dynamics in Maass 2002
            
        self.tau_ref = config.tau_ref
        if neuron_type == 'I' and config.model_type == NeuronModelType.MAASS_2002_LIF:
            self.tau_ref = 2.0  # 2ms for inhibitory vs 3ms for excitatory
            
        # Initialize state variables
        self.v_membrane = config.v_rest
        self.refractory_time = 0.0
        self.last_spike_time = -np.inf
        
        # Synaptic currents
        self.i_syn_exc = 0.0
        self.i_syn_inh = 0.0
        
        # Adaptation current (for adaptive models)
        self.i_adaptation = 0.0
        self.tau_adaptation = 100.0  # Adaptation time constant
        self.g_adaptation = 0.1  # Adaptation conductance
        
    def update(self, dt: float, synaptic_input: float = 0.0, external_current: float = 0.0) -> bool:
        """Update neuron state and return True if spike occurred"""
        
        # Skip update if in refractory period
        if self.refractory_time > 0:
            self.refractory_time -= dt
            return False
            
        # Total input current
        total_current = (
            self.config.background_current + 
            synaptic_input + 
            external_current - 
            self.i_adaptation
        )
        
        # Add noise if configured
        if self.config.current_noise_std > 0:
            total_current += np.random.normal(0, self.config.current_noise_std)
            
        # Membrane potential update (Maass 2002 accurate)
        dv_dt = (
            -(self.v_membrane - self.config.v_rest) + 
            self.config.input_resistance * total_current
        ) / self.tau_m
        
        self.v_membrane += dv_dt * dt
        
        # Add membrane noise if configured
        if self.config.membrane_noise_std > 0:
            self.v_membrane += np.random.normal(0, self.config.membrane_noise_std * np.sqrt(dt))
            
        # Update adaptation current
        if self.config.model_type == NeuronModelType.ADAPTIVE_LIF:
            self.i_adaptation += (-self.i_adaptation / self.tau_adaptation) * dt
            
        # Check for spike
        if self.v_membrane >= self.config.v_thresh:
            # Spike occurred
            self.v_membrane = self.config.v_reset
            self.refractory_time = self.tau_ref
            self.last_spike_time = 0.0  # Relative to current time
            
            # Update adaptation for adaptive models
            if self.config.model_type == NeuronModelType.ADAPTIVE_LIF:
                self.i_adaptation += self.g_adaptation
                
            return True
            
        return False
    
    def get_membrane_potential(self) -> float:
        """Get current membrane potential"""
        return self.v_membrane
    
    def get_synaptic_current(self) -> float:
        """Get total synaptic current"""
        return self.i_syn_exc - self.i_syn_inh
    
    def reset_state(self):
        """Reset neuron to resting state"""
        self.v_membrane = self.config.v_rest
        self.refractory_time = 0.0
        self.last_spike_time = -np.inf
        self.i_syn_exc = 0.0
        self.i_syn_inh = 0.0
        self.i_adaptation = 0.0
    
    def set_position(self, position: np.ndarray):
        """Set 3D position for distance-dependent connectivity"""
        self.position = position.copy()
    
    def distance_to(self, other: 'LIFNeuron') -> float:
        """Calculate Euclidean distance to another neuron"""
        return np.linalg.norm(self.position - other.position)
    
    def is_excitatory(self) -> bool:
        """Check if neuron is excitatory"""
        return self.neuron_type == 'E'
    
    def is_inhibitory(self) -> bool:
        """Check if neuron is inhibitory"""
        return self.neuron_type == 'I'
    
    def get_state_dict(self) -> dict:
        """Get current state as dictionary for visualization/analysis"""
        return {
            'membrane_potential': self.v_membrane,
            'refractory_time': self.refractory_time,
            'last_spike_time': self.last_spike_time,
            'synaptic_exc_current': self.i_syn_exc,
            'synaptic_inh_current': self.i_syn_inh,
            'adaptation_current': self.i_adaptation,
            'neuron_type': self.neuron_type,
            'position': self.position.tolist(),
            'config': {
                'tau_m': self.tau_m,
                'tau_ref': self.tau_ref,
                'v_thresh': self.config.v_thresh,
                'v_reset': self.config.v_reset,
                'v_rest': self.config.v_rest
            }
        }


class LIFNeuronPopulation:
    """Collection of LIF neurons with efficient batch operations"""
    
    def __init__(self, n_neurons: int, config: LIFNeuronConfig, 
                 exc_ratio: float = 0.8, random_positions: bool = True):
        """
        Create population of LIF neurons
        
        Args:
            n_neurons: Number of neurons in population
            config: Neuron configuration
            exc_ratio: Ratio of excitatory neurons (0.8 = 80% excitatory)
            random_positions: Generate random 3D positions
        """
        self.n_neurons = n_neurons
        self.config = config
        self.exc_ratio = exc_ratio
        
        # Create neurons
        self.neurons = []
        n_exc = int(n_neurons * exc_ratio)
        
        for i in range(n_neurons):
            # Determine neuron type
            neuron_type = 'E' if i < n_exc else 'I'
            
            # Generate random position if requested
            if random_positions:
                # Random positions in unit cube
                position = np.random.random(3)
            else:
                position = np.zeros(3)
            
            # Create neuron
            neuron = LIFNeuron(config, neuron_type, position)
            self.neurons.append(neuron)
    
    def update_all(self, dt: float, synaptic_inputs: np.ndarray = None, 
                   external_currents: np.ndarray = None) -> np.ndarray:
        """
        Update all neurons in population
        
        Args:
            dt: Time step
            synaptic_inputs: Array of synaptic inputs for each neuron
            external_currents: Array of external currents for each neuron
            
        Returns:
            Boolean array indicating which neurons spiked
        """
        if synaptic_inputs is None:
            synaptic_inputs = np.zeros(self.n_neurons)
        if external_currents is None:
            external_currents = np.zeros(self.n_neurons)
        
        spikes = np.zeros(self.n_neurons, dtype=bool)
        
        for i, neuron in enumerate(self.neurons):
            spikes[i] = neuron.update(dt, synaptic_inputs[i], external_currents[i])
        
        return spikes
    
    def get_membrane_potentials(self) -> np.ndarray:
        """Get membrane potentials of all neurons"""
        return np.array([neuron.get_membrane_potential() for neuron in self.neurons])
    
    def get_positions(self) -> np.ndarray:
        """Get positions of all neurons as (n_neurons, 3) array"""
        return np.array([neuron.position for neuron in self.neurons])
    
    def get_neuron_types(self) -> list:
        """Get list of neuron types ('E' or 'I')"""
        return [neuron.neuron_type for neuron in self.neurons]
    
    def reset_all(self):
        """Reset all neurons to resting state"""
        for neuron in self.neurons:
            neuron.reset_state()
    
    def get_excitatory_indices(self) -> np.ndarray:
        """Get indices of excitatory neurons"""
        return np.array([i for i, neuron in enumerate(self.neurons) if neuron.is_excitatory()])
    
    def get_inhibitory_indices(self) -> np.ndarray:
        """Get indices of inhibitory neurons"""
        return np.array([i for i, neuron in enumerate(self.neurons) if neuron.is_inhibitory()])
    
    def compute_distance_matrix(self) -> np.ndarray:
        """Compute pairwise distance matrix between all neurons"""
        positions = self.get_positions()
        n = len(positions)
        distances = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i+1, n):
                dist = np.linalg.norm(positions[i] - positions[j])
                distances[i, j] = dist
                distances[j, i] = dist
        
        return distances