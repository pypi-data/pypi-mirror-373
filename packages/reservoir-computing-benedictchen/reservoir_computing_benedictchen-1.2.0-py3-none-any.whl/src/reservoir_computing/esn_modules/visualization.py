"""
🎨 Advanced Visualization for Echo State Networks - Comprehensive Analysis Suite
=============================================================================

Author: Benedict Chen (benedict@benedictchen.com)

💰 Donations: Help support this work! Buy me a coffee ☕, beer 🍺, or lamborghini 🏎️
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Please consider recurring donations to fully support continued research

🎯 ELI5 Summary:
This module provides comprehensive visualization tools for analyzing Echo State Networks.
Like having a microscope, telescope, and oscilloscope all in one for examining your
reservoir's behavior from every angle - network structure, dynamics, performance,
spectral properties, and comparative analysis.

🔬 Research Background:
======================
Visualization is crucial for understanding reservoir computing dynamics. This module
builds on foundational work from:

1. Jaeger, H. (2001) - Original ESN visualization of spectral radius and connectivity
2. Lukoševičius, M. & Jaeger, H. (2009) - Reservoir computing survey with analysis methods  
3. Verstraeten, D. et al. (2007) - Memory capacity and visualization techniques
4. Schrauwen, B. et al. (2007) - Network topology analysis for reservoir computing
5. Deng, Z. & Zhang, Y. (2007) - Dynamic analysis visualization methods
6. Appeltant, L. et al. (2011) - Information processing capacity visualization

🏗️ Visualization Categories:
============================
1. Network Structure Analysis - Topology, weights, connectivity patterns
2. Dynamic Behavior - State evolution, memory capacity, transient analysis  
3. Spectral Analysis - Eigenvalues, stability regions, frequency response
4. Performance Metrics - Training curves, prediction accuracy, error analysis
5. Comparative Analysis - Multiple configurations, parameter sensitivity
6. Information Processing - Input-output relationships, nonlinear transformations

🎨 Professional Plotting Standards:
==================================
- High-resolution vector graphics suitable for publication
- Consistent color schemes following perceptual uniformity (viridis, plasma)
- Clear typography with appropriate font sizes
- Comprehensive legends and annotations
- Statistical error bars and confidence intervals
- Interactive capabilities where beneficial
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.animation import FuncAnimation
import seaborn as sns
from scipy import signal, stats
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram
import networkx as nx
from typing import Optional, Tuple, Dict, Any, List, Union, Callable
import warnings
from mpl_toolkits.mplot3d import Axes3D
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import pandas as pd

# Set professional plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class VisualizationMixin:
    """
    🎨 Comprehensive Visualization Mixin for Echo State Networks
    
    This mixin provides extensive visualization capabilities for analyzing
    reservoir computing systems from multiple perspectives.
    """
    
    def visualize_reservoir(self, figsize: Tuple[int, int] = (15, 10), save_path: Optional[str] = None):
        """
        Enhanced reservoir visualization with comprehensive analysis
        
        Based on Jaeger (2001) original visualization extended with modern analysis
        """
        
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        fig.suptitle('Echo State Network Reservoir Analysis', fontsize=16, fontweight='bold')
        
        # 1. Enhanced Reservoir connectivity matrix with statistical overlay
        ax1 = axes[0, 0]
        im1 = ax1.imshow(self.W_reservoir, cmap='RdBu_r', aspect='auto', 
                        vmin=-np.max(np.abs(self.W_reservoir)), 
                        vmax=np.max(np.abs(self.W_reservoir)))
        ax1.set_title(f'Reservoir Matrix ({self.n_reservoir}×{self.n_reservoir})\n'
                     f'Density: {np.mean(self.W_reservoir != 0):.1%}')
        ax1.set_xlabel('From Neuron')
        ax1.set_ylabel('To Neuron')
        cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
        cbar1.set_label('Connection Strength', rotation=270, labelpad=15)
        
        # 2. Enhanced eigenvalue analysis with stability regions
        eigenvals = np.linalg.eigvals(self.W_reservoir)
        ax2 = axes[0, 1]
        scatter = ax2.scatter(eigenvals.real, eigenvals.imag, alpha=0.7, 
                            c=np.abs(eigenvals), cmap='viridis', s=30)
        
        # Unit circle for stability
        circle = plt.Circle((0, 0), 1, fill=False, color='red', linestyle='--', linewidth=2)
        ax2.add_patch(circle)
        
        # Echo state property region (|λ| < 1)
        max_eigenval = np.max(np.abs(eigenvals))
        ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        ax2.axvline(x=0, color='k', linestyle='-', alpha=0.3)
        
        ax2.set_title(f'Eigenvalue Spectrum\nSpectral Radius: {max_eigenval:.4f}')
        ax2.set_xlabel('Real Part')
        ax2.set_ylabel('Imaginary Part')
        ax2.axis('equal')
        ax2.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax2, shrink=0.8, label='|λ|')
        
        # Add stability annotation
        if max_eigenval < 1:
            ax2.text(0.02, 0.98, '✓ Echo State Property', transform=ax2.transAxes,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7),
                    verticalalignment='top')
        else:
            ax2.text(0.02, 0.98, '⚠ Unstable Regime', transform=ax2.transAxes,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.7),
                    verticalalignment='top')
        
        # 3. Advanced connection analysis
        degrees = np.sum(self.W_reservoir != 0, axis=1)
        ax3 = axes[0, 2]
        
        # Histogram with statistical overlay
        n, bins, patches = ax3.hist(degrees, bins=20, alpha=0.7, edgecolor='black', density=True)
        
        # Add normal distribution overlay if appropriate
        mu, sigma = stats.norm.fit(degrees)
        x = np.linspace(degrees.min(), degrees.max(), 100)
        ax3.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
                label=f'Normal fit (μ={mu:.1f}, σ={sigma:.1f})')
        
        ax3.set_title(f'Degree Distribution\nSparsity: {self.sparsity:.1%}')
        ax3.set_xlabel('Number of Connections')
        ax3.set_ylabel('Probability Density')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Weight distribution with statistical analysis
        weights = self.W_reservoir[self.W_reservoir != 0]
        ax4 = axes[1, 0]
        
        # Enhanced histogram with multiple statistics
        n, bins, patches = ax4.hist(weights, bins=50, alpha=0.7, edgecolor='black', density=True)
        
        # Add statistical overlays
        ax4.axvline(weights.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {weights.mean():.3f}')
        ax4.axvline(np.median(weights), color='orange', linestyle='--', linewidth=2, label=f'Median: {np.median(weights):.3f}')
        
        ax4.set_title('Weight Distribution Analysis')
        ax4.set_xlabel('Weight Value')
        ax4.set_ylabel('Probability Density')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Add text box with statistics
        stats_text = f'Std: {weights.std():.3f}\nSkew: {stats.skew(weights):.3f}\nKurt: {stats.kurtosis(weights):.3f}'
        ax4.text(0.02, 0.98, stats_text, transform=ax4.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                verticalalignment='top', fontsize=9)
        
        # 5. Network topology visualization (sample for large networks)
        ax5 = axes[1, 1]
        if self.n_reservoir <= 100:  # Only for manageable sizes
            # Create networkx graph
            G = nx.from_numpy_array(self.W_reservoir, create_using=nx.DiGraph)
            pos = nx.spring_layout(G, k=1/np.sqrt(self.n_reservoir), iterations=50)
            
            # Draw network with edge weights represented by thickness and color
            edges = G.edges()
            weights_nx = [G[u][v]['weight'] for u, v in edges]
            
            nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                                 node_size=50, alpha=0.8, ax=ax5)
            nx.draw_networkx_edges(G, pos, edge_color=weights_nx, edge_cmap=plt.cm.RdBu_r,
                                 width=[abs(w)*3 for w in weights_nx], alpha=0.6, ax=ax5)
            
            ax5.set_title('Network Topology\n(Spring Layout)')
        else:
            # For large networks, show connection pattern heatmap
            # Sample a subset for visualization
            sample_size = min(50, self.n_reservoir)
            indices = np.random.choice(self.n_reservoir, sample_size, replace=False)
            sample_matrix = self.W_reservoir[np.ix_(indices, indices)]
            
            im5 = ax5.imshow(sample_matrix, cmap='RdBu_r', aspect='auto')
            ax5.set_title(f'Connection Pattern\n(Random {sample_size}×{sample_size} Sample)')
            plt.colorbar(im5, ax=ax5, shrink=0.6)
        
        ax5.axis('off')
        
        # 6. Spectral analysis - eigenvalue distribution
        ax6 = axes[1, 2]
        eigenval_magnitudes = np.abs(eigenvals)
        eigenval_phases = np.angle(eigenvals)
        
        # Polar histogram of eigenvalue phases
        ax6_polar = plt.subplot(2, 3, 6, projection='polar')
        ax6_polar.hist(eigenval_phases, bins=20, alpha=0.7)
        ax6_polar.set_title('Eigenvalue Phase Distribution')
        ax6_polar.set_theta_zero_location('E')
        
        plt.tight_layout()
        
        # Save if requested
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        # Enhanced statistics reporting
        self._print_reservoir_statistics(eigenvals, degrees, weights)
    
    def visualize_dynamics(self, states: np.ndarray, inputs: Optional[np.ndarray] = None, 
                          outputs: Optional[np.ndarray] = None, figsize: Tuple[int, int] = (15, 10),
                          save_path: Optional[str] = None):
        """
        Comprehensive visualization of reservoir dynamics and temporal behavior
        
        Args:
            states: Reservoir state matrix (time_steps × n_reservoir)
            inputs: Input sequence (time_steps × n_inputs) [optional]
            outputs: Output sequence (time_steps × n_outputs) [optional]
        """
        
        fig = plt.figure(figsize=figsize)
        fig.suptitle('Echo State Network Dynamics Analysis', fontsize=16, fontweight='bold')
        
        # 1. State evolution heatmap
        ax1 = plt.subplot(2, 3, 1)
        
        # Sample neurons for visualization if too many
        max_neurons_display = 50
        if states.shape[1] > max_neurons_display:
            neuron_indices = np.random.choice(states.shape[1], max_neurons_display, replace=False)
            display_states = states[:, neuron_indices]
            title_suffix = f" (Random {max_neurons_display} neurons)"
        else:
            display_states = states
            neuron_indices = np.arange(states.shape[1])
            title_suffix = ""
            
        im1 = ax1.imshow(display_states.T, cmap='viridis', aspect='auto', interpolation='nearest')
        ax1.set_title(f'State Evolution{title_suffix}')
        ax1.set_xlabel('Time Step')
        ax1.set_ylabel('Neuron Index')
        plt.colorbar(im1, ax=ax1, shrink=0.8, label='Activation')
        
        # 2. State trajectory in reduced space (PCA)
        ax2 = plt.subplot(2, 3, 2)
        if states.shape[1] >= 3:
            pca = PCA(n_components=3)
            states_pca = pca.fit_transform(states)
            
            # 3D trajectory
            ax2 = plt.subplot(2, 3, 2, projection='3d')
            scatter = ax2.scatter(states_pca[:, 0], states_pca[:, 1], states_pca[:, 2],
                                c=np.arange(len(states_pca)), cmap='plasma', s=20)
            ax2.set_title(f'State Trajectory (PCA)\nVariance Explained: {pca.explained_variance_ratio_[:3].sum():.1%}')
            ax2.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
            ax2.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
            ax2.set_zlabel(f'PC3 ({pca.explained_variance_ratio_[2]:.1%})')
            plt.colorbar(scatter, ax=ax2, shrink=0.5, label='Time')
        else:
            ax2.text(0.5, 0.5, 'Insufficient dimensions\nfor PCA visualization', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('State Trajectory (PCA)')
        
        # 3. Activity patterns
        ax3 = plt.subplot(2, 3, 3)
        
        # Calculate and plot activity statistics
        mean_activity = np.mean(states, axis=0)
        std_activity = np.std(states, axis=0)
        
        ax3.scatter(mean_activity, std_activity, alpha=0.6, s=30)
        ax3.set_xlabel('Mean Activity')
        ax3.set_ylabel('Activity Std')
        ax3.set_title('Neuron Activity Statistics')
        ax3.grid(True, alpha=0.3)
        
        # Add correlation coefficient
        corr_coef = np.corrcoef(mean_activity, std_activity)[0, 1]
        ax3.text(0.02, 0.98, f'Correlation: {corr_coef:.3f}', 
                transform=ax3.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                verticalalignment='top')
        
        # 4. Temporal correlation analysis
        ax4 = plt.subplot(2, 3, 4)
        
        # Compute autocorrelation for sample of neurons
        max_lag = min(50, states.shape[0] // 4)
        sample_neurons = min(10, states.shape[1])
        autocorrs = []
        
        for i in range(sample_neurons):
            autocorr = np.correlate(states[:, i], states[:, i], mode='full')
            autocorr = autocorr[len(autocorr)//2:][:max_lag]
            autocorr = autocorr / autocorr[0]  # Normalize
            autocorrs.append(autocorr)
        
        # Plot mean autocorrelation with confidence bands
        mean_autocorr = np.mean(autocorrs, axis=0)
        std_autocorr = np.std(autocorrs, axis=0)
        lags = np.arange(max_lag)
        
        ax4.plot(lags, mean_autocorr, 'b-', linewidth=2, label='Mean')
        ax4.fill_between(lags, mean_autocorr - std_autocorr, mean_autocorr + std_autocorr, 
                        alpha=0.3, label='±1 Std')
        ax4.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax4.set_title('Temporal Autocorrelation')
        ax4.set_xlabel('Lag (time steps)')
        ax4.set_ylabel('Autocorrelation')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Input-State relationship (if inputs provided)
        ax5 = plt.subplot(2, 3, 5)
        if inputs is not None:
            # Cross-correlation between input and reservoir states
            sample_size = min(100, states.shape[0])
            indices = np.random.choice(states.shape[0], sample_size, replace=False)
            
            input_sample = inputs[indices] if inputs.ndim > 1 else inputs[indices].reshape(-1, 1)
            state_sample = states[indices]
            
            # Calculate cross-correlation matrix
            n_inputs = input_sample.shape[1]
            n_display_neurons = min(20, states.shape[1])
            cross_corr = np.corrcoef(input_sample.T, state_sample[:, :n_display_neurons].T)[:n_inputs, n_inputs:]
            
            im5 = ax5.imshow(cross_corr, cmap='RdBu_r', aspect='auto', 
                           vmin=-1, vmax=1)
            ax5.set_title('Input-State Cross-correlation')
            ax5.set_xlabel('Reservoir Neurons')
            ax5.set_ylabel('Input Dimensions')
            plt.colorbar(im5, ax=ax5, shrink=0.8, label='Correlation')
        else:
            ax5.text(0.5, 0.5, 'No input data\nprovided', ha='center', va='center', 
                    transform=ax5.transAxes)
            ax5.set_title('Input-State Relationship')
        
        # 6. Spectral analysis of dynamics
        ax6 = plt.subplot(2, 3, 6)
        
        # Power spectral density of sample neurons
        sample_neurons = min(5, states.shape[1])
        frequencies = []
        power_spectra = []
        
        for i in range(sample_neurons):
            if len(states[:, i]) > 10:  # Ensure sufficient data
                f, Pxx = signal.periodogram(states[:, i], nperseg=min(256, len(states)//4))
                frequencies.append(f)
                power_spectra.append(Pxx)
        
        if power_spectra:
            mean_spectrum = np.mean(power_spectra, axis=0)
            std_spectrum = np.std(power_spectra, axis=0)
            
            ax6.loglog(frequencies[0], mean_spectrum, 'b-', linewidth=2, label='Mean PSD')
            ax6.fill_between(frequencies[0], 
                           np.maximum(mean_spectrum - std_spectrum, 1e-10),
                           mean_spectrum + std_spectrum, 
                           alpha=0.3, label='±1 Std')
            ax6.set_title('Power Spectral Density')
            ax6.set_xlabel('Frequency (normalized)')
            ax6.set_ylabel('Power')
            ax6.legend()
            ax6.grid(True, alpha=0.3)
        else:
            ax6.text(0.5, 0.5, 'Insufficient data\nfor spectral analysis', 
                    ha='center', va='center', transform=ax6.transAxes)
            ax6.set_title('Power Spectral Density')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.show()
        
        # Print dynamics statistics
        self._print_dynamics_statistics(states, inputs, outputs)
    
    def visualize_training_progress(self, train_errors: List[float], val_errors: Optional[List[float]] = None,
                                  metrics: Optional[Dict[str, List[float]]] = None,
                                  figsize: Tuple[int, int] = (12, 8), save_path: Optional[str] = None):
        """
        Visualize training progress and performance metrics
        
        Args:
            train_errors: Training errors over epochs
            val_errors: Validation errors over epochs [optional]  
            metrics: Dictionary of additional metrics to plot [optional]
        """
        
        n_plots = 2 + (1 if metrics else 0)
        fig, axes = plt.subplots(1, n_plots, figsize=figsize)
        if n_plots == 1:
            axes = [axes]
        elif n_plots == 2:
            axes = list(axes)
            
        fig.suptitle('Training Progress and Performance Analysis', fontsize=14, fontweight='bold')
        
        # 1. Error curves
        ax1 = axes[0]
        epochs = np.arange(1, len(train_errors) + 1)
        
        ax1.semilogy(epochs, train_errors, 'b-', linewidth=2, label='Training Error', marker='o', markersize=4)
        
        if val_errors is not None and len(val_errors) == len(train_errors):
            ax1.semilogy(epochs, val_errors, 'r-', linewidth=2, label='Validation Error', marker='s', markersize=4)
            
            # Find best epoch
            best_epoch = np.argmin(val_errors) + 1
            ax1.axvline(x=best_epoch, color='green', linestyle='--', alpha=0.7, 
                       label=f'Best Epoch: {best_epoch}')
            
            # Add text annotation for best performance
            ax1.text(0.7, 0.95, f'Best Val Error: {min(val_errors):.6f}\nAt Epoch: {best_epoch}', 
                    transform=ax1.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7),
                    verticalalignment='top')
        
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Error (log scale)')
        ax1.set_title('Training Error Curves')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Learning rate analysis
        ax2 = axes[1]
        if len(train_errors) > 1:
            # Calculate improvement rate
            improvements = []
            for i in range(1, len(train_errors)):
                improvement = (train_errors[i-1] - train_errors[i]) / train_errors[i-1]
                improvements.append(improvement * 100)  # Convert to percentage
            
            ax2.plot(epochs[1:], improvements, 'g-', linewidth=2, marker='o', markersize=4)
            ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('Improvement (%)')
            ax2.set_title('Learning Rate Analysis')
            ax2.grid(True, alpha=0.3)
            
            # Add statistics
            mean_improvement = np.mean(improvements)
            ax2.text(0.02, 0.98, f'Mean Improvement: {mean_improvement:.2f}%', 
                    transform=ax2.transAxes, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                    verticalalignment='top')
        else:
            ax2.text(0.5, 0.5, 'Insufficient data\nfor learning rate analysis', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Learning Rate Analysis')
        
        # 3. Additional metrics (if provided)
        if metrics and len(axes) > 2:
            ax3 = axes[2]
            
            for metric_name, metric_values in metrics.items():
                if len(metric_values) == len(train_errors):
                    ax3.plot(epochs, metric_values, linewidth=2, label=metric_name, marker='o', markersize=3)
            
            ax3.set_xlabel('Epoch')
            ax3.set_ylabel('Metric Value')
            ax3.set_title('Additional Performance Metrics')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.show()
    
    def visualize_performance_analysis(self, predictions: np.ndarray, targets: np.ndarray,
                                     inputs: Optional[np.ndarray] = None, 
                                     figsize: Tuple[int, int] = (15, 10),
                                     save_path: Optional[str] = None):
        """
        Comprehensive performance analysis visualization
        
        Args:
            predictions: Model predictions
            targets: True target values  
            inputs: Input sequence [optional]
        """
        
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        fig.suptitle('Performance Analysis and Prediction Quality', fontsize=16, fontweight='bold')
        
        # Calculate errors
        errors = predictions - targets
        mse = np.mean(errors**2)
        mae = np.mean(np.abs(errors))
        
        # 1. Prediction vs Target scatter plot
        ax1 = axes[0, 0]
        
        # Handle multi-dimensional outputs
        if predictions.ndim > 1 and predictions.shape[1] > 1:
            # For multi-output, plot first dimension or flattened
            pred_plot = predictions[:, 0] if predictions.shape[1] > 1 else predictions.flatten()
            target_plot = targets[:, 0] if targets.shape[1] > 1 else targets.flatten()
        else:
            pred_plot = predictions.flatten()
            target_plot = targets.flatten()
        
        ax1.scatter(target_plot, pred_plot, alpha=0.6, s=20)
        
        # Perfect prediction line
        min_val, max_val = min(target_plot.min(), pred_plot.min()), max(target_plot.max(), pred_plot.max())
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
        
        # Calculate R²
        r2 = 1 - np.sum((target_plot - pred_plot)**2) / np.sum((target_plot - np.mean(target_plot))**2)
        
        ax1.set_xlabel('True Values')
        ax1.set_ylabel('Predictions')
        ax1.set_title(f'Prediction Quality\nR² = {r2:.4f}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Add statistics box
        stats_text = f'MSE: {mse:.6f}\nMAE: {mae:.6f}\nR²: {r2:.4f}'
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                verticalalignment='top', fontsize=9)
        
        # 2. Time series comparison
        ax2 = axes[0, 1]
        
        # Show a subset for clarity
        display_length = min(200, len(predictions))
        indices = np.linspace(0, len(predictions)-1, display_length).astype(int)
        
        ax2.plot(indices, target_plot[indices], 'b-', linewidth=2, label='True', alpha=0.8)
        ax2.plot(indices, pred_plot[indices], 'r--', linewidth=2, label='Predicted', alpha=0.8)
        ax2.fill_between(indices, target_plot[indices], pred_plot[indices], alpha=0.3, color='gray')
        
        ax2.set_xlabel('Time Step')
        ax2.set_ylabel('Value')
        ax2.set_title(f'Time Series Comparison\n(Showing {display_length} points)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Error distribution analysis
        ax3 = axes[0, 2]
        
        error_flat = errors.flatten()
        
        # Histogram with statistical overlays
        n, bins, patches = ax3.hist(error_flat, bins=50, alpha=0.7, density=True, edgecolor='black')
        
        # Fit normal distribution
        mu, sigma = stats.norm.fit(error_flat)
        x = np.linspace(error_flat.min(), error_flat.max(), 100)
        ax3.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
                label=f'Normal fit\n(μ={mu:.4f}, σ={sigma:.4f})')
        
        # Add zero line
        ax3.axvline(x=0, color='green', linestyle='--', linewidth=2, label='Zero Error')
        
        ax3.set_xlabel('Prediction Error')
        ax3.set_ylabel('Density')
        ax3.set_title('Error Distribution')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Error evolution over time
        ax4 = axes[1, 0]
        
        # Calculate rolling statistics
        window_size = max(1, len(error_flat) // 50)
        if len(error_flat) > window_size:
            rolling_mse = pd.Series(error_flat**2).rolling(window=window_size).mean()
            rolling_mae = pd.Series(np.abs(error_flat)).rolling(window=window_size).mean()
            
            ax4.plot(rolling_mse, label=f'Rolling MSE (window={window_size})', linewidth=2)
            ax4.plot(rolling_mae, label=f'Rolling MAE (window={window_size})', linewidth=2)
        else:
            ax4.plot(error_flat**2, label='Squared Error', linewidth=1, alpha=0.7)
            ax4.plot(np.abs(error_flat), label='Absolute Error', linewidth=1, alpha=0.7)
        
        ax4.set_xlabel('Time Step')
        ax4.set_ylabel('Error')
        ax4.set_title('Error Evolution')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Residuals autocorrelation
        ax5 = axes[1, 1]
        
        # Autocorrelation of residuals
        max_lag = min(50, len(error_flat) // 4)
        if max_lag > 1:
            autocorr = np.correlate(error_flat, error_flat, mode='full')
            autocorr = autocorr[len(autocorr)//2:][:max_lag]
            autocorr = autocorr / autocorr[0]  # Normalize
            
            lags = np.arange(max_lag)
            ax5.plot(lags, autocorr, 'b-', linewidth=2, marker='o', markersize=4)
            ax5.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            
            # Add confidence bands (approximate)
            n_samples = len(error_flat)
            conf_interval = 1.96 / np.sqrt(n_samples)
            ax5.axhline(y=conf_interval, color='r', linestyle=':', alpha=0.7, label='95% Confidence')
            ax5.axhline(y=-conf_interval, color='r', linestyle=':', alpha=0.7)
            
            ax5.set_xlabel('Lag')
            ax5.set_ylabel('Autocorrelation')
            ax5.set_title('Residual Autocorrelation')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
        else:
            ax5.text(0.5, 0.5, 'Insufficient data\nfor autocorrelation', 
                    ha='center', va='center', transform=ax5.transAxes)
            ax5.set_title('Residual Autocorrelation')
        
        # 6. Performance by prediction magnitude
        ax6 = axes[1, 2]
        
        # Bin predictions by magnitude and show average error
        if len(pred_plot) > 20:  # Ensure sufficient data
            n_bins = 10
            bin_edges = np.linspace(pred_plot.min(), pred_plot.max(), n_bins + 1)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            bin_errors = []
            bin_counts = []
            
            for i in range(n_bins):
                mask = (pred_plot >= bin_edges[i]) & (pred_plot < bin_edges[i + 1])
                if i == n_bins - 1:  # Include right edge for last bin
                    mask = (pred_plot >= bin_edges[i]) & (pred_plot <= bin_edges[i + 1])
                
                if np.sum(mask) > 0:
                    bin_errors.append(np.mean(np.abs(error_flat[mask])))
                    bin_counts.append(np.sum(mask))
                else:
                    bin_errors.append(0)
                    bin_counts.append(0)
            
            # Bar plot with error bars
            ax6.bar(bin_centers, bin_errors, width=np.diff(bin_edges)[0]*0.8, 
                   alpha=0.7, edgecolor='black')
            
            ax6.set_xlabel('Prediction Magnitude')
            ax6.set_ylabel('Mean Absolute Error')
            ax6.set_title('Error vs Prediction Magnitude')
            ax6.grid(True, alpha=0.3)
            
            # Add sample count as text
            for i, (center, count) in enumerate(zip(bin_centers, bin_counts)):
                if count > 0:
                    ax6.text(center, bin_errors[i], str(count), 
                           ha='center', va='bottom', fontsize=8)
        else:
            ax6.text(0.5, 0.5, 'Insufficient data\nfor magnitude analysis', 
                    ha='center', va='center', transform=ax6.transAxes)
            ax6.set_title('Error vs Prediction Magnitude')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.show()
        
        # Print comprehensive performance statistics
        self._print_performance_statistics(predictions, targets, errors)
    
    def visualize_comparative_analysis(self, results: Dict[str, Dict[str, Any]], 
                                     figsize: Tuple[int, int] = (16, 10),
                                     save_path: Optional[str] = None):
        """
        Compare multiple ESN configurations or experiments
        
        Args:
            results: Dictionary with experiment names as keys and result dictionaries as values
                    Each result dict should contain: 'mse', 'mae', 'r2', 'params', etc.
        """
        
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        fig.suptitle('Comparative Analysis Across Configurations', fontsize=16, fontweight='bold')
        
        # Extract data for plotting
        experiment_names = list(results.keys())
        n_experiments = len(experiment_names)
        
        if n_experiments < 2:
            fig.text(0.5, 0.5, 'At least 2 experiments required for comparative analysis', 
                    ha='center', va='center', fontsize=14)
            plt.show()
            return
        
        # Collect metrics
        metrics = {}
        params = {}
        
        for name, result in results.items():
            for key, value in result.items():
                if key not in ['params'] and isinstance(value, (int, float)):
                    if key not in metrics:
                        metrics[key] = {}
                    metrics[key][name] = value
                elif key == 'params':
                    params[name] = value
        
        # 1. Performance comparison
        ax1 = axes[0, 0]
        
        performance_metrics = ['mse', 'mae', 'r2']
        available_metrics = [m for m in performance_metrics if m in metrics]
        
        if available_metrics:
            x_pos = np.arange(n_experiments)
            width = 0.25
            
            for i, metric in enumerate(available_metrics):
                values = [metrics[metric].get(name, 0) for name in experiment_names]
                ax1.bar(x_pos + i*width, values, width, label=metric.upper(), alpha=0.8)
            
            ax1.set_xlabel('Experiment')
            ax1.set_ylabel('Value')
            ax1.set_title('Performance Metrics Comparison')
            ax1.set_xticks(x_pos + width)
            ax1.set_xticklabels(experiment_names, rotation=45, ha='right')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        else:
            ax1.text(0.5, 0.5, 'No performance metrics\navailable', ha='center', va='center', 
                    transform=ax1.transAxes)
            ax1.set_title('Performance Metrics Comparison')
        
        # 2. Parameter sensitivity analysis
        ax2 = axes[0, 1]
        
        if params:
            # Extract common parameters
            all_param_keys = set()
            for param_dict in params.values():
                all_param_keys.update(param_dict.keys())
            
            # Focus on numeric parameters that vary
            varying_params = []
            for param_key in all_param_keys:
                values = []
                for name in experiment_names:
                    if param_key in params[name] and isinstance(params[name][param_key], (int, float)):
                        values.append(params[name][param_key])
                
                if len(set(values)) > 1 and len(values) == n_experiments:  # Parameter varies
                    varying_params.append(param_key)
            
            if varying_params and 'mse' in metrics:
                # Plot parameter vs performance
                param_to_plot = varying_params[0]  # Use first varying parameter
                param_values = [params[name][param_to_plot] for name in experiment_names]
                mse_values = [metrics['mse'][name] for name in experiment_names]
                
                ax2.scatter(param_values, mse_values, s=100, alpha=0.7)
                
                # Add trend line if enough points
                if len(param_values) > 2:
                    z = np.polyfit(param_values, mse_values, 1)
                    p = np.poly1d(z)
                    ax2.plot(sorted(param_values), p(sorted(param_values)), "r--", alpha=0.8)
                
                ax2.set_xlabel(f'{param_to_plot}')
                ax2.set_ylabel('MSE')
                ax2.set_title(f'Parameter Sensitivity: {param_to_plot}')
                ax2.grid(True, alpha=0.3)
                
                # Add labels for each point
                for name, x, y in zip(experiment_names, param_values, mse_values):
                    ax2.annotate(name, (x, y), xytext=(5, 5), textcoords='offset points', 
                               fontsize=8, alpha=0.8)
            else:
                ax2.text(0.5, 0.5, 'No varying parameters\nfor sensitivity analysis', 
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Parameter Sensitivity Analysis')
        else:
            ax2.text(0.5, 0.5, 'No parameter data\navailable', ha='center', va='center', 
                    transform=ax2.transAxes)
            ax2.set_title('Parameter Sensitivity Analysis')
        
        # 3. Ranking and scoring
        ax3 = axes[0, 2]
        
        if 'mse' in metrics and 'r2' in metrics:
            # Create composite score (lower MSE is better, higher R² is better)
            mse_values = np.array([metrics['mse'][name] for name in experiment_names])
            r2_values = np.array([metrics['r2'][name] for name in experiment_names])
            
            # Normalize metrics (0-1 scale)
            mse_norm = 1 - (mse_values - mse_values.min()) / (mse_values.max() - mse_values.min() + 1e-8)
            r2_norm = (r2_values - r2_values.min()) / (r2_values.max() - r2_values.min() + 1e-8)
            
            # Composite score (equal weight)
            composite_scores = 0.5 * mse_norm + 0.5 * r2_norm
            
            # Sort by composite score
            sorted_indices = np.argsort(composite_scores)[::-1]
            sorted_names = [experiment_names[i] for i in sorted_indices]
            sorted_scores = composite_scores[sorted_indices]
            
            # Horizontal bar chart
            y_pos = np.arange(len(sorted_names))
            bars = ax3.barh(y_pos, sorted_scores, alpha=0.8)
            
            # Color bars by rank
            colors = plt.cm.RdYlGn(sorted_scores)
            for bar, color in zip(bars, colors):
                bar.set_color(color)
            
            ax3.set_yticks(y_pos)
            ax3.set_yticklabels(sorted_names)
            ax3.set_xlabel('Composite Score')
            ax3.set_title('Overall Ranking')
            ax3.grid(True, alpha=0.3)
        else:
            ax3.text(0.5, 0.5, 'Insufficient metrics\nfor ranking', ha='center', va='center', 
                    transform=ax3.transAxes)
            ax3.set_title('Overall Ranking')
        
        # 4. Training efficiency comparison
        ax4 = axes[1, 0]
        
        if 'training_time' in metrics:
            training_times = [metrics['training_time'][name] for name in experiment_names]
            mse_values = [metrics['mse'].get(name, 0) for name in experiment_names]
            
            # Efficiency: lower time and lower error is better
            ax4.scatter(training_times, mse_values, s=100, alpha=0.7)
            
            ax4.set_xlabel('Training Time')
            ax4.set_ylabel('MSE')
            ax4.set_title('Training Efficiency')
            ax4.grid(True, alpha=0.3)
            
            # Add labels
            for name, x, y in zip(experiment_names, training_times, mse_values):
                ax4.annotate(name, (x, y), xytext=(5, 5), textcoords='offset points', 
                           fontsize=8, alpha=0.8)
        else:
            ax4.text(0.5, 0.5, 'No training time\ndata available', ha='center', va='center', 
                    transform=ax4.transAxes)
            ax4.set_title('Training Efficiency')
        
        # 5. Stability analysis
        ax5 = axes[1, 1]
        
        if 'spectral_radius' in metrics:
            spectral_radii = [metrics['spectral_radius'][name] for name in experiment_names]
            performance_values = [metrics.get('mse', {}).get(name, 0) for name in experiment_names]
            
            ax5.scatter(spectral_radii, performance_values, s=100, alpha=0.7)
            
            # Add stability boundary
            ax5.axvline(x=1.0, color='red', linestyle='--', alpha=0.7, label='Stability Boundary')
            
            ax5.set_xlabel('Spectral Radius')
            ax5.set_ylabel('MSE')
            ax5.set_title('Stability vs Performance')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
            
            # Add labels
            for name, x, y in zip(experiment_names, spectral_radii, performance_values):
                ax5.annotate(name, (x, y), xytext=(5, 5), textcoords='offset points', 
                           fontsize=8, alpha=0.8)
        else:
            ax5.text(0.5, 0.5, 'No spectral radius\ndata available', ha='center', va='center', 
                    transform=ax5.transAxes)
            ax5.set_title('Stability vs Performance')
        
        # 6. Memory capacity comparison (if available)
        ax6 = axes[1, 2]
        
        if 'memory_capacity' in metrics:
            memory_capacities = [metrics['memory_capacity'][name] for name in experiment_names]
            
            ax6.bar(range(n_experiments), memory_capacities, alpha=0.8)
            ax6.set_xticks(range(n_experiments))
            ax6.set_xticklabels(experiment_names, rotation=45, ha='right')
            ax6.set_ylabel('Memory Capacity')
            ax6.set_title('Memory Capacity Comparison')
            ax6.grid(True, alpha=0.3)
        else:
            # Show parameter distribution instead
            if params:
                param_counts = {}
                for param_dict in params.values():
                    for key, value in param_dict.items():
                        if key not in param_counts:
                            param_counts[key] = []
                        param_counts[key].append(value)
                
                # Show distribution of first numeric parameter
                numeric_params = [(k, v) for k, v in param_counts.items() 
                                if all(isinstance(x, (int, float)) for x in v)]
                
                if numeric_params:
                    param_name, param_vals = numeric_params[0]
                    ax6.hist(param_vals, bins=min(10, len(set(param_vals))), alpha=0.7, edgecolor='black')
                    ax6.set_xlabel(param_name)
                    ax6.set_ylabel('Frequency')
                    ax6.set_title(f'Parameter Distribution: {param_name}')
                    ax6.grid(True, alpha=0.3)
                else:
                    ax6.text(0.5, 0.5, 'No numeric parameters\nfor distribution', 
                            ha='center', va='center', transform=ax6.transAxes)
                    ax6.set_title('Parameter Distribution')
            else:
                ax6.text(0.5, 0.5, 'No memory capacity\nor parameter data', 
                        ha='center', va='center', transform=ax6.transAxes)
                ax6.set_title('Memory Capacity / Parameters')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.show()
        
        # Print comparative summary
        self._print_comparative_summary(results)
    
    def visualize_spectral_analysis(self, figsize: Tuple[int, int] = (15, 10), 
                                   save_path: Optional[str] = None):
        """
        Advanced spectral analysis of reservoir properties
        """
        
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        fig.suptitle('Advanced Spectral Analysis of Reservoir', fontsize=16, fontweight='bold')
        
        # Compute eigenvalues and eigenvectors
        eigenvals, eigenvecs = np.linalg.eig(self.W_reservoir)
        eigenvals_sorted_idx = np.argsort(np.abs(eigenvals))[::-1]
        eigenvals_sorted = eigenvals[eigenvals_sorted_idx]
        eigenvecs_sorted = eigenvecs[:, eigenvals_sorted_idx]
        
        # 1. Eigenvalue spectrum with detailed analysis
        ax1 = axes[0, 0]
        
        magnitudes = np.abs(eigenvals_sorted)
        phases = np.angle(eigenvals_sorted)
        
        scatter = ax1.scatter(eigenvals_sorted.real, eigenvals_sorted.imag, 
                            c=magnitudes, cmap='viridis', s=50, alpha=0.8)
        
        # Unit circle
        circle = plt.Circle((0, 0), 1, fill=False, color='red', linestyle='--', linewidth=2)
        ax1.add_patch(circle)
        
        # Spectral radius
        max_eigenval = np.max(magnitudes)
        spectral_circle = plt.Circle((0, 0), max_eigenval, fill=False, color='orange', 
                                   linestyle=':', linewidth=2, alpha=0.7)
        ax1.add_patch(spectral_circle)
        
        ax1.set_xlabel('Real Part')
        ax1.set_ylabel('Imaginary Part')
        ax1.set_title(f'Eigenvalue Spectrum\nSpectral Radius: {max_eigenval:.4f}')
        ax1.axis('equal')
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax1, shrink=0.8, label='|λ|')
        
        # 2. Eigenvalue magnitude distribution
        ax2 = axes[0, 1]
        
        ax2.plot(range(1, len(magnitudes) + 1), magnitudes, 'bo-', markersize=4, linewidth=1)
        ax2.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Stability threshold')
        ax2.set_xlabel('Eigenvalue Index (sorted)')
        ax2.set_ylabel('|λ|')
        ax2.set_title('Eigenvalue Magnitude Decay')
        ax2.set_yscale('log')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Eigenvector analysis - dominant modes
        ax3 = axes[0, 2]
        
        # Show first few dominant eigenvectors
        n_modes = min(5, self.n_reservoir)
        for i in range(n_modes):
            eigenvec = eigenvecs_sorted[:, i].real
            ax3.plot(eigenvec, alpha=0.7, linewidth=2, 
                    label=f'Mode {i+1} (λ={magnitudes[i]:.3f})')
        
        ax3.set_xlabel('Neuron Index')
        ax3.set_ylabel('Eigenvector Component')
        ax3.set_title(f'Dominant Eigenmodes (Top {n_modes})')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Spectral gap analysis
        ax4 = axes[1, 0]
        
        # Calculate gaps between consecutive eigenvalues
        if len(magnitudes) > 1:
            spectral_gaps = np.diff(magnitudes)
            ax4.plot(range(1, len(spectral_gaps) + 1), -spectral_gaps, 'ro-', markersize=4)
            ax4.set_xlabel('Gap Index')
            ax4.set_ylabel('Spectral Gap')
            ax4.set_title('Spectral Gap Analysis')
            ax4.grid(True, alpha=0.3)
            
            # Highlight largest gaps
            largest_gaps_idx = np.argsort(-spectral_gaps)[:3]
            for idx in largest_gaps_idx:
                ax4.annotate(f'Gap {idx+1}', (idx+1, -spectral_gaps[idx]), 
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
        else:
            ax4.text(0.5, 0.5, 'Insufficient eigenvalues\nfor gap analysis', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Spectral Gap Analysis')
        
        # 5. Condition number and numerical stability
        ax5 = axes[1, 1]
        
        # Condition number analysis
        condition_number = np.linalg.cond(self.W_reservoir)
        
        # SVD for more detailed analysis
        U, s, Vh = np.linalg.svd(self.W_reservoir)
        
        ax5.semilogy(range(1, len(s) + 1), s, 'bo-', markersize=4)
        ax5.set_xlabel('Singular Value Index')
        ax5.set_ylabel('Singular Value')
        ax5.set_title(f'Singular Value Spectrum\nCondition Number: {condition_number:.2e}')
        ax5.grid(True, alpha=0.3)
        
        # Add condition number category
        if condition_number < 1e12:
            stability_text = "Well-conditioned"
            color = 'green'
        elif condition_number < 1e15:
            stability_text = "Moderately conditioned"
            color = 'orange'
        else:
            stability_text = "Ill-conditioned"
            color = 'red'
        
        ax5.text(0.02, 0.98, stability_text, transform=ax5.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.3),
                verticalalignment='top')
        
        # 6. Effective rank and dimensionality
        ax6 = axes[1, 2]
        
        # Effective rank using different thresholds
        thresholds = np.logspace(-8, 0, 50)
        effective_ranks = []
        
        for threshold in thresholds:
            effective_rank = np.sum(s / s[0] > threshold)
            effective_ranks.append(effective_rank)
        
        ax6.semilogx(thresholds, effective_ranks, 'b-', linewidth=2)
        ax6.axhline(y=self.n_reservoir, color='red', linestyle='--', alpha=0.7, label='Full rank')
        ax6.set_xlabel('Relative Threshold')
        ax6.set_ylabel('Effective Rank')
        ax6.set_title('Effective Dimensionality')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # Add specific thresholds
        for thresh, name in [(1e-6, '1e-6'), (1e-3, '1e-3'), (1e-1, '1e-1')]:
            eff_rank = np.sum(s / s[0] > thresh)
            ax6.axvline(x=thresh, color='gray', linestyle=':', alpha=0.5)
            ax6.text(thresh, eff_rank, f'{eff_rank}', rotation=90, 
                    verticalalignment='bottom', fontsize=8)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
        plt.show()
        
        # Print spectral analysis summary
        self._print_spectral_statistics(eigenvals, s, condition_number)
    
    def create_animation(self, states: np.ndarray, figsize: Tuple[int, int] = (10, 8),
                        interval: int = 100, save_path: Optional[str] = None):
        """
        Create animated visualization of reservoir state evolution
        
        Args:
            states: Reservoir states over time (time_steps × n_reservoir)
            interval: Animation interval in milliseconds
            save_path: Path to save animation (as gif or mp4)
        """
        
        # Sample neurons if too many
        max_neurons = 50
        if states.shape[1] > max_neurons:
            neuron_indices = np.random.choice(states.shape[1], max_neurons, replace=False)
            display_states = states[:, neuron_indices]
            title_suffix = f" ({max_neurons} sampled neurons)"
        else:
            display_states = states
            title_suffix = ""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        fig.suptitle(f'Reservoir State Evolution Animation{title_suffix}', fontsize=14)
        
        # Initialize plots
        im1 = ax1.imshow(display_states[0].reshape(-1, 1), cmap='viridis', 
                        vmin=display_states.min(), vmax=display_states.max(),
                        aspect='auto')
        ax1.set_title('Current State')
        ax1.set_xlabel('State Value')
        ax1.set_ylabel('Neuron Index')
        
        # State trajectory plot
        ax2.set_xlim(0, len(display_states))
        ax2.set_ylim(display_states.min(), display_states.max())
        ax2.set_title('State Trajectories Over Time')
        ax2.set_xlabel('Time Step')
        ax2.set_ylabel('Activation')
        
        # Initialize trajectory lines
        n_trajectories = min(10, display_states.shape[1])
        trajectory_indices = np.linspace(0, display_states.shape[1]-1, n_trajectories).astype(int)
        lines = []
        for i in trajectory_indices:
            line, = ax2.plot([], [], alpha=0.7, linewidth=1)
            lines.append(line)
        
        # Time text
        time_text = ax1.text(0.02, 0.98, '', transform=ax1.transAxes, 
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
                           verticalalignment='top')
        
        def animate(frame):
            # Update state visualization
            im1.set_array(display_states[frame].reshape(-1, 1))
            
            # Update trajectories
            for i, line in enumerate(lines):
                neuron_idx = trajectory_indices[i]
                line.set_data(range(frame+1), display_states[:frame+1, neuron_idx])
            
            # Update time
            time_text.set_text(f'Time: {frame}')
            
            return [im1] + lines + [time_text]
        
        # Create animation
        anim = FuncAnimation(fig, animate, frames=len(display_states), 
                           interval=interval, blit=False, repeat=True)
        
        if save_path:
            if save_path.endswith('.gif'):
                anim.save(save_path, writer='pillow', fps=10)
            elif save_path.endswith('.mp4'):
                anim.save(save_path, writer='ffmpeg', fps=10)
            else:
                warnings.warn("Animation save format not recognized. Use .gif or .mp4")
        
        plt.show()
        return anim
    
    def _print_reservoir_statistics(self, eigenvals: np.ndarray, degrees: np.ndarray, weights: np.ndarray):
        """Print comprehensive reservoir statistics"""
        
        print(f"\n📊 Enhanced Reservoir Statistics:")
        print(f"=" * 50)
        
        # Basic properties
        print(f"🏗️  Architecture:")
        print(f"   • Size: {self.n_reservoir} neurons")
        print(f"   • Connections: {np.sum(self.W_reservoir != 0):,} ({self.sparsity:.1%} sparsity)")
        print(f"   • Density: {np.mean(self.W_reservoir != 0):.1%}")
        
        # Spectral properties
        spectral_radius = np.max(np.abs(eigenvals))
        print(f"\n🌊 Spectral Properties:")
        print(f"   • Spectral radius: {spectral_radius:.4f}")
        print(f"   • Echo state property: {'✓ Satisfied' if spectral_radius < 1 else '⚠ Violated'}")
        print(f"   • Complex eigenvalues: {np.sum(np.abs(eigenvals.imag) > 1e-10)}")
        print(f"   • Eigenvalue spread: {np.max(np.abs(eigenvals)) - np.min(np.abs(eigenvals)):.4f}")
        
        # Connectivity statistics
        print(f"\n🔗 Connectivity:")
        print(f"   • Mean degree: {degrees.mean():.1f} ± {degrees.std():.1f}")
        print(f"   • Degree range: [{degrees.min()}, {degrees.max()}]")
        print(f"   • Degree coefficient of variation: {degrees.std() / degrees.mean():.3f}")
        
        # Weight statistics
        print(f"\n⚖️  Weight Distribution:")
        print(f"   • Weight range: [{weights.min():.4f}, {weights.max():.4f}]")
        print(f"   • Mean |weight|: {np.mean(np.abs(weights)):.4f}")
        print(f"   • Weight std: {weights.std():.4f}")
        print(f"   • Skewness: {stats.skew(weights):.3f}")
        print(f"   • Kurtosis: {stats.kurtosis(weights):.3f}")
        
        # Numerical properties
        condition_number = np.linalg.cond(self.W_reservoir)
        print(f"\n🔢 Numerical Properties:")
        print(f"   • Condition number: {condition_number:.2e}")
        print(f"   • Numerical stability: {self._assess_condition_number(condition_number)}")
        
        print("=" * 50)
    
    def _print_dynamics_statistics(self, states: np.ndarray, inputs: Optional[np.ndarray], 
                                 outputs: Optional[np.ndarray]):
        """Print dynamics analysis statistics"""
        
        print(f"\n🌊 Reservoir Dynamics Statistics:")
        print(f"=" * 50)
        
        # Basic dynamics
        print(f"📈 Activity Patterns:")
        print(f"   • Time steps: {states.shape[0]:,}")
        print(f"   • Active neurons: {np.sum(np.std(states, axis=0) > 1e-6)}/{states.shape[1]}")
        print(f"   • Mean activity: {np.mean(states):.4f} ± {np.std(states):.4f}")
        print(f"   • Activity range: [{states.min():.4f}, {states.max():.4f}]")
        
        # Temporal properties
        print(f"\n⏱️  Temporal Properties:")
        if states.shape[0] > 1:
            # Simple measure of temporal correlation
            temporal_corr = np.mean([np.corrcoef(states[:-1, i], states[1:, i])[0, 1] 
                                   for i in range(min(10, states.shape[1]))])
            print(f"   • Mean temporal correlation: {temporal_corr:.4f}")
            
            # Activity diversity
            pairwise_corr = np.corrcoef(states.T)
            mean_corr = np.mean(pairwise_corr[np.triu_indices_from(pairwise_corr, k=1)])
            print(f"   • Mean pairwise correlation: {mean_corr:.4f}")
        
        # Memory characteristics
        if states.shape[0] > 10:
            # Simple memory capacity estimate
            memory_capacity = self._estimate_memory_capacity(states[:100])  # Use subset for speed
            print(f"   • Estimated memory capacity: {memory_capacity:.2f}")
        
        print("=" * 50)
    
    def _print_performance_statistics(self, predictions: np.ndarray, targets: np.ndarray, errors: np.ndarray):
        """Print comprehensive performance statistics"""
        
        print(f"\n🎯 Performance Analysis:")
        print(f"=" * 50)
        
        # Basic metrics
        mse = np.mean(errors**2)
        mae = np.mean(np.abs(errors))
        rmse = np.sqrt(mse)
        
        # R² calculation
        ss_res = np.sum(errors**2)
        ss_tot = np.sum((targets - np.mean(targets))**2)
        r2 = 1 - (ss_res / (ss_tot + 1e-8))
        
        print(f"📊 Error Metrics:")
        print(f"   • MSE: {mse:.6f}")
        print(f"   • RMSE: {rmse:.6f}")
        print(f"   • MAE: {mae:.6f}")
        print(f"   • R²: {r2:.4f}")
        
        # Relative metrics
        target_range = np.max(targets) - np.min(targets)
        relative_error = rmse / (target_range + 1e-8)
        print(f"   • Relative RMSE: {relative_error:.1%}")
        
        # Error distribution
        print(f"\n📈 Error Distribution:")
        print(f"   • Error std: {np.std(errors):.6f}")
        print(f"   • Error skewness: {stats.skew(errors.flatten()):.3f}")
        print(f"   • Error kurtosis: {stats.kurtosis(errors.flatten()):.3f}")
        
        # Prediction quality
        pred_target_corr = np.corrcoef(predictions.flatten(), targets.flatten())[0, 1]
        print(f"\n🔍 Prediction Quality:")
        print(f"   • Prediction-target correlation: {pred_target_corr:.4f}")
        
        # Accuracy brackets
        tolerance_levels = [0.01, 0.05, 0.1]
        for tol in tolerance_levels:
            accuracy = np.mean(np.abs(errors) <= tol * np.std(targets))
            print(f"   • Accuracy within {tol*100:.0f}% std: {accuracy:.1%}")
        
        print("=" * 50)
    
    def _print_comparative_summary(self, results: Dict[str, Dict[str, Any]]):
        """Print comparative analysis summary"""
        
        print(f"\n🏆 Comparative Analysis Summary:")
        print(f"=" * 60)
        
        experiment_names = list(results.keys())
        
        # Best performance in each metric
        metrics_to_compare = ['mse', 'mae', 'r2']
        
        for metric in metrics_to_compare:
            if metric in results[experiment_names[0]]:
                values = {name: results[name][metric] for name in experiment_names 
                         if metric in results[name]}
                
                if metric in ['mse', 'mae']:  # Lower is better
                    best_name = min(values, key=values.get)
                    best_value = values[best_name]
                    print(f"🥇 Best {metric.upper()}: {best_name} ({best_value:.6f})")
                elif metric == 'r2':  # Higher is better
                    best_name = max(values, key=values.get)
                    best_value = values[best_name]
                    print(f"🥇 Best {metric.upper()}: {best_name} ({best_value:.4f})")
        
        # Parameter insights
        print(f"\n📋 Configuration Insights:")
        all_params = set()
        for result in results.values():
            if 'params' in result:
                all_params.update(result['params'].keys())
        
        for param in all_params:
            param_values = []
            for name in experiment_names:
                if 'params' in results[name] and param in results[name]['params']:
                    param_values.append(results[name]['params'][param])
            
            if len(set(param_values)) > 1:  # Parameter varies
                print(f"   • {param}: varies across experiments")
                if all(isinstance(v, (int, float)) for v in param_values):
                    print(f"     Range: [{min(param_values)}, {max(param_values)}]")
        
        print("=" * 60)
    
    def _print_spectral_statistics(self, eigenvals: np.ndarray, singular_vals: np.ndarray, condition_number: float):
        """Print spectral analysis statistics"""
        
        print(f"\n🌈 Spectral Analysis Summary:")
        print(f"=" * 50)
        
        # Eigenvalue properties
        magnitudes = np.abs(eigenvals)
        print(f"🔍 Eigenvalue Properties:")
        print(f"   • Number of eigenvalues: {len(eigenvals)}")
        print(f"   • Spectral radius: {np.max(magnitudes):.4f}")
        print(f"   • Real eigenvalues: {np.sum(np.abs(eigenvals.imag) < 1e-10)}")
        print(f"   • Complex eigenvalues: {np.sum(np.abs(eigenvals.imag) >= 1e-10)}")
        print(f"   • Eigenvalues |λ| > 1: {np.sum(magnitudes > 1)}")
        
        # Singular value properties
        print(f"\n📊 Singular Value Properties:")
        print(f"   • Largest singular value: {singular_vals[0]:.4f}")
        print(f"   • Smallest singular value: {singular_vals[-1]:.2e}")
        print(f"   • Condition number: {condition_number:.2e}")
        print(f"   • Effective rank (1e-6): {np.sum(singular_vals / singular_vals[0] > 1e-6)}")
        
        # Stability assessment
        print(f"\n⚖️  Stability Assessment:")
        stability = self._assess_spectral_stability(eigenvals)
        print(f"   • Overall stability: {stability}")
        print(f"   • Numerical conditioning: {self._assess_condition_number(condition_number)}")
        
        print("=" * 50)
    
    def _assess_condition_number(self, condition_number: float) -> str:
        """Assess numerical conditioning based on condition number"""
        if condition_number < 1e12:
            return "Well-conditioned"
        elif condition_number < 1e15:
            return "Moderately conditioned"
        else:
            return "Ill-conditioned"
    
    def _assess_spectral_stability(self, eigenvals: np.ndarray) -> str:
        """Assess spectral stability"""
        max_magnitude = np.max(np.abs(eigenvals))
        
        if max_magnitude < 0.9:
            return "Highly stable"
        elif max_magnitude < 1.0:
            return "Stable (Echo state property)"
        elif max_magnitude < 1.1:
            return "Marginally stable"
        else:
            return "Unstable"
    
    def _estimate_memory_capacity(self, states: np.ndarray) -> float:
        """Estimate memory capacity using linear correlation method"""
        if states.shape[0] < 20:
            return 0.0
        
        # Simple memory capacity estimation
        # Correlate current state with past inputs (using state as proxy)
        max_delay = min(10, states.shape[0] // 2)
        total_capacity = 0.0
        
        for delay in range(1, max_delay + 1):
            if delay < states.shape[0]:
                # Use first dimension as reference signal
                reference = states[:-delay, 0] if states.shape[1] > 0 else states[:-delay].mean(axis=1)
                current = states[delay:, :].mean(axis=1)
                
                if len(reference) > 0 and len(current) > 0:
                    correlation = abs(np.corrcoef(reference, current)[0, 1])
                    total_capacity += correlation**2
        
        return total_capacity


# Example usage and demonstration
if __name__ == "__main__":
    print("🎨 Advanced ESN Visualization Module")
    print("=" * 50)
    print("This module provides comprehensive visualization capabilities")
    print("for Echo State Network analysis and research.")
    print("\n✨ Features:")
    print("  • Enhanced reservoir structure visualization")
    print("  • Dynamic behavior analysis")
    print("  • Spectral properties examination") 
    print("  • Performance metrics visualization")
    print("  • Comparative configuration analysis")
    print("  • Professional publication-ready plots")
    print("=" * 50)