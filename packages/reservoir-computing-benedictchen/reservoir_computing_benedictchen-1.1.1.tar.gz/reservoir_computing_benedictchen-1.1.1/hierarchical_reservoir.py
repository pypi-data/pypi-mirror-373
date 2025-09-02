"""
Hierarchical Reservoir Computing Implementation
Based on: Pathak et al. (2018) "Hybrid forecasting of chaotic processes"

Implements multi-level reservoir hierarchies for complex temporal processing.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from .echo_state_network import EchoStateNetwork


class HierarchicalReservoir:
    """
    Hierarchical Echo State Network
    
    Creates a hierarchy of reservoirs where higher levels process
    increasingly abstracted representations of the input dynamics.
    """
    
    def __init__(
        self,
        reservoir_sizes: List[int] = [500, 200, 100],
        spectral_radii: List[float] = [0.95, 0.9, 0.85],
        sparsities: List[float] = [0.1, 0.15, 0.2],
        input_scalings: List[float] = [1.0, 0.5, 0.3],
        inter_level_scaling: float = 0.1,
        random_seed: Optional[int] = None
    ):
        """
        Initialize Hierarchical Reservoir
        
        Args:
            reservoir_sizes: Sizes of reservoirs at each level
            spectral_radii: Spectral radius for each level
            sparsities: Sparsity for each level
            input_scalings: Input scaling for each level
            inter_level_scaling: Scaling for connections between levels
            random_seed: Random seed for reproducibility
        """
        
        self.n_levels = len(reservoir_sizes)
        self.reservoir_sizes = reservoir_sizes
        self.inter_level_scaling = inter_level_scaling
        
        if random_seed is not None:
            np.random.seed(random_seed)
            
        # Create ESN for each level
        self.reservoirs = []
        for i in range(self.n_levels):
            esn = EchoStateNetwork(
                n_reservoir=reservoir_sizes[i],
                spectral_radius=spectral_radii[i] if i < len(spectral_radii) else 0.9,
                sparsity=sparsities[i] if i < len(sparsities) else 0.1,
                input_scaling=input_scalings[i] if i < len(input_scalings) else 1.0,
                random_seed=random_seed + i if random_seed is not None else None
            )
            self.reservoirs.append(esn)
            
        # Inter-level connection matrices
        self.W_inter = []
        for i in range(self.n_levels - 1):
            # Connection from level i to level i+1
            W = np.random.uniform(
                -inter_level_scaling,
                inter_level_scaling,
                (reservoir_sizes[i+1], reservoir_sizes[i])
            )
            self.W_inter.append(W)
            
        # Training state
        self.is_trained = False
        self.readout_weights = []
        self.last_states = None
        
        print(f"✓ Hierarchical Reservoir initialized:")
        print(f"   Levels: {self.n_levels}")
        print(f"   Sizes: {reservoir_sizes}")
        
    def run_hierarchy(self, inputs: np.ndarray, washout: int = 100) -> List[np.ndarray]:
        """
        Run input through hierarchical reservoirs
        
        Args:
            inputs: Input sequence (time_steps, n_inputs)
            washout: Washout period
            
        Returns:
            List of state sequences for each level
        """
        
        time_steps, n_inputs = inputs.shape
        
        # Initialize states for all levels
        states_per_level = [[] for _ in range(self.n_levels)]
        current_states = [np.zeros(size) for size in self.reservoir_sizes]
        
        # Initialize input weights for first level if needed
        if not hasattr(self.reservoirs[0], 'W_input'):
            self.reservoirs[0]._initialize_input_weights(n_inputs)
            
        # Process each time step
        for t in range(time_steps):
            # Level 0: Process external input
            current_states[0] = self.reservoirs[0]._update_state(
                current_states[0], inputs[t]
            )
            
            # Higher levels: Process lower level states + external input
            for level in range(1, self.n_levels):
                # Combine external input with lower level state
                lower_level_input = self.W_inter[level-1] @ current_states[level-1]
                
                # Initialize input weights for this level if needed
                if not hasattr(self.reservoirs[level], 'W_input'):
                    combined_input_size = n_inputs + len(lower_level_input)
                    self.reservoirs[level]._initialize_input_weights(combined_input_size)
                
                # Combine external input with processed lower level
                combined_input = np.concatenate([inputs[t], lower_level_input])
                
                current_states[level] = self.reservoirs[level]._update_state(
                    current_states[level], combined_input
                )
            
            # Collect states after washout
            if t >= washout:
                for level in range(self.n_levels):
                    states_per_level[level].append(current_states[level].copy())
                    
        # Store final states
        self.last_states = current_states
        
        # Convert to arrays
        return [np.array(states) for states in states_per_level]
        
    def train(self, inputs: np.ndarray, targets: np.ndarray, 
              reg_param: float = 1e-6, washout: int = 100,
              level_weights: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Train hierarchical reservoir
        
        Args:
            inputs: Training inputs
            targets: Training targets
            reg_param: Regularization parameter
            washout: Washout period
            level_weights: Weights for combining different levels
            
        Returns:
            Training results
        """
        
        print(f"🎯 Training Hierarchical Reservoir...")
        
        # Get states from all levels
        states_per_level = self.run_hierarchy(inputs, washout)
        
        # Combine states from all levels
        if level_weights is None:
            level_weights = [1.0] * self.n_levels
            
        combined_states = []
        for states, weight in zip(states_per_level, level_weights):
            if len(combined_states) == 0:
                combined_states = states * weight
            else:
                combined_states = np.column_stack([combined_states, states * weight])
                
        # Add bias term
        X = np.column_stack([combined_states, np.ones(len(combined_states))])
        y = targets[washout:]
        
        # Train linear readout
        from sklearn.linear_model import Ridge
        ridge = Ridge(alpha=reg_param)
        ridge.fit(X, y)
        
        self.W_out = ridge.coef_
        self.bias = ridge.intercept_
        self.is_trained = True
        
        # Calculate performance
        predictions = ridge.predict(X)
        mse = np.mean((predictions - y) ** 2)
        
        results = {
            'mse': mse,
            'n_levels': self.n_levels,
            'combined_state_dim': X.shape[1] - 1,  # Exclude bias
            'level_contributions': [states.shape[1] for states in states_per_level]
        }
        
        print(f"✓ Hierarchical training complete: MSE = {mse:.6f}")
        print(f"   Combined state dimension: {X.shape[1] - 1}")
        
        return results
        
    def predict(self, inputs: np.ndarray, washout: int = 100) -> np.ndarray:
        """Generate predictions using trained hierarchical reservoir"""
        
        if not self.is_trained:
            raise ValueError("Hierarchical reservoir must be trained first!")
            
        # Get states from all levels
        states_per_level = self.run_hierarchy(inputs, washout)
        
        # Combine states (using same weights as training)
        combined_states = []
        for states in states_per_level:
            if len(combined_states) == 0:
                combined_states = states
            else:
                combined_states = np.column_stack([combined_states, states])
                
        # Add bias term
        X = np.column_stack([combined_states, np.ones(len(combined_states))])
        
        # Generate predictions
        predictions = X @ self.W_out.T + self.bias
        
        return predictions
        
    def generate_hierarchical(self, n_steps: int, 
                             initial_input: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Generate sequence using hierarchical feedback
        """
        
        if not self.is_trained:
            raise ValueError("Hierarchical reservoir must be trained first!")
            
        if self.last_states is None:
            raise ValueError("Must run reservoir at least once before generation!")
            
        # Initialize
        states = [state.copy() for state in self.last_states]
        outputs = []
        
        if initial_input is None:
            current_input = np.zeros(self.reservoirs[0].W_input.shape[1])
        else:
            current_input = initial_input.copy()
            
        for step in range(n_steps):
            # Update level 0
            states[0] = self.reservoirs[0]._update_state(states[0], current_input)
            
            # Update higher levels
            for level in range(1, self.n_levels):
                lower_level_input = self.W_inter[level-1] @ states[level-1]
                combined_input = np.concatenate([current_input, lower_level_input])
                states[level] = self.reservoirs[level]._update_state(
                    states[level], combined_input
                )
            
            # Generate output from combined states
            combined_state = np.concatenate(states + [np.array([1.0])])  # Add bias
            output = combined_state @ self.W_out.T + self.bias
            
            outputs.append(output)
            
            # Use output as next input (closed loop)
            current_input = output if len(output) == len(current_input) else current_input
            
        return np.array(outputs)
        
    def get_level_analysis(self) -> Dict[str, Any]:
        """Analyze properties of each hierarchical level"""
        
        analysis = {
            'level_sizes': self.reservoir_sizes,
            'spectral_radii': [],
            'sparsities': [],
            'inter_level_connections': [W.shape for W in self.W_inter]
        }
        
        for reservoir in self.reservoirs:
            # Calculate spectral radius
            eigenvals = np.linalg.eigvals(reservoir.W_reservoir)
            spectral_radius = np.max(np.abs(eigenvals))
            analysis['spectral_radii'].append(spectral_radius)
            
            # Calculate sparsity
            sparsity = np.mean(reservoir.W_reservoir != 0)
            analysis['sparsities'].append(sparsity)
            
        return analysis