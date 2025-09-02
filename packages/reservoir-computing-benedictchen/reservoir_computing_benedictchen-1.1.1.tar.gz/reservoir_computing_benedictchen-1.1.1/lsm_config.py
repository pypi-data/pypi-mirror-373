"""
Configuration classes and enums for Liquid State Machine
Based on: Maass, Natschläger & Markram (2002) "Real-Time Computing Without Stable States"
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class NeuronModelType(Enum):
    """Types of neuron models available"""
    SIMPLE_LIF = "simple_lif"  # Current simplified implementation
    LEAKY_INTEGRATE_AND_FIRE = "simple_lif"  # Backward compatibility alias
    INTEGRATE_AND_FIRE = "simple_lif"  # Another backward compatibility alias
    MAASS_2002_LIF = "maass_2002_lif"  # Paper-accurate parameters
    BIOLOGICAL_LIF = "biological_lif"  # Full biological realism
    ADAPTIVE_LIF = "adaptive_lif"  # With adaptation currents


class SynapseModelType(Enum):
    """Types of synapse models"""
    STATIC = "static"  # Current implementation
    MARKRAM_DYNAMIC = "markram_dynamic"  # Maass 2002 dynamic synapses
    TSODYKS_MARKRAM = "tsodyks_markram"  # Full TM model
    STP_ENHANCED = "stp_enhanced"  # Enhanced short-term plasticity


class ConnectivityType(Enum):
    """Types of connectivity patterns"""
    RANDOM_UNIFORM = "random_uniform"  # Current random connectivity
    DISTANCE_DEPENDENT = "distance_dependent"  # Maass 2002 distance-based
    COLUMN_STRUCTURED = "column_structured"  # 3D column organization
    SMALL_WORLD = "small_world"  # Small-world topology
    SCALE_FREE = "scale_free"  # Scale-free networks


class LiquidStateType(Enum):
    """Types of liquid state extraction"""
    SPIKE_COUNTS = "spike_counts"  # Current implementation
    PSP_DECAY = "psp_decay"  # Maass 2002 correct implementation
    MEMBRANE_POTENTIALS = "membrane_potentials"  # Direct V_m readout
    FIRING_RATES = "firing_rates"  # Population firing rates
    MULTI_TIMESCALE = "multi_timescale"  # Multiple decay constants


class ReadoutType(Enum):
    """Types of readout mechanisms"""
    LINEAR_REGRESSION = "linear_regression"  # Current implementation
    POPULATION_NEURONS = "population_neurons"  # Maass 2002 I&F populations
    P_DELTA_LEARNING = "p_delta_learning"  # Biologically realistic learning
    PERCEPTRON = "perceptron"  # Simple perceptron
    SVM = "svm"  # Support Vector Machine


@dataclass
class LIFNeuronConfig:
    """
    Configurable LIF Neuron parameters with multiple preset options
    
    Now supports paper-accurate parameters from Maass 2002
    """
    # Model type determines parameter defaults
    model_type: NeuronModelType = NeuronModelType.MAASS_2002_LIF
    
    # Core LIF parameters (will be set based on model_type if None)
    tau_m: Optional[float] = None  # Membrane time constant (ms)
    tau_ref: Optional[float] = None  # Refractory period (ms)
    v_reset: Optional[float] = None  # Reset potential (mV)
    v_thresh: Optional[float] = None  # Spike threshold (mV)
    v_rest: Optional[float] = None  # Resting potential (mV)
    
    # Biological parameters (Maass 2002 accurate)
    input_resistance: Optional[float] = None  # Input resistance (MΩ)
    background_current: Optional[float] = None  # Background current (nA)
    
    # Synaptic parameters
    tau_syn_exc: Optional[float] = None  # Excitatory synaptic time constant (ms)
    tau_syn_inh: Optional[float] = None  # Inhibitory synaptic time constant (ms)
    
    # Noise parameters
    membrane_noise_std: float = 0.0  # Membrane noise standard deviation
    current_noise_std: float = 0.0  # Current noise standard deviation
    
    def __post_init__(self):
        """Set default parameters based on model type"""
        if self.model_type == NeuronModelType.SIMPLE_LIF:
            # Current implementation defaults
            self.tau_m = self.tau_m or 20.0
            self.tau_ref = self.tau_ref or 2.0
            self.v_reset = self.v_reset or -70.0
            self.v_thresh = self.v_thresh or -54.0
            self.v_rest = self.v_rest or -70.0
            self.input_resistance = self.input_resistance or 1.0
            self.background_current = self.background_current or 0.0
            self.tau_syn_exc = self.tau_syn_exc or 5.0
            self.tau_syn_inh = self.tau_syn_inh or 10.0
            
        elif self.model_type == NeuronModelType.MAASS_2002_LIF:
            # Paper-accurate parameters from Maass 2002
            self.tau_m = self.tau_m or 30.0  # 30ms membrane time constant
            self.tau_ref = self.tau_ref or 2.0  # 2ms refractory period
            self.v_reset = self.v_reset or -60.0  # -60mV reset
            self.v_thresh = self.v_thresh or -50.0  # -50mV threshold
            self.v_rest = self.v_rest or -60.0  # -60mV resting
            self.input_resistance = self.input_resistance or 1.0
            self.background_current = self.background_current or 13.5  # 13.5nA
            self.tau_syn_exc = self.tau_syn_exc or 3.0  # 3ms AMPA
            self.tau_syn_inh = self.tau_syn_inh or 6.0  # 6ms GABA
            
        elif self.model_type == NeuronModelType.BIOLOGICAL_LIF:
            # Biologically realistic parameters
            self.tau_m = self.tau_m or 20.0
            self.tau_ref = self.tau_ref or 1.0
            self.v_reset = self.v_reset or -65.0
            self.v_thresh = self.v_thresh or -55.0
            self.v_rest = self.v_rest or -65.0
            self.input_resistance = self.input_resistance or 100.0  # 100 MΩ
            self.background_current = self.background_current or 0.1  # 0.1 nA
            self.tau_syn_exc = self.tau_syn_exc or 2.0  # Fast AMPA
            self.tau_syn_inh = self.tau_syn_inh or 10.0  # Slow GABA
            
        elif self.model_type == NeuronModelType.ADAPTIVE_LIF:
            # With adaptation currents
            self.tau_m = self.tau_m or 20.0
            self.tau_ref = self.tau_ref or 2.0
            self.v_reset = self.v_reset or -70.0
            self.v_thresh = self.v_thresh or -50.0
            self.v_rest = self.v_rest or -70.0
            self.input_resistance = self.input_resistance or 1.0
            self.background_current = self.background_current or 0.0
            self.tau_syn_exc = self.tau_syn_exc or 5.0
            self.tau_syn_inh = self.tau_syn_inh or 10.0


@dataclass
class LSMConfig:
    """
    Complete LSM Configuration - Controls all aspects of the network
    
    This replaces many separate parameters with a unified configuration system
    """
    # Network topology
    n_liquid: int = 135  # Maass 2002 default microcircuit size
    n_input: int = 1
    n_output: int = 1
    
    # Neuron configuration
    neuron_config: LIFNeuronConfig = None  # Will default to MAASS_2002_LIF
    
    # Connectivity
    connectivity_type: ConnectivityType = ConnectivityType.DISTANCE_DEPENDENT
    p_connect: float = 0.1  # Connection probability
    
    # Liquid state extraction
    liquid_state_type: LiquidStateType = LiquidStateType.PSP_DECAY
    readout_type: ReadoutType = ReadoutType.POPULATION_NEURONS
    
    # Synapse model
    synapse_type: SynapseModelType = SynapseModelType.MARKRAM_DYNAMIC
    
    # Simulation parameters
    dt: float = 1.0  # Time step (ms)
    
    def __post_init__(self):
        """Initialize default neuron config if not provided"""
        if self.neuron_config is None:
            self.neuron_config = LIFNeuronConfig()


@dataclass
class DynamicSynapseConfig:
    """Configuration for dynamic synapses (Tsodyks-Markram model)"""
    
    # Model type determines parameter defaults
    synapse_type: SynapseModelType = SynapseModelType.MARKRAM_DYNAMIC
    
    # Connection type (EE, EI, IE, II)
    connection_type: str = "EE"
    
    # Core TM parameters (will be set based on synapse_type if None)
    tau_rec: Optional[float] = None  # Recovery time constant (ms)
    tau_fac: Optional[float] = None  # Facilitation time constant (ms)
    U: Optional[float] = None  # Release probability
    
    # Scaling amplitude
    amplitude: float = 30.0  # nA - scaling factor
    
    # Synaptic delay (important for realistic neural dynamics)
    delay: float = 1.0  # ms - synaptic transmission delay
    
    def __post_init__(self):
        """Set default parameters based on synapse type and connection type"""
        if self.synapse_type == SynapseModelType.STATIC:
            # Static synapses
            self.tau_rec = 0.0
            self.tau_fac = 0.0
            self.U = self.U or 0.5
            
        elif self.synapse_type == SynapseModelType.MARKRAM_DYNAMIC:
            # Maass 2002 connection-specific parameters
            if self.connection_type == "EE":
                self.U = self.U or 0.5
                self.tau_rec = self.tau_rec or 1100.0  # Convert to ms
                self.tau_fac = self.tau_fac or 50.0
                self.amplitude = self.amplitude or 30.0
            elif self.connection_type == "EI":
                self.U = self.U or 0.05
                self.tau_rec = self.tau_rec or 125.0
                self.tau_fac = self.tau_fac or 1200.0
                self.amplitude = self.amplitude or 60.0
            elif self.connection_type == "IE":
                self.U = self.U or 0.25
                self.tau_rec = self.tau_rec or 700.0
                self.tau_fac = self.tau_fac or 20.0
                self.amplitude = self.amplitude or -19.0  # Inhibitory
            elif self.connection_type == "II":
                self.U = self.U or 0.32
                self.tau_rec = self.tau_rec or 144.0
                self.tau_fac = self.tau_fac or 60.0
                self.amplitude = self.amplitude or -19.0  # Inhibitory
            
        elif self.synapse_type == SynapseModelType.TSODYKS_MARKRAM:
            # Full TM model with facilitation
            self.tau_rec = self.tau_rec or 100.0  # 100ms recovery
            self.tau_fac = self.tau_fac or 1000.0  # 1s facilitation
            self.U = self.U or 0.03  # 3% initial release
            
        elif self.synapse_type == SynapseModelType.STP_ENHANCED:
            # Enhanced short-term plasticity
            self.tau_rec = self.tau_rec or 500.0
            self.tau_fac = self.tau_fac or 200.0
            self.U = self.U or 0.2