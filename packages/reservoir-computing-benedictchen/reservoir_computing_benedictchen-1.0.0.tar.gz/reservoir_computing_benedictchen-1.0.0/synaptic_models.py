"""
Synaptic Models for Liquid State Machine
Based on: Maass, Natschläger & Markram (2002) "Real-Time Computing Without Stable States"
"""

import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from .lsm_config import SynapseModelType, ConnectivityType, DynamicSynapseConfig


class DynamicSynapse:
    """
    Dynamic synapse model implementing Tsodyks-Markram short-term plasticity
    
    Based on: Markram et al. (1997, 1998) and used in Maass et al. (2002)
    """
    
    def __init__(self, config: DynamicSynapseConfig):
        self.config = config
        
        # Dynamic variables
        self.x = 1.0  # Available resources (0-1)
        self.u = config.U  # Utilization of resources (0-1)
        self.I_syn = 0.0  # Current synaptic current
        
        # Connection properties
        self.weight = getattr(config, 'amplitude', 30.0)  # Synaptic weight/amplitude
        self.delay = getattr(config, 'delay', 1.0)  # Synaptic delay (ms)
        
        # Time constants (convert to milliseconds if needed)
        self.tau_rec = getattr(config, 'tau_rec', 800.0)  # Recovery time constant (ms)
        self.tau_fac = getattr(config, 'tau_fac', 0.0)  # Facilitation time constant (ms)
        
        # Pre-synaptic spike history for delay handling
        self.spike_buffer = []
        self.max_delay_steps = int(config.delay / 0.1) + 1  # Assuming 0.1ms timestep
    
    def update(self, dt: float, presynaptic_spike: bool = False) -> float:
        """
        Update synapse state and return synaptic current
        
        Args:
            dt: Time step (ms)
            presynaptic_spike: Whether presynaptic neuron spiked
            
        Returns:
            Synaptic current (nA)
        """
        # Handle synaptic delay
        self.spike_buffer.append(presynaptic_spike)
        if len(self.spike_buffer) > self.max_delay_steps:
            delayed_spike = self.spike_buffer.pop(0)
        else:
            delayed_spike = False
        
        # Update dynamic variables
        if delayed_spike:
            # Spike arrival: update utilization and available resources
            self.u += self.config.U * (1 - self.u)  # Facilitation
            delta_I = self.u * self.x * self.weight  # Current increment
            self.x *= (1 - self.u)  # Resource depletion
            
            # Update synaptic current
            self.I_syn += delta_I
        
        # Recovery dynamics (between spikes)  
        tau_rec_ms = self.tau_rec
        tau_fac_ms = self.tau_fac if self.tau_fac > 0 else np.inf
        
        # Resource recovery
        self.x += (1 - self.x) * dt / tau_rec_ms
        
        # Facilitation decay
        if tau_fac_ms < np.inf:
            self.u -= (self.u - self.config.U) * dt / tau_fac_ms
        
        # Synaptic current decay (exponential)
        tau_syn = 3.0  # Synaptic time constant (ms)
        self.I_syn *= np.exp(-dt / tau_syn)
        
        return self.I_syn
    
    def reset(self):
        """Reset synapse to initial state"""
        self.x = 1.0
        self.u = self.config.U
        self.I_syn = 0.0
        self.spike_buffer = []
    
    def get_state(self) -> Dict[str, float]:
        """Get current synapse state"""
        return {
            'available_resources': self.x,
            'utilization': self.u,
            'synaptic_current': self.I_syn,
            'weight': self.weight,
            'delay': self.delay
        }


class StaticSynapse:
    """
    Simple static synapse (no plasticity)
    
    For comparison with dynamic synapses
    """
    
    def __init__(self, weight: float, delay: float = 1.0):
        self.weight = weight
        self.delay = delay
        self.I_syn = 0.0
        
        # Spike buffer for delay
        self.spike_buffer = []
        self.max_delay_steps = int(delay / 0.1) + 1
    
    def update(self, dt: float, presynaptic_spike: bool = False) -> float:
        """Update static synapse"""
        # Handle delay
        self.spike_buffer.append(presynaptic_spike)
        if len(self.spike_buffer) > self.max_delay_steps:
            delayed_spike = self.spike_buffer.pop(0)
        else:
            delayed_spike = False
        
        # Update current
        if delayed_spike:
            self.I_syn += self.weight
        
        # Exponential decay
        tau_syn = 3.0  # ms
        self.I_syn *= np.exp(-dt / tau_syn)
        
        return self.I_syn
    
    def reset(self):
        """Reset synapse"""
        self.I_syn = 0.0
        self.spike_buffer = []


class ConnectivityMatrix:
    """
    Manages connectivity patterns for LSM networks
    
    Supports various connectivity types from Maass 2002
    """
    
    def __init__(self, n_neurons: int, connectivity_type: ConnectivityType,
                 p_connect: float = 0.1, **kwargs):
        self.n_neurons = n_neurons
        self.connectivity_type = connectivity_type
        self.p_connect = p_connect
        
        # Connection matrix
        self.connections = self._generate_connectivity(**kwargs)
        
        # Synapse objects for each connection
        self.synapses = {}
        self._initialize_synapses()
    
    def _generate_connectivity(self, **kwargs) -> np.ndarray:
        """Generate connectivity matrix based on type"""
        
        if self.connectivity_type == ConnectivityType.RANDOM_UNIFORM:
            return self._random_uniform_connectivity()
        
        elif self.connectivity_type == ConnectivityType.DISTANCE_DEPENDENT:
            positions = kwargs.get('positions')
            if positions is None:
                raise ValueError("Positions required for distance-dependent connectivity")
            # Remove positions from kwargs to avoid duplicate parameter
            other_kwargs = {k: v for k, v in kwargs.items() if k != 'positions'}
            return self._distance_dependent_connectivity(positions, **other_kwargs)
        
        elif self.connectivity_type == ConnectivityType.COLUMN_STRUCTURED:
            return self._column_structured_connectivity(**kwargs)
        
        elif self.connectivity_type == ConnectivityType.SMALL_WORLD:
            return self._small_world_connectivity(**kwargs)
        
        elif self.connectivity_type == ConnectivityType.SCALE_FREE:
            return self._scale_free_connectivity(**kwargs)
        
        else:
            raise ValueError(f"Unknown connectivity type: {self.connectivity_type}")
    
    def _random_uniform_connectivity(self) -> np.ndarray:
        """Random uniform connectivity"""
        connections = np.random.random((self.n_neurons, self.n_neurons)) < self.p_connect
        # Remove self-connections
        np.fill_diagonal(connections, False)
        return connections
    
    def _distance_dependent_connectivity(self, positions: np.ndarray, **kwargs) -> np.ndarray:
        """Distance-dependent connectivity (Maass 2002)"""
        lambda_param = kwargs.get('lambda', 2.0)  # Connection length constant
        
        connections = np.zeros((self.n_neurons, self.n_neurons), dtype=bool)
        
        for i in range(self.n_neurons):
            for j in range(self.n_neurons):
                if i != j:
                    # Calculate distance
                    distance = np.linalg.norm(positions[i] - positions[j])
                    
                    # Connection probability decreases with distance
                    p_conn = self.p_connect * np.exp(-distance / lambda_param)
                    
                    # Create connection based on probability
                    connections[i, j] = np.random.random() < p_conn
        
        return connections
    
    def _column_structured_connectivity(self, **kwargs) -> np.ndarray:
        """Column-based 3D structure"""
        n_columns = kwargs.get('n_columns', 5)
        neurons_per_column = self.n_neurons // n_columns
        
        connections = np.zeros((self.n_neurons, self.n_neurons), dtype=bool)
        
        for i in range(self.n_neurons):
            column_i = i // neurons_per_column
            
            for j in range(self.n_neurons):
                if i != j:
                    column_j = j // neurons_per_column
                    
                    # Higher connectivity within columns
                    if column_i == column_j:
                        p_conn = self.p_connect * 3.0  # 3x higher intra-column
                    else:
                        p_conn = self.p_connect * 0.5  # 0.5x lower inter-column
                    
                    connections[i, j] = np.random.random() < p_conn
        
        return connections
    
    def _small_world_connectivity(self, **kwargs) -> np.ndarray:
        """Small-world network topology"""
        k = kwargs.get('k', 6)  # Number of nearest neighbors
        p_rewire = kwargs.get('p_rewire', 0.1)  # Rewiring probability
        
        connections = np.zeros((self.n_neurons, self.n_neurons), dtype=bool)
        
        # Start with regular ring lattice
        for i in range(self.n_neurons):
            for j in range(1, k//2 + 1):
                # Connect to k nearest neighbors
                neighbor1 = (i + j) % self.n_neurons
                neighbor2 = (i - j) % self.n_neurons
                connections[i, neighbor1] = True
                connections[i, neighbor2] = True
        
        # Rewire edges with probability p_rewire
        for i in range(self.n_neurons):
            neighbors = np.where(connections[i])[0]
            for neighbor in neighbors:
                if np.random.random() < p_rewire:
                    # Remove old connection
                    connections[i, neighbor] = False
                    
                    # Create new random connection
                    new_target = np.random.choice(self.n_neurons)
                    if new_target != i:
                        connections[i, new_target] = True
        
        return connections
    
    def _scale_free_connectivity(self, **kwargs) -> np.ndarray:
        """Scale-free network using preferential attachment"""
        m = kwargs.get('m', 2)  # Number of edges per new node
        
        connections = np.zeros((self.n_neurons, self.n_neurons), dtype=bool)
        degrees = np.zeros(self.n_neurons)
        
        # Start with small connected network
        for i in range(min(m+1, self.n_neurons)):
            for j in range(i+1, min(m+1, self.n_neurons)):
                connections[i, j] = True
                connections[j, i] = True
                degrees[i] += 1
                degrees[j] += 1
        
        # Add remaining nodes with preferential attachment
        for i in range(m+1, self.n_neurons):
            total_degree = np.sum(degrees[:i])
            
            if total_degree > 0:
                # Probabilities proportional to degree
                probs = degrees[:i] / total_degree
                
                # Select m nodes to connect to
                targets = np.random.choice(i, size=min(m, i), replace=False, p=probs)
                
                for target in targets:
                    connections[i, target] = True
                    connections[target, i] = True
                    degrees[i] += 1
                    degrees[target] += 1
        
        return connections
    
    def _initialize_synapses(self):
        """Initialize synapse objects for each connection"""
        for i in range(self.n_neurons):
            for j in range(self.n_neurons):
                if self.connections[i, j]:
                    # Determine connection type (simplified)
                    exc_ratio = 0.8
                    is_i_exc = i < int(self.n_neurons * exc_ratio)
                    is_j_exc = j < int(self.n_neurons * exc_ratio)
                    
                    if is_i_exc and is_j_exc:
                        conn_type = "EE"
                    elif is_i_exc and not is_j_exc:
                        conn_type = "EI"
                    elif not is_i_exc and is_j_exc:
                        conn_type = "IE"
                    else:
                        conn_type = "II"
                    
                    # Create synapse configuration
                    config = DynamicSynapseConfig(
                        synapse_type=SynapseModelType.MARKRAM_DYNAMIC,
                        connection_type=conn_type
                    )
                    
                    # Create synapse
                    self.synapses[(i, j)] = DynamicSynapse(config)
    
    def get_synaptic_current(self, post_neuron_idx: int, dt: float, 
                           spike_times: Dict[int, bool]) -> float:
        """Get total synaptic current for a postsynaptic neuron"""
        total_current = 0.0
        
        # Sum currents from all presynaptic neurons
        for pre_idx in range(self.n_neurons):
            if self.connections[pre_idx, post_neuron_idx]:
                synapse = self.synapses[(pre_idx, post_neuron_idx)]
                pre_spike = spike_times.get(pre_idx, False)
                current = synapse.update(dt, pre_spike)
                total_current += current
        
        return total_current
    
    def reset_all_synapses(self):
        """Reset all synapses to initial state"""
        for synapse in self.synapses.values():
            synapse.reset()
    
    def get_connectivity_stats(self) -> Dict[str, Any]:
        """Get statistics about the connectivity"""
        n_connections = np.sum(self.connections)
        total_possible = self.n_neurons * (self.n_neurons - 1)
        density = n_connections / total_possible
        
        # In-degree and out-degree statistics
        in_degrees = np.sum(self.connections, axis=0)
        out_degrees = np.sum(self.connections, axis=1)
        
        return {
            'total_connections': int(n_connections),
            'density': float(density),
            'mean_in_degree': float(np.mean(in_degrees)),
            'mean_out_degree': float(np.mean(out_degrees)),
            'std_in_degree': float(np.std(in_degrees)),
            'std_out_degree': float(np.std(out_degrees)),
            'max_in_degree': int(np.max(in_degrees)),
            'max_out_degree': int(np.max(out_degrees))
        }


def create_connectivity_matrix(n_neurons: int, connectivity_type: str, 
                             p_connect: float = 0.1, **kwargs) -> ConnectivityMatrix:
    """Factory function to create connectivity matrices"""
    
    conn_type_map = {
        'random_uniform': ConnectivityType.RANDOM_UNIFORM,
        'distance_dependent': ConnectivityType.DISTANCE_DEPENDENT,
        'column_structured': ConnectivityType.COLUMN_STRUCTURED,
        'small_world': ConnectivityType.SMALL_WORLD,
        'scale_free': ConnectivityType.SCALE_FREE,
        # Aliases for convenience
        'random': ConnectivityType.RANDOM_UNIFORM,
        'distance': ConnectivityType.DISTANCE_DEPENDENT,
        'column': ConnectivityType.COLUMN_STRUCTURED,
    }
    
    conn_type = conn_type_map.get(connectivity_type.lower())
    if conn_type is None:
        raise ValueError(f"Unknown connectivity type: {connectivity_type}")
    
    return ConnectivityMatrix(n_neurons, conn_type, p_connect, **kwargs)