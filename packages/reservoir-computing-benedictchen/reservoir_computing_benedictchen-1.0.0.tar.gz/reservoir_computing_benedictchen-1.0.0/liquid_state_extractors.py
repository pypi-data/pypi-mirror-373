"""
Liquid State Extractors for LSM
Based on: Maass, Natschläger & Markram (2002) "Real-Time Computing Without Stable States"
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class LiquidStateExtractor(ABC):
    """
    Abstract base class for liquid state extraction methods
    
    The liquid state defines what information from the liquid dynamics 
    is available to the readout - a crucial concept from Maass 2002
    """
    
    @abstractmethod
    def extract_state(self, spike_matrix: np.ndarray, times: np.ndarray, 
                     current_time: float, **kwargs) -> np.ndarray:
        """
        🧠 Extract Liquid State Vector at Current Time - Maass 2002 Implementation!
        
        Args:
            spike_matrix: Matrix of spike events [n_neurons, n_timesteps]
            times: Array of time points corresponding to spike_matrix columns
            current_time: Current simulation time for state extraction
            **kwargs: Additional parameters for subclasses
            
        Returns:
            np.ndarray: Liquid state vector representing current neural activity
            
        📚 **Reference**: Maass, W., Natschläger, T., & Markram, H. (2002)
        "Real-time computing without stable states: A new framework for neural 
        computation based on perturbations"
        """
        pass
    
    @abstractmethod
    def reset_state(self):
        """
        🔄 Reset Internal State Variables - Prepare for New Simulation!
        
        Resets any internal state variables to initial conditions.
        Essential for proper liquid state computation across multiple trials.
        """
        pass


class PSPDecayExtractor(LiquidStateExtractor):
    """
    CORRECT liquid state extraction using PSP decay from Maass 2002
    
    "The liquid state x^M(t) at time t is defined as the vector of values 
    that the outputs of all liquid neurons would contribute to the membrane 
    potential of a readout neuron if they were connected to that readout neuron"
    
    This is the paper-accurate implementation of liquid state extraction.
    """
    
    def __init__(self, tau_decay: float = 30.0, n_liquid: int = 135):
        self.tau_decay = tau_decay  # PSP decay time constant (ms)
        self.n_liquid = n_liquid
        self.psp_traces = np.zeros(n_liquid)  # Current PSP values
        
    def extract_state(self, spike_matrix: np.ndarray, times: np.ndarray, 
                     current_time: float, dt: float = 0.1) -> np.ndarray:
        """Extract PSP-based liquid state"""
        # Find current time index
        time_idx = int(current_time / dt)
        
        if time_idx < spike_matrix.shape[1]:
            # Update PSP traces with exponential decay
            self.psp_traces *= np.exp(-dt / self.tau_decay)
            
            # Add spike contributions
            current_spikes = spike_matrix[:, time_idx]
            self.psp_traces += current_spikes
            
        return self.psp_traces.copy()
    
    def reset_state(self):
        """Reset PSP traces"""
        self.psp_traces.fill(0.0)


class SpikeCountExtractor(LiquidStateExtractor):
    """
    Simplified approach using spike counts in time windows
    
    Kept for backward compatibility but not paper-accurate
    """
    
    def __init__(self, window_size: float = 50.0, n_liquid: int = 135):
        self.window_size = window_size  # ms
        self.n_liquid = n_liquid
        
    def extract_state(self, spike_matrix: np.ndarray, times: np.ndarray, 
                     current_time: float, dt: float = 0.1) -> np.ndarray:
        """Extract spike count features in time window"""
        window_steps = int(self.window_size / dt)
        time_idx = int(current_time / dt)
        
        start_idx = max(0, time_idx - window_steps)
        end_idx = min(spike_matrix.shape[1], time_idx + 1)
        
        if start_idx < end_idx:
            spike_counts = np.sum(spike_matrix[:, start_idx:end_idx], axis=1)
        else:
            spike_counts = np.zeros(self.n_liquid)
            
        return spike_counts
    
    def reset_state(self):
        """No internal state to reset for spike counts"""
        pass


class MembranePotentialExtractor(LiquidStateExtractor):
    """
    Direct membrane potential readout
    
    Uses current membrane potentials as liquid state
    """
    
    def __init__(self, n_liquid: int = 135):
        self.n_liquid = n_liquid
        
    def extract_state(self, spike_matrix: np.ndarray, times: np.ndarray, 
                     current_time: float, membrane_potentials: np.ndarray = None, 
                     **kwargs) -> np.ndarray:
        """Extract membrane potential state"""
        if membrane_potentials is not None:
            return membrane_potentials.copy()
        else:
            # Fallback to zeros if membrane potentials not provided
            return np.zeros(self.n_liquid)
    
    def reset_state(self):
        """No internal state to reset"""
        pass


class FiringRateExtractor(LiquidStateExtractor):
    """
    Population firing rate based extraction
    
    Computes instantaneous firing rates for neuron populations
    """
    
    def __init__(self, window_size: float = 20.0, n_liquid: int = 135, 
                 population_size: int = 10):
        self.window_size = window_size  # ms
        self.n_liquid = n_liquid
        self.population_size = population_size
        self.n_populations = max(1, n_liquid // population_size)
        
    def extract_state(self, spike_matrix: np.ndarray, times: np.ndarray, 
                     current_time: float, dt: float = 0.1) -> np.ndarray:
        """Extract population firing rates"""
        window_steps = int(self.window_size / dt)
        time_idx = int(current_time / dt)
        
        start_idx = max(0, time_idx - window_steps)
        end_idx = min(spike_matrix.shape[1], time_idx + 1)
        
        if start_idx < end_idx:
            # Compute spike counts for each neuron
            spike_counts = np.sum(spike_matrix[:, start_idx:end_idx], axis=1)
            
            # Convert to firing rates (Hz)
            firing_rates = spike_counts / (self.window_size / 1000.0)
            
            # Group into populations and compute population rates
            pop_rates = np.zeros(self.n_populations)
            for i in range(self.n_populations):
                start_neuron = i * self.population_size
                end_neuron = min((i + 1) * self.population_size, self.n_liquid)
                pop_rates[i] = np.mean(firing_rates[start_neuron:end_neuron])
            
            return pop_rates
        else:
            return np.zeros(self.n_populations)
    
    def reset_state(self):
        """No internal state to reset"""
        pass


class MultiTimescaleExtractor(LiquidStateExtractor):
    """
    Multi-timescale liquid state extraction
    
    Uses multiple decay time constants to capture dynamics at different scales
    """
    
    def __init__(self, tau_fast: float = 10.0, tau_medium: float = 30.0, 
                 tau_slow: float = 100.0, n_liquid: int = 135):
        self.tau_fast = tau_fast
        self.tau_medium = tau_medium  
        self.tau_slow = tau_slow
        self.n_liquid = n_liquid
        
        # Initialize trace arrays for each timescale
        self.fast_traces = np.zeros(n_liquid)
        self.medium_traces = np.zeros(n_liquid)
        self.slow_traces = np.zeros(n_liquid)
        
    def extract_state(self, spike_matrix: np.ndarray, times: np.ndarray, 
                     current_time: float, dt: float = 0.1) -> np.ndarray:
        """Extract multi-timescale liquid state"""
        time_idx = int(current_time / dt)
        
        if time_idx < spike_matrix.shape[1]:
            # Update traces with different decay constants
            self.fast_traces *= np.exp(-dt / self.tau_fast)
            self.medium_traces *= np.exp(-dt / self.tau_medium)
            self.slow_traces *= np.exp(-dt / self.tau_slow)
            
            # Add spike contributions
            current_spikes = spike_matrix[:, time_idx]
            self.fast_traces += current_spikes
            self.medium_traces += current_spikes
            self.slow_traces += current_spikes
        
        # Concatenate all timescales into single state vector
        return np.concatenate([self.fast_traces, self.medium_traces, self.slow_traces])
    
    def reset_state(self):
        """Reset all trace arrays"""
        self.fast_traces.fill(0.0)
        self.medium_traces.fill(0.0)
        self.slow_traces.fill(0.0)


class AdaptiveExtractor(LiquidStateExtractor):
    """
    Adaptive liquid state extractor that learns optimal features
    
    Uses simple adaptation to adjust extraction parameters based on task demands
    """
    
    def __init__(self, n_liquid: int = 135, adaptation_rate: float = 0.01):
        self.n_liquid = n_liquid
        self.adaptation_rate = adaptation_rate
        
        # Learned feature weights (initially uniform)
        self.feature_weights = np.ones(n_liquid)
        self.psp_traces = np.zeros(n_liquid)
        self.tau_decay = 30.0  # Initial decay constant
        
    def extract_state(self, spike_matrix: np.ndarray, times: np.ndarray, 
                     current_time: float, dt: float = 0.1) -> np.ndarray:
        """Extract adaptive liquid state"""
        time_idx = int(current_time / dt)
        
        if time_idx < spike_matrix.shape[1]:
            # Update PSP traces
            self.psp_traces *= np.exp(-dt / self.tau_decay)
            current_spikes = spike_matrix[:, time_idx]
            self.psp_traces += current_spikes
        
        # Apply learned feature weights
        weighted_state = self.psp_traces * self.feature_weights
        
        return weighted_state
    
    def update_weights(self, error_signal: np.ndarray):
        """Update feature weights based on error signal"""
        if len(error_signal) == len(self.feature_weights):
            # Simple gradient-based adaptation
            self.feature_weights += self.adaptation_rate * error_signal
            # Keep weights positive
            self.feature_weights = np.maximum(self.feature_weights, 0.01)
    
    def reset_state(self):
        """Reset PSP traces but keep learned weights"""
        self.psp_traces.fill(0.0)


def create_liquid_state_extractor(extractor_type: str, n_liquid: int = 135, 
                                **kwargs) -> LiquidStateExtractor:
    """Factory function to create liquid state extractors"""
    
    if extractor_type.lower() == 'psp_decay':
        tau_decay = kwargs.get('tau_decay', 30.0)
        return PSPDecayExtractor(tau_decay, n_liquid)
    
    elif extractor_type.lower() == 'spike_counts':
        window_size = kwargs.get('window_size', 50.0)
        return SpikeCountExtractor(window_size, n_liquid)
    
    elif extractor_type.lower() == 'membrane_potentials':
        return MembranePotentialExtractor(n_liquid)
    
    elif extractor_type.lower() == 'firing_rates':
        window_size = kwargs.get('window_size', 20.0)
        pop_size = kwargs.get('population_size', 10)
        return FiringRateExtractor(window_size, n_liquid, pop_size)
    
    elif extractor_type.lower() == 'multi_timescale':
        tau_fast = kwargs.get('tau_fast', 10.0)
        tau_medium = kwargs.get('tau_medium', 30.0) 
        tau_slow = kwargs.get('tau_slow', 100.0)
        return MultiTimescaleExtractor(tau_fast, tau_medium, tau_slow, n_liquid)
    
    elif extractor_type.lower() == 'adaptive':
        adapt_rate = kwargs.get('adaptation_rate', 0.01)
        return AdaptiveExtractor(n_liquid, adapt_rate)
    
    else:
        raise ValueError(f"Unknown extractor type: {extractor_type}")


def compare_extractors(spike_matrix: np.ndarray, times: np.ndarray, 
                      extractor_types: List[str], n_liquid: int = 135) -> Dict[str, np.ndarray]:
    """
    Compare different liquid state extractors on the same spike data
    
    Useful for analyzing which extraction method works best for a given task
    """
    results = {}
    
    # Create extractors
    extractors = {}
    for ext_type in extractor_types:
        extractors[ext_type] = create_liquid_state_extractor(ext_type, n_liquid)
    
    # Extract states at multiple time points
    n_timepoints = len(times)
    dt = times[1] - times[0] if len(times) > 1 else 1.0
    
    for ext_name, extractor in extractors.items():
        extractor.reset_state()
        states = []
        
        for t_idx, current_time in enumerate(times):
            state = extractor.extract_state(spike_matrix, times, current_time, dt=dt)
            states.append(state)
        
        results[ext_name] = np.array(states)
    
    return results