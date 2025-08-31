#!/usr/bin/env python3
"""
Simple test to isolate the infinite loop issue
"""

import sys
import os
import numpy as np

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the LSM classes
from liquid_state_machine import LiquidStateMachine, LSMConfig, NeuronModelType

print("Testing simple LSM initialization...")

# Create a simple configuration without spatial organization
simple_config = LSMConfig(
    n_liquid=10,  # Small network
    spatial_organization=False,  # Disable spatial organization
    connectivity_prob=0.1,  # Low connectivity
    dt=1.0
)

print("Configuration created, initializing LSM...")

try:
    lsm = LiquidStateMachine(config=simple_config)
    print("✅ Simple LSM initialized successfully!")
    print(f"   Neurons: {lsm.n_liquid}")
    print(f"   Connectivity: {np.sum(lsm.W_liquid != 0) / (lsm.n_liquid ** 2):.1%}")
except Exception as e:
    print(f"❌ LSM initialization failed: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")