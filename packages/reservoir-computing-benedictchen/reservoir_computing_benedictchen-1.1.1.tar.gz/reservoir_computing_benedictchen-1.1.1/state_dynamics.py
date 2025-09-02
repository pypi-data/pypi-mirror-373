"""
State Dynamics for Echo State Networks
Handles state updates, feedback processing, and temporal dynamics
"""

import numpy as np
from typing import Optional, Dict, Any, List


class StateDynamics:
    """Handles ESN state updates and temporal dynamics"""
    
    def __init__(self, esn_instance):
        self.esn = esn_instance
    
    def update_state(self, state: np.ndarray, input_vec: np.ndarray, 
                    output_feedback: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Core state update equation: x(t+1) = (1-α)x(t) + α·f(W_in·u(t) + W_res·x(t))
        From Jaeger 2001 Equation (1)
        """
        # Ensure proper input dimensions
        input_vec = self._ensure_input_dimensions(input_vec)
        
        # Compute reservoir input
        reservoir_input = self.esn.input_weights @ input_vec
        reservoir_recurrent = self.esn.reservoir_weights @ state
        
        # Ensure proper shapes
        if reservoir_input.ndim > 1:
            reservoir_input = reservoir_input.flatten()
        if reservoir_recurrent.ndim > 1:
            reservoir_recurrent = reservoir_recurrent.flatten()
        
        # Add bias if available
        if hasattr(self.esn, 'bias_vector') and self.esn.bias_vector is not None:
            bias_vector = self.esn.bias_vector
            # Ensure bias vector is 1D and same length as reservoir_input
            if bias_vector.ndim > 1:
                bias_vector = bias_vector.flatten()
            
            if len(bias_vector) == len(reservoir_input):
                reservoir_input += bias_vector
            else:
                # Skip bias if dimensions don't match
                import warnings
                warnings.warn(f"Bias vector length {len(bias_vector)} doesn't match reservoir input {len(reservoir_input)}. Skipping bias.")
        
        # Add output feedback if enabled
        if output_feedback is not None and hasattr(self.esn, 'output_feedback_weights'):
            feedback_contribution = self._compute_feedback_contribution(output_feedback)
            reservoir_input += feedback_contribution
        
        # Add noise if specified
        if hasattr(self.esn, 'noise_level') and self.esn.noise_level > 0:
            reservoir_input += self._apply_noise(reservoir_input)
        
        # Total net input
        net_input = reservoir_input + reservoir_recurrent
        
        # Apply activation function
        activated = self._apply_activation(net_input)
        
        # Apply leak rate (temporal integration)
        alpha = getattr(self.esn, 'leak_rate', 1.0)
        new_state = (1 - alpha) * state + alpha * activated
        
        # Ensure proper output shape
        if new_state.ndim > 1:
            new_state = new_state.flatten()
        
        return new_state
    
    def update_state_with_feedback(self, state: np.ndarray, input_vec: np.ndarray, 
                                 feedback: np.ndarray) -> np.ndarray:
        """Update state with explicit output feedback"""
        return self.update_state(state, input_vec, output_feedback=feedback)
    
    def run_reservoir(self, input_sequence: np.ndarray, 
                     initial_state: Optional[np.ndarray] = None,
                     washout: int = 0,
                     return_states: bool = True) -> np.ndarray:
        """
        Run reservoir through input sequence and collect states
        Implements Algorithm 1 from Jaeger 2001
        """
        seq_length, n_inputs = input_sequence.shape
        
        # Initialize state
        if initial_state is None:
            state = np.zeros(self.esn.reservoir_size)
        else:
            state = initial_state.copy()
        
        # Collect states
        if return_states:
            states = np.zeros((seq_length, self.esn.reservoir_size))
        
        # Run through sequence
        for t, input_vec in enumerate(input_sequence):
            state = self.update_state(state, input_vec)
            
            if return_states:
                states[t] = state
        
        # Apply washout (remove transient states)
        if washout > 0 and return_states:
            states = states[washout:]
        
        return states if return_states else state
    
    def run_with_teacher_forcing(self, input_sequence: np.ndarray,
                               target_sequence: np.ndarray,
                               initial_state: Optional[np.ndarray] = None) -> np.ndarray:
        """Run reservoir with teacher forcing (ground truth feedback)"""
        seq_length = len(input_sequence)
        
        if initial_state is None:
            state = np.zeros(self.esn.reservoir_size)
        else:
            state = initial_state.copy()
        
        states = np.zeros((seq_length, self.esn.reservoir_size))
        
        for t in range(seq_length):
            # Use ground truth as feedback
            feedback = target_sequence[t] if t > 0 else None
            state = self.update_state(state, input_sequence[t], feedback)
            states[t] = state
        
        return states
    
    def run_autonomous(self, n_steps: int, 
                      initial_state: Optional[np.ndarray] = None,
                      initial_output: Optional[np.ndarray] = None) -> tuple:
        """Run ESN autonomously (closed-loop) for prediction"""
        if not hasattr(self.esn, 'output_weights') or self.esn.output_weights is None:
            raise ValueError("ESN must be trained before autonomous operation")
        
        if initial_state is None:
            state = np.zeros(self.esn.reservoir_size)
        else:
            state = initial_state.copy()
        
        states = np.zeros((n_steps, self.esn.reservoir_size))
        outputs = np.zeros((n_steps, self.esn.n_outputs))
        
        current_output = initial_output
        
        for t in range(n_steps):
            # Use previous output as input (autonomous mode)
            if current_output is not None:
                input_vec = current_output  # Output feedback as input
            else:
                input_vec = np.zeros(self.esn.n_inputs)
            
            # Update state
            state = self.update_state(state, input_vec, current_output)
            
            # Compute output
            current_output = self._compute_output(state)
            
            states[t] = state
            outputs[t] = current_output
        
        return states, outputs
    
    def _ensure_input_dimensions(self, input_vec: np.ndarray) -> np.ndarray:
        """Ensure input vector has correct dimensions"""
        if self.esn.n_inputs is None:
            # If n_inputs not set, infer from input_weights shape
            if hasattr(self.esn, 'input_weights') and self.esn.input_weights is not None:
                expected_inputs = self.esn.input_weights.shape[1]
            else:
                # Default to input vector length
                return input_vec
        else:
            expected_inputs = self.esn.n_inputs
            
        if len(input_vec) != expected_inputs:
            if len(input_vec) < expected_inputs:
                # Pad with zeros
                padded = np.zeros(expected_inputs)
                padded[:len(input_vec)] = input_vec
                return padded
            else:
                # Truncate
                return input_vec[:expected_inputs]
        return input_vec
    
    def _compute_feedback_contribution(self, output_feedback: np.ndarray) -> np.ndarray:
        """Compute output feedback contribution to reservoir input"""
        if hasattr(self.esn, 'output_feedback_weights') and self.esn.output_feedback_weights is not None:
            # Ensure proper dimensions for matrix multiplication
            feedback_weights = self.esn.output_feedback_weights
            if feedback_weights.size == 0:
                return np.zeros(self.esn.reservoir_size)
            
            # Ensure output_feedback is properly shaped
            if output_feedback.ndim == 0:
                output_feedback = np.array([output_feedback])
            elif output_feedback.ndim > 1:
                output_feedback = output_feedback.flatten()
            
            # Ensure feedback_weights has proper dimensions
            if feedback_weights.ndim == 1:
                feedback_weights = feedback_weights.reshape(-1, 1)
            
            return feedback_weights @ output_feedback
        return np.zeros(self.esn.reservoir_size)
    
    def _apply_noise(self, reservoir_input: np.ndarray) -> np.ndarray:
        """Apply noise to reservoir input"""
        noise_scale = getattr(self.esn, 'noise_level', 0.0)
        if noise_scale > 0:
            return np.random.normal(0, noise_scale, size=reservoir_input.shape)
        return np.zeros_like(reservoir_input)
    
    def _apply_activation(self, net_input: np.ndarray) -> np.ndarray:
        """Apply activation function to net input"""
        activation_fn = getattr(self.esn, 'activation_function', 'tanh')
        
        if callable(activation_fn):
            return activation_fn(net_input)
        elif activation_fn == 'tanh':
            return np.tanh(net_input)
        elif activation_fn == 'sigmoid':
            return 1 / (1 + np.exp(-np.clip(net_input, -500, 500)))
        elif activation_fn == 'relu':
            return np.maximum(0, net_input)
        elif activation_fn == 'linear':
            return net_input
        else:
            # Default to tanh
            return np.tanh(net_input)
    
    def _compute_output(self, state: np.ndarray) -> np.ndarray:
        """Compute output from current state"""
        if hasattr(self.esn, 'output_weights') and self.esn.output_weights is not None:
            # Add bias term if available
            if hasattr(self.esn, 'output_bias') and self.esn.output_bias is not None:
                extended_state = np.concatenate([state, [1.0]])  # Add bias
                
                # Handle bias concatenation properly
                bias = self.esn.output_bias
                weights = self.esn.output_weights
                
                # Ensure weights are 2D
                if weights.ndim == 1:
                    weights = weights.reshape(1, -1)  # Shape: (n_outputs, n_reservoir)
                    
                # Ensure bias is proper shape for concatenation
                if bias.ndim == 1:
                    bias = bias.reshape(-1, 1)  # Shape: (n_outputs, 1)
                elif bias.ndim == 2 and bias.shape[1] != 1:
                    bias = bias.reshape(-1, 1)
                
                # Concatenate weights and bias along feature axis
                extended_weights = np.concatenate([weights, bias], axis=1)  # Shape: (n_outputs, n_reservoir + 1)
                output = extended_weights @ extended_state  # extended_state has shape (n_reservoir + 1,)
                
                return output.flatten() if output.ndim > 1 and output.shape[0] == 1 else output
            else:
                # Simple case without bias
                weights = self.esn.output_weights
                if weights.ndim == 1:
                    return weights @ state
                else:
                    output = weights @ state
                    return output.flatten() if output.ndim > 1 and output.shape[0] == 1 else output
        else:
            raise ValueError("Output weights not available")
    
    def apply_multiple_timescales(self, state: np.ndarray, input_vec: np.ndarray,
                                timescale_groups: List[Dict[str, Any]]) -> np.ndarray:
        """Apply different leak rates to different neuron groups"""
        new_state = state.copy()
        
        # Compute base activations
        reservoir_input = self.esn.input_weights @ input_vec
        reservoir_recurrent = self.esn.reservoir_weights @ state
        net_input = reservoir_input + reservoir_recurrent
        activated = self._apply_activation(net_input)
        
        # Apply different timescales to different groups
        for group in timescale_groups:
            indices = group.get('indices', range(len(state)))
            leak_rate = group.get('leak_rate', 1.0)
            
            # Apply group-specific leak rate
            for idx in indices:
                if idx < len(state):
                    new_state[idx] = (1 - leak_rate) * state[idx] + leak_rate * activated[idx]
        
        return new_state
    
    def compute_state_statistics(self, states: np.ndarray) -> Dict[str, Any]:
        """Compute statistical properties of reservoir states"""
        return {
            'mean_activation': np.mean(states, axis=0),
            'std_activation': np.std(states, axis=0),
            'max_activation': np.max(states, axis=0),
            'min_activation': np.min(states, axis=0),
            'mean_activity': np.mean(np.abs(states)),
            'state_diversity': np.mean(np.std(states, axis=1)),
            'temporal_correlation': self._compute_temporal_correlation(states)
        }
    
    def _compute_temporal_correlation(self, states: np.ndarray) -> float:
        """Compute average temporal correlation in states"""
        if len(states) < 2:
            return 0.0
        
        correlations = []
        for i in range(states.shape[1]):
            if len(states) > 1:
                correlation = np.corrcoef(states[:-1, i], states[1:, i])[0, 1]
                if not np.isnan(correlation):
                    correlations.append(correlation)
        
        return np.mean(correlations) if correlations else 0.0