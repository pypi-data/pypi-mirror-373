"""
🌊 Echo State Network (ESN) - Unified Complete Implementation
============================================================

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Herbert Jaeger (2001) "The 'Echo State' Approach to Analysing and Training Recurrent Neural Networks"

💰 Support This Research: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Unified implementation combining:
- Clean modular architecture from refactored version
- Complete functionality from comprehensive original version
- All advanced features and benchmark tasks
- Full theoretical analysis capabilities

🎯 ELI5 Summary:
Think of an Echo State Network like a pond with many interconnected ripples.
When you drop a stone (input), it creates complex wave patterns that echo
through the water. The network just needs to learn how to "read" these patterns
at the surface - no need to control the complex dynamics underneath!

🔬 Research Background:
========================
Herbert Jaeger's 2001 breakthrough solved a fundamental problem: training 
recurrent neural networks was extremely slow and difficult due to vanishing/
exploding gradients. His insight: don't train the recurrent connections at all!

The ESN revolution:
- Fixed random recurrent reservoir (the "pond")
- Only train simple linear readout (the "surface reader")  
- 1000x faster training than traditional RNNs
- Natural handling of temporal dependencies
- Rich dynamics from simple random connectivity

This launched the entire field of "Reservoir Computing" and influenced
modern architectures like LSTMs and Transformers.

🏗️ Architecture:
================
Input → [Input Weights] → [Reservoir] → [Readout] → Output
  u           W_in          x(t+1)       W_out       y
              ↓               ↑            ↑
              └─── [Recurrent W_res] ──────┘
                      (fixed!)        (trainable!)
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass
import warnings
import time
from scipy import linalg
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigs

# Import modular components (maintaining backward compatibility if they exist)
try:
    from .reservoir_topology import ReservoirTopology
    from .echo_state_validation import EchoStatePropertyValidator as ExternalValidator
    from .state_dynamics import StateDynamics
    from .esn_training import ESNTraining
    from .esn_configuration import ESNConfiguration
    MODULAR_COMPONENTS_AVAILABLE = True
except ImportError:
    MODULAR_COMPONENTS_AVAILABLE = False
    warnings.warn("Modular components not available, using unified implementation")


@dataclass
class ESNState:
    """Current state of the ESN"""
    reservoir_state: np.ndarray
    last_output: Optional[np.ndarray] = None
    time_step: int = 0


@dataclass 
class ESNConfig:
    """Configuration for ESN with all possible options"""
    reservoir_size: int = 100
    spectral_radius: float = 0.95
    leak_rate: float = 1.0
    connectivity: float = 0.1
    input_scaling: float = 1.0
    noise_level: float = 0.0
    reservoir_topology: str = 'random'
    activation_function: str = 'tanh'
    output_feedback: bool = False
    feedback_scaling: float = 0.1
    teacher_forcing: bool = False
    washout_length: int = 100
    ridge_regression: float = 1e-8
    seed: Optional[int] = None


class EchoStateNetwork:
    """
    🌊 Echo State Network - Unified Complete Implementation
    
    Combines the clean modular architecture with comprehensive functionality,
    including all advanced features, benchmark tasks, and theoretical analysis.
    """
    
    def __init__(
        self,
        reservoir_size: int = None,
        spectral_radius: float = 0.95,
        leak_rate: float = 1.0,
        connectivity: float = 0.1,
        input_scaling: float = 1.0,
        noise_level: float = 0.0,
        random_seed: Optional[int] = None,
        reservoir_topology: str = 'random',
        activation_function: str = 'tanh',
        output_feedback: bool = False,
        feedback_scaling: float = 0.1,
        teacher_forcing: bool = False,
        washout_length: int = 100,
        ridge_regression: float = 1e-8,
        # Backward compatibility parameters
        n_reservoir: int = None,
        n_inputs: int = None,
        n_outputs: int = None,
        **kwargs
    ):
        """Initialize unified ESN with full functionality"""
        
        # Handle backward compatibility
        if n_reservoir is not None and reservoir_size is None:
            reservoir_size = n_reservoir
        if reservoir_size is None:
            reservoir_size = 100
            
        # Core parameters
        self.reservoir_size = reservoir_size
        self.spectral_radius = spectral_radius
        self.leak_rate = leak_rate
        self.connectivity = connectivity
        self.input_scaling = input_scaling
        self.noise_level = noise_level
        self.reservoir_topology = reservoir_topology
        self.activation_function = activation_function
        self.output_feedback = output_feedback
        self.feedback_scaling = feedback_scaling
        self.teacher_forcing = teacher_forcing
        self.washout_length = washout_length
        self.ridge_regression = ridge_regression
        
        # Initialize random seed
        if random_seed is not None:
            np.random.seed(random_seed)
            
        # Network matrices (will be initialized later)
        self.W_in = None    # Input weights
        self.W_res = None   # Reservoir weights  
        self.W_out = None   # Output weights
        self.W_fb = None    # Feedback weights
        
        # Dimensions
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self.input_dim = None
        self.output_dim = None
        
        # State variables
        self.reservoir_state = np.zeros(reservoir_size)
        self.last_output = None
        self.is_trained = False
        
        # Training data storage
        self.collected_states = []
        self.collected_targets = []
        
        # Performance metrics
        self.training_error = None
        self.validation_error = None
        self.memory_capacity = None
        
        # Initialize activation function
        self.activation_func = self._get_activation_function(activation_function)
        
        print(f"✓ ESN initialized: {reservoir_size} reservoir neurons")
        print(f"   Spectral radius: {spectral_radius}")
        print(f"   Leak rate: {leak_rate}")
        print(f"   Topology: {reservoir_topology}")
        print(f"   Output feedback: {output_feedback}")
    
    def _get_activation_function(self, name: str) -> Callable:
        """Get activation function by name"""
        functions = {
            'tanh': np.tanh,
            'sigmoid': lambda x: 1 / (1 + np.exp(-np.clip(x, -500, 500))),
            'relu': lambda x: np.maximum(0, x),
            'linear': lambda x: x,
            'sin': np.sin,
            'identity': lambda x: x
        }
        
        if name not in functions:
            warnings.warn(f"Unknown activation function '{name}', using tanh")
            return functions['tanh']
            
        return functions[name]
    
    def initialize_reservoir(self, input_dim: int, output_dim: int = 1):
        """Initialize all network matrices"""
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.n_inputs = input_dim
        self.n_outputs = output_dim
        
        # Initialize input weights
        self.W_in = np.random.uniform(
            -self.input_scaling, 
            self.input_scaling,
            (self.reservoir_size, input_dim)
        )
        
        # Initialize reservoir weights based on topology
        self.W_res = self._create_reservoir_matrix()
        
        # Initialize feedback weights if needed
        if self.output_feedback:
            self.W_fb = np.random.uniform(
                -self.feedback_scaling,
                self.feedback_scaling,
                (self.reservoir_size, output_dim)
            )
        
        print(f"✓ Reservoir initialized: {input_dim}→{self.reservoir_size}→{output_dim}")
    
    def _create_reservoir_matrix(self) -> np.ndarray:
        """Create reservoir weight matrix with specified topology"""
        
        if self.reservoir_topology == 'random':
            return self._create_random_topology()
        elif self.reservoir_topology == 'ring':
            return self._create_ring_topology()
        elif self.reservoir_topology == 'small_world':
            return self._create_small_world_topology()
        elif self.reservoir_topology == 'scale_free':
            return self._create_scale_free_topology()
        else:
            warnings.warn(f"Unknown topology '{self.reservoir_topology}', using random")
            return self._create_random_topology()
    
    def _create_random_topology(self) -> np.ndarray:
        """Create random sparse reservoir matrix"""
        # Create sparse random matrix
        W = np.random.normal(0, 1, (self.reservoir_size, self.reservoir_size))
        
        # Apply sparsity
        mask = np.random.random((self.reservoir_size, self.reservoir_size)) < self.connectivity
        W *= mask
        
        # Scale to desired spectral radius
        W = self._scale_spectral_radius(W, self.spectral_radius)
        
        return W
    
    def _create_ring_topology(self) -> np.ndarray:
        """Create ring topology reservoir"""
        W = np.zeros((self.reservoir_size, self.reservoir_size))
        
        # Forward connections
        for i in range(self.reservoir_size - 1):
            W[i+1, i] = 1.0
        
        # Close the ring  
        W[0, self.reservoir_size-1] = 1.0
        
        # Add some random connections for complexity
        extra_connections = int(self.connectivity * self.reservoir_size**2)
        for _ in range(extra_connections):
            i, j = np.random.randint(0, self.reservoir_size, 2)
            if i != j:
                W[i, j] = np.random.normal(0, 1)
        
        return self._scale_spectral_radius(W, self.spectral_radius)
    
    def _create_small_world_topology(self, k: int = 6, p: float = 0.1) -> np.ndarray:
        """Create small-world network topology (Watts-Strogatz)"""
        n = self.reservoir_size
        W = np.zeros((n, n))
        
        # Start with ring lattice
        for i in range(n):
            for j in range(1, k//2 + 1):
                W[i, (i+j) % n] = np.random.normal(0, 1)
                W[i, (i-j) % n] = np.random.normal(0, 1)
        
        # Rewire with probability p
        edges = []
        for i in range(n):
            for j in range(1, k//2 + 1):
                if np.random.random() < p:
                    # Rewire edge
                    new_j = np.random.randint(0, n)
                    while new_j == i or W[i, new_j] != 0:
                        new_j = np.random.randint(0, n) 
                    W[i, (i+j) % n] = 0
                    W[i, new_j] = np.random.normal(0, 1)
        
        return self._scale_spectral_radius(W, self.spectral_radius)
    
    def _create_scale_free_topology(self) -> np.ndarray:
        """Create scale-free network topology (Barabási-Albert)"""
        n = self.reservoir_size
        m = max(1, int(self.connectivity * n))  # Number of edges to attach
        
        W = np.zeros((n, n))
        degrees = np.zeros(n)
        
        # Start with small complete graph
        for i in range(min(m+1, n)):
            for j in range(i+1, min(m+1, n)):
                weight = np.random.normal(0, 1)
                W[i, j] = weight
                W[j, i] = weight
                degrees[i] += 1
                degrees[j] += 1
        
        # Add remaining nodes with preferential attachment
        for i in range(m+1, n):
            targets = []
            while len(targets) < m and len(targets) < i:
                # Preferential attachment based on degree
                probs = degrees[:i] / np.sum(degrees[:i])
                target = np.random.choice(i, p=probs)
                if target not in targets:
                    targets.append(target)
            
            # Add edges
            for target in targets:
                weight = np.random.normal(0, 1)
                W[i, target] = weight
                W[target, i] = weight
                degrees[i] += 1
                degrees[target] += 1
        
        return self._scale_spectral_radius(W, self.spectral_radius)
    
    def _scale_spectral_radius(self, W: np.ndarray, target_radius: float) -> np.ndarray:
        """Scale matrix to have desired spectral radius"""
        try:
            # Get largest eigenvalue
            eigenvals = eigs(W, k=1, which='LM', return_eigenvectors=False)
            current_radius = np.abs(eigenvals[0])
            
            if current_radius > 1e-12:  # Avoid division by zero
                W = W * (target_radius / current_radius)
        except:
            # Fallback for very small matrices
            eigenvals = np.linalg.eigvals(W)
            current_radius = np.max(np.abs(eigenvals))
            if current_radius > 1e-12:
                W = W * (target_radius / current_radius)
        
        return W
    
    def update_state(self, input_vec: np.ndarray, output_feedback: np.ndarray = None) -> np.ndarray:
        """Update reservoir state with input"""
        if self.W_in is None:
            raise ValueError("Reservoir not initialized. Call initialize_reservoir() first.")
        
        # Ensure input is proper shape
        if input_vec.ndim == 1:
            input_vec = input_vec.reshape(-1, 1)
        elif input_vec.ndim == 2 and input_vec.shape[1] != 1:
            input_vec = input_vec.T
        
        # Calculate input contribution
        input_contrib = self.W_in @ input_vec.flatten()
        
        # Calculate reservoir contribution  
        reservoir_contrib = self.W_res @ self.reservoir_state
        
        # Add feedback if enabled
        feedback_contrib = 0
        if self.output_feedback and self.W_fb is not None and output_feedback is not None:
            if output_feedback.ndim == 1:
                output_feedback = output_feedback.reshape(-1, 1)
            feedback_contrib = self.W_fb @ output_feedback.flatten()
        
        # Add noise if specified
        noise = 0
        if self.noise_level > 0:
            noise = np.random.normal(0, self.noise_level, self.reservoir_size)
        
        # Update with leaky integration
        new_state = (1 - self.leak_rate) * self.reservoir_state + \
                    self.leak_rate * self.activation_func(
                        input_contrib + reservoir_contrib + feedback_contrib + noise
                    )
        
        self.reservoir_state = new_state
        return new_state
    
    def collect_states(self, inputs: np.ndarray, targets: np.ndarray = None, 
                      teacher_forcing: bool = None):
        """Collect reservoir states for training"""
        if self.W_in is None:
            self.initialize_reservoir(inputs.shape[1] if inputs.ndim > 1 else 1,
                                    targets.shape[1] if targets is not None and targets.ndim > 1 else 1)
        
        if teacher_forcing is None:
            teacher_forcing = self.teacher_forcing
            
        n_steps = len(inputs)
        states = np.zeros((n_steps, self.reservoir_size))
        
        # Reset state
        self.reservoir_state = np.zeros(self.reservoir_size)
        
        for t in range(n_steps):
            # Determine feedback signal
            feedback = None
            if self.output_feedback:
                if teacher_forcing and targets is not None:
                    feedback = targets[t] if t > 0 else np.zeros(self.output_dim or 1)
                else:
                    feedback = self.last_output if self.last_output is not None else np.zeros(self.output_dim or 1)
            
            # Update state
            state = self.update_state(inputs[t], feedback)
            states[t] = state
            
            # Store for potential feedback
            if self.output_feedback and not teacher_forcing and self.W_out is not None:
                self.last_output = self.W_out @ state
        
        # Store states for training
        self.collected_states = states
        if targets is not None:
            self.collected_targets = targets
            
        return states
    
    def train(self, inputs: np.ndarray, targets: np.ndarray, 
             teacher_forcing: bool = None, return_states: bool = False):
        """Train the ESN using ridge regression"""
        
        # Collect states
        states = self.collect_states(inputs, targets, teacher_forcing)
        
        # Remove washout period
        if self.washout_length > 0:
            states = states[self.washout_length:]
            targets = targets[self.washout_length:]
        
        # Add bias term
        states_with_bias = np.column_stack([states, np.ones(len(states))])
        
        # Ridge regression
        try:
            # Solve using normal equations with regularization
            XTX = states_with_bias.T @ states_with_bias
            XTY = states_with_bias.T @ targets
            
            # Add ridge regularization
            reg_matrix = self.ridge_regression * np.eye(XTX.shape[0])
            reg_matrix[-1, -1] = 0  # Don't regularize bias
            
            self.W_out = linalg.solve(XTX + reg_matrix, XTY)
            
        except np.linalg.LinAlgError:
            # Fallback to pseudoinverse
            self.W_out = linalg.pinv(states_with_bias) @ targets
        
        # Calculate training error
        predictions = states_with_bias @ self.W_out
        self.training_error = np.mean((predictions - targets)**2)
        
        self.is_trained = True
        
        print(f"✓ ESN trained - RMSE: {np.sqrt(self.training_error):.4f}")
        
        if return_states:
            return states
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'EchoStateNetwork':
        """Sklearn-compatible fit method - wrapper around train()"""
        self.train(X, y)
        return self
    
    def predict(self, inputs: np.ndarray, autonomous_steps: int = 0) -> np.ndarray:
        """Make predictions with trained ESN"""
        if not self.is_trained:
            raise ValueError("ESN not trained. Call train() first.")
        
        # Collect states for input sequence
        states = self.collect_states(inputs)
        
        # Make predictions
        states_with_bias = np.column_stack([states, np.ones(len(states))])
        predictions = states_with_bias @ self.W_out
        
        # Autonomous generation if requested
        if autonomous_steps > 0:
            autonomous_preds = []
            current_state = self.reservoir_state.copy()
            last_pred = predictions[-1] if len(predictions) > 0 else np.zeros(self.output_dim or 1)
            
            for _ in range(autonomous_steps):
                # Use prediction as next input (assuming output_dim == input_dim)
                next_input = last_pred if len(last_pred.shape) > 0 else np.array([last_pred])
                
                # Update state
                current_state = self.update_state(next_input, last_pred if self.output_feedback else None)
                
                # Make prediction
                state_with_bias = np.append(current_state, 1)
                next_pred = self.W_out.T @ state_with_bias
                
                autonomous_preds.append(next_pred)
                last_pred = next_pred
            
            # Combine predictions
            predictions = np.vstack([predictions, autonomous_preds])
        
        return predictions
    
    def reset_state(self):
        """Reset reservoir state"""
        self.reservoir_state = np.zeros(self.reservoir_size)
        self.last_output = None
    
    def get_reservoir_state(self) -> np.ndarray:
        """Get current reservoir state"""
        return self.reservoir_state.copy()
    
    def get_spectral_radius(self) -> float:
        """Get actual spectral radius of reservoir matrix"""
        if self.W_res is None:
            return 0.0
        
        eigenvals = np.linalg.eigvals(self.W_res)
        return np.max(np.abs(eigenvals))
    
    def get_effective_spectral_radius(self) -> float:
        """Get effective spectral radius including leak rate"""
        return (1 - self.leak_rate) + self.leak_rate * self.get_spectral_radius()


# ==================== ADVANCED FEATURES ====================

class EchoStatePropertyValidator:
    """Validate and analyze Echo State Property"""
    
    @staticmethod
    def verify_echo_state_property(esn: EchoStateNetwork, n_tests: int = 10, 
                                  test_length: int = 200) -> Dict[str, Any]:
        """
        Verify Echo State Property by testing state contraction
        
        ESP requires that different initial conditions converge to same attractor
        """
        if esn.W_res is None:
            esn.initialize_reservoir(1)  # Default initialization
            
        max_distance = 0
        distances_over_time = []
        
        for test in range(n_tests):
            # Two random initial states
            state1 = np.random.normal(0, 1, esn.reservoir_size)
            state2 = np.random.normal(0, 1, esn.reservoir_size)
            
            # Same random input sequence
            inputs = np.random.normal(0, 1, (test_length, esn.input_dim or 1))
            
            # Evolve both states
            test_distances = []
            for t in range(test_length):
                # Update both states with same input
                input_contrib = esn.W_in @ inputs[t]
                
                state1 = (1 - esn.leak_rate) * state1 + \
                        esn.leak_rate * esn.activation_func(input_contrib + esn.W_res @ state1)
                state2 = (1 - esn.leak_rate) * state2 + \
                        esn.leak_rate * esn.activation_func(input_contrib + esn.W_res @ state2)
                
                # Calculate distance
                distance = np.linalg.norm(state1 - state2)
                test_distances.append(distance)
                max_distance = max(max_distance, distance)
            
            distances_over_time.append(test_distances)
        
        # Analyze convergence
        final_distances = [distances[-1] for distances in distances_over_time]
        convergence_rate = np.mean(final_distances) / np.mean([distances[0] for distances in distances_over_time])
        
        esp_satisfied = convergence_rate < 1.0 and max_distance < 100  # Heuristic thresholds
        
        return {
            'esp_satisfied': esp_satisfied,
            'max_pairwise_distance': max_distance,
            'convergence_rate': convergence_rate,
            'distances_over_time': distances_over_time,
            'final_distances': final_distances,
            'spectral_radius': esn.get_spectral_radius(),
            'effective_spectral_radius': esn.get_effective_spectral_radius()
        }
    
    @staticmethod
    def measure_memory_capacity(esn: EchoStateNetwork, max_delay: int = 50, 
                              n_samples: int = 2000) -> Dict[str, Any]:
        """
        Measure memory capacity following Jaeger 2001
        
        Memory capacity is the sum of correlation coefficients between
        delayed input signals and linear readouts
        """
        if esn.input_dim is None:
            esn.initialize_reservoir(1)
            
        # Generate random input sequence
        inputs = np.random.uniform(-1, 1, (n_samples + max_delay, 1))
        
        # Collect reservoir states
        states = esn.collect_states(inputs)
        
        # Calculate memory capacity for each delay
        memory_capacities = []
        
        for delay in range(1, max_delay + 1):
            # Target is input delayed by 'delay' steps
            targets = inputs[:-delay] if delay > 0 else inputs
            states_subset = states[delay:]
            
            # Train linear readout for this delay
            states_with_bias = np.column_stack([states_subset, np.ones(len(states_subset))])
            
            try:
                weights = linalg.pinv(states_with_bias) @ targets
                predictions = states_with_bias @ weights
                
                # Calculate correlation coefficient
                correlation = np.corrcoef(predictions.flatten(), targets.flatten())[0, 1]
                memory_capacity = correlation**2 if not np.isnan(correlation) else 0
                
            except:
                memory_capacity = 0
                
            memory_capacities.append(memory_capacity)
        
        total_capacity = np.sum(memory_capacities)
        theoretical_max = esn.reservoir_size  # Theoretical upper bound
        efficiency = total_capacity / theoretical_max
        
        return {
            'total_memory_capacity': total_capacity,
            'memory_capacities_by_delay': memory_capacities,
            'efficiency': efficiency,
            'theoretical_maximum': theoretical_max,
            'effective_delays': np.sum(np.array(memory_capacities) > 0.01)  # Delays with >1% capacity
        }


class StructuredReservoirTopologies:
    """Advanced reservoir topologies beyond basic random"""
    
    @staticmethod
    def create_ring_topology(size: int, k: int = 4) -> np.ndarray:
        """Create ring topology with k neighbors"""
        W = np.zeros((size, size))
        
        for i in range(size):
            for j in range(1, k//2 + 1):
                # Forward connections
                W[i, (i + j) % size] = np.random.normal(0, 1)
                # Backward connections  
                W[i, (i - j) % size] = np.random.normal(0, 1)
                
        return W
    
    @staticmethod
    def create_small_world_topology(size: int, k: int = 6, p: float = 0.1) -> np.ndarray:
        """Watts-Strogatz small-world topology"""
        W = StructuredReservoirTopologies.create_ring_topology(size, k)
        
        # Rewire edges with probability p
        for i in range(size):
            for j in range(1, k//2 + 1):
                if np.random.random() < p:
                    # Remove old edge
                    old_target = (i + j) % size
                    W[i, old_target] = 0
                    
                    # Add new random edge
                    new_target = np.random.randint(0, size)
                    while new_target == i or W[i, new_target] != 0:
                        new_target = np.random.randint(0, size)
                    W[i, new_target] = np.random.normal(0, 1)
        
        return W
    
    @staticmethod 
    def create_scale_free_topology(size: int, m: int = 3) -> np.ndarray:
        """Barabási-Albert scale-free topology"""
        W = np.zeros((size, size))
        degrees = np.zeros(size)
        
        # Start with complete graph of m+1 nodes
        for i in range(min(m+1, size)):
            for j in range(i+1, min(m+1, size)):
                weight = np.random.normal(0, 1)
                W[i, j] = weight
                W[j, i] = weight
                degrees[i] += 1
                degrees[j] += 1
        
        # Add remaining nodes with preferential attachment
        for i in range(m+1, size):
            targets = set()
            
            while len(targets) < m:
                # Preferential attachment probabilities
                if np.sum(degrees[:i]) > 0:
                    probs = degrees[:i] / np.sum(degrees[:i])
                    target = np.random.choice(i, p=probs)
                    targets.add(target)
                else:
                    targets.add(np.random.randint(0, i))
            
            # Connect to chosen targets
            for target in targets:
                weight = np.random.normal(0, 1)
                W[i, target] = weight
                W[target, i] = weight
                degrees[i] += 1
                degrees[target] += 1
        
        return W


class JaegerBenchmarkTasks:
    """Benchmark tasks from Jaeger 2001 paper for validation"""
    
    @staticmethod
    def henon_map_task(n_steps: int = 5000, a: float = 1.4, b: float = 0.3) -> Tuple[np.ndarray, np.ndarray]:
        """
        Henon map chaotic system prediction task
        
        x(n+1) = 1 - a*x(n)² + y(n)
        y(n+1) = b*x(n)
        """
        x, y = 0.0, 0.0
        trajectory = []
        
        for _ in range(n_steps):
            x_next = 1 - a * x**2 + y
            y_next = b * x
            x, y = x_next, y_next
            trajectory.append([x, y])
        
        trajectory = np.array(trajectory)
        inputs = trajectory[:-1]    # Current state
        targets = trajectory[1:]    # Next state
        
        return inputs, targets
    
    @staticmethod  
    def lorenz_attractor_task(n_steps: int = 10000, dt: float = 0.01,
                            sigma: float = 10.0, rho: float = 28.0, 
                            beta: float = 8.0/3.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Lorenz attractor generation task
        
        dx/dt = σ(y - x)
        dy/dt = x(ρ - z) - y  
        dz/dt = xy - βz
        """
        x, y, z = 1.0, 1.0, 1.0
        trajectory = []
        
        for _ in range(n_steps):
            dx = sigma * (y - x) * dt
            dy = (x * (rho - z) - y) * dt
            dz = (x * y - beta * z) * dt
            
            x += dx
            y += dy
            z += dz
            
            trajectory.append([x, y, z])
        
        trajectory = np.array(trajectory)
        inputs = trajectory[:-1]
        targets = trajectory[1:]
        
        return inputs, targets
    
    @staticmethod
    def sine_wave_task(n_steps: int = 2000, frequency: float = 0.1, 
                      noise_level: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """Simple sine wave prediction task"""
        t = np.arange(n_steps) * 2 * np.pi * frequency
        signal = np.sin(t)
        
        if noise_level > 0:
            signal += np.random.normal(0, noise_level, n_steps)
        
        inputs = signal[:-1].reshape(-1, 1)
        targets = signal[1:].reshape(-1, 1)
        
        return inputs, targets
    
    @staticmethod
    def pattern_classification_task(n_patterns: int = 100, 
                                  pattern_length: int = 50) -> Tuple[List[np.ndarray], np.ndarray]:
        """
        Temporal pattern classification task
        Generate sequences that belong to different classes
        """
        patterns = []
        labels = []
        
        for i in range(n_patterns):
            class_id = i % 3  # 3 classes
            
            if class_id == 0:
                # Sine wave with specific frequency
                t = np.linspace(0, 4*np.pi, pattern_length)
                pattern = np.sin(t).reshape(-1, 1)
            elif class_id == 1:
                # Square wave
                t = np.linspace(0, 4*np.pi, pattern_length)
                pattern = np.sign(np.sin(t)).reshape(-1, 1)
            else:
                # Random walk
                pattern = np.cumsum(np.random.normal(0, 0.1, pattern_length)).reshape(-1, 1)
                
            patterns.append(pattern)
            labels.append(class_id)
        
        return patterns, np.array(labels)


class OutputFeedbackESN(EchoStateNetwork):
    """ESN with output feedback capabilities"""
    
    def __init__(self, feedback_scaling: float = 0.1, **kwargs):
        kwargs['output_feedback'] = True
        kwargs['feedback_scaling'] = feedback_scaling
        super().__init__(**kwargs)


class TeacherForcingTrainer:
    """Advanced training with teacher forcing capabilities"""
    
    def __init__(self, esn: EchoStateNetwork):
        self.esn = esn
        
    def train_with_teacher_forcing(self, inputs: np.ndarray, targets: np.ndarray, 
                                  teacher_forcing_ratio: float = 1.0):
        """Train with probabilistic teacher forcing"""
        n_steps = len(inputs)
        states = []
        
        # Reset state
        self.esn.reset_state()
        
        for t in range(n_steps):
            # Decide whether to use teacher forcing
            use_teacher_forcing = np.random.random() < teacher_forcing_ratio
            
            # Determine feedback signal
            feedback = None
            if self.esn.output_feedback:
                if use_teacher_forcing and t > 0:
                    feedback = targets[t-1]
                else:
                    feedback = self.esn.last_output
            
            # Update state and collect
            state = self.esn.update_state(inputs[t], feedback)
            states.append(state)
        
        return np.array(states)


class OnlineLearningESN:
    """Online learning methods for ESN"""
    
    def __init__(self, esn: EchoStateNetwork, forgetting_factor: float = 0.999):
        self.esn = esn
        self.forgetting_factor = forgetting_factor
        
        # RLS parameters
        self.P = None  # Inverse correlation matrix
        self.w = None  # Weight vector
        
    def initialize_rls(self, n_features: int, initial_variance: float = 1000.0):
        """Initialize recursive least squares"""
        self.P = np.eye(n_features) * initial_variance
        self.w = np.zeros(n_features)
        
    def update_online(self, state: np.ndarray, target: float) -> float:
        """Online RLS update with single (state, target) pair"""
        if self.P is None:
            n_features = len(state) + 1  # +1 for bias
            self.initialize_rls(n_features)
            
        # Add bias term
        x = np.append(state, 1.0)
        
        # RLS update equations
        k = (self.P @ x) / (self.forgetting_factor + x.T @ self.P @ x)
        prediction = x.T @ self.w
        error = target - prediction
        
        self.w = self.w + k * error
        self.P = (self.P - np.outer(k, x.T @ self.P)) / self.forgetting_factor
        
        return prediction


# ==================== UTILITY FUNCTIONS ====================

def optimize_spectral_radius(esn_config: dict, inputs: np.ndarray, targets: np.ndarray, 
                           search_range: Tuple[float, float] = (0.5, 1.2), 
                           n_trials: int = 10) -> Tuple[float, float]:
    """
    Find optimal spectral radius via grid search
    Returns: (optimal_radius, best_error)
    """
    radii = np.linspace(search_range[0], search_range[1], n_trials)
    best_radius = radii[0]
    best_error = float('inf')
    
    for radius in radii:
        try:
            config = esn_config.copy()
            config['spectral_radius'] = radius
            
            esn = EchoStateNetwork(**config)
            esn.train(inputs, targets)
            error = esn.training_error
            
            if error < best_error:
                best_error = error
                best_radius = radius
                
        except Exception as e:
            print(f"Warning: Failed to test radius {radius}: {e}")
            continue
    
    return best_radius, best_error


def validate_esp(esn: EchoStateNetwork, verbose: bool = True) -> bool:
    """Quick validation of Echo State Property"""
    validator = EchoStatePropertyValidator()
    results = validator.verify_echo_state_property(esn)
    
    if verbose:
        print(f"Echo State Property: {'✓ SATISFIED' if results['esp_satisfied'] else '✗ VIOLATED'}")
        print(f"Spectral Radius: {results['spectral_radius']:.3f}")
        print(f"Effective Spectral Radius: {results['effective_spectral_radius']:.3f}")
        print(f"Max Pairwise Distance: {results['max_pairwise_distance']:.2e}")
    
    return results['esp_satisfied']


def run_benchmark_suite(esn: EchoStateNetwork, verbose: bool = True) -> Dict[str, float]:
    """Run complete benchmark task suite"""
    results = {}
    
    if verbose:
        print("🔬 Running ESN Benchmark Suite")
        print("=" * 40)
    
    # 1. Henon Map Prediction
    try:
        inputs, targets = JaegerBenchmarkTasks.henon_map_task(2000)
        esn.train(inputs[:1500], targets[:1500])
        preds = esn.predict(inputs[1500:])
        henon_error = np.mean((preds - targets[1500:])**2)
        results['henon_mse'] = henon_error
        
        if verbose:
            print(f"✓ Henon Map MSE: {henon_error:.4f}")
    except Exception as e:
        results['henon_mse'] = float('inf')
        if verbose:
            print(f"✗ Henon Map failed: {e}")
    
    # 2. Sine Wave Prediction  
    try:
        inputs, targets = JaegerBenchmarkTasks.sine_wave_task(1000)
        esn.train(inputs[:800], targets[:800])
        preds = esn.predict(inputs[800:])
        sine_error = np.mean((preds - targets[800:])**2)
        results['sine_mse'] = sine_error
        
        if verbose:
            print(f"✓ Sine Wave MSE: {sine_error:.4f}")
    except Exception as e:
        results['sine_mse'] = float('inf')  
        if verbose:
            print(f"✗ Sine Wave failed: {e}")
    
    # 3. Memory Capacity
    try:
        validator = EchoStatePropertyValidator()
        mc_results = validator.measure_memory_capacity(esn)
        results['memory_capacity'] = mc_results['total_memory_capacity']
        
        if verbose:
            print(f"✓ Memory Capacity: {mc_results['total_memory_capacity']:.2f}")
    except Exception as e:
        results['memory_capacity'] = 0
        if verbose:
            print(f"✗ Memory Capacity failed: {e}")
    
    return results


# ==================== DEMONSTRATION FUNCTION ====================

def demonstrate_unified_esn():
    """Complete demonstration of unified ESN functionality"""
    print("🌊 Unified Echo State Network Demonstration")
    print("=" * 50)
    
    # 1. Basic ESN
    print("\n1. Basic ESN Configuration")
    esn = EchoStateNetwork(
        reservoir_size=100,
        spectral_radius=0.95,
        leak_rate=0.3,
        connectivity=0.1
    )
    
    # 2. Test Echo State Property
    print("\n2. Validating Echo State Property")
    esp_valid = validate_esp(esn)
    
    # 3. Advanced topology
    print("\n3. Advanced Topology ESN")
    esn_advanced = EchoStateNetwork(
        reservoir_size=200,
        reservoir_topology='small_world',
        spectral_radius=0.9,
        output_feedback=True
    )
    
    # 4. Run benchmark tasks
    print("\n4. Benchmark Task Performance")
    benchmark_results = run_benchmark_suite(esn)
    
    # 5. Memory capacity analysis
    print("\n5. Memory Capacity Analysis")
    validator = EchoStatePropertyValidator()
    mc_results = validator.measure_memory_capacity(esn)
    print(f"   Total Capacity: {mc_results['total_memory_capacity']:.2f}")
    print(f"   Efficiency: {mc_results['efficiency']:.1%}")
    
    print("\n✅ Unified ESN demonstration complete!")
    print("🚀 All features integrated successfully!")


if __name__ == "__main__":
    demonstrate_unified_esn()