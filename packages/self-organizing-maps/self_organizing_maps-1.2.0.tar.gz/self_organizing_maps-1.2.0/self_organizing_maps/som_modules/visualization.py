"""
Visualization and Analysis Module

This module provides comprehensive visualization and analysis tools for
Self-Organizing Maps, including U-matrix calculation, hit histograms,
training progress plots, and map statistics.

Based on: Kohonen (1982) "Self-Organized Formation of Topologically Correct Feature Maps"
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, Dict, Any
import warnings
warnings.filterwarnings('ignore')


class SOMVisualizer:
    """
    Comprehensive visualization toolkit for Self-Organizing Maps
    
    Provides multiple visualization methods to understand SOM structure,
    training progress, and data organization patterns.
    """
    
    def __init__(self, som_core, topology_manager):
        """
        Initialize visualizer with SOM components
        
        Args:
            som_core: Core SOM algorithm instance
            topology_manager: Topology and neighborhood manager
        """
        self.som_core = som_core
        self.topology_manager = topology_manager
        
    def visualize_map(self, training_data: Optional[np.ndarray] = None,
                     training_history: Optional[Dict] = None,
                     figsize: Tuple[int, int] = (15, 12)) -> None:
        """
        Create comprehensive SOM visualization with multiple subplots
        
        Args:
            training_data: Optional training data for hit histogram
            training_history: Optional training history for progress plots
            figsize: Figure size for the visualization
        """
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        fig.suptitle('Self-Organizing Map Visualization', fontsize=14)
        
        weights = self.som_core.get_neuron_weights()
        map_height, map_width = weights.shape[:2]
        input_dim = weights.shape[2]
        
        # 1. Weight components visualization
        self._plot_weight_components(axes[0, 0], axes[0, 1], weights, input_dim)
        
        # 2. U-Matrix (Unified Distance Matrix)
        self._plot_u_matrix(axes[0, 2], weights)
        
        # 3. Hit histogram (if training data provided)
        if training_data is not None:
            self._plot_hit_histogram(axes[1, 0], training_data, input_dim)
        else:
            axes[1, 0].text(0.5, 0.5, 'No training data\nprovided for\nhit histogram',
                           ha='center', va='center', transform=axes[1, 0].transAxes)
            axes[1, 0].set_title('Hit Histogram')
        
        # 4. Training progress (if history provided)
        if training_history and training_history.get('quantization_errors'):
            self._plot_training_progress(axes[1, 1], training_history)
        else:
            axes[1, 1].text(0.5, 0.5, 'No training history\navailable',
                           ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('Training Progress')
        
        # 5. Learning parameters over time
        if training_history and training_history.get('learning_rates'):
            self._plot_learning_parameters(axes[1, 2], training_history)
        else:
            axes[1, 2].text(0.5, 0.5, 'No parameter history\navailable',
                           ha='center', va='center', transform=axes[1, 2].transAxes)
            axes[1, 2].set_title('Learning Parameters')
        
        plt.tight_layout()
        plt.show()
        
        # Print map statistics
        if training_data is not None:
            self.print_map_statistics(training_data)
    
    def _plot_weight_components(self, ax1, ax2, weights: np.ndarray, input_dim: int):
        """Plot weight components for first two dimensions"""
        if input_dim >= 2:
            # Plot first two weight components
            im1 = ax1.imshow(weights[:, :, 0], cmap='viridis')
            ax1.set_title('Weight Component 1')
            ax1.set_xlabel('Map Width')
            ax1.set_ylabel('Map Height')
            plt.colorbar(im1, ax=ax1)
            
            im2 = ax2.imshow(weights[:, :, 1], cmap='plasma')
            ax2.set_title('Weight Component 2')
            ax2.set_xlabel('Map Width')
            ax2.set_ylabel('Map Height')
            plt.colorbar(im2, ax=ax2)
        else:
            # Single dimension case
            im1 = ax1.imshow(weights[:, :, 0], cmap='viridis')
            ax1.set_title('Weight Values')
            ax1.set_xlabel('Map Width')
            ax1.set_ylabel('Map Height')
            plt.colorbar(im1, ax=ax1)
            
            # Hide second axis for 1D case
            ax2.axis('off')
    
    def _plot_u_matrix(self, ax, weights: np.ndarray):
        """Plot U-Matrix (Unified Distance Matrix)"""
        u_matrix = self.calculate_u_matrix(weights)
        im = ax.imshow(u_matrix, cmap='gray')
        ax.set_title('U-Matrix (Distance Map)')
        ax.set_xlabel('Map Width')
        ax.set_ylabel('Map Height')
        plt.colorbar(im, ax=ax)
    
    def _plot_hit_histogram(self, ax, training_data: np.ndarray, input_dim: int):
        """Plot hit histogram showing neuron activation frequencies"""
        assignments, hit_counts = self.create_cluster_map(training_data)
        im = ax.imshow(hit_counts, cmap='hot')
        ax.set_title('Hit Histogram')
        ax.set_xlabel('Map Width')
        ax.set_ylabel('Map Height')
        plt.colorbar(im, ax=ax)
        
        # Overlay training data points for 2D case
        if input_dim == 2 and len(training_data) > 0:
            # Sample data points for visibility
            sample_size = min(100, len(training_data))
            sample_indices = np.random.choice(len(training_data), sample_size, replace=False)
            
            for idx in sample_indices:
                sample = training_data[idx]
                bmu_pos = self.som_core.map_input(sample)
                ax.scatter(bmu_pos[1], bmu_pos[0], c='cyan', s=10, alpha=0.3)
    
    def _plot_training_progress(self, ax, training_history: Dict):
        """Plot training progress curves"""
        qe_history = training_history.get('quantization_errors', [])
        te_history = training_history.get('topographic_errors', [])
        
        if qe_history:
            # Calculate iteration points based on history length
            total_iterations = len(training_history.get('learning_rates', qe_history))
            iterations = np.linspace(0, total_iterations, len(qe_history))
            
            ax.plot(iterations, qe_history, 'b-', label='Quantization Error', linewidth=2)
            
            if te_history:
                ax.plot(iterations, te_history, 'r-', label='Topographic Error', linewidth=2)
            
            ax.set_title('Training Progress')
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Error')
            ax.legend()
            ax.grid(True, alpha=0.3)
    
    def _plot_learning_parameters(self, ax, training_history: Dict):
        """Plot learning rate and neighborhood radius over time"""
        lr_history = training_history.get('learning_rates', [])
        radius_history = training_history.get('neighborhood_radii', [])
        
        if lr_history:
            iterations = range(len(lr_history))
            ax_twin = ax.twinx()
            
            line1 = ax.plot(iterations, lr_history, 'g-', label='Learning Rate', linewidth=2)
            
            if radius_history:
                line2 = ax_twin.plot(iterations, radius_history, 'orange', 
                                   label='Neighborhood Radius', linewidth=2)
            
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Learning Rate', color='g')
            ax_twin.set_ylabel('Neighborhood Radius', color='orange')
            ax.set_title('Learning Parameters')
            
            # Combine legends
            if radius_history:
                lines = line1 + line2
                labels = [l.get_label() for l in lines]
                ax.legend(lines, labels, loc='upper right')
            else:
                ax.legend()
    
    def calculate_u_matrix(self, weights: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Calculate Unified Distance Matrix (U-Matrix)
        
        Shows average distance between each neuron and its neighbors.
        Useful for cluster boundary visualization. Dark regions indicate
        cluster boundaries, light regions indicate cluster centers.
        
        Args:
            weights: Optional weight array, if None uses current neuron weights
            
        Returns:
            U-Matrix as 2D numpy array
        """
        if weights is None:
            weights = self.som_core.get_neuron_weights()
        
        map_height, map_width, input_dim = weights.shape
        u_matrix = np.zeros((map_height, map_width))
        
        for i in range(map_height):
            for j in range(map_width):
                current_weights = weights[i, j]
                distances = []
                
                # Check all neighbors (8-connectivity)
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue  # Skip self
                        
                        ni, nj = i + di, j + dj
                        if 0 <= ni < map_height and 0 <= nj < map_width:
                            neighbor_weights = weights[ni, nj]
                            distance = np.linalg.norm(current_weights - neighbor_weights)
                            distances.append(distance)
                
                u_matrix[i, j] = np.mean(distances) if distances else 0
        
        return u_matrix
    
    def create_cluster_map(self, training_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create cluster assignment map and hit counts
        
        Args:
            training_data: Training data array
            
        Returns:
            Tuple of (assignments, hit_counts) arrays
        """
        map_height, map_width = self.som_core.map_height, self.som_core.map_width
        assignments = np.full((map_height, map_width), -1, dtype=int)
        hit_counts = np.zeros((map_height, map_width))
        
        for idx, input_vector in enumerate(training_data):
            bmu_pos = self.som_core.map_input(input_vector)
            i, j = bmu_pos
            
            hit_counts[i, j] += 1
            if assignments[i, j] == -1:
                assignments[i, j] = idx
        
        return assignments, hit_counts
    
    def print_map_statistics(self, training_data: Optional[np.ndarray] = None):
        """Print detailed map statistics"""
        map_height, map_width = self.som_core.map_height, self.som_core.map_width
        input_dim = self.som_core.input_dim
        
        print(f"\n📊 SOM Statistics:")
        print(f"   • Map size: {map_height}×{map_width} = {map_height * map_width} neurons")
        print(f"   • Input dimension: {input_dim}")
        print(f"   • Topology: {self.topology_manager.topology_name}")
        print(f"   • Neighborhood function: {self.topology_manager.neighborhood_name}")
        
        if training_data is not None:
            assignments, hit_counts = self.create_cluster_map(training_data)
            active_neurons = np.sum(hit_counts > 0)
            max_hits = np.max(hit_counts)
            avg_hits = np.mean(hit_counts[hit_counts > 0]) if active_neurons > 0 else 0
            
            utilization = active_neurons / (map_height * map_width) * 100
            
            print(f"   • Active neurons: {active_neurons}/{map_height * map_width} ({utilization:.1f}%)")
            print(f"   • Max hits per neuron: {max_hits:.0f}")
            print(f"   • Average hits per active neuron: {avg_hits:.1f}")
    
    def plot_weight_evolution(self, weight_history: list, figsize: Tuple[int, int] = (12, 8)):
        """
        Plot evolution of neuron weights over training
        
        Args:
            weight_history: List of weight arrays at different time points
            figsize: Figure size
        """
        if not weight_history:
            print("No weight history provided")
            return
        
        n_snapshots = len(weight_history)
        fig, axes = plt.subplots(1, min(n_snapshots, 4), figsize=figsize)
        if n_snapshots == 1:
            axes = [axes]
        
        fig.suptitle('Weight Evolution During Training', fontsize=14)
        
        for i, weights in enumerate(weight_history[:4]):
            ax = axes[i] if i < len(axes) else axes[-1]
            
            # Plot first weight component
            im = ax.imshow(weights[:, :, 0], cmap='viridis')
            ax.set_title(f'Iteration {i * (len(weight_history) // 4)}')
            ax.set_xlabel('Map Width')
            ax.set_ylabel('Map Height')
            plt.colorbar(im, ax=ax)
        
        plt.tight_layout()
        plt.show()
    
    def plot_neighborhood_visualization(self, center_pos: Tuple[int, int], 
                                      radius: float, figsize: Tuple[int, int] = (8, 6)):
        """
        Visualize neighborhood function around a specific position
        
        Args:
            center_pos: Center position (i, j)
            radius: Neighborhood radius
            figsize: Figure size
        """
        map_height, map_width = self.som_core.map_height, self.som_core.map_width
        influence_map = np.zeros((map_height, map_width))
        
        for i in range(map_height):
            for j in range(map_width):
                distance = self.topology_manager.calculate_distance((i, j), center_pos)
                influence = self.topology_manager.calculate_neighborhood_influence(distance, radius)
                influence_map[i, j] = influence
        
        plt.figure(figsize=figsize)
        plt.imshow(influence_map, cmap='hot', interpolation='bilinear')
        plt.colorbar(label='Neighborhood Influence')
        plt.title(f'Neighborhood Function Visualization\n'
                 f'Center: {center_pos}, Radius: {radius:.2f}, '
                 f'Function: {self.topology_manager.neighborhood_name}')
        plt.xlabel('Map Width')
        plt.ylabel('Map Height')
        
        # Mark center position
        plt.scatter(center_pos[1], center_pos[0], c='cyan', s=100, marker='x', linewidths=3)
        plt.show()


def create_som_visualizer(som_core, topology_manager) -> SOMVisualizer:
    """Factory function to create SOM visualizer"""
    return SOMVisualizer(som_core, topology_manager)