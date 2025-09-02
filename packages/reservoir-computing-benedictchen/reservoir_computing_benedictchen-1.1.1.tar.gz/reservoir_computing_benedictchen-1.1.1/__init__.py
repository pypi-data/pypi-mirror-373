"""
Reservoir Computing Library
Based on: Jaeger (2001) Echo State Networks & Maass (2002) Liquid State Machines

This library implements the revolutionary concept of fixed random reservoirs
with trainable readout layers, enabling efficient temporal pattern processing.
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🌊 Reservoir Computing Library - Made possible by Benedict Chen")
        print("   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\")
        print("   Support his work: \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\🍺 Buy him a beer\033]8;;\033\\")
    except:
        print("\n🌊 Reservoir Computing Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("   Support: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")

# Core unified implementations
from .echo_state_network import (
    EchoStateNetwork,
    EchoStatePropertyValidator,
    StructuredReservoirTopologies, 
    JaegerBenchmarkTasks,
    OutputFeedbackESN,
    TeacherForcingTrainer,
    OnlineLearningESN,
    optimize_spectral_radius,
    validate_esp,
    run_benchmark_suite
)
from .liquid_state_machine import (
    LiquidStateMachine,
    LSMConfig,
    NeuronModelType,
    SynapseModelType,
    ConnectivityType,
    LiquidStateType,
    ReadoutType,
    LIFNeuron,
    DynamicSynapse,
    LiquidStateExtractor,
    PSPDecayExtractor,
    SpikeCountExtractor,
    MembranePotentialExtractor,
    FiringRateExtractor,
    MultiTimescaleExtractor,
    ReadoutMechanism,
    LinearReadout,
    PopulationReadout,
    LSMTheoreticalAnalysis,
    MaassBenchmarkTasks,
    create_lsm_with_presets,
    run_lsm_benchmark_suite
)
from .hierarchical_reservoir import HierarchicalReservoir
from .reservoir_optimizer import ReservoirOptimizer
from .neuromorphic_interface import NeuromorphicReservoir

# Show attribution on library import
_print_attribution()

__version__ = "1.0.0"
__authors__ = ["Based on Jaeger (2001)", "Maass et al. (2002)"]

__all__ = [
    # Core Networks
    "EchoStateNetwork",
    "LiquidStateMachine", 
    "HierarchicalReservoir",
    "NeuromorphicReservoir",
    
    # ESN Advanced Features
    "EchoStatePropertyValidator",
    "StructuredReservoirTopologies",
    "JaegerBenchmarkTasks",
    "OutputFeedbackESN",
    "TeacherForcingTrainer", 
    "OnlineLearningESN",
    
    # LSM Advanced Features
    "LSMConfig",
    "NeuronModelType",
    "SynapseModelType", 
    "ConnectivityType",
    "LiquidStateType",
    "ReadoutType",
    "LIFNeuron",
    "DynamicSynapse",
    "LiquidStateExtractor",
    "PSPDecayExtractor",
    "SpikeCountExtractor", 
    "MembranePotentialExtractor",
    "FiringRateExtractor",
    "MultiTimescaleExtractor",
    "ReadoutMechanism",
    "LinearReadout",
    "PopulationReadout",
    "LSMTheoreticalAnalysis",
    "MaassBenchmarkTasks",
    "create_lsm_with_presets",
    "run_lsm_benchmark_suite",
    
    # Utilities
    "ReservoirOptimizer",
    "optimize_spectral_radius",
    "validate_esp",
    "run_benchmark_suite"
]