"""
Metrics and Utilities Module

This module provides quality metrics for Self-Organizing Maps including
quantization error, topographic error, and various utility functions for
SOM analysis and evaluation.

Based on: Kohonen (1982) "Self-Organized Formation of Topologically Correct Feature Maps"
"""

import numpy as np
from typing import Tuple, Dict, List, Optional, Any
from collections import defaultdict


class SOMMetrics:
    """
    Quality metrics and evaluation tools for Self-Organizing Maps
    
    Provides comprehensive metrics to evaluate SOM training quality,
    topological preservation, and data representation accuracy.
    """
    
    def __init__(self, som_core, topology_manager):
        """
        Initialize metrics calculator
        
        Args:
            som_core: Core SOM algorithm instance
            topology_manager: Topology and neighborhood manager
        """
        self.som_core = som_core
        self.topology_manager = topology_manager
    
    def calculate_quantization_error(self, data: np.ndarray) -> float:
        """
        Calculate quantization error (average distance from inputs to BMUs)
        
        The quantization error measures how well the SOM represents the input data.
        It's the average distance between each input vector and its Best Matching Unit.
        
        QE = (1/N) * Σ ||x_i - w_c(x_i)||
        
        where:
        - N: number of input samples
        - x_i: input vector i
        - w_c(x_i): weight vector of BMU for input x_i
        
        Lower values indicate better data representation.
        
        Args:
            data: Input data array of shape (n_samples, n_features)
            
        Returns:
            Average quantization error
        """
        total_error = 0.0
        
        for input_vector in data:
            bmu_pos = self.som_core.find_bmu(input_vector)
            bmu = self.som_core.neurons[bmu_pos[0], bmu_pos[1]]
            error = np.linalg.norm(input_vector - bmu.weight_vector)
            total_error += error
        
        return total_error / len(data)
    
    def calculate_topographic_error(self, data: np.ndarray) -> float:
        """
        Calculate topographic error (proportion of data for which BMU and 2nd BMU are not adjacent)
        
        The topographic error measures how well the SOM preserves the topology of the input space.
        For each input, it checks if the Best Matching Unit (BMU) and the second-best BMU
        are adjacent on the map. If they're not adjacent, it's considered a topographic error.
        
        TE = (1/N) * Σ u(x_i)
        
        where:
        - N: number of input samples  
        - u(x_i) = 1 if BMU and 2nd BMU are not adjacent, 0 otherwise
        
        Lower values indicate better topological preservation.
        
        Args:
            data: Input data array of shape (n_samples, n_features)
            
        Returns:
            Topographic error as proportion (0.0 to 1.0)
        """
        topographic_errors = 0
        
        for input_vector in data:
            # Find BMU and second BMU
            distances = []
            positions = []
            
            for i in range(self.som_core.map_height):
                for j in range(self.som_core.map_width):
                    neuron = self.som_core.neurons[i, j]
                    distance = np.linalg.norm(neuron.weight_vector - input_vector)
                    distances.append(distance)
                    positions.append((i, j))
            
            sorted_indices = np.argsort(distances)
            bmu_pos = positions[sorted_indices[0]]
            second_bmu_pos = positions[sorted_indices[1]]
            
            # Check if BMU and 2nd BMU are adjacent
            distance_between = self.topology_manager.calculate_distance(bmu_pos, second_bmu_pos)
            if distance_between > 1.5:  # Not adjacent (allowing for diagonal)
                topographic_errors += 1
        
        return topographic_errors / len(data)
    
    def calculate_neighborhood_preservation(self, data: np.ndarray, k: int = 5) -> float:
        """
        Calculate neighborhood preservation metric
        
        Measures how well k-nearest neighbors in input space are preserved
        as neighbors in the SOM output space.
        
        Args:
            data: Input data array
            k: Number of nearest neighbors to consider
            
        Returns:
            Neighborhood preservation ratio (0.0 to 1.0)
        """
        if len(data) < k + 1:
            return 1.0  # Perfect preservation for small datasets
        
        total_preserved = 0
        total_comparisons = 0
        
        for i, input_vector in enumerate(data):
            # Find k nearest neighbors in input space
            input_distances = []
            for j, other_vector in enumerate(data):
                if i != j:
                    dist = np.linalg.norm(input_vector - other_vector)
                    input_distances.append((dist, j))
            
            input_distances.sort()
            input_neighbors = [idx for _, idx in input_distances[:k]]
            
            # Map input and neighbors to SOM space
            input_bmu = self.som_core.find_bmu(input_vector)
            neighbor_bmus = [self.som_core.find_bmu(data[idx]) for idx in input_neighbors]
            
            # Count how many input neighbors are also SOM neighbors
            som_neighbors = self._get_som_neighbors(input_bmu, k)
            preserved = len(set(neighbor_bmus).intersection(set(som_neighbors)))
            
            total_preserved += preserved
            total_comparisons += k
        
        return total_preserved / total_comparisons if total_comparisons > 0 else 1.0
    
    def _get_som_neighbors(self, position: Tuple[int, int], k: int) -> List[Tuple[int, int]]:
        """Get k nearest neighbors of a position on the SOM grid"""
        distances = []
        
        for i in range(self.som_core.map_height):
            for j in range(self.som_core.map_width):
                if (i, j) != position:
                    dist = self.topology_manager.calculate_distance((i, j), position)
                    distances.append((dist, (i, j)))
        
        distances.sort()
        return [pos for _, pos in distances[:k]]
    
    def calculate_trustworthiness(self, data: np.ndarray, k: int = 5) -> float:
        """
        Calculate trustworthiness metric
        
        Measures whether points that are close in the SOM space are also
        close in the original input space.
        
        Args:
            data: Input data array
            k: Number of nearest neighbors to consider
            
        Returns:
            Trustworthiness score (0.0 to 1.0, higher is better)
        """
        if len(data) < k + 1:
            return 1.0
        
        n = len(data)
        sum_penalty = 0
        
        # Map all data to SOM positions
        som_positions = []
        for input_vector in data:
            bmu_pos = self.som_core.find_bmu(input_vector)
            som_positions.append(bmu_pos)
        
        for i in range(n):
            # Find k nearest neighbors in SOM space
            som_distances = []
            for j in range(n):
                if i != j:
                    dist = self.topology_manager.calculate_distance(som_positions[i], som_positions[j])
                    som_distances.append((dist, j))
            
            som_distances.sort()
            som_neighbors = [idx for _, idx in som_distances[:k]]
            
            # Find k nearest neighbors in input space
            input_distances = []
            for j in range(n):
                if i != j:
                    dist = np.linalg.norm(data[i] - data[j])
                    input_distances.append((dist, j))
            
            input_distances.sort()
            input_neighbors = set(idx for _, idx in input_distances[:k])
            
            # Calculate penalty for SOM neighbors not in input neighbors
            for rank, som_neighbor in enumerate(som_neighbors):
                if som_neighbor not in input_neighbors:
                    # Find rank in input space
                    input_rank = next((r for r, (_, idx) in enumerate(input_distances) 
                                     if idx == som_neighbor), n-1)
                    if input_rank >= k:
                        sum_penalty += input_rank - k + 1
        
        max_penalty = k * n * (2*n - 3*k - 1) / 2
        return 1 - (2 * sum_penalty) / max_penalty if max_penalty > 0 else 1.0
    
    def calculate_map_resolution(self) -> Dict[str, float]:
        """
        Calculate map resolution metrics
        
        Returns:
            Dictionary with resolution metrics
        """
        weights = self.som_core.get_neuron_weights()
        map_height, map_width, input_dim = weights.shape
        
        # Calculate average distance between adjacent neurons
        adjacent_distances = []
        
        for i in range(map_height):
            for j in range(map_width):
                current_weight = weights[i, j]
                
                # Check immediate neighbors (4-connectivity)
                neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
                
                for ni, nj in neighbors:
                    if 0 <= ni < map_height and 0 <= nj < map_width:
                        neighbor_weight = weights[ni, nj]
                        distance = np.linalg.norm(current_weight - neighbor_weight)
                        adjacent_distances.append(distance)
        
        return {
            'mean_adjacent_distance': np.mean(adjacent_distances),
            'std_adjacent_distance': np.std(adjacent_distances),
            'min_adjacent_distance': np.min(adjacent_distances),
            'max_adjacent_distance': np.max(adjacent_distances)
        }


class SOMUtils:
    """Utility functions for SOM analysis and data processing"""
    
    @staticmethod
    def normalize_data(data: np.ndarray, method: str = 'minmax') -> Tuple[np.ndarray, Dict]:
        """
        Normalize data using specified method
        
        Args:
            data: Input data array
            method: Normalization method ('minmax', 'zscore', 'unit')
            
        Returns:
            Tuple of (normalized_data, normalization_parameters)
        """
        if method == 'minmax':
            data_min = np.min(data, axis=0)
            data_max = np.max(data, axis=0)
            data_range = data_max - data_min
            data_range[data_range == 0] = 1  # Avoid division by zero
            
            normalized = (data - data_min) / data_range
            params = {'method': 'minmax', 'min': data_min, 'max': data_max, 'range': data_range}
            
        elif method == 'zscore':
            data_mean = np.mean(data, axis=0)
            data_std = np.std(data, axis=0)
            data_std[data_std == 0] = 1  # Avoid division by zero
            
            normalized = (data - data_mean) / data_std
            params = {'method': 'zscore', 'mean': data_mean, 'std': data_std}
            
        elif method == 'unit':
            data_norm = np.linalg.norm(data, axis=1, keepdims=True)
            data_norm[data_norm == 0] = 1  # Avoid division by zero
            
            normalized = data / data_norm
            params = {'method': 'unit'}
            
        else:
            raise ValueError(f"Unknown normalization method: {method}")
        
        return normalized, params
    
    @staticmethod
    def denormalize_data(normalized_data: np.ndarray, params: Dict) -> np.ndarray:
        """
        Denormalize data using stored parameters
        
        Args:
            normalized_data: Normalized data array
            params: Parameters from normalize_data
            
        Returns:
            Denormalized data array
        """
        method = params['method']
        
        if method == 'minmax':
            return normalized_data * params['range'] + params['min']
        elif method == 'zscore':
            return normalized_data * params['std'] + params['mean']
        elif method == 'unit':
            return normalized_data  # Cannot denormalize unit vectors without original norms
        else:
            raise ValueError(f"Unknown normalization method: {method}")
    
    @staticmethod
    def calculate_data_statistics(data: np.ndarray) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics for input data
        
        Args:
            data: Input data array
            
        Returns:
            Dictionary with data statistics
        """
        return {
            'n_samples': len(data),
            'n_features': data.shape[1] if data.ndim > 1 else 1,
            'mean': np.mean(data, axis=0),
            'std': np.std(data, axis=0),
            'min': np.min(data, axis=0),
            'max': np.max(data, axis=0),
            'median': np.median(data, axis=0),
            'data_range': np.max(data, axis=0) - np.min(data, axis=0)
        }
    
    @staticmethod
    def suggest_map_size(n_samples: int, heuristic: str = 'vesanto') -> Tuple[int, int]:
        """
        Suggest appropriate map size based on data size
        
        Args:
            n_samples: Number of training samples
            heuristic: Heuristic method ('vesanto', 'sqrt', 'log')
            
        Returns:
            Suggested (height, width) for the map
        """
        if heuristic == 'vesanto':
            # Vesanto et al. heuristic: map size ≈ 5*sqrt(N)
            map_units = max(4, int(5 * np.sqrt(n_samples)))
        elif heuristic == 'sqrt':
            # Simple square root heuristic
            map_units = max(4, int(np.sqrt(n_samples)))
        elif heuristic == 'log':
            # Logarithmic heuristic for large datasets
            map_units = max(4, int(np.log2(n_samples) * 2))
        else:
            raise ValueError(f"Unknown heuristic: {heuristic}")
        
        # Create square or slightly rectangular map
        side = int(np.sqrt(map_units))
        return (side, side + (map_units - side*side) // side)
    
    @staticmethod
    def estimate_training_iterations(map_size: Tuple[int, int], n_samples: int) -> int:
        """
        Estimate appropriate number of training iterations
        
        Args:
            map_size: Map dimensions (height, width)
            n_samples: Number of training samples
            
        Returns:
            Suggested number of training iterations
        """
        n_neurons = map_size[0] * map_size[1]
        # Rule of thumb: 500-1000 iterations per neuron, adjusted by data size
        base_iterations = n_neurons * 500
        data_factor = max(0.5, min(2.0, n_samples / 1000))
        return int(base_iterations * data_factor)


def create_som_metrics(som_core, topology_manager) -> SOMMetrics:
    """Factory function to create SOM metrics calculator"""
    return SOMMetrics(som_core, topology_manager)