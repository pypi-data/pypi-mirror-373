"""
Growing Self-Organizing Map (Growing SOM)
Based on: Fritzke (1995) "A Growing Neural Gas Network Learns Topologies"

Implements dynamic topology learning where the network structure
adapts during training by adding and removing neurons.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import matplotlib.pyplot as plt
from dataclasses import dataclass
from .self_organizing_map import SOMNeuron

@dataclass
class GrowingSOMNode:
    """Node in the Growing SOM network"""
    weights: np.ndarray
    error: float = 0.0
    age_connections: Dict[int, int] = None
    neighbors: List[int] = None
    
    def __post_init__(self):
        if self.age_connections is None:
            self.age_connections = {}
        if self.neighbors is None:
            self.neighbors = []

class GrowingSelfOrganizingMap:
    """
    Growing Self-Organizing Map with dynamic topology
    
    Key features:
    - Dynamically adds neurons during training
    - Removes neurons with low utility
    - Learns optimal network topology
    - Preserves neighborhood relationships
    """
    
    def __init__(self,
                 input_dim: int,
                 initial_nodes: int = 2,
                 max_nodes: int = 100,
                 insertion_frequency: int = 100,
                 max_age: int = 200,
                 alpha: float = 0.1,
                 beta: float = 0.01,
                 gamma: float = 0.1,
                 random_seed: Optional[int] = None):
        """
        Initialize Growing SOM
        
        Args:
            input_dim: Dimensionality of input vectors
            initial_nodes: Number of initial nodes
            max_nodes: Maximum number of nodes allowed
            insertion_frequency: How often to insert new nodes
            max_age: Maximum age for connections before removal
            alpha: Learning rate for winner
            beta: Learning rate for neighbors
            gamma: Error reduction factor
            random_seed: Random seed for reproducibility
        """
        self.input_dim = input_dim
        self.max_nodes = max_nodes
        self.insertion_frequency = insertion_frequency
        self.max_age = max_age
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Initialize network with two random nodes
        self.nodes = []
        self.connections = set()  # Set of (i, j) tuples representing connections
        
        for i in range(initial_nodes):
            weights = np.random.randn(input_dim) * 0.1
            self.nodes.append(GrowingSOMNode(weights=weights))
        
        # Connect initial nodes
        if initial_nodes >= 2:
            self._add_connection(0, 1)
        
        self.iteration_count = 0
        self.training_history = []
        
    def _add_connection(self, i: int, j: int):
        """Add connection between nodes i and j"""
        if i != j and (i, j) not in self.connections and (j, i) not in self.connections:
            self.connections.add((min(i, j), max(i, j)))
            self.nodes[i].neighbors.append(j)
            self.nodes[j].neighbors.append(i)
            self.nodes[i].age_connections[j] = 0
            self.nodes[j].age_connections[i] = 0
    
    def _remove_connection(self, i: int, j: int):
        """Remove connection between nodes i and j"""
        connection = (min(i, j), max(i, j))
        if connection in self.connections:
            self.connections.remove(connection)
            
            if j in self.nodes[i].neighbors:
                self.nodes[i].neighbors.remove(j)
            if i in self.nodes[j].neighbors:
                self.nodes[j].neighbors.remove(i)
                
            self.nodes[i].age_connections.pop(j, None)
            self.nodes[j].age_connections.pop(i, None)
    
    def _find_winners(self, input_vector: np.ndarray) -> Tuple[int, int]:
        """Find the two closest nodes to input vector"""
        distances = []
        for i, node in enumerate(self.nodes):
            dist = np.linalg.norm(input_vector - node.weights)
            distances.append((dist, i))
        
        distances.sort()
        winner1 = distances[0][1]
        winner2 = distances[1][1] if len(distances) > 1 else winner1
        
        return winner1, winner2
    
    def _increment_age(self):
        """Increment age of all connections"""
        for i, node in enumerate(self.nodes):
            for neighbor_idx in list(node.age_connections.keys()):
                node.age_connections[neighbor_idx] += 1
                
                # Remove old connections
                if node.age_connections[neighbor_idx] > self.max_age:
                    self._remove_connection(i, neighbor_idx)
    
    def _remove_isolated_nodes(self):
        """Remove nodes with no connections"""
        nodes_to_remove = []
        
        for i, node in enumerate(self.nodes):
            if len(node.neighbors) == 0:
                nodes_to_remove.append(i)
        
        # Remove nodes in reverse order to maintain indices
        for i in sorted(nodes_to_remove, reverse=True):
            self._remove_node(i)
    
    def _remove_node(self, node_idx: int):
        """Remove a node and update all connections"""
        if 0 <= node_idx < len(self.nodes):
            # Remove all connections involving this node
            neighbors = self.nodes[node_idx].neighbors.copy()
            for neighbor in neighbors:
                self._remove_connection(node_idx, neighbor)
            
            # Remove the node
            self.nodes.pop(node_idx)
            
            # Update connection indices
            new_connections = set()
            for i, j in self.connections:
                new_i = i if i < node_idx else i - 1
                new_j = j if j < node_idx else j - 1
                if new_i >= 0 and new_j >= 0:
                    new_connections.add((min(new_i, new_j), max(new_i, new_j)))
            
            self.connections = new_connections
            
            # Update neighbor lists and age connections
            for node in self.nodes:
                # Update neighbor indices
                new_neighbors = []
                for neighbor in node.neighbors:
                    if neighbor < node_idx:
                        new_neighbors.append(neighbor)
                    elif neighbor > node_idx:
                        new_neighbors.append(neighbor - 1)
                    # Skip if neighbor == node_idx (removed node)
                node.neighbors = new_neighbors
                
                # Update age_connections keys
                new_age_connections = {}
                for neighbor, age in node.age_connections.items():
                    if neighbor < node_idx:
                        new_age_connections[neighbor] = age
                    elif neighbor > node_idx:
                        new_age_connections[neighbor - 1] = age
                    # Skip if neighbor == node_idx (removed node)
                node.age_connections = new_age_connections
    
    def _add_node(self, winner1: int, winner2: int):
        """Add new node between winner1 and winner2"""
        if len(self.nodes) >= self.max_nodes:
            return
        
        # Create new node with weights as midpoint
        new_weights = 0.5 * (self.nodes[winner1].weights + self.nodes[winner2].weights)
        new_node = GrowingSOMNode(weights=new_weights)
        
        # Add to network
        new_idx = len(self.nodes)
        self.nodes.append(new_node)
        
        # Remove connection between winner1 and winner2 if it exists
        self._remove_connection(winner1, winner2)
        
        # Connect new node to both winners
        self._add_connection(new_idx, winner1)
        self._add_connection(new_idx, winner2)
        
        # Reduce error of winner nodes
        self.nodes[winner1].error *= self.gamma
        self.nodes[winner2].error *= self.gamma
        new_node.error = 0.5 * (self.nodes[winner1].error + self.nodes[winner2].error)
    
    def train_step(self, input_vector: np.ndarray):
        """
        Perform one training step with Growing SOM algorithm
        
        Args:
            input_vector: Input data point
        """
        if len(self.nodes) == 0:
            return
        
        # Find two closest nodes
        winner1, winner2 = self._find_winners(input_vector)
        
        # Update error of winner
        error = np.linalg.norm(input_vector - self.nodes[winner1].weights)
        self.nodes[winner1].error += error
        
        # Update weights of winner
        self.nodes[winner1].weights += self.alpha * (input_vector - self.nodes[winner1].weights)
        
        # Connect winner and second winner if not already connected
        if winner1 != winner2:
            if (min(winner1, winner2), max(winner1, winner2)) not in self.connections:
                self._add_connection(winner1, winner2)
            else:
                # Reset age of this connection
                self.nodes[winner1].age_connections[winner2] = 0
                self.nodes[winner2].age_connections[winner1] = 0
        
        # Update neighbors of winner
        for neighbor in self.nodes[winner1].neighbors:
            if neighbor != winner2:  # Avoid double update
                self.nodes[neighbor].weights += self.beta * (input_vector - self.nodes[neighbor].weights)
        
        # Increment age of all connections from winner
        self._increment_age()
        
        # Remove old connections and isolated nodes
        self._remove_isolated_nodes()
        
        # Add new node periodically
        if self.iteration_count > 0 and self.iteration_count % self.insertion_frequency == 0:
            if len(self.nodes) < self.max_nodes:
                # Find node with highest error
                max_error_idx = max(range(len(self.nodes)), key=lambda i: self.nodes[i].error)
                
                # Find neighbor with highest error
                neighbors = self.nodes[max_error_idx].neighbors
                if neighbors:
                    max_error_neighbor = max(neighbors, key=lambda i: self.nodes[i].error)
                    self._add_node(max_error_idx, max_error_neighbor)
        
        self.iteration_count += 1
    
    def train(self, data: np.ndarray, n_epochs: int = 100) -> Dict[str, Any]:
        """
        Train Growing SOM on dataset
        
        Args:
            data: Training data, shape (n_samples, input_dim)
            n_epochs: Number of training epochs
            
        Returns:
            Training statistics and history
        """
        print(f"Training Growing SOM for {n_epochs} epochs...")
        
        initial_nodes = len(self.nodes)
        
        for epoch in range(n_epochs):
            # Shuffle data for each epoch
            shuffled_data = data[np.random.permutation(len(data))]
            
            epoch_errors = []
            
            for input_vector in shuffled_data:
                self.train_step(input_vector)
                
                # Calculate quantization error
                if len(self.nodes) > 0:
                    winner, _ = self._find_winners(input_vector)
                    error = np.linalg.norm(input_vector - self.nodes[winner].weights)
                    epoch_errors.append(error)
            
            avg_error = np.mean(epoch_errors) if epoch_errors else 0
            
            self.training_history.append({
                "epoch": epoch,
                "avg_error": avg_error,
                "n_nodes": len(self.nodes),
                "n_connections": len(self.connections)
            })
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: Nodes={len(self.nodes)}, "
                      f"Connections={len(self.connections)}, Error={avg_error:.4f}")
        
        final_nodes = len(self.nodes)
        
        return {
            "initial_nodes": initial_nodes,
            "final_nodes": final_nodes,
            "nodes_added": final_nodes - initial_nodes,
            "final_error": self.training_history[-1]["avg_error"] if self.training_history else 0,
            "training_history": self.training_history
        }
    
    def predict(self, input_vector: np.ndarray) -> int:
        """
        Find best matching unit for input vector
        
        Args:
            input_vector: Input data point
            
        Returns:
            Index of best matching node
        """
        if len(self.nodes) == 0:
            return -1
        
        winner, _ = self._find_winners(input_vector)
        return winner
    
    def get_node_positions(self) -> np.ndarray:
        """
        Get weight vectors of all nodes
        
        Returns:
            Array of shape (n_nodes, input_dim) with node weights
        """
        if len(self.nodes) == 0:
            return np.empty((0, self.input_dim))
        
        return np.array([node.weights for node in self.nodes])
    
    def get_topology_graph(self) -> Tuple[np.ndarray, List[Tuple[int, int]]]:
        """
        Get network topology as node positions and connections
        
        Returns:
            Tuple of (node_positions, connections_list)
        """
        positions = self.get_node_positions()
        connections_list = list(self.connections)
        
        return positions, connections_list
    
    def visualize_2d(self, data: Optional[np.ndarray] = None, figsize: Tuple[int, int] = (10, 8)):
        """
        Visualize Growing SOM topology for 2D data
        
        Args:
            data: Optional training data to overlay
            figsize: Figure size for matplotlib
        """
        if self.input_dim != 2:
            print("Visualization only available for 2D input data")
            return
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot training data if provided
        if data is not None:
            ax.scatter(data[:, 0], data[:, 1], alpha=0.3, c='lightblue', s=20, label='Training Data')
        
        # Plot nodes
        positions = self.get_node_positions()
        if len(positions) > 0:
            ax.scatter(positions[:, 0], positions[:, 1], 
                      c='red', s=100, marker='o', label='SOM Nodes', zorder=5)
            
            # Label nodes
            for i, pos in enumerate(positions):
                ax.annotate(f'{i}', (pos[0], pos[1]), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8)
        
        # Plot connections
        for i, j in self.connections:
            if i < len(positions) and j < len(positions):
                ax.plot([positions[i, 0], positions[j, 0]], 
                       [positions[i, 1], positions[j, 1]], 
                       'k-', alpha=0.6, linewidth=1)
        
        ax.set_title(f'Growing SOM Topology ({len(self.nodes)} nodes, {len(self.connections)} connections)')
        ax.set_xlabel('Feature 1')
        ax.set_ylabel('Feature 2')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get current network statistics
        
        Returns:
            Dictionary with network statistics
        """
        if len(self.nodes) == 0:
            return {"n_nodes": 0, "n_connections": 0, "avg_error": 0}
        
        total_error = sum(node.error for node in self.nodes)
        avg_connections_per_node = 2 * len(self.connections) / len(self.nodes) if len(self.nodes) > 0 else 0
        
        return {
            "n_nodes": len(self.nodes),
            "n_connections": len(self.connections),
            "total_error": total_error,
            "avg_error_per_node": total_error / len(self.nodes),
            "avg_connections_per_node": avg_connections_per_node,
            "max_error": max(node.error for node in self.nodes),
            "min_error": min(node.error for node in self.nodes)
        }