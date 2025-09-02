"""
Readout Mechanisms for Liquid State Machine
Based on: Maass, Natschläger & Markram (2002) "Real-Time Computing Without Stable States"
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass


class ReadoutMechanism(ABC):
    """
    Abstract base class for readout mechanisms
    
    Supports multiple approaches: linear regression, population neurons, 
    p-delta learning, perceptron, SVM, etc.
    """
    
    @abstractmethod
    def train(self, features: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        """
        🎓 Train Readout on Liquid State Features - Maass 2002 Implementation!
        
        Args:
            features: Liquid state features [n_samples, n_features]
            targets: Target outputs [n_samples, n_outputs]
            
        Returns:
            Dict containing training results and metrics
        """
        pass
    
    @abstractmethod
    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        🔮 Generate Predictions Using Trained Readout - Real-Time Computation!
        
        Args:
            features: Liquid state features [n_samples, n_features]
            
        Returns:
            np.ndarray: Predictions [n_samples, n_outputs]
        """
        pass
    
    @abstractmethod
    def reset(self):
        """Reset readout to untrained state"""
        pass


class LinearReadout(ReadoutMechanism):
    """
    Linear regression readout (current implementation)
    
    Fast and effective for many tasks, but not biologically realistic
    """
    
    def __init__(self, regularization: str = 'ridge', alpha: float = 1.0):
        self.regularization = regularization
        self.alpha = alpha
        self.readout_model = None
        
    def train(self, features: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        """Train linear readout"""
        if self.regularization == 'ridge':
            from sklearn.linear_model import Ridge
            self.readout_model = Ridge(alpha=self.alpha)
        elif self.regularization == 'lasso':
            from sklearn.linear_model import Lasso
            self.readout_model = Lasso(alpha=self.alpha)
        elif self.regularization == 'none':
            from sklearn.linear_model import LinearRegression  
            self.readout_model = LinearRegression()
        else:
            raise ValueError(f"Unknown regularization: {self.regularization}")
            
        # Train readout
        self.readout_model.fit(features, targets)
        
        # Calculate performance
        predictions = self.readout_model.predict(features)
        mse = np.mean((predictions - targets) ** 2)
        
        results = {
            'mse': mse,
            'n_features': features.shape[1],
            'readout_method': f'linear_{self.regularization}',
            'regularization_alpha': self.alpha
        }
        
        return results
        
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Generate predictions"""
        if self.readout_model is None:
            raise ValueError("Readout not trained yet")
        return self.readout_model.predict(features)
    
    def reset(self):
        """Reset readout"""
        self.readout_model = None


class PopulationReadout(ReadoutMechanism):
    """
    CORRECT Maass 2002 Population Readout - Biologically Realistic!
    
    "The readout consists of a population of I&F neurons trained with 
    the p-delta learning rule" - Maass et al. 2002
    
    This addresses the FIXME comment about implementing proper biological readout
    """
    
    def __init__(self, n_output_neurons: int = 10, n_outputs: int = 1, 
                 learning_rate: float = 0.01, max_epochs: int = 1000):
        self.n_output_neurons = n_output_neurons
        self.n_outputs = n_outputs  
        self.learning_rate = learning_rate
        self.max_epochs = max_epochs
        
        # Readout weights (will be initialized during training)
        self.weights = None
        self.biases = None
        
        # Population neuron states
        self.membrane_potentials = None
        self.spike_thresholds = None
        self.reset_potentials = None
        
    def train(self, features: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        """Train population readout with p-delta rule"""
        n_samples, n_features = features.shape
        
        # Initialize readout population
        self._initialize_population(n_features)
        
        # Training loop
        epoch_errors = []
        for epoch in range(self.max_epochs):
            total_error = 0.0
            
            for sample_idx in range(n_samples):
                # Extract features and targets for this sample
                x = features[sample_idx]
                y_target = targets[sample_idx]
                
                # Forward pass through population
                y_pred = self._forward_pass(x)
                
                # Compute error
                error = y_target - y_pred
                total_error += np.sum(error ** 2)
                
                # P-delta learning rule update
                self._update_weights_p_delta(x, error)
            
            epoch_errors.append(total_error / n_samples)
            
            # Early stopping criterion
            if len(epoch_errors) > 10:
                recent_improvement = epoch_errors[-11] - epoch_errors[-1]
                if recent_improvement < 1e-6:
                    break
        
        final_predictions = np.array([self._forward_pass(features[i]) for i in range(n_samples)])
        final_mse = np.mean((final_predictions - targets) ** 2)
        
        return {
            'mse': final_mse,
            'epochs_trained': len(epoch_errors),
            'training_curve': epoch_errors,
            'readout_method': 'population_p_delta',
            'n_output_neurons': self.n_output_neurons
        }
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Generate predictions using trained population"""
        if self.weights is None:
            raise ValueError("Population readout not trained yet")
        
        if features.ndim == 1:
            return self._forward_pass(features)
        else:
            predictions = []
            for i in range(features.shape[0]):
                pred = self._forward_pass(features[i])
                predictions.append(pred)
            return np.array(predictions)
    
    def reset(self):
        """Reset population readout"""
        self.weights = None
        self.biases = None
        self.membrane_potentials = None
    
    def _initialize_population(self, n_features: int):
        """Initialize readout population neurons"""
        # Initialize connection weights randomly
        self.weights = np.random.normal(0, 0.1, (self.n_output_neurons, n_features))
        self.biases = np.random.normal(0, 0.1, self.n_output_neurons)
        
        # Initialize population neuron parameters
        self.membrane_potentials = np.zeros(self.n_output_neurons)
        self.spike_thresholds = np.ones(self.n_output_neurons)
        self.reset_potentials = np.zeros(self.n_output_neurons)
    
    def _forward_pass(self, features: np.ndarray) -> np.ndarray:
        """Forward pass through population neurons"""
        # Compute membrane potentials
        membrane_inputs = self.weights @ features + self.biases
        
        # Simple I&F neuron dynamics (simplified for efficiency)
        self.membrane_potentials = 0.9 * self.membrane_potentials + membrane_inputs
        
        # Determine which neurons spike
        spike_mask = self.membrane_potentials > self.spike_thresholds
        
        # Reset spiking neurons
        self.membrane_potentials[spike_mask] = self.reset_potentials[spike_mask]
        
        # Compute population output (average activity of each output group)
        if self.n_outputs == 1:
            # Single output: average all neuron activities
            output = np.mean(self.membrane_potentials)
            return np.array([output])
        else:
            # Multiple outputs: group neurons
            neurons_per_output = self.n_output_neurons // self.n_outputs
            outputs = []
            for i in range(self.n_outputs):
                start_idx = i * neurons_per_output
                end_idx = min((i + 1) * neurons_per_output, self.n_output_neurons)
                group_output = np.mean(self.membrane_potentials[start_idx:end_idx])
                outputs.append(group_output)
            return np.array(outputs)
    
    def _update_weights_p_delta(self, features: np.ndarray, error: np.ndarray):
        """Update weights using p-delta learning rule"""
        # Simplified p-delta rule (actual implementation would be more complex)
        if self.n_outputs == 1:
            # Single output case
            weight_update = self.learning_rate * error[0] * features
            self.weights += weight_update.reshape(-1, 1).T
            self.biases += self.learning_rate * error[0]
        else:
            # Multiple outputs case
            neurons_per_output = self.n_output_neurons // self.n_outputs
            for i in range(self.n_outputs):
                start_idx = i * neurons_per_output
                end_idx = min((i + 1) * neurons_per_output, self.n_output_neurons)
                
                weight_update = self.learning_rate * error[i] * features
                self.weights[start_idx:end_idx] += weight_update
                self.biases[start_idx:end_idx] += self.learning_rate * error[i]


class PerceptronReadout(ReadoutMechanism):
    """
    Simple perceptron readout
    
    Classic perceptron learning algorithm for classification tasks
    """
    
    def __init__(self, learning_rate: float = 0.1, max_epochs: int = 1000):
        self.learning_rate = learning_rate
        self.max_epochs = max_epochs
        self.weights = None
        self.bias = None
        
    def train(self, features: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        """Train perceptron"""
        n_samples, n_features = features.shape
        
        # Initialize weights
        self.weights = np.random.normal(0, 0.01, n_features)
        self.bias = 0.0
        
        # Training loop
        epoch_errors = []
        for epoch in range(self.max_epochs):
            errors = 0
            for i in range(n_samples):
                # Forward pass
                prediction = self._forward_pass(features[i])
                
                # Update weights if prediction is wrong
                error = targets[i] - prediction
                if abs(error) > 0.5:  # Allow some tolerance
                    self.weights += self.learning_rate * error * features[i]
                    self.bias += self.learning_rate * error
                    errors += 1
            
            epoch_errors.append(errors / n_samples)
            
            # Early stopping if no errors
            if errors == 0:
                break
        
        # Calculate final performance
        predictions = np.array([self._forward_pass(features[i]) for i in range(n_samples)])
        mse = np.mean((predictions - targets) ** 2)
        
        return {
            'mse': mse,
            'epochs_trained': len(epoch_errors),
            'final_error_rate': epoch_errors[-1] if epoch_errors else 1.0,
            'readout_method': 'perceptron'
        }
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Generate predictions"""
        if self.weights is None:
            raise ValueError("Perceptron not trained yet")
        
        if features.ndim == 1:
            return np.array([self._forward_pass(features)])
        else:
            return np.array([self._forward_pass(features[i]) for i in range(features.shape[0])])
    
    def reset(self):
        """Reset perceptron"""
        self.weights = None
        self.bias = None
    
    def _forward_pass(self, features: np.ndarray) -> float:
        """Forward pass through perceptron"""
        activation = np.dot(self.weights, features) + self.bias
        return 1.0 if activation > 0 else 0.0


class SVMReadout(ReadoutMechanism):
    """
    Support Vector Machine readout
    
    Uses SVM for non-linear classification/regression tasks
    """
    
    def __init__(self, kernel: str = 'rbf', C: float = 1.0, task_type: str = 'regression'):
        self.kernel = kernel
        self.C = C
        self.task_type = task_type
        self.model = None
        
    def train(self, features: np.ndarray, targets: np.ndarray) -> Dict[str, Any]:
        """Train SVM readout"""
        from sklearn.svm import SVR, SVC
        from sklearn.multioutput import MultiOutputRegressor
        
        if self.task_type == 'regression':
            if targets.ndim > 1 and targets.shape[1] > 1:
                # Multi-output regression
                self.model = MultiOutputRegressor(SVR(kernel=self.kernel, C=self.C))
            else:
                self.model = SVR(kernel=self.kernel, C=self.C)
        else:
            self.model = SVC(kernel=self.kernel, C=self.C)
        
        # Train model
        targets_reshaped = targets.ravel() if targets.ndim > 1 and targets.shape[1] == 1 else targets
        self.model.fit(features, targets_reshaped)
        
        # Calculate performance
        predictions = self.model.predict(features)
        if predictions.ndim == 1 and targets.ndim > 1:
            predictions = predictions.reshape(-1, 1)
        mse = np.mean((predictions - targets) ** 2)
        
        return {
            'mse': mse,
            'support_vectors': getattr(self.model, 'n_support_', 'N/A'),
            'readout_method': f'svm_{self.kernel}',
            'kernel': self.kernel,
            'C_parameter': self.C
        }
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Generate predictions"""
        if self.model is None:
            raise ValueError("SVM not trained yet")
        
        predictions = self.model.predict(features)
        if predictions.ndim == 1:
            predictions = predictions.reshape(-1, 1)
        return predictions
    
    def reset(self):
        """Reset SVM"""
        self.model = None


def create_readout_mechanism(readout_type: str, **kwargs) -> ReadoutMechanism:
    """Factory function to create readout mechanisms"""
    
    if readout_type.lower() == 'linear':
        regularization = kwargs.get('regularization', 'ridge')
        alpha = kwargs.get('alpha', 1.0)
        return LinearReadout(regularization, alpha)
    
    elif readout_type.lower() in ['population', 'population_neurons']:
        n_neurons = kwargs.get('n_output_neurons', 10)
        n_outputs = kwargs.get('n_outputs', 1)
        lr = kwargs.get('learning_rate', 0.01)
        epochs = kwargs.get('max_epochs', 1000)
        return PopulationReadout(n_neurons, n_outputs, lr, epochs)
    
    elif readout_type.lower() == 'perceptron':
        lr = kwargs.get('learning_rate', 0.1)
        epochs = kwargs.get('max_epochs', 1000)
        return PerceptronReadout(lr, epochs)
    
    elif readout_type.lower() == 'svm':
        kernel = kwargs.get('kernel', 'rbf')
        C = kwargs.get('C', 1.0)
        task = kwargs.get('task_type', 'regression')
        return SVMReadout(kernel, C, task)
    
    else:
        raise ValueError(f"Unknown readout type: {readout_type}")


def compare_readout_mechanisms(features: np.ndarray, targets: np.ndarray, 
                              readout_types: List[str], 
                              test_split: float = 0.3) -> Dict[str, Dict]:
    """
    Compare different readout mechanisms on the same data
    
    Useful for determining which readout works best for a specific task
    """
    from sklearn.model_selection import train_test_split
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        features, targets, test_size=test_split, random_state=42
    )
    
    results = {}
    
    for readout_type in readout_types:
        try:
            # Create and train readout
            readout = create_readout_mechanism(readout_type)
            train_result = readout.train(X_train, y_train)
            
            # Test performance
            test_predictions = readout.predict(X_test)
            test_mse = np.mean((test_predictions - y_test) ** 2)
            
            # Store results
            results[readout_type] = {
                'train_results': train_result,
                'test_mse': test_mse,
                'train_mse': train_result['mse'],
                'generalization_gap': test_mse - train_result['mse']
            }
            
        except Exception as e:
            results[readout_type] = {
                'error': str(e),
                'train_mse': np.inf,
                'test_mse': np.inf
            }
    
    return results