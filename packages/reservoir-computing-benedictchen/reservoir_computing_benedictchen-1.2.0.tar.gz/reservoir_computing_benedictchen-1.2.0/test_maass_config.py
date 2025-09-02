#!/usr/bin/env python3
"""
Test the Maass 2002 configuration specifically
"""

import sys
import os
import numpy as np

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the LSM classes
from liquid_state_machine import (LiquidStateMachine, LSMConfig, NeuronModelType, 
                                 ConnectivityType, SynapseModelType, LiquidStateType, 
                                 ReadoutType, LIFNeuronConfig)

print("Testing Maass 2002 configuration...")

# Create the exact same config from the failing example
maass_config = LSMConfig(
    n_liquid=135,  # Paper default: 15×3×3
    neuron_config=LIFNeuronConfig(model_type=NeuronModelType.MAASS_2002_LIF),
    connectivity_type=ConnectivityType.DISTANCE_DEPENDENT,
    synapse_type=SynapseModelType.MARKRAM_DYNAMIC,
    state_type=LiquidStateType.PSP_DECAY,
    readout_type=ReadoutType.POPULATION_NEURONS,
    spatial_organization=True,
    dt=1.0
)

print("Configuration created, initializing LSM...")

try:
    lsm_maass = LiquidStateMachine(config=maass_config)
    print("✅ Maass 2002 LSM initialized successfully!")
    print(f"   Neurons: {lsm_maass.n_liquid}")
    print(f"   Spatial organization: {lsm_maass.spatial_organization}")
    print(f"   Dynamic synapses: {lsm_maass.dynamic_synapses}")
    print(f"   Connectivity: {np.sum(lsm_maass.W_liquid != 0) / (lsm_maass.n_liquid ** 2):.1%}")
    
except Exception as e:
    print(f"❌ LSM initialization failed: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")