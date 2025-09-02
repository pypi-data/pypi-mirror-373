"""
🌊 Echo State Network Core - Modular Integration
===============================================

📚 Research Foundation:
Jaeger, H. (2001) "The 'Echo State' Approach to Analysing and Training Recurrent Neural Networks"
Technical Report GMD-148, German National Research Center for Information Technology

🎯 Module Purpose:
This module integrates all the modular ESN components into the main EchoStateNetwork class.
Uses mixin pattern to combine specialized functionality while maintaining clean separation
of concerns and research accuracy.

🧠 Architectural Innovation:
This modular design represents the evolution of reservoir computing implementations:
- Clean separation between initialization, dynamics, training, and analysis
- Research-grade documentation with mathematical foundations
- Comprehensive configurability without sacrificing performance  
- Extensible design for future reservoir computing research

🔧 Integrated Components:
- ReservoirInitializationMixin: Reservoir setup and weight initialization
- EspValidationMixin: Echo State Property validation methods
- StateUpdatesMixin: Core dynamics and temporal processing
- TrainingMethodsMixin: Linear readout training and optimization
- PredictionGenerationMixin: Prediction and autonomous generation
- TopologyManagementMixin: Network topology creation and management
- ConfigurationOptimizationMixin: Parameter optimization and tuning
- VisualizationMixin: Comprehensive analysis and visualization
"""

import numpy as np
from scipy import sparse
from typing import Optional, Callable, Dict, Any, Tuple, List, Union
import warnings
warnings.filterwarnings('ignore')

# Import all modular components
from .reservoir_initialization import ReservoirInitializationMixin
from .esp_validation import EspValidationMixin
from .state_updates import StateUpdatesMixin
from .training_methods import TrainingMethodsMixin
from .prediction_generation import PredictionGenerationMixin
from .topology_management import TopologyManagementMixin
from .configuration_optimization import ConfigurationOptimizationMixin
from .visualization import VisualizationMixin


class EchoStateNetwork(
    ReservoirInitializationMixin,
    EspValidationMixin,
    StateUpdatesMixin,
    TrainingMethodsMixin,
    PredictionGenerationMixin,
    TopologyManagementMixin,
    ConfigurationOptimizationMixin,
    VisualizationMixin
):
    """
    Modular Echo State Network Implementation
    
    🌊 Revolutionary Reservoir Computing Architecture
    
    Based on Herbert Jaeger's groundbreaking 2001 paper, this implementation
    provides a complete, research-grade Echo State Network with modular
    design for maximum flexibility and extensibility.
    
    🧠 Theoretical Foundation:
    The Echo State Network exploits the principle of "liquid state machines"
    where a fixed random recurrent network (the "reservoir") projects input
    sequences into a high-dimensional space with rich temporal dynamics.
    Only the linear readout weights are trained, making ESNs:
    
    - 1000x faster to train than traditional RNNs
    - Naturally suited for temporal pattern recognition
    - Capable of universal approximation with the Echo State Property
    - Robust to hyperparameter choices when ESP is satisfied
    
    🏗️ Architecture Overview:
    Input u(t) → [W_in] → Reservoir x(t) → [W_out] → Output y(t)
                            ↑     ↓
                         [W_res] [W_back]
                         (fixed) (optional)
    
    Mathematical Dynamics:
    x(t+1) = (1-α)x(t) + α·f(W_res·x(t) + W_in·u(t) + W_back·y(t) + noise)
    y(t) = W_out·[x(t); u(t)]
    
    Where:
    - α: leak rate (temporal memory control)
    - f: activation function (typically tanh)
    - W_res: fixed reservoir matrix (spectral radius < 1)
    - W_in: input weights (scaled for proper dynamics)
    - W_out: trainable output weights (linear regression)
    - W_back: optional feedback weights (autonomous generation)
    
    🔧 Modular Components:
    - Initialization: Advanced reservoir setup with ESP validation
    - Dynamics: Comprehensive state update methods with multiple integration modes
    - Training: Ridge regression, LSQR, pseudo-inverse, and elastic net solvers
    - Generation: Open-loop prediction and closed-loop autonomous generation
    - Topology: Ring, small-world, scale-free, and custom network structures
    - Optimization: Hyperparameter tuning and automatic configuration
    - Analysis: Comprehensive visualization and performance analysis
    - Validation: Multiple ESP validation methods for stability assurance
    
    Parameters:
        n_reservoir (int): Number of reservoir units (default: 500)
        spectral_radius (float): Largest eigenvalue magnitude (default: 0.95)
        sparsity (float): Reservoir connectivity density (default: 0.1)
        input_scaling (float): Input weight scaling factor (default: 1.0)
        noise_level (float): State noise magnitude (default: 0.01)
        leak_rate (float): Leaky integration parameter (default: 1.0)
        random_seed (Optional[int]): Reproducibility seed
        
    Advanced Parameters:
        output_feedback (bool): Enable closed-loop generation (default: False)
        activation_function (str): Activation type (default: 'tanh')
        input_shift (float): Input bias term (default: 0.0)
        reservoir_bias (bool): Enable reservoir bias terms (default: False)
        teacher_forcing (bool): Enable teacher forcing training (default: False)
        washout_adaptive (bool): Adaptive washout period (default: False)
        
    Example:
        >>> # Create and configure ESN
        >>> esn = EchoStateNetwork(
        ...     n_reservoir=1000,
        ...     spectral_radius=0.95,
        ...     sparsity=0.1,
        ...     input_scaling=1.0,
        ...     leak_rate=0.3,
        ...     random_seed=42
        ... )
        >>>
        >>> # Train on time series data
        >>> esn.train(X_train, y_train, washout=100)
        >>>
        >>> # Make predictions
        >>> y_pred = esn.predict(X_test, washout=100)
        >>>
        >>> # Generate autonomous sequences
        >>> y_gen = esn.generate(n_steps=1000, 
        ...                      initial_input=X_test[0])
        >>>
        >>> # Visualize reservoir properties
        >>> esn.visualize_reservoir()
        >>> esn.visualize_dynamics(X_test[:500])
    """
    
    def __init__(
        self,
        n_reservoir: int = 500,
        spectral_radius: float = 0.95,
        sparsity: float = 0.1,
        input_scaling: float = 1.0,
        noise_level: float = 0.01,
        leak_rate: float = 1.0,
        random_seed: Optional[int] = None,
        # Enhanced parameters from Jaeger 2001 Section 2:
        output_feedback: bool = False,
        activation_function: str = 'tanh',
        input_shift: float = 0.0,
        reservoir_bias: bool = False,
        teacher_forcing: bool = False,
        washout_adaptive: bool = False,
        # Advanced configuration options:
        connection_topology: str = 'random',
        input_connectivity: float = 1.0,
        feedback_connectivity: float = 1.0,
        reservoir_connectivity_mask: Optional[np.ndarray] = None,
        # Comprehensive FIXME implementations:
        spectral_scaling_method: str = 'standard',
        handle_complex_eigenvalues: bool = True,
        verify_esp_after_scaling: bool = True,
        esp_validation_method: str = 'fast',
        multiple_timescales: bool = False,
        leak_mode: str = 'post_activation',
        bias_type: str = 'random',
        noise_type: str = 'additive',
        output_feedback_mode: str = 'direct',
        teacher_forcing_strategy: str = 'full',
        training_solver: str = 'ridge',
        state_collection_method: str = 'all_states'
    ):
        """
        Initialize modular Echo State Network
        
        🧠 Initialization Process (Following Jaeger 2001 Guidelines):
        1. Set core hyperparameters and validate ranges
        2. Initialize random number generator for reproducibility
        3. Create reservoir matrix with specified topology
        4. Scale spectral radius and validate Echo State Property
        5. Setup comprehensive configuration options
        6. Initialize all modular components
        
        The initialization follows best practices from ESN literature while
        providing maximum configurability for research applications.
        """
        # Core ESN hyperparameters
        self.n_reservoir = n_reservoir
        self.spectral_radius = spectral_radius
        self.sparsity = sparsity
        self.input_scaling = input_scaling
        self.noise_level = noise_level
        self.leak_rate = leak_rate
        self.random_seed = random_seed
        
        # Enhanced parameters
        self.output_feedback = output_feedback
        self.activation_function = activation_function
        self.input_shift = input_shift
        self.reservoir_bias = reservoir_bias
        self.teacher_forcing = teacher_forcing
        self.washout_adaptive = washout_adaptive
        
        # Advanced configuration
        self.connection_topology = connection_topology
        self.input_connectivity = input_connectivity
        self.feedback_connectivity = feedback_connectivity
        self.reservoir_connectivity_mask = reservoir_connectivity_mask
        
        # Comprehensive configuration options
        self.spectral_scaling_method = spectral_scaling_method
        self.handle_complex_eigenvalues = handle_complex_eigenvalues
        self.verify_esp_after_scaling = verify_esp_after_scaling
        self.esp_validation_method = esp_validation_method
        self.multiple_timescales = multiple_timescales
        self.leak_mode = leak_mode
        self.bias_type = bias_type
        self.noise_type = noise_type
        self.output_feedback_mode = output_feedback_mode
        self.teacher_forcing_strategy = teacher_forcing_strategy
        self.training_solver = training_solver
        self.state_collection_method = state_collection_method
        
        # Initialize matrices (will be set during training)
        self.W_reservoir = None
        self.W_input = None
        self.W_output = None
        self.W_feedback = None
        self.W_back = None  # Alias for compatibility
        
        # Training state
        self.is_trained = False
        self.training_error = None
        self.last_state = None
        
        # Advanced state tracking
        self.output_feedback_enabled = output_feedback
        self.training_mode = True
        self.sparse_computation_enabled = False
        
        # Performance tracking
        self.training_time = None
        self.prediction_time = None
        
        # Set random seed for reproducibility
        if random_seed is not None:
            np.random.seed(random_seed)
            
        # Initialize reservoir - this triggers the initialization cascade
        print(f"🌊 Initializing Echo State Network...")
        print(f"   Architecture: {n_reservoir} reservoir units")
        print(f"   Spectral radius: {spectral_radius}")
        print(f"   Sparsity: {sparsity}")
        print(f"   Input scaling: {input_scaling}")
        print(f"   Leak rate: {leak_rate}")
        print(f"   Topology: {connection_topology}")
        
        # Initialize reservoir and all modular components
        self._initialize_reservoir()
        
        print(f"✅ Echo State Network initialized successfully!")
        print(f"   ESP validated: {getattr(self, 'esp_validated', 'Pending')}")
        print(f"   Ready for training and analysis")

    def fit(self, X: np.ndarray, y: np.ndarray, washout: int = 100, **kwargs):
        """
        Scikit-learn compatible training interface
        
        Alias for train() method to provide familiar scikit-learn interface
        for users coming from machine learning background.
        
        Args:
            X: Input sequences [n_samples, n_features]
            y: Target outputs [n_samples, n_outputs]  
            washout: Transient washout period
            **kwargs: Additional training parameters
            
        Returns:
            self: Trained ESN instance (for method chaining)
        """
        self.train(X, y, washout=washout, **kwargs)
        return self

    def transform(self, X: np.ndarray, washout: int = 100) -> np.ndarray:
        """
        Scikit-learn compatible prediction interface
        
        Alias for predict() method to provide familiar scikit-learn interface.
        
        Args:
            X: Input sequences [n_samples, n_features]
            washout: Washout period for predictions
            
        Returns:
            Predictions [n_samples, n_outputs]
        """
        return self.predict(X, washout=washout)

    def fit_transform(self, X: np.ndarray, y: np.ndarray, washout: int = 100) -> np.ndarray:
        """
        Scikit-learn compatible fit and transform
        
        Train the ESN and immediately make predictions on the same data.
        
        Args:
            X: Input sequences
            y: Target outputs
            washout: Washout period
            
        Returns:
            Predictions on training data
        """
        self.fit(X, y, washout=washout)
        return self.transform(X, washout=washout)

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        """
        Get ESN parameters (scikit-learn compatibility)
        
        Returns:
            Dictionary of all ESN parameters
        """
        return {
            'n_reservoir': self.n_reservoir,
            'spectral_radius': self.spectral_radius,
            'sparsity': self.sparsity,
            'input_scaling': self.input_scaling,
            'noise_level': self.noise_level,
            'leak_rate': self.leak_rate,
            'random_seed': self.random_seed,
            'output_feedback': self.output_feedback,
            'activation_function': self.activation_function,
            'connection_topology': self.connection_topology,
            'esp_validation_method': self.esp_validation_method,
            'training_solver': self.training_solver
        }

    def set_params(self, **params) -> 'EchoStateNetwork':
        """
        Set ESN parameters (scikit-learn compatibility)
        
        Note: Changing parameters requires re-initialization
        """
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid parameter: {key}")
        
        # Re-initialize if reservoir parameters changed
        reservoir_params = {'n_reservoir', 'spectral_radius', 'sparsity', 
                          'connection_topology', 'esp_validation_method'}
        if any(key in reservoir_params for key in params.keys()):
            self._initialize_reservoir()
            self.is_trained = False
            
        return self

    def summary(self) -> str:
        """
        Generate comprehensive ESN summary
        
        Returns formatted summary of ESN configuration, training status,
        and performance characteristics for research documentation.
        """
        summary_lines = [
            "🌊 Echo State Network Summary",
            "=" * 50,
            f"Architecture:",
            f"  Reservoir size: {self.n_reservoir} units",
            f"  Spectral radius: {self.spectral_radius}",
            f"  Sparsity: {self.sparsity}",
            f"  Input scaling: {self.input_scaling}",
            f"  Leak rate: {self.leak_rate}",
            f"",
            f"Configuration:",
            f"  Topology: {self.connection_topology}",
            f"  Activation: {self.activation_function}",
            f"  ESP validation: {self.esp_validation_method}",
            f"  Training solver: {self.training_solver}",
            f"  Output feedback: {self.output_feedback}",
            f"",
            f"Status:",
            f"  Trained: {self.is_trained}",
            f"  ESP validated: {getattr(self, 'esp_validated', 'Unknown')}",
        ]
        
        if self.is_trained and self.training_error is not None:
            summary_lines.extend([
                f"  Training error: {self.training_error:.6f}",
                f"  Training time: {getattr(self, 'training_time', 'N/A')}",
            ])
            
        return "\n".join(summary_lines)

    def __repr__(self) -> str:
        """String representation of ESN"""
        return (f"EchoStateNetwork(n_reservoir={self.n_reservoir}, "
                f"spectral_radius={self.spectral_radius}, "
                f"trained={self.is_trained})")

    def __str__(self) -> str:
        """Human-readable string representation"""
        return self.summary()


# Factory function for convenient ESN creation
def create_echo_state_network(
    preset: str = 'balanced',
    n_reservoir: int = 500,
    **kwargs
) -> EchoStateNetwork:
    """
    Factory function for creating ESNs with research-validated presets
    
    🎯 Presets based on published ESN research and best practices:
    
    Args:
        preset: Configuration preset ('fast', 'balanced', 'accurate', 'research')
        n_reservoir: Override reservoir size
        **kwargs: Additional parameter overrides
        
    Returns:
        Configured EchoStateNetwork instance
    """
    presets = {
        'fast': {
            'spectral_radius': 0.9,
            'sparsity': 0.05,
            'leak_rate': 1.0,
            'esp_validation_method': 'fast',
            'training_solver': 'ridge'
        },
        'balanced': {
            'spectral_radius': 0.95,
            'sparsity': 0.1,
            'leak_rate': 0.3,
            'esp_validation_method': 'convergence',
            'training_solver': 'ridge'
        },
        'accurate': {
            'spectral_radius': 0.99,
            'sparsity': 0.15,
            'leak_rate': 0.1,
            'esp_validation_method': 'rigorous',
            'training_solver': 'lsqr',
            'noise_level': 0.001
        },
        'research': {
            'spectral_radius': 0.95,
            'sparsity': 0.1,
            'leak_rate': 0.2,
            'esp_validation_method': 'lyapunov',
            'training_solver': 'elastic_net',
            'verify_esp_after_scaling': True,
            'connection_topology': 'small_world'
        }
    }
    
    if preset not in presets:
        raise ValueError(f"Unknown preset: {preset}. Choose from {list(presets.keys())}")
    
    config = presets[preset].copy()
    config['n_reservoir'] = n_reservoir
    config.update(kwargs)
    
    return EchoStateNetwork(**config)


# Export main classes and functions
__all__ = ['EchoStateNetwork', 'create_echo_state_network']