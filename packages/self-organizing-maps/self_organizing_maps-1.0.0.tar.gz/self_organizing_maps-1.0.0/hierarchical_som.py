"""
Hierarchical Self-Organizing Map (HSOM)
Based on: Rauber et al. (2002) "The Growing Hierarchical Self-Organizing Map"

Implements hierarchical feature learning with multiple layers of SOMs,
allowing for multi-resolution representation and hierarchical clustering.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
import matplotlib.pyplot as plt
from dataclasses import dataclass
from .self_organizing_map import SelfOrganizingMap, SOMNeuron

@dataclass
class HierarchicalLayer:
    """Single layer in hierarchical SOM"""
    som: SelfOrganizingMap
    level: int
    parent_indices: Optional[np.ndarray] = None
    children_soms: Optional[List['HierarchicalLayer']] = None
    
    def __post_init__(self):
        if self.children_soms is None:
            self.children_soms = []

class HierarchicalSOM:
    """
    Hierarchical Self-Organizing Map with multiple resolution levels
    
    Features:
    - Multi-layer architecture with increasing resolution
    - Hierarchical clustering and representation learning
    - Automatic depth adaptation based on data complexity
    - Top-down and bottom-up information flow
    """
    
    def __init__(self,
                 input_dim: int,
                 base_map_size: Tuple[int, int] = (5, 5),
                 max_levels: int = 3,
                 expansion_factor: int = 2,
                 learning_rate_decay: float = 0.9,
                 neighborhood_decay: float = 0.9,
                 min_data_per_node: int = 5,
                 expansion_threshold: float = 0.1,
                 random_seed: Optional[int] = None):
        """
        Initialize Hierarchical SOM
        
        Args:
            input_dim: Dimensionality of input vectors
            base_map_size: Size of root SOM layer (width, height)
            max_levels: Maximum number of hierarchical levels
            expansion_factor: Factor by which to expand child maps
            learning_rate_decay: Decay factor for learning rate per level
            neighborhood_decay: Decay factor for neighborhood per level
            min_data_per_node: Minimum data points to create child SOM
            expansion_threshold: Error threshold for creating new levels
            random_seed: Random seed for reproducibility
        """
        self.input_dim = input_dim
        self.base_map_size = base_map_size
        self.max_levels = max_levels
        self.expansion_factor = expansion_factor
        self.learning_rate_decay = learning_rate_decay
        self.neighborhood_decay = neighborhood_decay
        self.min_data_per_node = min_data_per_node
        self.expansion_threshold = expansion_threshold
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Initialize root layer
        self.root_layer = self._create_layer(
            level=0,
            map_size=base_map_size,
            input_dim=input_dim,
            learning_rate=0.1,
            neighborhood_radius=max(base_map_size) // 2
        )
        
        self.layers = [self.root_layer]
        self.training_history = []
        self.data_assignment = {}  # Track which data belongs to which nodes
        
    def _create_layer(self,
                     level: int,
                     map_size: Tuple[int, int],
                     input_dim: int,
                     learning_rate: float,
                     neighborhood_radius: float) -> HierarchicalLayer:
        """Create a new hierarchical layer"""
        
        som = SelfOrganizingMap(
            width=map_size[0],
            height=map_size[1], 
            input_dim=input_dim,
            learning_rate=learning_rate,
            initial_neighborhood_radius=neighborhood_radius
        )
        
        return HierarchicalLayer(som=som, level=level)
    
    def _assign_data_to_nodes(self, data: np.ndarray, layer: HierarchicalLayer) -> Dict[Tuple[int, int], List[int]]:
        """Assign data points to SOM nodes in a layer"""
        assignments = {}
        
        for i, datapoint in enumerate(data):
            winner = layer.som.find_best_matching_unit(datapoint)
            if winner not in assignments:
                assignments[winner] = []
            assignments[winner].append(i)
        
        return assignments
    
    def _should_expand_node(self, node_data: np.ndarray, layer: HierarchicalLayer) -> bool:
        """Determine if a node should be expanded into a child SOM"""
        
        # Check minimum data requirement
        if len(node_data) < self.min_data_per_node:
            return False
        
        # Check if we've reached maximum levels
        if layer.level >= self.max_levels - 1:
            return False
        
        # Check data variance (expansion threshold)
        if len(node_data) > 1:
            data_variance = np.var(node_data, axis=0).mean()
            if data_variance < self.expansion_threshold:
                return False
        
        return True
    
    def _create_child_som(self,
                         parent_layer: HierarchicalLayer,
                         parent_node: Tuple[int, int],
                         node_data: np.ndarray) -> HierarchicalLayer:
        """Create child SOM for a parent node"""
        
        child_level = parent_layer.level + 1
        
        # Scale map size based on expansion factor
        child_width = min(self.base_map_size[0] * self.expansion_factor, len(node_data))
        child_height = min(self.base_map_size[1] * self.expansion_factor, len(node_data))
        
        # Adjust learning parameters for deeper levels
        child_learning_rate = 0.1 * (self.learning_rate_decay ** child_level)
        child_neighborhood = max(child_width, child_height) // 2 * (self.neighborhood_decay ** child_level)
        
        child_layer = self._create_layer(
            level=child_level,
            map_size=(child_width, child_height),
            input_dim=self.input_dim,
            learning_rate=child_learning_rate,
            neighborhood_radius=child_neighborhood
        )
        
        # Initialize child SOM weights with data centroid and some noise
        data_centroid = np.mean(node_data, axis=0)
        for i in range(child_width):
            for j in range(child_height):
                noise = np.random.normal(0, 0.1, self.input_dim)
                child_layer.som.neurons[i][j].weights = data_centroid + noise
        
        return child_layer
    
    def _get_layer_data_subset(self, layer: HierarchicalLayer, full_data: np.ndarray) -> np.ndarray:
        """Get proper data subset for child layer based on parent assignments"""
        
        # Find parent layer
        parent_layer = None
        for l in self.layers:
            if l.level == layer.level - 1:
                # Check if this layer is a child of l
                if layer in l.children_soms:
                    parent_layer = l
                    break
        
        if parent_layer is None:
            # No parent found, return full data (fallback)
            return full_data
        
        # Find which parent node this child corresponds to
        parent_node_coord = None
        for i, child in enumerate(parent_layer.children_soms):
            if child == layer:
                # Find the parent node that created this child
                # This requires tracking the mapping during creation
                if hasattr(layer, '_parent_node_coord'):
                    parent_node_coord = layer._parent_node_coord
                break
        
        if parent_node_coord is None:
            # Fallback: assign data based on current parent layer state
            return self._assign_data_to_child_automatically(layer, parent_layer, full_data)
        
        # Get data assigned to the parent node
        parent_assignments = self._assign_data_to_nodes(full_data, parent_layer)
        child_data_indices = parent_assignments.get(parent_node_coord, [])
        
        if len(child_data_indices) == 0:
            # No data assigned to parent, return subset
            return full_data[:max(1, len(full_data) // 10)]  # At least some data
        
        return full_data[child_data_indices]
    
    def _assign_data_to_child_automatically(self, child_layer: HierarchicalLayer, 
                                          parent_layer: HierarchicalLayer, 
                                          full_data: np.ndarray) -> np.ndarray:
        """Automatically assign data to child layer based on parent layer clustering"""
        
        # Get parent layer assignments
        parent_assignments = self._assign_data_to_nodes(full_data, parent_layer)
        
        # Find the best matching parent node for this child
        # Use the centroid of child layer weights as representative
        child_centroid = self._compute_layer_centroid(child_layer)
        
        best_parent_node = None
        best_distance = float('inf')
        
        for parent_coord in parent_assignments.keys():
            # Get parent node weights
            parent_weights = parent_layer.som.neurons[parent_coord[0]][parent_coord[1]].weights
            
            # Calculate distance to child centroid
            distance = np.linalg.norm(parent_weights - child_centroid)
            
            if distance < best_distance:
                best_distance = distance
                best_parent_node = parent_coord
        
        # Return data assigned to best matching parent node
        if best_parent_node and best_parent_node in parent_assignments:
            child_data_indices = parent_assignments[best_parent_node]
            return full_data[child_data_indices]
        
        # Fallback: return random subset
        subset_size = max(self.min_data_per_node, len(full_data) // (2 ** child_layer.level))
        indices = np.random.choice(len(full_data), size=min(subset_size, len(full_data)), replace=False)
        return full_data[indices]
    
    def _compute_layer_centroid(self, layer: HierarchicalLayer) -> np.ndarray:
        """Compute centroid of all neurons in a layer"""
        all_weights = []
        
        for i in range(layer.som.width):
            for j in range(layer.som.height):
                all_weights.append(layer.som.neurons[i][j].weights)
        
        return np.mean(all_weights, axis=0)
    
    def train_layer(self, 
                   data: np.ndarray,
                   layer: HierarchicalLayer,
                   n_epochs: int = 100) -> Dict[str, Any]:
        """Train a single layer of the hierarchical SOM"""
        
        print(f"Training layer {layer.level} for {n_epochs} epochs...")
        
        # Train the SOM
        training_result = layer.som.train(data, n_epochs=n_epochs)
        
        # Assign data to nodes
        assignments = self._assign_data_to_nodes(data, layer)
        
        # Create child SOMs for nodes with sufficient data and variance
        children_created = 0
        
        for node_coord, data_indices in assignments.items():
            node_data = data[data_indices]
            
            if self._should_expand_node(node_data, layer):
                child_layer = self._create_child_som(layer, node_coord, node_data)
                
                # Track parent-child relationship
                child_layer._parent_node_coord = node_coord
                child_layer._parent_layer = layer
                child_layer._assigned_data_indices = data_indices
                
                layer.children_soms.append(child_layer)
                self.layers.append(child_layer)
                children_created += 1
                
                print(f"  Created child SOM for node {node_coord} with {len(node_data)} data points")
        
        return {
            "level": layer.level,
            "training_result": training_result,
            "node_assignments": assignments,
            "children_created": children_created,
            "total_children": len(layer.children_soms)
        }
    
    def train(self, data: np.ndarray, n_epochs_per_level: int = 100) -> Dict[str, Any]:
        """
        Train hierarchical SOM with breadth-first layer training
        
        Args:
            data: Training data, shape (n_samples, input_dim)
            n_epochs_per_level: Number of epochs to train each level
            
        Returns:
            Training statistics for all levels
        """
        print(f"Training Hierarchical SOM with {len(data)} data points...")
        
        training_results = []
        
        # Train level by level
        current_level_layers = [self.root_layer]
        
        for level in range(self.max_levels):
            if not current_level_layers:
                break
                
            print(f"\n=== Training Level {level} ({len(current_level_layers)} SOMs) ===")
            
            next_level_layers = []
            level_results = []
            
            for layer in current_level_layers:
                # Determine data subset for this layer
                if layer.level == 0:
                    # Root layer gets all data
                    layer_data = data
                else:
                    # Child layers get data assigned to their parent node
                    layer_data = self._get_layer_data_subset(layer, data)
                
                # Train this layer
                layer_result = self.train_layer(layer_data, layer, n_epochs_per_level)
                level_results.append(layer_result)
                
                # Collect child layers for next level
                next_level_layers.extend(layer.children_soms)
            
            training_results.append({
                "level": level,
                "n_soms": len(current_level_layers),
                "layer_results": level_results
            })
            
            current_level_layers = next_level_layers
        
        self.training_history = training_results
        
        return {
            "n_levels_trained": len(training_results),
            "total_soms": len(self.layers),
            "training_results": training_results
        }
    
    def predict(self, input_vector: np.ndarray) -> Dict[str, Any]:
        """
        Predict hierarchical representation for input vector
        
        Args:
            input_vector: Input data point
            
        Returns:
            Hierarchical prediction with winners at each level
        """
        hierarchical_path = []
        current_layer = self.root_layer
        
        while current_layer is not None:
            # Find winner in current layer
            winner = current_layer.som.find_best_matching_unit(input_vector)
            
            hierarchical_path.append({
                "level": current_layer.level,
                "winner": winner,
                "winner_weights": current_layer.som.neurons[winner[0]][winner[1]].weights.copy()
            })
            
            # Find child SOM corresponding to winner
            next_layer = None
            if current_layer.children_soms:
                # Find child SOM that corresponds to the winning node
                for child in current_layer.children_soms:
                    if hasattr(child, '_parent_node_coord') and child._parent_node_coord == winner:
                        next_layer = child
                        break
                
                # Fallback: if no exact match, find closest child
                if next_layer is None and current_layer.children_soms:
                    best_child = None
                    best_distance = float('inf')
                    winner_weights = current_layer.som.neurons[winner[0]][winner[1]].weights
                    
                    for child in current_layer.children_soms:
                        child_centroid = self._compute_layer_centroid(child)
                        distance = np.linalg.norm(winner_weights - child_centroid)
                        
                        if distance < best_distance:
                            best_distance = distance
                            best_child = child
                    
                    next_layer = best_child
            
            current_layer = next_layer
        
        return {
            "hierarchical_path": hierarchical_path,
            "final_level": len(hierarchical_path) - 1,
            "coarse_representation": hierarchical_path[0]["winner"],
            "fine_representation": hierarchical_path[-1]["winner"] if hierarchical_path else None
        }
    
    def get_hierarchical_representation(self, data: np.ndarray) -> Dict[int, np.ndarray]:
        """
        Get representations at all hierarchical levels
        
        Args:
            data: Input data points
            
        Returns:
            Dictionary mapping level -> representation vectors
        """
        representations = {}
        
        for level, layer in enumerate(self.layers):
            if layer.level not in representations:
                representations[layer.level] = []
            
            for datapoint in data:
                winner = layer.som.find_best_matching_unit(datapoint)
                # Convert 2D winner coordinates to 1D representation
                winner_1d = winner[0] * layer.som.height + winner[1]
                representations[layer.level].append(winner_1d)
        
        # Convert to arrays
        for level in representations:
            representations[level] = np.array(representations[level])
        
        return representations
    
    def visualize_hierarchy(self, figsize: Tuple[int, int] = (15, 10)):
        """
        Visualize the hierarchical structure
        
        Args:
            figsize: Figure size for matplotlib
        """
        if self.input_dim != 2:
            print("Visualization only available for 2D input data")
            return
        
        # Count levels and SOMs per level
        levels_dict = {}
        for layer in self.layers:
            level = layer.level
            if level not in levels_dict:
                levels_dict[level] = []
            levels_dict[level].append(layer)
        
        n_levels = len(levels_dict)
        if n_levels == 0:
            return
        
        # Create subplots
        fig, axes = plt.subplots(1, n_levels, figsize=figsize)
        if n_levels == 1:
            axes = [axes]
        
        for level_idx, (level, level_layers) in enumerate(sorted(levels_dict.items())):
            ax = axes[level_idx]
            
            # Plot first SOM in level (or combine multiple if needed)
            layer = level_layers[0]  # Simplification
            
            # Get neuron positions
            positions = []
            for i in range(layer.som.width):
                for j in range(layer.som.height):
                    positions.append(layer.som.neurons[i][j].weights[:2])  # Only 2D
            
            positions = np.array(positions)
            
            # Plot neurons
            ax.scatter(positions[:, 0], positions[:, 1], c='red', s=50, alpha=0.7)
            
            # Plot grid connections
            for i in range(layer.som.width):
                for j in range(layer.som.height):
                    # Horizontal connections
                    if i < layer.som.width - 1:
                        pos1 = layer.som.neurons[i][j].weights[:2]
                        pos2 = layer.som.neurons[i+1][j].weights[:2]
                        ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 'b-', alpha=0.3)
                    
                    # Vertical connections
                    if j < layer.som.height - 1:
                        pos1 = layer.som.neurons[i][j].weights[:2]
                        pos2 = layer.som.neurons[i][j+1].weights[:2]
                        ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 'b-', alpha=0.3)
            
            ax.set_title(f'Level {level} ({len(level_layers)} SOMs)')
            ax.set_xlabel('Feature 1')
            ax.set_ylabel('Feature 2')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.suptitle('Hierarchical SOM Structure', y=1.02)
        plt.show()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get hierarchical SOM statistics
        
        Returns:
            Dictionary with network statistics
        """
        # Count SOMs per level
        level_counts = {}
        for layer in self.layers:
            level = layer.level
            level_counts[level] = level_counts.get(level, 0) + 1
        
        total_neurons = 0
        for layer in self.layers:
            total_neurons += layer.som.width * layer.som.height
        
        return {
            "total_levels": len(level_counts),
            "total_soms": len(self.layers),
            "total_neurons": total_neurons,
            "soms_per_level": level_counts,
            "max_depth": max(level_counts.keys()) if level_counts else 0,
            "tree_width": max(level_counts.values()) if level_counts else 0
        }
    
    def prune_empty_branches(self, min_activation_threshold: float = 0.01):
        """
        Remove layers/SOMs that don't contribute meaningfully to the hierarchy.
        
        Args:
            min_activation_threshold: Minimum activation level to keep a neuron/SOM
        """
        if not self.is_trained:
            print("Warning: Cannot prune untrained hierarchy")
            return
        
        pruned_levels = {}
        total_pruned_neurons = 0
        
        # Start from the deepest level and work up
        for level in sorted(self.levels.keys(), reverse=True):
            som = self.levels[level]
            
            # Calculate activation frequency for each neuron
            if hasattr(som, '_activation_history'):
                activation_counts = som._activation_history
            else:
                # If no activation history, keep all neurons (can't determine usage)
                activation_counts = np.ones((som.output_dim, som.output_dim))
            
            total_activations = np.sum(activation_counts)
            if total_activations == 0:
                # Empty level - remove completely
                print(f"Pruning empty level {level} (no activations)")
                total_pruned_neurons += som.output_dim * som.output_dim
                continue
            
            # Calculate activation frequencies
            activation_freq = activation_counts / total_activations
            
            # Identify neurons to keep
            active_mask = activation_freq >= min_activation_threshold
            active_count = np.sum(active_mask)
            
            if active_count == 0:
                # No neurons meet threshold - remove level
                print(f"Pruning level {level} (no neurons above threshold {min_activation_threshold})")
                total_pruned_neurons += som.output_dim * som.output_dim
                continue
            
            # Prune inactive neurons from this level
            if active_count < som.output_dim * som.output_dim:
                pruned_neurons = som.output_dim * som.output_dim - active_count
                total_pruned_neurons += pruned_neurons
                print(f"Pruning {pruned_neurons} inactive neurons from level {level}")
                
                # Create pruned SOM with only active neurons
                # Note: This is a simplified approach - in practice you'd need to
                # restructure the weight matrix and update connections
                som._active_mask = active_mask
                som._pruned = True
            
            # Keep this level
            pruned_levels[level] = som
        
        # Update hierarchy with pruned levels
        removed_levels = len(self.levels) - len(pruned_levels)
        self.levels = pruned_levels
        
        print(f"Pruning complete:")
        print(f"  - Removed {removed_levels} empty levels")
        print(f"  - Pruned {total_pruned_neurons} inactive neurons")
        print(f"  - Retained {len(pruned_levels)} levels")
        
        # Recompute hierarchy structure after pruning
        if pruned_levels:
            self._recompute_hierarchy_structure()
    
    def get_cluster_hierarchy(self, data: np.ndarray) -> Dict[str, Any]:
        """
        Extract hierarchical clustering from trained HSOM
        
        Args:
            data: Data to cluster
            
        Returns:
            Hierarchical clustering information
        """
        clusters = {}
        
        # Get representations at each level
        representations = self.get_hierarchical_representation(data)
        
        for level, repr_vec in representations.items():
            # Group data by representation
            unique_reprs = np.unique(repr_vec)
            level_clusters = {}
            
            for repr_id in unique_reprs:
                indices = np.where(repr_vec == repr_id)[0]
                level_clusters[int(repr_id)] = indices.tolist()
            
            clusters[f"level_{level}"] = level_clusters
        
        return clusters
    
    def _recompute_hierarchy_structure(self):
        """Recompute hierarchy structure after pruning"""
        # Update parent-child relationships after pruning
        for level in sorted(self.levels.keys()):
            som = self.levels[level]
            
            # Update connections to pruned parent levels
            if level > 0 and (level - 1) in self.levels:
                parent_som = self.levels[level - 1]
                
                # If parent was pruned, update connection mapping
                if hasattr(parent_som, '_pruned') and parent_som._pruned:
                    # Remap connections to only active parent neurons
                    if hasattr(parent_som, '_active_mask'):
                        som._parent_connection_mask = parent_som._active_mask
            
            # Update child connections
            if level + 1 in self.levels:
                child_som = self.levels[level + 1]
                
                # If current level was pruned, update child connections
                if hasattr(som, '_pruned') and som._pruned:
                    if hasattr(som, '_active_mask') and hasattr(child_som, '_parent_connection_mask'):
                        child_som._parent_connection_mask = som._active_mask