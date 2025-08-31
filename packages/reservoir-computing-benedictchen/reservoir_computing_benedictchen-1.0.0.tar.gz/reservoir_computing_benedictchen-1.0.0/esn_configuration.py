"""
Configuration and Initialization for Echo State Networks
Handles parameter setup and component initialization
"""

import numpy as np
from typing import Optional, Dict, Any, Callable, List, Union


class ESNConfiguration:
    """Handles ESN configuration and initialization"""
    
    def __init__(self, esn_instance):
        self.esn = esn_instance
    
    def initialize_reservoir(self, topology: str = 'random', 
                           topology_params: Optional[Dict[str, Any]] = None):
        """Initialize reservoir weights with specified topology"""
        if topology_params is None:
            topology_params = {}
        
        # Create topology using ReservoirTopology class
        from .reservoir_topology import ReservoirTopology
        topology_creator = ReservoirTopology(self.esn.reservoir_size, self.esn.spectral_radius)
        
        if topology == 'random':
            connectivity = topology_params.get('connectivity', 0.1)
            self.esn.reservoir_weights = topology_creator.create_random_topology(connectivity)
        elif topology == 'ring':
            self.esn.reservoir_weights = topology_creator.create_ring_topology()
        elif topology == 'small_world':
            k = topology_params.get('k', 4)
            p = topology_params.get('p', 0.3)
            self.esn.reservoir_weights = topology_creator.create_small_world_topology(k, p)
        elif topology == 'scale_free':
            m = topology_params.get('m', 2)
            self.esn.reservoir_weights = topology_creator.create_scale_free_topology(m)
        else:
            raise ValueError(f"Unknown topology: {topology}")
        
        # ESP validation will be done after input weights are set
    
    def initialize_input_weights(self, n_inputs: int, 
                               input_scaling: float = 1.0,
                               input_shift: float = 0.0,
                               sparse_input: bool = False,
                               connectivity: float = 1.0):
        """Initialize input weights matrix"""
        self.esn.n_inputs = n_inputs
        self.esn.input_scaling = input_scaling
        self.esn.input_shift = input_shift
        
        # Create input weight matrix
        if sparse_input:
            # Sparse input connections
            self.esn.input_weights = np.random.uniform(-1, 1, 
                                                      (self.esn.reservoir_size, n_inputs))
            mask = np.random.random((self.esn.reservoir_size, n_inputs)) > connectivity
            self.esn.input_weights[mask] = 0
        else:
            # Dense input connections (default)
            self.esn.input_weights = np.random.uniform(-input_scaling, input_scaling,
                                                      (self.esn.reservoir_size, n_inputs))
        
        # Validate ESP after input weights are set
        self._validate_esp_after_initialization()
    
    def initialize_output_feedback(self, n_outputs: int, 
                                 feedback_scaling: float = 0.1,
                                 feedback_connectivity: float = 1.0):
        """Initialize output feedback connections"""
        self.esn.n_outputs = n_outputs
        self.esn.feedback_scaling = feedback_scaling
        
        # Create feedback weight matrix
        self.esn.output_feedback_weights = np.random.uniform(
            -feedback_scaling, feedback_scaling,
            (self.esn.reservoir_size, n_outputs))
        
        # Apply sparsity if specified
        if feedback_connectivity < 1.0:
            mask = np.random.random((self.esn.reservoir_size, n_outputs)) > feedback_connectivity
            self.esn.output_feedback_weights[mask] = 0
    
    def initialize_activation_functions(self, activation: Union[str, Callable] = 'tanh',
                                      custom_params: Optional[Dict[str, Any]] = None):
        """Initialize activation function"""
        if callable(activation):
            self.esn.activation_function = activation
        elif activation == 'tanh':
            self.esn.activation_function = np.tanh
        elif activation == 'sigmoid':
            self.esn.activation_function = lambda x: 1 / (1 + np.exp(-np.clip(x, -500, 500)))
        elif activation == 'relu':
            self.esn.activation_function = lambda x: np.maximum(0, x)
        elif activation == 'leaky_relu':
            alpha = custom_params.get('alpha', 0.01) if custom_params else 0.01
            self.esn.activation_function = lambda x: np.where(x > 0, x, alpha * x)
        elif activation == 'linear':
            self.esn.activation_function = lambda x: x
        else:
            raise ValueError(f"Unknown activation function: {activation}")
        
        self.esn.activation_name = activation if isinstance(activation, str) else 'custom'
    
    def initialize_bias_terms(self, use_bias: bool = True,
                            bias_scaling: float = 0.1):
        """Initialize bias terms for reservoir"""
        self.esn.use_bias = use_bias
        
        if use_bias:
            self.esn.bias_vector = np.random.uniform(-bias_scaling, bias_scaling,
                                                   self.esn.reservoir_size)
        else:
            self.esn.bias_vector = None
    
    def initialize_leak_rates(self, leak_rate: Union[float, np.ndarray] = 1.0,
                            multiple_timescales: bool = False,
                            timescale_groups: Optional[List[Dict[str, Any]]] = None):
        """Initialize leak rates (temporal dynamics)"""
        if multiple_timescales and timescale_groups:
            # Different leak rates for different neuron groups
            self.esn.leak_rates = np.ones(self.esn.reservoir_size)
            
            for group in timescale_groups:
                indices = group.get('indices', [])
                group_leak_rate = group.get('leak_rate', 1.0)
                
                for idx in indices:
                    if 0 <= idx < self.esn.reservoir_size:
                        self.esn.leak_rates[idx] = group_leak_rate
            
            self.esn.multiple_timescales = True
            self.esn.timescale_groups = timescale_groups
        else:
            # Single leak rate for all neurons
            if isinstance(leak_rate, (int, float)):
                self.esn.leak_rate = float(leak_rate)
                self.esn.leak_rates = None
            else:
                # Per-neuron leak rates
                self.esn.leak_rates = np.array(leak_rate)
                self.esn.leak_rate = np.mean(leak_rate)
            
            self.esn.multiple_timescales = multiple_timescales
    
    def configure_noise(self, noise_level: float = 0.0,
                       noise_type: str = 'gaussian'):
        """Configure noise injection"""
        self.esn.noise_level = noise_level
        self.esn.noise_type = noise_type
        
        if noise_type == 'gaussian':
            self.esn.noise_function = lambda size: np.random.normal(0, noise_level, size)
        elif noise_type == 'uniform':
            self.esn.noise_function = lambda size: np.random.uniform(-noise_level, noise_level, size)
        elif noise_type == 'binary':
            self.esn.noise_function = lambda size: np.random.choice([-noise_level, noise_level], size)
        else:
            raise ValueError(f"Unknown noise type: {noise_type}")
    
    def configure_regularization(self, regularization_type: str = 'ridge',
                               regularization_strength: float = 1e-6,
                               auto_tune: bool = False):
        """Configure regularization for training"""
        self.esn.regularization_type = regularization_type
        self.esn.regularization_strength = regularization_strength
        self.esn.auto_tune_regularization = auto_tune
    
    def configure_washout(self, washout_length: int = 100,
                         adaptive_washout: bool = False,
                         washout_threshold: float = 0.01):
        """Configure transient washout period"""
        self.esn.washout_length = washout_length
        self.esn.adaptive_washout = adaptive_washout
        self.esn.washout_threshold = washout_threshold
    
    def configure_online_learning(self, enable_online: bool = False,
                                learning_rate: float = 0.01,
                                forgetting_factor: float = 0.99):
        """Configure online learning parameters"""
        self.esn.online_learning = enable_online
        self.esn.online_learning_rate = learning_rate
        self.esn.online_forgetting_factor = forgetting_factor
    
    def set_advanced_options(self, **kwargs):
        """Set advanced configuration options"""
        # Input preprocessing
        if 'input_scaling' in kwargs:
            self.esn.input_scaling = kwargs['input_scaling']
        if 'input_shift' in kwargs:
            self.esn.input_shift = kwargs['input_shift']
        
        # Reservoir properties
        if 'connectivity' in kwargs:
            self.esn.connectivity = kwargs['connectivity']
        if 'spectral_radius_optimization' in kwargs:
            self.esn.spectral_radius_optimization = kwargs['spectral_radius_optimization']
        
        # Output configuration
        if 'output_activation' in kwargs:
            self.esn.output_activation = kwargs['output_activation']
        if 'teacher_forcing' in kwargs:
            self.esn.teacher_forcing = kwargs['teacher_forcing']
        
        # Performance options
        if 'parallel_updates' in kwargs:
            self.esn.parallel_updates = kwargs['parallel_updates']
        if 'sparse_computation' in kwargs:
            self.esn.sparse_computation = kwargs['sparse_computation']
    
    def _validate_esp_after_initialization(self):
        """Validate Echo State Property after initialization"""
        if hasattr(self.esn, 'esp_validator'):
            validation_result = self.esn.esp_validator.validate_comprehensive_esp()
            
            if not validation_result.get('overall_esp_valid', False):
                import warnings
                warnings.warn(
                    f"Echo State Property validation failed. "
                    f"Confidence: {validation_result.get('validation_confidence', 0):.2f}. "
                    f"Consider adjusting spectral_radius or other parameters."
                )
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration"""
        config = {
            'reservoir_size': self.esn.reservoir_size,
            'spectral_radius': getattr(self.esn, 'spectral_radius', 'unknown'),
            'n_inputs': getattr(self.esn, 'n_inputs', 'not_set'),
            'n_outputs': getattr(self.esn, 'n_outputs', 'not_set'),
            'activation_function': getattr(self.esn, 'activation_name', 'tanh'),
            'leak_rate': getattr(self.esn, 'leak_rate', 1.0),
            'multiple_timescales': getattr(self.esn, 'multiple_timescales', False),
            'noise_level': getattr(self.esn, 'noise_level', 0.0),
            'use_bias': getattr(self.esn, 'use_bias', True),
            'regularization_type': getattr(self.esn, 'regularization_type', 'ridge'),
            'regularization_strength': getattr(self.esn, 'regularization_strength', 1e-6),
            'washout_length': getattr(self.esn, 'washout_length', 100),
            'online_learning': getattr(self.esn, 'online_learning', False)
        }
        
        # Add topology information if available
        if hasattr(self.esn, 'reservoir_weights'):
            connectivity = np.mean(self.esn.reservoir_weights != 0)
            config['actual_connectivity'] = connectivity
            
            eigenvals = np.linalg.eigvals(self.esn.reservoir_weights)
            config['actual_spectral_radius'] = np.max(np.abs(eigenvals))
        
        return config
    
    def save_configuration(self, filepath: str):
        """Save configuration to file"""
        import json
        config = self.get_configuration_summary()
        
        # Convert numpy types to Python types for JSON serialization
        for key, value in config.items():
            if isinstance(value, np.ndarray):
                config[key] = value.tolist()
            elif isinstance(value, (np.integer, np.floating)):
                config[key] = float(value)
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_configuration(self, filepath: str):
        """Load configuration from file"""
        import json
        
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        # Apply loaded configuration
        for key, value in config.items():
            if hasattr(self.esn, key):
                setattr(self.esn, key, value)