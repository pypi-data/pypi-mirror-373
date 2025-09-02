"""
Echo State Property Validation for ESN
Implements ESP validation methods from Jaeger 2001 and extensions
"""

import numpy as np
from typing import Tuple, List, Dict, Any, Optional
import warnings


class EchoStatePropertyValidator:
    """Validates Echo State Property for reservoir networks"""
    
    def __init__(self, esn_instance):
        self.esn = esn_instance
    
    def validate_comprehensive_esp(self) -> Dict[str, Any]:
        """Comprehensive ESP validation using multiple methods"""
        results = {}
        
        # Method 1: Spectral radius check
        results['spectral_radius_check'] = self._validate_spectral_radius()
        
        # Method 2: Convergence test
        results['convergence_test'] = self._validate_convergence()
        
        # Method 3: Lyapunov exponent
        try:
            results['lyapunov_test'] = self._validate_lyapunov()
        except Exception as e:
            results['lyapunov_test'] = {'valid': False, 'error': str(e)}
        
        # Method 4: Jacobian analysis
        try:
            results['jacobian_test'] = self._validate_jacobian()
        except Exception as e:
            results['jacobian_test'] = {'valid': False, 'error': str(e)}
        
        # Overall ESP status
        valid_tests = [r.get('valid', False) for r in results.values() if isinstance(r, dict)]
        overall_valid = np.mean(valid_tests) > 0.5
        results['overall_esp_valid'] = overall_valid
        results['valid'] = overall_valid  # Compatibility with test expectations
        results['validation_confidence'] = np.mean(valid_tests)
        
        return results
    
    def _validate_spectral_radius(self) -> Dict[str, Any]:
        """Basic spectral radius validation"""
        eigenvals = np.linalg.eigvals(self.esn.reservoir_weights)
        spectral_radius = np.max(np.abs(eigenvals))
        
        return {
            'valid': spectral_radius < 1.0,
            'spectral_radius': float(spectral_radius),
            'method': 'spectral_radius',
            'confidence': 0.8 if spectral_radius < 0.95 else 0.6
        }
    
    def _validate_convergence(self, n_tests: int = 10, test_length: int = 1500, 
                            tolerance: float = 1e-6) -> Dict[str, Any]:
        """Test ESP through state convergence from different initial conditions"""
        convergence_results = []
        
        for test in range(n_tests):
            # Create two different initial states
            state1 = np.random.randn(self.esn.reservoir_size) * 0.1
            state2 = np.random.randn(self.esn.reservoir_size) * 0.1
            
            # Generate test input sequence
            input_seq = np.random.randn(test_length, self.esn.n_inputs) * 0.5
            
            # Run both states through same input sequence
            states1 = self._run_test_sequence(state1, input_seq)
            states2 = self._run_test_sequence(state2, input_seq)
            
            # Check final convergence
            final_diff = np.linalg.norm(states1[-1] - states2[-1])
            convergence_results.append(final_diff < tolerance)
        
        convergence_rate = np.mean(convergence_results)
        
        return {
            'valid': convergence_rate > 0.8,
            'convergence_rate': float(convergence_rate),
            'method': 'state_convergence',
            'n_tests': n_tests,
            'confidence': min(convergence_rate, 0.95)
        }
    
    def _validate_lyapunov(self) -> Dict[str, Any]:
        """Validate ESP using Lyapunov exponent analysis"""
        n_steps = 1000
        initial_state = np.random.randn(self.esn.reservoir_size) * 0.1
        input_seq = np.random.randn(n_steps, self.esn.n_inputs) * 0.5
        
        # Compute Lyapunov exponent
        lyapunov_sum = 0.0
        current_state = initial_state.copy()
        
        for t in range(n_steps):
            # Compute Jacobian at current state
            jacobian = self._compute_jacobian_at_state(current_state, input_seq[t])
            
            # Update Lyapunov sum
            eigenvals = np.linalg.eigvals(jacobian)
            max_eigenval = np.max(np.real(eigenvals))
            lyapunov_sum += np.log(abs(max_eigenval)) if max_eigenval != 0 else -10
            
            # Update state
            current_state = self._update_state_for_validation(current_state, input_seq[t])
        
        lyapunov_exponent = lyapunov_sum / n_steps
        
        return {
            'valid': lyapunov_exponent < 0,
            'lyapunov_exponent': float(lyapunov_exponent),
            'method': 'lyapunov_exponent',
            'confidence': 0.9 if lyapunov_exponent < -0.1 else 0.7
        }
    
    def _validate_jacobian(self) -> Dict[str, Any]:
        """Validate ESP through Jacobian spectral radius analysis"""
        # Sample random states and inputs
        n_samples = 20
        jacobian_radii = []
        
        for _ in range(n_samples):
            state = np.random.randn(self.esn.reservoir_size) * 0.5
            input_vec = np.random.randn(self.esn.n_inputs) * 0.5
            
            jacobian = self._compute_jacobian_at_state(state, input_vec)
            eigenvals = np.linalg.eigvals(jacobian)
            spectral_radius = np.max(np.abs(eigenvals))
            jacobian_radii.append(spectral_radius)
        
        mean_radius = np.mean(jacobian_radii)
        std_radius = np.std(jacobian_radii)
        
        return {
            'valid': mean_radius < 1.0,
            'mean_jacobian_radius': float(mean_radius),
            'std_jacobian_radius': float(std_radius),
            'method': 'jacobian_analysis',
            'confidence': 0.85 if mean_radius < 0.9 else 0.6
        }
    
    def _compute_jacobian_at_state(self, state: np.ndarray, input_vec: np.ndarray) -> np.ndarray:
        """Compute Jacobian of state update at given state and input"""
        # For tanh activation: d/dx tanh(x) = 1 - tanh²(x)
        net_input = (self.esn.input_weights @ input_vec + 
                    self.esn.reservoir_weights @ state)
        
        if hasattr(self.esn, 'bias_vector') and self.esn.bias_vector is not None:
            net_input += self.esn.bias_vector
        
        # Derivative of tanh
        tanh_derivative = 1 - np.tanh(net_input)**2
        
        # Jacobian: J = (1-α)I + α * diag(tanh'(net)) * W_res
        alpha = getattr(self.esn, 'leak_rate', 1.0)
        identity = np.eye(self.esn.reservoir_size)
        
        jacobian = ((1 - alpha) * identity + 
                   alpha * np.diag(tanh_derivative) @ self.esn.reservoir_weights)
        
        return jacobian
    
    def _run_test_sequence(self, initial_state: np.ndarray, 
                          input_sequence: np.ndarray) -> List[np.ndarray]:
        """Run ESN through test sequence for validation"""
        states = [initial_state.copy()]
        current_state = initial_state.copy()
        
        for input_vec in input_sequence:
            current_state = self._update_state_for_validation(current_state, input_vec)
            states.append(current_state.copy())
        
        return states
    
    def _update_state_for_validation(self, state: np.ndarray, 
                                   input_vec: np.ndarray) -> np.ndarray:
        """Update state for validation (simplified version)"""
        # Ensure input dimensions
        if len(input_vec) != self.esn.n_inputs:
            input_vec = np.resize(input_vec, self.esn.n_inputs)
        
        # Basic state update
        net_input = (self.esn.input_weights @ input_vec + 
                    self.esn.reservoir_weights @ state)
        
        if hasattr(self.esn, 'bias_vector') and self.esn.bias_vector is not None:
            net_input += self.esn.bias_vector
        
        # Apply activation
        activated = np.tanh(net_input)
        
        # Apply leak rate
        alpha = getattr(self.esn, 'leak_rate', 1.0)
        new_state = (1 - alpha) * state + alpha * activated
        
        return new_state
    
    def validate_echo_state_property_fast(self, n_tests: int = 3, 
                                        test_length: int = 100,
                                        tolerance: float = 1e-4) -> Dict[str, Any]:
        """Fast ESP validation for real-time use"""
        # Quick spectral radius check
        spectral_check = self._validate_spectral_radius()
        if not spectral_check['valid']:
            return {
                'valid': False,
                'method': 'fast_spectral',
                'reason': 'spectral_radius_exceeded',
                **spectral_check
            }
        
        # Quick convergence test
        convergence_results = []
        for _ in range(n_tests):
            state1 = np.random.randn(self.esn.reservoir_size) * 0.1
            state2 = np.random.randn(self.esn.reservoir_size) * 0.1
            input_seq = np.random.randn(test_length, self.esn.n_inputs) * 0.5
            
            # Short test
            for input_vec in input_seq[-20:]:  # Only last 20 steps
                state1 = self._update_state_for_validation(state1, input_vec)
                state2 = self._update_state_for_validation(state2, input_vec)
            
            diff = np.linalg.norm(state1 - state2)
            convergence_results.append(diff < tolerance * 10)  # More lenient
        
        convergence_rate = np.mean(convergence_results)
        
        return {
            'valid': convergence_rate > 0.6,
            'convergence_rate': float(convergence_rate),
            'spectral_radius': spectral_check['spectral_radius'],
            'method': 'fast_validation',
            'confidence': min(convergence_rate * 0.8, 0.8)
        }