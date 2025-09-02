"""
🌐 Network Topology Management for Echo State Networks
====================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module implements various network topologies for Echo State Network reservoirs,
based on established graph theory and network science research. The topology of the
reservoir significantly affects the computational properties and dynamics of the ESN.

🔬 Research Background:
======================

Network topology in reservoir computing draws from decades of research in complex
networks and graph theory:

1. **Small-World Networks (Watts & Strogatz, 1998)**:
   "Collective dynamics of 'small-world' networks" - Nature 393:440-442
   - High clustering coefficient with short path lengths
   - Optimal balance between local and global information flow
   - Critical for temporal pattern recognition and memory tasks

2. **Scale-Free Networks (Barabási & Albert, 1999)**:
   "Emergence of scaling in random networks" - Science 286:509-512
   - Power-law degree distribution: P(k) ~ k^(-γ)
   - Hub-based architecture with heterogeneous connectivity
   - Robust to random failures, vulnerable to targeted attacks

3. **Ring Topologies in Neural Networks**:
   - Simple periodic connectivity patterns
   - Efficient for cyclic and oscillatory dynamics
   - Foundation for more complex topologies

4. **Random Networks (Erdős-Rényi Model)**:
   - Baseline topology with uniform connection probability
   - Well-studied statistical properties
   - Standard comparison for other topologies

🎯 Computational Properties:
===========================

Different topologies provide distinct computational advantages:

- **Ring**: Excellent for periodic patterns, oscillations, and circular buffer dynamics
- **Small-World**: Balance between local clustering and global connectivity
- **Scale-Free**: Hierarchical processing with hub neurons as information integrators  
- **Random**: Uniform information mixing, baseline dynamics
- **Custom**: Task-specific architectures based on domain knowledge

🏗️ Mathematical Foundations:
============================

Each topology affects the reservoir's spectral properties:

1. **Spectral Radius**: λmax(W) determines echo state property
2. **Clustering Coefficient**: Local connectivity density
3. **Path Length**: Information propagation efficiency
4. **Degree Distribution**: Connection heterogeneity

The Echo State Property requires: ρ(W) < 1, where ρ is spectral radius.
"""

import numpy as np
from typing import Optional, Tuple
import warnings


class TopologyManagementMixin:
    """
    Mixin class providing network topology creation methods for Echo State Networks.
    
    This mixin implements various graph-theoretic topologies that can be used as
    reservoir connectivity patterns, each with distinct computational properties
    and mathematical foundations.
    
    The mixin assumes the following attributes exist in the parent class:
    - n_reservoir: Number of neurons in the reservoir
    - sparsity: Target connection density
    - reservoir_connectivity_mask: Optional custom connectivity pattern
    """
    
    def _create_ring_topology(self) -> np.ndarray:
        """
        Create ring topology reservoir with local connectivity patterns.
        
        🔬 **Research Background:**
        Ring topologies create circular connectivity patterns that are excellent
        for modeling periodic phenomena, oscillatory dynamics, and temporal
        sequences with cyclic structure.
        
        **Mathematical Properties:**
        - Regular graph with degree k = 2 * connections_per_node
        - Clustering coefficient: C ≈ 3(k-2) / 4(k-1) for k >> 1
        - Characteristic path length: L ≈ n/(2k) for large networks
        - Spectral properties: eigenvalues distributed on complex unit circle
        
        **Computational Advantages:**
        - Efficient for circular buffer operations
        - Natural periodic boundary conditions  
        - Stable oscillatory dynamics
        - Memory of recent temporal patterns
        
        **Implementation Details:**
        Creates bidirectional ring connections where each neuron connects to
        its k nearest neighbors (k/2 forward, k/2 backward). This creates
        locally connected neighborhoods with global circular structure.
        
        Returns:
            np.ndarray: Ring topology weight matrix (n_reservoir × n_reservoir)
            
        References:
            - Newman, M.E.J. (2003). "The structure and function of complex networks"
            - Watts, D.J. (1999). "Small Worlds: The Dynamics of Networks"
        """
        W = np.zeros((self.n_reservoir, self.n_reservoir))
        connections_per_node = max(1, int(self.sparsity * self.n_reservoir))
        
        for i in range(self.n_reservoir):
            # Create forward and backward connections for bidirectional ring
            for j in range(1, connections_per_node + 1):
                # Forward connections (clockwise)
                forward_target = (i + j) % self.n_reservoir
                W[i, forward_target] = np.random.uniform(-1, 1)
                
                # Backward connections (counter-clockwise) 
                # Only add half as many backward to maintain balance
                if j <= connections_per_node // 2:
                    backward_target = (i - j) % self.n_reservoir
                    W[i, backward_target] = np.random.uniform(-1, 1)
            
            # Add some random long-range connections for richer dynamics
            n_random = max(1, connections_per_node // 4)
            for _ in range(n_random):
                random_target = np.random.randint(self.n_reservoir)
                if random_target != i and W[i, random_target] == 0:
                    W[i, random_target] = np.random.uniform(-1, 1)
        
        print(f"   ✓ Ring topology created ({np.sum(W != 0)} connections)")
        return W
    
    def _create_small_world_topology(self) -> np.ndarray:
        """
        Create small-world topology using the Watts-Strogatz model.
        
        🔬 **Research Background:**
        The small-world model (Watts & Strogatz, 1998) captures the structure
        of many real-world networks including neural circuits, social networks,
        and information systems.
        
        **Key Innovation:**
        Small-world networks exhibit both high local clustering (like regular
        lattices) and short path lengths (like random graphs), making them
        ideal for both local processing and global information integration.
        
        **Mathematical Properties:**
        - High clustering coefficient: C >> C_random
        - Short path length: L ≈ L_random ~ log(N)
        - "Small-world" regime: C >> C_random and L ≈ L_random
        - Critical rewiring probability: p* ≈ 1/N for small-world emergence
        
        **Watts-Strogatz Algorithm:**
        1. Start with regular ring lattice (k neighbors per node)
        2. Rewire each edge with probability p to random target
        3. Preserve connectivity and avoid self-loops
        
        **Computational Advantages:**
        - Optimal balance of local and global connectivity
        - Efficient information propagation with local processing
        - Robust to perturbations and noise
        - Enhanced synchronization and pattern formation
        
        **Parameter Selection:**
        - p = 0.01-0.1: Creates small-world regime
        - k = 4-10: Provides sufficient local connectivity
        - Higher p: More randomness, lower clustering
        
        Returns:
            np.ndarray: Small-world topology weight matrix (n_reservoir × n_reservoir)
            
        References:
            - Watts, D.J., & Strogatz, S.H. (1998). "Collective dynamics of 
              'small-world' networks." Nature, 393(6684), 440-442.
            - Newman, M.E.J., & Watts, D.J. (1999). "Renormalization group 
              analysis of the small-world network model." Physics Letters A, 263(4-6), 341-346.
        """
        W = np.zeros((self.n_reservoir, self.n_reservoir))
        k = max(2, int(self.sparsity * self.n_reservoir))  # Average degree (must be even)
        if k % 2 == 1:
            k += 1  # Ensure even degree for symmetric ring
            
        # Step 1: Create regular ring lattice with k nearest neighbors
        for i in range(self.n_reservoir):
            for j in range(1, k // 2 + 1):  # Connect to k/2 neighbors on each side
                # Right neighbors
                right_neighbor = (i + j) % self.n_reservoir
                W[i, right_neighbor] = np.random.uniform(-1, 1)
                
                # Left neighbors  
                left_neighbor = (i - j) % self.n_reservoir
                W[i, left_neighbor] = np.random.uniform(-1, 1)
        
        # Step 2: Rewire edges with probability p to create small-world structure
        rewire_probability = 0.1  # Classic small-world parameter
        
        for i in range(self.n_reservoir):
            # Consider all existing connections for potential rewiring
            existing_connections = np.where(W[i, :] != 0)[0]
            
            for target in existing_connections:
                if np.random.random() < rewire_probability:
                    # Save original weight
                    original_weight = W[i, target]
                    
                    # Remove original connection
                    W[i, target] = 0
                    
                    # Create new random connection (avoid self-loops and duplicates)
                    attempts = 0
                    max_attempts = 10
                    
                    while attempts < max_attempts:
                        new_target = np.random.randint(self.n_reservoir)
                        if new_target != i and W[i, new_target] == 0:
                            W[i, new_target] = original_weight  # Preserve weight magnitude
                            break
                        attempts += 1
                    
                    # If couldn't find valid target, restore original connection
                    if attempts >= max_attempts:
                        W[i, target] = original_weight
        
        print(f"   ✓ Small-world topology created ({np.sum(W != 0)} connections)")
        return W
    
    def _create_scale_free_topology(self) -> np.ndarray:
        """
        Create scale-free topology using preferential attachment (Barabási-Albert model).
        
        🔬 **Research Background:**
        Scale-free networks exhibit power-law degree distributions and are ubiquitous
        in nature, from neural networks to the Internet. The Barabási-Albert model
        (1999) explains how such networks emerge through growth and preferential attachment.
        
        **Key Principle - "Rich Get Richer":**
        New connections preferentially attach to nodes that already have many connections,
        leading to the emergence of highly connected "hub" nodes and a power-law 
        degree distribution: P(k) ~ k^(-γ), where γ ≈ 3 for BA networks.
        
        **Mathematical Properties:**
        - Power-law degree distribution: P(k) ~ k^(-γ)
        - Scale-free: No characteristic scale in connectivity
        - Small-world property: L ~ log(log(N))
        - Clustering coefficient: C ~ k^(-1) 
        - Robust to random failures, fragile to targeted hub attacks
        
        **Barabási-Albert Algorithm:**
        1. Start with small connected seed network
        2. Add nodes one by one
        3. Each new node connects to m existing nodes
        4. Connection probability proportional to node degree: P_i ~ k_i
        
        **Computational Advantages:**
        - Hub nodes act as information integrators
        - Hierarchical processing architecture
        - Efficient global communication through hubs
        - Robust dynamics under random perturbations
        - Fast information spreading and synchronization
        
        **Applications in Reservoir Computing:**
        - Hub neurons can serve as memory centers
        - Hierarchical temporal pattern processing
        - Multi-scale dynamics from heterogeneous connectivity
        - Enhanced computational capacity through specialization
        
        **Implementation Notes:**
        This implementation uses a simplified preferential attachment where
        connection probability is proportional to current degree, creating
        the characteristic hub structure of scale-free networks.
        
        Returns:
            np.ndarray: Scale-free topology weight matrix (n_reservoir × n_reservoir)
            
        References:
            - Barabási, A.L., & Albert, R. (1999). "Emergence of scaling in random networks." 
              Science, 286(5439), 509-512.
            - Albert, R., & Barabási, A.L. (2002). "Statistical mechanics of complex networks." 
              Reviews of Modern Physics, 74(1), 47-97.
            - Newman, M.E.J. (2005). "Power laws, Pareto distributions and Zipf's law." 
              Contemporary Physics, 46(5), 323-351.
        """
        W = np.zeros((self.n_reservoir, self.n_reservoir))
        
        # Initialize with small fully connected seed network
        seed_size = min(5, self.n_reservoir // 10)  # Start with small seed
        for i in range(seed_size):
            for j in range(seed_size):
                if i != j:
                    W[i, j] = np.random.uniform(-1, 1)
        
        # Track node degrees for preferential attachment
        degree = np.sum(W != 0, axis=1) + np.sum(W != 0, axis=0)  # In + out degree
        degree = np.maximum(degree, 1)  # Avoid zero degree
        
        # Calculate total connections to add
        target_connections = int(self.sparsity * self.n_reservoir * self.n_reservoir)
        current_connections = np.sum(W != 0)
        connections_to_add = max(0, target_connections - current_connections)
        
        # Add connections using preferential attachment
        for _ in range(connections_to_add):
            # Select source node randomly
            source = np.random.randint(self.n_reservoir)
            
            # Select target using preferential attachment
            # Probability proportional to degree
            if np.sum(degree) > 0:
                probabilities = degree / np.sum(degree)
                target = np.random.choice(self.n_reservoir, p=probabilities)
                
                # Add connection if valid (no self-loops, no duplicates)
                if source != target and W[source, target] == 0:
                    W[source, target] = np.random.uniform(-1, 1)
                    
                    # Update degrees
                    degree[source] += 1  # Out-degree
                    degree[target] += 1   # In-degree
        
        # Ensure some bidirectional connections for richer dynamics
        # Randomly select a fraction of edges to make bidirectional
        nonzero_indices = np.where(W != 0)
        n_edges = len(nonzero_indices[0])
        n_bidirectional = int(0.3 * n_edges)  # Make 30% bidirectional
        
        if n_bidirectional > 0:
            bidirectional_indices = np.random.choice(n_edges, 
                                                   size=min(n_bidirectional, n_edges), 
                                                   replace=False)
            
            for idx in bidirectional_indices:
                i, j = nonzero_indices[0][idx], nonzero_indices[1][idx]
                if W[j, i] == 0:  # Only add if reverse connection doesn't exist
                    W[j, i] = np.random.uniform(-1, 1)
        
        print(f"   ✓ Scale-free topology created ({np.sum(W != 0)} connections)")
        
        # Optional: Print degree distribution statistics
        final_degrees = np.sum(W != 0, axis=1) + np.sum(W != 0, axis=0)
        if np.max(final_degrees) > 0:
            print(f"      Degree statistics: mean={np.mean(final_degrees):.1f}, "
                  f"max={np.max(final_degrees)}, hubs={np.sum(final_degrees > 2*np.mean(final_degrees))}")
        
        return W
    
    def _create_custom_topology(self) -> np.ndarray:
        """
        Create reservoir topology using custom connectivity mask.
        
        🔬 **Research Background:**
        Custom topologies allow incorporation of domain-specific knowledge and
        task-specific architectural constraints into the reservoir design. This
        approach enables the creation of specialized network structures based on:
        
        - **Biological neural circuit motifs** (feedforward, feedback, lateral inhibition)
        - **Task-specific connectivity patterns** (hierarchical, modular, layered)
        - **Mathematical graph structures** (lattices, trees, complete subgraphs)
        - **Engineered architectures** (convolutional, attention-like patterns)
        
        **Design Principles:**
        1. **Connectivity Mask**: Binary or weighted matrix defining allowed connections
        2. **Weight Assignment**: Random or structured weight assignment to allowed connections
        3. **Spectral Control**: Ensure spectral radius requirements are met
        4. **Sparsity Preservation**: Maintain computational efficiency
        
        **Applications:**
        - **Modular Reservoirs**: Separate modules for different input types
        - **Hierarchical Processing**: Multi-layer architectures with skip connections
        - **Spatially-Structured**: 2D/3D grids for spatial pattern processing
        - **Task-Specific**: Architectures optimized for particular problem domains
        
        **Mathematical Considerations:**
        The custom mask M must satisfy:
        - M[i,j] ∈ {0,1} for binary masks or M[i,j] ∈ ℝ for weighted masks
        - Resulting W = M ⊙ R where R is random weight matrix and ⊙ is element-wise product
        - Spectral radius ρ(W) must be scaled to satisfy Echo State Property
        
        **Implementation Details:**
        This method takes a pre-defined connectivity mask and assigns random weights
        to non-zero entries. The mask can be:
        - Binary: 1 indicates allowed connection, 0 indicates no connection
        - Weighted: Non-zero values indicate connection strength constraints
        
        Returns:
            np.ndarray: Custom topology weight matrix (n_reservoir × n_reservoir)
            
        Raises:
            ValueError: If connectivity mask shape doesn't match reservoir size
            AttributeError: If no connectivity mask is provided
            
        Examples:
            ```python
            # Create 2D grid topology
            mask = create_2d_grid_mask(n_reservoir, grid_size=(10, 10))
            esn = EchoStateNetwork(reservoir_connectivity_mask=mask)
            
            # Create modular topology
            mask = create_modular_mask(n_reservoir, n_modules=4)
            esn = EchoStateNetwork(reservoir_connectivity_mask=mask)
            ```
            
        References:
            - Appeltant, L., et al. (2011). "Information processing using a single 
              dynamical node as complex system." Nature Communications, 2, 468.
            - Lukoševičius, M. (2012). "A practical guide to applying echo state networks." 
              In Neural Networks: Tricks of the Trade (pp. 659-686).
        """
        if not hasattr(self, 'reservoir_connectivity_mask') or self.reservoir_connectivity_mask is None:
            raise AttributeError(
                "No connectivity mask provided. Set reservoir_connectivity_mask attribute "
                "or use a different topology method."
            )
        
        # Validate mask dimensions
        if self.reservoir_connectivity_mask.shape != (self.n_reservoir, self.n_reservoir):
            raise ValueError(
                f"Connectivity mask shape {self.reservoir_connectivity_mask.shape} "
                f"doesn't match reservoir size ({self.n_reservoir}, {self.n_reservoir})"
            )
        
        # Create weight matrix based on connectivity mask
        if np.all((self.reservoir_connectivity_mask == 0) | (self.reservoir_connectivity_mask == 1)):
            # Binary mask: assign random weights where mask is 1
            W = np.random.uniform(-1, 1, (self.n_reservoir, self.n_reservoir))
            W = W * self.reservoir_connectivity_mask
        else:
            # Weighted mask: use mask values as weight constraints
            W = self.reservoir_connectivity_mask.copy()
            
            # Add randomness while preserving structure
            nonzero_mask = (W != 0)
            random_factors = np.random.uniform(0.5, 1.5, W.shape)  # Vary weights by ±50%
            W[nonzero_mask] = W[nonzero_mask] * random_factors[nonzero_mask]
        
        # Validate connectivity
        n_connections = np.sum(W != 0)
        if n_connections == 0:
            warnings.warn(
                "Custom topology resulted in no connections. Check connectivity mask.",
                UserWarning
            )
        
        # Optional: Analyze connectivity properties
        if n_connections > 0:
            # Calculate basic network statistics
            actual_sparsity = n_connections / (self.n_reservoir ** 2)
            in_degrees = np.sum(W != 0, axis=0)
            out_degrees = np.sum(W != 0, axis=1)
            
            print(f"   ✓ Custom topology applied ({n_connections} connections)")
            print(f"      Actual sparsity: {actual_sparsity:.4f}")
            print(f"      Degree stats: in={np.mean(in_degrees):.1f}±{np.std(in_degrees):.1f}, "
                  f"out={np.mean(out_degrees):.1f}±{np.std(out_degrees):.1f}")
            
            # Check for isolated nodes
            isolated_nodes = np.sum((in_degrees == 0) & (out_degrees == 0))
            if isolated_nodes > 0:
                warnings.warn(
                    f"Custom topology has {isolated_nodes} isolated nodes. "
                    f"This may reduce computational capacity.",
                    UserWarning
                )
        
        return W
    
    def _scale_spectral_radius(self, W: np.ndarray, target_radius: float) -> np.ndarray:
        """
        Scale weight matrix to achieve target spectral radius while preserving topology.
        
        🔬 **Mathematical Background:**
        The spectral radius ρ(W) = max|λᵢ| where λᵢ are eigenvalues of W.
        For Echo State Property (ESP), we require ρ(W) < 1.
        
        **Scaling Methods:**
        1. **Uniform Scaling**: W_new = (target_radius / ρ(W)) * W
        2. **Structure-Preserving**: Maintains relative eigenvalue relationships
        3. **Complex-Aware**: Handles complex eigenvalues appropriately
        
        **Theoretical Foundation:**
        If W has spectral radius ρ, then αW has spectral radius α·ρ.
        This linear scaling preserves the network topology while controlling dynamics.
        
        Args:
            W: Weight matrix to scale
            target_radius: Desired spectral radius (typically < 1.0)
            
        Returns:
            np.ndarray: Scaled weight matrix with target spectral radius
            
        References:
            - Jaeger, H. (2001). "The 'echo state' approach to analysing and training RNNs."
            - Yildiz, I.B., et al. (2012). "Re-visiting the echo state property." Neural Networks, 35, 1-9.
        """
        if W.size == 0 or np.all(W == 0):
            return W
            
        # Calculate current spectral radius
        try:
            eigenvalues = np.linalg.eigvals(W)
            current_radius = np.max(np.abs(eigenvalues))
            
            # Scale if current radius is positive
            if current_radius > 1e-12:  # Avoid division by very small numbers
                scaling_factor = target_radius / current_radius
                W_scaled = W * scaling_factor
                
                # Verify scaling worked
                new_eigenvalues = np.linalg.eigvals(W_scaled)
                achieved_radius = np.max(np.abs(new_eigenvalues))
                
                if abs(achieved_radius - target_radius) > 1e-6:
                    warnings.warn(
                        f"Spectral radius scaling may be inaccurate. "
                        f"Target: {target_radius:.6f}, Achieved: {achieved_radius:.6f}",
                        UserWarning
                    )
                
                return W_scaled
            else:
                warnings.warn("Matrix has zero spectral radius, no scaling applied.", UserWarning)
                return W
                
        except np.linalg.LinAlgError as e:
            warnings.warn(f"Could not compute eigenvalues for scaling: {e}", UserWarning)
            return W