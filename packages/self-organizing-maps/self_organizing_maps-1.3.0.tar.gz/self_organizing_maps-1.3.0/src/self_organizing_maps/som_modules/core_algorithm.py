"""
Core SOM Algorithm Module - Competition, Cooperation, and Adaptation

This module contains the fundamental Kohonen algorithm implementing the three-phase
learning process: Competition (BMU finding), Cooperation (neighborhood), and 
Adaptation (weight updates).

Based on: Kohonen (1982) "Self-Organized Formation of Topologically Correct Feature Maps"
"""

import numpy as np
from typing import Tuple
from dataclasses import dataclass


@dataclass
class SOMNeuron:
    """
    SOM Neuron: Individual processing unit in the Self-Organizing Map
    
    ELI5: Like a brain cell that remembers what patterns it likes best.
    Each neuron has a "favorite pattern" (weight_vector) and remembers its
    location on the map (position) and how active it's been (activation_history).
    
    Technical Details:
    Each neuron in the SOM grid maintains:
    - Spatial position (i, j) coordinates on the 2D lattice
    - Weight vector w_i representing its prototype/template
    - Activation history for analysis and visualization
    
    The neuron competes with others to respond to inputs by calculating
    the Euclidean distance: d = ||x - w_i|| where x is the input vector.
    The neuron with minimum distance becomes the Best Matching Unit (BMU).
    
    Attributes:
    - position: (i, j) grid coordinates - where this neuron sits on the map
    - weight_vector: w_i ∈ ℝᵈ - this neuron's learned feature template  
    - activation_history: List of activation values over time
    
    Usage:
    Usually created automatically by SelfOrganizingMap, but you can inspect:
    ```python
    neuron = som.neurons[2, 3]  # Get neuron at position (2, 3)
    print(f"Position: {neuron.position}")
    print(f"Weights: {neuron.weight_vector}")
    print(f"Activation count: {len(neuron.activation_history)}")
    ```
    """
    position: Tuple[int, int]  # Grid coordinates (i, j)
    weight_vector: np.ndarray  # Feature weights w_i ∈ ℝᵈ  
    activation_history: list  # History of activations for analysis


class SOMCoreAlgorithm:
    """
    Core SOM Algorithm implementing Kohonen's three-phase learning process:
    1. Competition: Find Best Matching Unit (BMU)
    2. Cooperation: Calculate neighborhood influence 
    3. Adaptation: Update weights using competitive learning
    
    This class handles the fundamental neural network operations while remaining
    agnostic to specific neighborhood functions and parameter schedules.
    """
    
    def __init__(self, map_size: Tuple[int, int], input_dim: int):
        """Initialize core algorithm with map dimensions and input size"""
        self.map_height, self.map_width = map_size
        self.input_dim = input_dim
        self.neurons = None
        
    def initialize_neurons(self, initialization: str = 'random') -> np.ndarray:
        """
        Initialize neuron weights using specified method
        
        Args:
            initialization: 'random' or 'linear'
            
        Returns:
            Grid of initialized SOMNeuron objects
        """
        neurons = np.empty((self.map_height, self.map_width), dtype=object)
        
        for i in range(self.map_height):
            for j in range(self.map_width):
                if initialization == 'random':
                    weight_vector = np.random.uniform(-1, 1, self.input_dim)
                elif initialization == 'linear':
                    # Linear initialization along principal components
                    x_ratio = j / max(1, self.map_width - 1)
                    y_ratio = i / max(1, self.map_height - 1)
                    
                    if self.input_dim == 2:
                        weight_vector = np.array([x_ratio * 2 - 1, y_ratio * 2 - 1])
                    else:
                        weight_vector = np.random.uniform(-1, 1, self.input_dim)
                        weight_vector[0] = x_ratio * 2 - 1  # First dim follows x
                        if self.input_dim > 1:
                            weight_vector[1] = y_ratio * 2 - 1  # Second dim follows y
                else:
                    raise ValueError(f"Unknown initialization: {initialization}")
                
                neurons[i, j] = SOMNeuron(
                    position=(i, j),
                    weight_vector=weight_vector,
                    activation_history=[]
                )
        
        self.neurons = neurons
        return neurons
    
    def find_bmu(self, input_vector: np.ndarray) -> Tuple[int, int]:
        """
        Find Best Matching Unit (BMU) - Competition Phase of Kohonen Algorithm
        
        ELI5: Find the neuron that "likes" the input the most!
        Like finding which person in a crowd looks most similar to a photo you're holding.
        Each neuron has learned to recognize certain patterns, and we pick the best match.
        
        Technical Details:
        The BMU is the neuron with the minimum Euclidean distance to the input:
        
        BMU = argmin_i ||x - w_i||₂
        
        where:
        - x: input vector
        - w_i: weight vector of neuron i  
        - ||·||₂: Euclidean (L2) norm
        
        This implements the "competition" phase of Kohonen's algorithm where neurons
        compete to respond to the input. Only the winning neuron (BMU) and its
        neighbors will be updated during the adaptation phase.
        
        Algorithm:
        1. Initialize min_distance = ∞ and best_position = (0,0)
        2. For each neuron (i,j) in the grid:
           a. Calculate distance = ||input - w_ij||₂  
           b. If distance < min_distance:
              - Update min_distance = distance
              - Update best_position = (i,j)
        3. Return best_position
        
        Performance Notes:
        - Time Complexity: O(N × D) where N = neurons, D = dimensions
        - Space Complexity: O(1) - constant memory usage
        - For large maps, consider using approximate methods (k-d trees, etc.)
        
        Args:
            input_vector (np.ndarray): Input pattern to match, shape (input_dim,)
        
        Returns:
            Tuple[int, int]: (row, col) grid coordinates of the BMU
        
        Example:
            ```python
            # Find BMU for a 2D input
            input_data = np.array([0.3, 0.7])
            bmu_position = core.find_bmu(input_data)
            print(f"BMU at grid position: {bmu_position}")
            
            # Get the actual BMU neuron
            bmu_neuron = core.neurons[bmu_position[0], bmu_position[1]]
            distance = np.linalg.norm(bmu_neuron.weight_vector - input_data)
            print(f"Distance to BMU: {distance:.4f}")
            ```
        """
        if self.neurons is None:
            raise ValueError("Neurons not initialized. Call initialize_neurons() first.")
        
        min_distance = float('inf')
        bmu_position = (0, 0)
        
        for i in range(self.map_height):
            for j in range(self.map_width):
                neuron = self.neurons[i, j]
                distance = np.linalg.norm(neuron.weight_vector - input_vector)
                
                if distance < min_distance:
                    min_distance = distance
                    bmu_position = (i, j)
                    
        return bmu_position
    
    def update_weights(self, input_vector: np.ndarray, bmu_position: Tuple[int, int],
                      neighborhood_func, distance_func, learning_rate: float, 
                      radius: float) -> None:
        """
        Update neuron weights - Cooperation and Adaptation phases
        
        This implements the cooperation (neighborhood calculation) and adaptation 
        (weight update) phases of Kohonen's algorithm.
        
        Args:
            input_vector: The training input
            bmu_position: BMU coordinates from competition phase
            neighborhood_func: Function to calculate neighborhood influence
            distance_func: Function to calculate distance between positions
            learning_rate: Current learning rate
            radius: Current neighborhood radius
        """
        if self.neurons is None:
            raise ValueError("Neurons not initialized. Call initialize_neurons() first.")
        
        # Update BMU and its neighbors
        for i in range(self.map_height):
            for j in range(self.map_width):
                neuron = self.neurons[i, j]
                
                # Calculate distance from BMU (Cooperation phase)
                distance = distance_func((i, j), bmu_position)
                
                # Calculate neighborhood influence (Cooperation phase)
                influence = neighborhood_func(distance, radius)
                
                # Update neuron weights if within influence (Adaptation phase)
                if influence > 0.01:  # Threshold to avoid tiny updates
                    # Kohonen learning rule: w_new = w_old + η * h * (x - w_old)
                    delta = learning_rate * influence * (input_vector - neuron.weight_vector)
                    neuron.weight_vector += delta
    
    def train_step(self, input_vector: np.ndarray, neighborhood_func, distance_func,
                   learning_rate: float, radius: float) -> Tuple[int, int]:
        """
        Perform one complete training step implementing Kohonen's three phases:
        1. Competition: Find BMU
        2. Cooperation: Calculate neighborhood
        3. Adaptation: Update weights
        
        Args:
            input_vector: Training sample
            neighborhood_func: Neighborhood function
            distance_func: Distance calculation function
            learning_rate: Current learning rate
            radius: Current neighborhood radius
            
        Returns:
            BMU position for this training step
        """
        # Phase 1: Competition - Find Best Matching Unit
        bmu_pos = self.find_bmu(input_vector)
        
        # Phase 2 & 3: Cooperation and Adaptation
        self.update_weights(input_vector, bmu_pos, neighborhood_func, 
                          distance_func, learning_rate, radius)
        
        return bmu_pos
    
    def get_neuron_weights(self) -> np.ndarray:
        """Get all neuron weights as a 3D array (height, width, input_dim)"""
        if self.neurons is None:
            raise ValueError("Neurons not initialized. Call initialize_neurons() first.")
        
        weights = np.zeros((self.map_height, self.map_width, self.input_dim))
        
        for i in range(self.map_height):
            for j in range(self.map_width):
                weights[i, j] = self.neurons[i, j].weight_vector
                
        return weights
    
    def map_input(self, input_vector: np.ndarray) -> Tuple[int, int]:
        """Map an input vector to its BMU position on the grid"""
        return self.find_bmu(input_vector)