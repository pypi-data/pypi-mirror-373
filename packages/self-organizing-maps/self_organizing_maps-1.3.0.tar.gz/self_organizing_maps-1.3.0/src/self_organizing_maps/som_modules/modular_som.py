"""
Modular Self-Organizing Map Implementation

This is the main SOM class that integrates all the modular components:
- Core algorithm (competition, cooperation, adaptation)
- Topology and neighborhood functions 
- Parameter scheduling
- Visualization and analysis
- Metrics and utilities

Based on: Kohonen (1982) "Self-Organized Formation of Topologically Correct Feature Maps"
"""

import numpy as np
from typing import Dict, List, Tuple, Union, Optional, Any
from dataclasses import dataclass

from .core_algorithm import SOMCoreAlgorithm
from .topology_neighborhood import TopologyNeighborhoodManager
from .parameter_schedules import ParameterScheduleManager
from .visualization import SOMVisualizer
from .metrics_utils import SOMMetrics, SOMUtils


class ModularSelfOrganizingMap:
    """
    Modular Self-Organizing Map - Kohonen's Topological Learning Algorithm
    
    This is a fully modular implementation that maintains the same interface
    as the original monolithic version while providing better separation of
    concerns and extensibility.
    
    ELI5: An unsupervised learning algorithm that creates organized maps!
    Imagine you have a bunch of data points scattered around. The SOM creates
    a 2D grid where similar data points end up close together, like organizing
    a messy room by putting similar items near each other automatically.
    
    Technical Implementation:
    The SOM implements Kohonen's three-step algorithm:
    1. Competition: Find Best Matching Unit (BMU) using Euclidean distance
    2. Cooperation: Define neighborhood function around BMU
    3. Adaptation: Update BMU and neighbors using competitive learning
    
    Mathematical Foundation:
    - BMU Selection: c(x) = argmin_i ||x - w_i||
    - Neighborhood Function: h_ci(t) = α(t) × N(||r_c - r_i||, σ(t))
    - Weight Update: w_i(t+1) = w_i(t) + h_ci(t)[x(t) - w_i(t)]
    
    Where:
    - x(t): Input vector at time t
    - w_i(t): Weight vector of neuron i at time t  
    - α(t): Learning rate (decreases over time)
    - σ(t): Neighborhood radius (decreases over time)
    - N(): Neighborhood function (gaussian, mexican_hat, etc.)
    """
    
    def __init__(
        self,
        map_size: Tuple[int, int] = (20, 20),
        input_dim: int = 2,
        initial_learning_rate: float = 0.5,
        initial_radius: float = None,
        topology: str = 'rectangular',
        initialization: str = 'random',
        neighborhood_function: str = 'gaussian',
        parameter_schedule: str = 'exponential',
        schedule_parameters: Optional[Dict[str, float]] = None,
        random_seed: Optional[int] = None
    ):
        """
        Initialize Modular Self-Organizing Map
        
        Args:
            map_size: Grid dimensions (height, width)
            input_dim: Dimensionality of input data vectors
            initial_learning_rate: Starting learning rate α₀
            initial_radius: Starting neighborhood radius σ₀ (auto if None)
            topology: Grid topology ('rectangular' or 'hexagonal')
            initialization: Weight initialization ('random' or 'linear')
            neighborhood_function: Neighborhood function type
            parameter_schedule: Learning parameter decay schedule
            schedule_parameters: Additional parameters for schedules
            random_seed: Random seed for reproducibility
        """
        self.map_height, self.map_width = map_size
        self.input_dim = input_dim
        self.initial_learning_rate = initial_learning_rate
        self.topology_name = topology
        self.neighborhood_function_name = neighborhood_function
        self.parameter_schedule_name = parameter_schedule
        self.schedule_parameters = schedule_parameters or {}
        self.initialization = initialization
        
        # Set initial radius if not provided
        if initial_radius is None:
            self.initial_radius = max(self.map_height, self.map_width) / 2
        else:
            self.initial_radius = initial_radius
        
        # Set random seed if provided
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Initialize modular components
        self._initialize_components()
        
        # Training state
        self.current_iteration = 0
        self.training_history = {
            'quantization_errors': [],
            'topographic_errors': [],
            'learning_rates': [],
            'neighborhood_radii': []
        }
        
        # Print configuration summary
        self._print_initialization_summary()
    
    def _initialize_components(self):
        """Initialize all modular components"""
        # Core algorithm
        self.core_algorithm = SOMCoreAlgorithm(
            map_size=(self.map_height, self.map_width),
            input_dim=self.input_dim
        )
        
        # Initialize neurons
        self.core_algorithm.initialize_neurons(self.initialization)
        
        # Topology and neighborhood manager
        self.topology_manager = TopologyNeighborhoodManager(
            topology=self.topology_name,
            neighborhood_function=self.neighborhood_function_name
        )
        
        # Parameter schedule manager
        self.parameter_manager = ParameterScheduleManager(
            schedule_type=self.parameter_schedule_name,
            schedule_parameters=self.schedule_parameters
        )
        
        # Visualization and metrics (lazy initialization)
        self._visualizer = None
        self._metrics = None
    
    @property
    def visualizer(self) -> SOMVisualizer:
        """Lazy-loaded visualizer"""
        if self._visualizer is None:
            self._visualizer = SOMVisualizer(self.core_algorithm, self.topology_manager)
        return self._visualizer
    
    @property
    def metrics(self) -> SOMMetrics:
        """Lazy-loaded metrics calculator"""
        if self._metrics is None:
            self._metrics = SOMMetrics(self.core_algorithm, self.topology_manager)
        return self._metrics
    
    @property
    def neurons(self):
        """Access to neuron grid for backward compatibility"""
        return self.core_algorithm.neurons
    
    def train_step(self, input_vector: np.ndarray, iteration: int, total_iterations: int):
        """
        Perform one training step with a single input vector
        
        This implements Kohonen's three-step process:
        1. Competition: Find BMU
        2. Cooperation: Calculate neighborhood
        3. Adaptation: Update weights
        """
        # Get current learning parameters
        learning_rate, radius = self.parameter_manager.get_parameters(
            iteration, total_iterations, self.initial_learning_rate, self.initial_radius
        )
        
        # Perform training step using modular components
        bmu_pos = self.core_algorithm.train_step(
            input_vector,
            neighborhood_func=self.topology_manager.calculate_neighborhood_influence,
            distance_func=self.topology_manager.calculate_distance,
            learning_rate=learning_rate,
            radius=radius
        )
        
        # Store training parameters
        self.training_history['learning_rates'].append(learning_rate)
        self.training_history['neighborhood_radii'].append(radius)
        
        return bmu_pos
    
    def train(self, training_data: np.ndarray, n_iterations: int = 1000, 
              verbose: bool = True) -> Dict[str, Any]:
        """
        Train the SOM on a dataset
        
        Args:
            training_data: Input data (n_samples, input_dim)
            n_iterations: Number of training iterations
            verbose: Whether to print progress
            
        Returns:
            Training statistics
        """
        n_samples = len(training_data)
        
        if verbose:
            print(f"🎯 Training SOM for {n_iterations} iterations on {n_samples} samples...")
        
        # Training loop
        for iteration in range(n_iterations):
            # Select random input vector
            sample_idx = np.random.randint(0, n_samples)
            input_vector = training_data[sample_idx]
            
            # Perform training step
            self.train_step(input_vector, iteration, n_iterations)
            
            # Calculate and store quality metrics periodically
            if (iteration + 1) % (n_iterations // 10) == 0 or iteration == n_iterations - 1:
                qe = self.metrics.calculate_quantization_error(training_data)
                te = self.metrics.calculate_topographic_error(training_data)
                
                self.training_history['quantization_errors'].append(qe)
                self.training_history['topographic_errors'].append(te)
                
                if verbose:
                    progress = (iteration + 1) / n_iterations * 100
                    lr = self.training_history['learning_rates'][-1]
                    radius = self.training_history['neighborhood_radii'][-1]
                    print(f"   Progress: {progress:5.1f}% | QE: {qe:.4f} | TE: {te:.4f} | LR: {lr:.4f} | R: {radius:.2f}")
        
        self.current_iteration = n_iterations
        
        # Final metrics
        final_qe = self.metrics.calculate_quantization_error(training_data)
        final_te = self.metrics.calculate_topographic_error(training_data)
        
        results = {
            'final_quantization_error': final_qe,
            'final_topographic_error': final_te,
            'n_iterations': n_iterations,
            'n_samples': n_samples,
            'map_size': (self.map_height, self.map_width)
        }
        
        if verbose:
            print(f"✅ Training complete!")
            print(f"   Final quantization error: {final_qe:.4f}")
            print(f"   Final topographic error: {final_te:.4f}")
        
        return results
    
    def map_input(self, input_vector: np.ndarray) -> Tuple[int, int]:
        """Map an input vector to its BMU position on the grid"""
        return self.core_algorithm.map_input(input_vector)
    
    def get_neuron_weights(self) -> np.ndarray:
        """Get all neuron weights as a 3D array (height, width, input_dim)"""
        return self.core_algorithm.get_neuron_weights()
    
    def create_cluster_map(self, training_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create cluster assignment map and hit counts"""
        return self.visualizer.create_cluster_map(training_data)
    
    def visualize_map(self, training_data: Optional[np.ndarray] = None, 
                     figsize: Tuple[int, int] = (15, 12)):
        """Visualize the Self-Organizing Map and its properties"""
        self.visualizer.visualize_map(training_data, self.training_history, figsize)
    
    def _print_initialization_summary(self):
        """Print initialization summary"""
        print(f"✓ Modular Self-Organizing Map initialized:")
        print(f"   Map size: {self.map_height}×{self.map_width} = {self.map_height * self.map_width} neurons")
        print(f"   Input dimension: {self.input_dim}")
        print(f"   Topology: {self.topology_name}")
        print(f"   Neighborhood function: {self.neighborhood_function_name}")
        print(f"   Parameter schedule: {self.parameter_schedule_name}")
        print(f"   Initial learning rate: {self.initial_learning_rate}")
        print(f"   Initial radius: {self.initial_radius:.2f}")
        print(f"   Initialization method: {self.initialization}")
    
    # ============================================================================
    # SKLEARN-COMPATIBLE INTERFACE
    # ============================================================================
    
    def fit(self, X: np.ndarray, y=None):
        """
        Scikit-learn compatible fit method
        
        Args:
            X: Training data of shape (n_samples, n_features)
            y: Ignored (unsupervised learning)
            
        Returns:
            self: Fitted SOM instance
        """
        self.train(X, n_iterations=1000, verbose=False)
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Scikit-learn compatible predict method
        
        Returns BMU (Best Matching Unit) coordinates for each input
        
        Args:
            X: Input data of shape (n_samples, n_features)
            
        Returns:
            BMU coordinates array of shape (n_samples, 2)
        """
        if self.neurons is None:
            raise ValueError("SOM not fitted. Call fit() first.")
        
        predictions = []
        for sample in X:
            bmu_row, bmu_col = self.map_input(sample)
            predictions.append([bmu_row, bmu_col])
        
        return np.array(predictions)
    
    def fit_predict(self, X: np.ndarray, y=None) -> np.ndarray:
        """
        Scikit-learn compatible fit_predict method
        
        Args:
            X: Training data of shape (n_samples, n_features)
            y: Ignored (unsupervised learning)
            
        Returns:
            BMU coordinates array of shape (n_samples, 2)
        """
        return self.fit(X, y).predict(X)
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform input data to SOM space (BMU coordinates)
        
        Args:
            X: Input data of shape (n_samples, n_features)
            
        Returns:
            Transformed data (BMU coordinates) of shape (n_samples, 2)
        """
        return self.predict(X)
    
    # ============================================================================
    # ADDITIONAL MODULAR FUNCTIONALITY
    # ============================================================================
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get complete SOM configuration"""
        return {
            'map_size': (self.map_height, self.map_width),
            'input_dim': self.input_dim,
            'initial_learning_rate': self.initial_learning_rate,
            'initial_radius': self.initial_radius,
            'topology': self.topology_manager.get_configuration(),
            'parameter_schedule': self.parameter_manager.get_configuration(),
            'initialization': self.initialization
        }
    
    def calculate_comprehensive_metrics(self, data: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive quality metrics"""
        return {
            'quantization_error': self.metrics.calculate_quantization_error(data),
            'topographic_error': self.metrics.calculate_topographic_error(data),
            'neighborhood_preservation': self.metrics.calculate_neighborhood_preservation(data),
            'trustworthiness': self.metrics.calculate_trustworthiness(data),
            **self.metrics.calculate_map_resolution()
        }
    
    def visualize_neighborhood_function(self, center_pos: Tuple[int, int], 
                                      radius: float, figsize: Tuple[int, int] = (8, 6)):
        """Visualize neighborhood function around a specific position"""
        self.visualizer.plot_neighborhood_visualization(center_pos, radius, figsize)
    
    @staticmethod
    def suggest_parameters(data: np.ndarray) -> Dict[str, Any]:
        """Suggest SOM parameters based on data characteristics"""
        n_samples, n_features = data.shape
        
        # Suggest map size
        map_size = SOMUtils.suggest_map_size(n_samples, 'vesanto')
        
        # Suggest training iterations
        n_iterations = SOMUtils.estimate_training_iterations(map_size, n_samples)
        
        # Calculate data statistics
        data_stats = SOMUtils.calculate_data_statistics(data)
        
        return {
            'suggested_map_size': map_size,
            'suggested_iterations': n_iterations,
            'data_statistics': data_stats,
            'normalization_recommended': np.any(data_stats['data_range'] > 10) or 
                                        np.any(data_stats['data_range'] < 0.1)
        }


# For backward compatibility, create an alias
SelfOrganizingMap = ModularSelfOrganizingMap