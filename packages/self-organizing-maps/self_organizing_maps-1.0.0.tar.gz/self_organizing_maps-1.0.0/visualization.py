"""
Self-Organizing Map Visualization Tools
Based on: Kohonen (1982) and various SOM visualization techniques

Provides comprehensive visualization methods for analyzing SOMs including:
- U-matrix, component planes, hit histograms, trajectory plots
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
from typing import Optional, Tuple, List, Dict, Any, Union
from dataclasses import dataclass
import seaborn as sns
from .self_organizing_map import SelfOrganizingMap

@dataclass
class SOMVisualization:
    """Configuration for SOM visualization"""
    colormap: str = "viridis"
    figsize: Tuple[int, int] = (12, 10)
    show_grid: bool = True
    show_labels: bool = False
    interpolation: str = "nearest"

class SOMVisualizer:
    """
    Comprehensive visualization toolkit for Self-Organizing Maps
    
    Provides various analysis and visualization methods:
    - U-matrix for cluster boundary visualization
    - Component planes showing feature distributions
    - Hit histograms for data distribution analysis
    - Trajectory plots for temporal data analysis
    """
    
    def __init__(self, som: SelfOrganizingMap, config: Optional[SOMVisualization] = None):
        """
        Initialize SOM Visualizer
        
        Args:
            som: Trained SelfOrganizingMap instance
            config: Visualization configuration
        """
        self.som = som
        self.config = config or SOMVisualization()
        
        # Cache for computed visualizations
        self._umatrix_cache = None
        self._component_planes_cache = None
    
    def plot_umatrix(self, 
                    show_colorbar: bool = True,
                    show_data_points: bool = False,
                    data: Optional[np.ndarray] = None,
                    figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Plot U-matrix (Unified Distance Matrix) showing cluster boundaries
        
        The U-matrix shows the average distance between each neuron and its neighbors,
        revealing cluster boundaries as dark valleys and cluster centers as light areas.
        
        Args:
            show_colorbar: Whether to show colorbar
            show_data_points: Whether to overlay data points
            data: Data points to overlay (if show_data_points=True)
            figsize: Custom figure size
            
        Returns:
            Matplotlib figure
        """
        if self._umatrix_cache is None:
            self._umatrix_cache = self._calculate_umatrix()
        
        figsize = figsize or self.config.figsize
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot U-matrix
        im = ax.imshow(self._umatrix_cache, 
                      cmap=self.config.colormap,
                      interpolation=self.config.interpolation,
                      origin='lower')
        
        if show_colorbar:
            plt.colorbar(im, ax=ax, label='Average Distance to Neighbors')
        
        # Overlay data points if requested
        if show_data_points and data is not None:
            self._overlay_data_points(ax, data, marker_size=30, alpha=0.7)
        
        # Configure plot
        ax.set_title('U-Matrix: Cluster Boundaries and Structure')
        ax.set_xlabel('SOM Width')
        ax.set_ylabel('SOM Height')
        
        if self.config.show_grid:
            ax.grid(True, alpha=0.3)
            
        plt.tight_layout()
        return fig
    
    def _calculate_umatrix(self) -> np.ndarray:
        """Calculate U-matrix showing average distances between neighboring neurons"""
        width, height = self.som.width, self.som.height
        umatrix = np.zeros((height, width))
        
        for i in range(width):
            for j in range(height):
                current_weights = self.som.neurons[i][j].weights
                neighbor_distances = []
                
                # Check all 8 neighbors (including diagonals)
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:  # Skip self
                            continue
                            
                        ni, nj = i + di, j + dj
                        
                        # Check bounds
                        if 0 <= ni < width and 0 <= nj < height:
                            neighbor_weights = self.som.neurons[ni][nj].weights
                            distance = np.linalg.norm(current_weights - neighbor_weights)
                            neighbor_distances.append(distance)
                
                # Average distance to neighbors
                umatrix[j, i] = np.mean(neighbor_distances) if neighbor_distances else 0
        
        return umatrix
    
    def plot_component_planes(self, 
                            feature_names: Optional[List[str]] = None,
                            n_cols: int = 3,
                            figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Plot component planes showing distribution of each input feature across the SOM
        
        Each component plane shows how one input feature varies across the SOM grid,
        helping to understand which areas of the map respond to which features.
        
        Args:
            feature_names: Names for input features (for labeling)
            n_cols: Number of columns in subplot grid
            figsize: Custom figure size
            
        Returns:
            Matplotlib figure
        """
        n_features = self.som.input_dim
        n_rows = int(np.ceil(n_features / n_cols))
        
        figsize = figsize or (4 * n_cols, 3 * n_rows)
        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        
        # Handle single row/column cases
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        if n_cols == 1:
            axes = axes.reshape(-1, 1)
        
        for feature_idx in range(n_features):
            row = feature_idx // n_cols
            col = feature_idx % n_cols
            ax = axes[row, col]
            
            # Create component plane for this feature
            component_plane = self._calculate_component_plane(feature_idx)
            
            # Plot
            im = ax.imshow(component_plane,
                          cmap=self.config.colormap,
                          interpolation=self.config.interpolation,
                          origin='lower')
            
            # Labels
            feature_name = feature_names[feature_idx] if feature_names else f"Feature {feature_idx}"
            ax.set_title(f'{feature_name}')
            
            if self.config.show_grid:
                ax.grid(True, alpha=0.3)
                
            plt.colorbar(im, ax=ax)
        
        # Hide unused subplots
        for feature_idx in range(n_features, n_rows * n_cols):
            row = feature_idx // n_cols
            col = feature_idx % n_cols
            axes[row, col].set_visible(False)
        
        plt.suptitle('Component Planes: Feature Distribution Across SOM')
        plt.tight_layout()
        return fig
    
    def _calculate_component_plane(self, feature_idx: int) -> np.ndarray:
        """Calculate component plane for a specific feature"""
        width, height = self.som.width, self.som.height
        component_plane = np.zeros((height, width))
        
        for i in range(width):
            for j in range(height):
                component_plane[j, i] = self.som.neurons[i][j].weights[feature_idx]
        
        return component_plane
    
    def plot_hit_histogram(self, 
                          data: np.ndarray,
                          normalize: bool = True,
                          show_colorbar: bool = True,
                          figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Plot hit histogram showing how many data points map to each SOM neuron
        
        Reveals data distribution patterns and identifies popular/unused areas of the map.
        
        Args:
            data: Training/test data to map onto SOM
            normalize: Whether to normalize hit counts
            show_colorbar: Whether to show colorbar
            figsize: Custom figure size
            
        Returns:
            Matplotlib figure
        """
        hit_counts = self._calculate_hit_histogram(data)
        
        if normalize:
            hit_counts = hit_counts / np.sum(hit_counts)
        
        figsize = figsize or self.config.figsize
        fig, ax = plt.subplots(figsize=figsize)
        
        im = ax.imshow(hit_counts,
                      cmap=self.config.colormap,
                      interpolation=self.config.interpolation,
                      origin='lower')
        
        if show_colorbar:
            label = 'Normalized Hit Count' if normalize else 'Hit Count'
            plt.colorbar(im, ax=ax, label=label)
        
        ax.set_title('Hit Histogram: Data Point Distribution')
        ax.set_xlabel('SOM Width')
        ax.set_ylabel('SOM Height')
        
        if self.config.show_grid:
            ax.grid(True, alpha=0.3)
            
        plt.tight_layout()
        return fig
    
    def _calculate_hit_histogram(self, data: np.ndarray) -> np.ndarray:
        """Calculate hit histogram for given data"""
        width, height = self.som.width, self.som.height
        hit_counts = np.zeros((height, width))
        
        for datapoint in data:
            winner = self.som.find_best_matching_unit(datapoint)
            hit_counts[winner[1], winner[0]] += 1
        
        return hit_counts
    
    def plot_weight_evolution(self, 
                            training_history: Optional[List[Dict]] = None,
                            sample_neurons: Optional[List[Tuple[int, int]]] = None,
                            figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Plot evolution of neuron weights during training
        
        Shows how selected neurons' weights change over training epochs.
        
        Args:
            training_history: History of training (if available)
            sample_neurons: List of (x, y) coordinates of neurons to track
            figsize: Custom figure size
            
        Returns:
            Matplotlib figure
        """
        if training_history is None:
            print("Training history not available")
            return plt.figure()
        
        if sample_neurons is None:
            # Sample a few neurons randomly
            sample_neurons = [
                (0, 0),  # Corner
                (self.som.width//2, self.som.height//2),  # Center
                (self.som.width-1, self.som.height-1)  # Opposite corner
            ]
        
        figsize = figsize or (12, 8)
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        # This is a placeholder since training history structure depends on implementation
        # Real implementation would track weight evolution during training
        
        for idx, (x, y) in enumerate(sample_neurons[:4]):
            ax = axes[idx]
            
            # Placeholder plot - would show actual weight evolution
            epochs = range(len(training_history))
            # weights_over_time = [history['neuron_weights'][x][y] for history in training_history]
            
            # For now, just show current weights as bar plot
            current_weights = self.som.neurons[x][y].weights
            ax.bar(range(len(current_weights)), current_weights)
            ax.set_title(f'Neuron ({x}, {y}) Weights')
            ax.set_xlabel('Feature Dimension')
            ax.set_ylabel('Weight Value')
            ax.grid(True, alpha=0.3)
        
        plt.suptitle('Neuron Weight Evolution During Training')
        plt.tight_layout()
        return fig
    
    def plot_trajectory(self, 
                       sequential_data: np.ndarray,
                       show_arrows: bool = True,
                       show_start_end: bool = True,
                       figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Plot trajectory of sequential data through the SOM
        
        Useful for analyzing temporal patterns or sequences.
        
        Args:
            sequential_data: Sequential data points, shape (n_timesteps, n_features)
            show_arrows: Whether to show trajectory direction
            show_start_end: Whether to mark start/end points
            figsize: Custom figure size
            
        Returns:
            Matplotlib figure
        """
        figsize = figsize or self.config.figsize
        fig, ax = plt.subplots(figsize=figsize)
        
        # Map sequential data to SOM coordinates
        trajectory_coords = []
        for datapoint in sequential_data:
            winner = self.som.find_best_matching_unit(datapoint)
            trajectory_coords.append(winner)
        
        trajectory_coords = np.array(trajectory_coords)
        
        # Plot SOM grid (background)
        self._plot_som_grid(ax, alpha=0.3)
        
        # Plot trajectory
        ax.plot(trajectory_coords[:, 0], trajectory_coords[:, 1], 
               'r-', linewidth=2, alpha=0.7, label='Trajectory')
        
        # Add arrows for direction
        if show_arrows and len(trajectory_coords) > 1:
            for i in range(0, len(trajectory_coords)-1, max(1, len(trajectory_coords)//20)):
                dx = trajectory_coords[i+1, 0] - trajectory_coords[i, 0]
                dy = trajectory_coords[i+1, 1] - trajectory_coords[i, 1]
                ax.arrow(trajectory_coords[i, 0], trajectory_coords[i, 1],
                        dx*0.8, dy*0.8, head_width=0.1, head_length=0.1, 
                        fc='red', ec='red', alpha=0.6)
        
        # Mark start and end points
        if show_start_end and len(trajectory_coords) > 0:
            start = trajectory_coords[0]
            end = trajectory_coords[-1]
            ax.scatter(start[0], start[1], c='green', s=100, marker='o', 
                      label='Start', zorder=5)
            ax.scatter(end[0], end[1], c='red', s=100, marker='s', 
                      label='End', zorder=5)
        
        ax.set_title('Sequential Data Trajectory Through SOM')
        ax.set_xlabel('SOM Width')
        ax.set_ylabel('SOM Height')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def _plot_som_grid(self, ax: plt.Axes, alpha: float = 0.5):
        """Plot SOM grid structure as background"""
        width, height = self.som.width, self.som.height
        
        # Plot grid lines
        for i in range(width + 1):
            ax.axvline(i - 0.5, color='gray', alpha=alpha, linewidth=0.5)
        for j in range(height + 1):
            ax.axhline(j - 0.5, color='gray', alpha=alpha, linewidth=0.5)
        
        # Set limits
        ax.set_xlim(-0.5, width - 0.5)
        ax.set_ylim(-0.5, height - 0.5)
    
    def _overlay_data_points(self, ax: plt.Axes, data: np.ndarray, 
                           marker_size: float = 20, alpha: float = 0.6):
        """Overlay data points on SOM visualization"""
        data_coords = []
        for datapoint in data:
            winner = self.som.find_best_matching_unit(datapoint)
            # Add small random offset to avoid overlapping
            jitter = np.random.normal(0, 0.1, 2)
            data_coords.append([winner[0] + jitter[0], winner[1] + jitter[1]])
        
        data_coords = np.array(data_coords)
        ax.scatter(data_coords[:, 0], data_coords[:, 1], 
                  c='white', s=marker_size, alpha=alpha, edgecolor='black')
    
    def plot_cluster_boundaries(self, 
                               data: np.ndarray,
                               labels: np.ndarray,
                               figsize: Optional[Tuple[int, int]] = None) -> plt.Figure:
        """
        Plot cluster boundaries based on labeled data
        
        Args:
            data: Input data
            labels: Cluster labels for data points
            figsize: Custom figure size
            
        Returns:
            Matplotlib figure
        """
        figsize = figsize or self.config.figsize
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create cluster map
        width, height = self.som.width, self.som.height
        cluster_map = np.full((height, width), -1)
        
        unique_labels = np.unique(labels)
        colors = plt.cm.Set3(np.linspace(0, 1, len(unique_labels)))
        
        # Assign majority cluster to each neuron
        for i in range(width):
            for j in range(height):
                # Find data points that map to this neuron
                neuron_data_indices = []
                for idx, datapoint in enumerate(data):
                    winner = self.som.find_best_matching_unit(datapoint)
                    if winner == (i, j):
                        neuron_data_indices.append(idx)
                
                if neuron_data_indices:
                    # Assign majority label
                    neuron_labels = labels[neuron_data_indices]
                    cluster_map[j, i] = np.bincount(neuron_labels).argmax()
        
        # Plot cluster map
        im = ax.imshow(cluster_map, cmap=ListedColormap(colors), 
                      origin='lower', vmin=0, vmax=len(unique_labels)-1)
        
        # Add colorbar with cluster labels
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_ticks(range(len(unique_labels)))
        cbar.set_ticklabels([f'Cluster {i}' for i in unique_labels])
        
        ax.set_title('SOM Cluster Boundaries')
        ax.set_xlabel('SOM Width')
        ax.set_ylabel('SOM Height')
        
        if self.config.show_grid:
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_dashboard(self, 
                        data: np.ndarray,
                        feature_names: Optional[List[str]] = None,
                        labels: Optional[np.ndarray] = None,
                        figsize: Tuple[int, int] = (20, 15)) -> plt.Figure:
        """
        Create comprehensive SOM analysis dashboard
        
        Args:
            data: Training/analysis data
            feature_names: Names of input features
            labels: Optional cluster labels
            figsize: Figure size
            
        Returns:
            Matplotlib figure with multiple subplots
        """
        fig = plt.figure(figsize=figsize)
        
        # U-matrix
        plt.subplot(2, 3, 1)
        self._umatrix_cache = self._calculate_umatrix()
        plt.imshow(self._umatrix_cache, cmap='viridis', origin='lower')
        plt.title('U-Matrix')
        plt.colorbar()
        
        # Hit histogram
        plt.subplot(2, 3, 2)
        hit_counts = self._calculate_hit_histogram(data)
        plt.imshow(hit_counts, cmap='viridis', origin='lower')
        plt.title('Hit Histogram')
        plt.colorbar()
        
        # Component plane (first feature)
        plt.subplot(2, 3, 3)
        if self.som.input_dim > 0:
            component_plane = self._calculate_component_plane(0)
            plt.imshow(component_plane, cmap='viridis', origin='lower')
            feature_name = feature_names[0] if feature_names else "Feature 0"
            plt.title(f'Component Plane: {feature_name}')
            plt.colorbar()
        
        # Cluster boundaries (if labels provided)
        if labels is not None:
            plt.subplot(2, 3, 4)
            width, height = self.som.width, self.som.height
            cluster_map = np.full((height, width), -1)
            
            for i in range(width):
                for j in range(height):
                    neuron_labels = []
                    for idx, datapoint in enumerate(data):
                        winner = self.som.find_best_matching_unit(datapoint)
                        if winner == (i, j):
                            neuron_labels.append(labels[idx])
                    
                    if neuron_labels:
                        cluster_map[j, i] = max(set(neuron_labels), key=neuron_labels.count)
            
            plt.imshow(cluster_map, cmap='Set3', origin='lower')
            plt.title('Cluster Map')
            plt.colorbar()
        
        # Statistics
        plt.subplot(2, 3, 5)
        stats_text = f"SOM Size: {self.som.width}×{self.som.height}\n"
        stats_text += f"Input Dim: {self.som.input_dim}\n"
        stats_text += f"Data Points: {len(data)}\n"
        if hasattr(self.som, 'training_history'):
            stats_text += f"Training Epochs: {len(self.som.training_history)}\n"
        
        plt.text(0.1, 0.5, stats_text, fontsize=12, verticalalignment='center')
        plt.title('SOM Statistics')
        plt.axis('off')
        
        plt.suptitle('Self-Organizing Map Analysis Dashboard', fontsize=16)
        plt.tight_layout()
        
        return fig