"""
Reservoir Topology Creation for Echo State Networks
Implements various network topologies from Jaeger 2001 and extensions
"""

import numpy as np
import networkx as nx
from typing import Tuple, Optional, Dict, Any
from scipy.sparse import csr_matrix


class ReservoirTopology:
    """Creates various reservoir topologies for ESN"""
    
    def __init__(self, reservoir_size: int, spectral_radius: float = 0.95):
        self.reservoir_size = reservoir_size
        self.spectral_radius = spectral_radius
    
    def create_random_topology(self, connectivity: float = 0.1) -> np.ndarray:
        """Create classical sparse random topology (Jaeger 2001)"""
        # Create sparse random matrix
        reservoir_weights = np.random.randn(self.reservoir_size, self.reservoir_size)
        
        # Apply sparsity
        mask = np.random.random((self.reservoir_size, self.reservoir_size)) < connectivity
        reservoir_weights *= mask
        
        # Scale to desired spectral radius
        return self._scale_spectral_radius(reservoir_weights)
    
    def create_ring_topology(self) -> np.ndarray:
        """Simple ring topology for periodic patterns"""
        reservoir_weights = np.zeros((self.reservoir_size, self.reservoir_size))
        
        # Create ring connections
        for i in range(self.reservoir_size):
            next_idx = (i + 1) % self.reservoir_size
            reservoir_weights[i, next_idx] = np.random.uniform(-1, 1)
        
        return self._scale_spectral_radius(reservoir_weights)
    
    def create_small_world_topology(self, k: int = 4, p: float = 0.3) -> np.ndarray:
        """Watts-Strogatz small-world networks"""
        # Create small-world graph using NetworkX
        G = nx.watts_strogatz_graph(self.reservoir_size, k, p)
        
        # Convert to weighted adjacency matrix
        adj_matrix = nx.adjacency_matrix(G).astype(float)
        reservoir_weights = adj_matrix.toarray()
        
        # Add random weights
        mask = reservoir_weights > 0
        reservoir_weights[mask] = np.random.uniform(-1, 1, size=np.sum(mask))
        
        return self._scale_spectral_radius(reservoir_weights)
    
    def create_scale_free_topology(self, m: int = 2) -> np.ndarray:
        """Barabási-Albert preferential attachment (scale-free)"""
        # Create scale-free graph
        G = nx.barabasi_albert_graph(self.reservoir_size, m)
        
        # Convert to weighted adjacency matrix  
        adj_matrix = nx.adjacency_matrix(G).astype(float)
        reservoir_weights = adj_matrix.toarray()
        
        # Add random weights
        mask = reservoir_weights > 0
        reservoir_weights[mask] = np.random.uniform(-1, 1, size=np.sum(mask))
        
        # Make it asymmetric for directed dynamics
        asymmetric_mask = np.random.random(reservoir_weights.shape) < 0.5
        reservoir_weights *= asymmetric_mask
        
        return self._scale_spectral_radius(reservoir_weights)
    
    def create_custom_topology(self, topology_params: Dict[str, Any]) -> np.ndarray:
        """Create custom topology based on parameters"""
        topology_type = topology_params.get('type', 'random')
        
        if topology_type == 'random':
            connectivity = topology_params.get('connectivity', 0.1)
            return self.create_random_topology(connectivity)
        elif topology_type == 'ring':
            return self.create_ring_topology()
        elif topology_type == 'small_world':
            k = topology_params.get('k', 4)
            p = topology_params.get('p', 0.3)
            return self.create_small_world_topology(k, p)
        elif topology_type == 'scale_free':
            m = topology_params.get('m', 2)
            return self.create_scale_free_topology(m)
        else:
            raise ValueError(f"Unknown topology type: {topology_type}")
    
    def _scale_spectral_radius(self, matrix: np.ndarray) -> np.ndarray:
        """Scale matrix to desired spectral radius for Echo State Property"""
        # Compute current spectral radius (largest eigenvalue magnitude)
        eigenvalues = np.linalg.eigvals(matrix)
        current_radius = np.max(np.abs(eigenvalues))
        
        if current_radius > 1e-10:  # Avoid division by zero
            # Scale matrix
            scaled_matrix = matrix * (self.spectral_radius / current_radius)
        else:
            scaled_matrix = matrix
        
        return scaled_matrix
    
    def generate_correlated_noise(self, correlation_length: int = 5) -> np.ndarray:
        """Generate spatially correlated noise for reservoir initialization"""
        # Generate uncorrelated noise
        noise = np.random.randn(self.reservoir_size)
        
        # Apply spatial correlation using convolution
        if correlation_length > 1:
            kernel = np.exp(-np.arange(-correlation_length, correlation_length+1)**2 / (2 * (correlation_length/3)**2))
            kernel /= np.sum(kernel)
            
            # Convolve with periodic boundary conditions
            noise_padded = np.concatenate([noise[-correlation_length:], noise, noise[:correlation_length]])
            correlated = np.convolve(noise_padded, kernel, mode='valid')[correlation_length:-correlation_length]
            return correlated
        
        return noise
    
    def validate_topology_properties(self, reservoir_weights: np.ndarray) -> Dict[str, Any]:
        """Validate topological properties of reservoir"""
        eigenvalues = np.linalg.eigvals(reservoir_weights)
        spectral_radius = np.max(np.abs(eigenvalues))
        
        # Compute connectivity
        connectivity = np.mean(reservoir_weights != 0)
        
        # Compute clustering coefficient if possible
        try:
            G = nx.from_numpy_array(reservoir_weights)
            clustering = nx.average_clustering(G)
        except:
            clustering = 0.0
        
        return {
            'spectral_radius': spectral_radius,
            'connectivity': connectivity, 
            'clustering_coefficient': clustering,
            'eigenvalue_spread': np.std(np.abs(eigenvalues)),
            'largest_eigenvalue': np.max(np.real(eigenvalues)),
            'echo_state_satisfied': spectral_radius < 1.0
        }