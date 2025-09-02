"""
Echo State Network - Main Module File
Based on: Jaeger (2001) "The 'Echo State' Approach to Analysing and Training Recurrent Neural Networks"

This module provides the main imports and functions for the Echo State Network implementation.
Uses modular components from esn_modules for the actual implementation.
"""

# Import core classes from modular components
from .esn_modules import (
    EchoStateNetwork,
    create_echo_state_network,
    ReservoirInitializationMixin,
    EspValidationMixin,
    StateUpdatesMixin,
    TrainingMethodsMixin,
    PredictionGenerationMixin,
    TopologyManagementMixin,
    ConfigurationOptimizationMixin,
    VisualizationMixin
)

# Create aliases for backward compatibility
EchoStatePropertyValidator = EspValidationMixin
StructuredReservoirTopologies = TopologyManagementMixin
JaegerBenchmarkTasks = ConfigurationOptimizationMixin
OutputFeedbackESN = EchoStateNetwork  # Same class with output_feedback=True
TeacherForcingTrainer = TrainingMethodsMixin
OnlineLearningESN = EchoStateNetwork  # Same class with online capabilities

def optimize_spectral_radius(X_train, y_train, esn=None, radius_range=(0.1, 1.5), n_points=15, cv_folds=3):
    """
    Optimize spectral radius using grid search
    
    Wrapper function that creates an ESN if not provided and runs optimization.
    
    Args:
        X_train: Training input data
        y_train: Training target data  
        esn: Optional ESN instance (creates new one if None)
        radius_range: Range of spectral radius values to test
        n_points: Number of points to test in range
        cv_folds: Number of cross-validation folds
        
    Returns:
        Dict with optimization results
    """
    if esn is None:
        esn = EchoStateNetwork(random_seed=42)
        
    return esn.optimize_spectral_radius(X_train, y_train, radius_range, n_points, cv_folds)

def validate_esp(esn, method='fast', **kwargs):
    """
    Validate Echo State Property of an ESN
    
    Args:
        esn: EchoStateNetwork instance
        method: ESP validation method ('fast', 'rigorous', 'convergence', 'lyapunov')
        **kwargs: Additional validation parameters
        
    Returns:
        bool: True if ESP is satisfied
    """
    esn.esp_validation_method = method
    return esn._validate_comprehensive_esp()

def run_benchmark_suite(esn_configs=None, benchmarks=['memory_capacity', 'nonlinear_capacity'], verbose=True):
    """
    Run comprehensive benchmark suite on ESN configurations
    
    Args:
        esn_configs: List of ESN configurations to test
        benchmarks: List of benchmark tasks to run
        verbose: Whether to print detailed results
        
    Returns:
        Dict with benchmark results for each configuration
    """
    if esn_configs is None:
        esn_configs = [
            {'preset': 'fast'},
            {'preset': 'balanced'},
            {'preset': 'accurate'}
        ]
    
    results = {}
    
    for i, config in enumerate(esn_configs):
        config_name = config.get('name', f'config_{i+1}')
        if verbose:
            print(f"🧪 Running benchmarks for {config_name}...")
        
        # Create ESN with configuration
        if 'preset' in config:
            esn = create_echo_state_network(config['preset'], **{k:v for k,v in config.items() if k != 'preset'})
        else:
            esn = EchoStateNetwork(**config)
        
        config_results = {}
        
        for benchmark in benchmarks:
            if benchmark == 'memory_capacity':
                # Simple memory capacity test
                import numpy as np
                # Generate delay line task data
                n_samples = 1000
                delays = range(1, 21)  # Test delays 1-20
                input_seq = np.random.uniform(-1, 1, (n_samples, 1))
                
                memory_scores = []
                for delay in delays:
                    if n_samples > delay:
                        target = np.roll(input_seq, delay, axis=0)
                        target[:delay] = 0
                        
                        try:
                            esn.train(input_seq, target, washout=100)
                            pred = esn.predict(input_seq, washout=100)
                            
                            # Calculate correlation coefficient
                            correlation = np.corrcoef(target[100:].flatten(), pred[100:].flatten())[0,1]
                            if np.isnan(correlation):
                                correlation = 0.0
                            memory_scores.append(max(0, correlation))
                        except:
                            memory_scores.append(0.0)
                    else:
                        memory_scores.append(0.0)
                
                config_results['memory_capacity'] = {
                    'scores': memory_scores,
                    'total_capacity': sum(memory_scores),
                    'effective_capacity': sum(1 for score in memory_scores if score > 0.1)
                }
                
        results[config_name] = config_results
        
        if verbose:
            print(f"   ✅ {config_name} completed")
    
    return results

# Export main classes and functions
__all__ = [
    'EchoStateNetwork',
    'create_echo_state_network', 
    'EchoStatePropertyValidator',
    'StructuredReservoirTopologies',
    'JaegerBenchmarkTasks', 
    'OutputFeedbackESN',
    'TeacherForcingTrainer',
    'OnlineLearningESN',
    'optimize_spectral_radius',
    'validate_esp',
    'run_benchmark_suite'
]