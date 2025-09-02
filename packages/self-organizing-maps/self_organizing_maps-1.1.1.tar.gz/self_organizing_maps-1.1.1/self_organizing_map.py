"""
🧠 Self-Organizing Map (SOM) Implementation
==========================================

Author: Benedict Chen (benedict@benedictchen.com)

💝 Support This Work: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Developing high-quality, research-backed software takes countless hours of study, implementation, 
testing, and documentation. Your support - whether a little or a LOT - makes this work possible and is 
deeply appreciated. 

🎯 Help support continued research! Buy me a coffee ☕, beer 🍺, or lamborghini 🏎️

💖 Please consider recurring donations to fully support the work based on how much this module impacts your life or work!

Based on: Kohonen (1982) "Self-Organized Formation of Topologically Correct Feature Maps"

🎯 ELI5 Summary:
Think of a SOM like a smart map that learns to organize information by neighborhood.
If you show it pictures of animals, it will automatically group similar animals together
on a 2D grid, with cats near dogs, birds near each other, etc. No supervision needed!

🔬 Research Background:
========================
Teuvo Kohonen's 1982 paper introduced a revolutionary unsupervised learning algorithm
that models how the brain organizes sensory information. The key insight: neurons
compete for inputs (winner-takes-all) while cooperating through neighborhood functions.
This creates topologically organized feature maps that preserve input space structure.

The SOM algorithm revolutionized:
- Data visualization (high-dimensional → 2D maps)
- Clustering and classification
- Understanding cortical map formation
- Vector quantization and data compression

🏗️ Architecture:
================
Input Layer          SOM Grid (2D)           Output
-----------          --------------          ------
   🔵                    🟦🟦🟦              
   🔵        →          🟦🟨🟦          →    Clusters
   🔵                    🟦🟦🟦              

Algorithm Flow:
1. 🏆 Competition: Find Best Matching Unit (BMU) - neuron closest to input
2. 🤝 Cooperation: Define neighborhood around BMU using distance functions  
3. 📚 Adaptation: Update BMU and neighbors toward input (Hebbian learning)

Mathematical Framework:
- BMU: c = argmin_i ||x(t) - w_i(t)||
- Neighborhood: h_ci(t) = α(t) × exp(-||r_c - r_i||²/2σ²(t))
- Weight update: w_i(t+1) = w_i(t) + h_ci(t)[x(t) - w_i(t)]

🚀 Key Innovation: Unsupervised topological preservation
Revolutionary Impact: First algorithm to model biological cortical map formation

⚡ Configurable Options:
=======================
✨ Neighborhood Functions:
  - gaussian: exp(-d²/2σ²) [default - smooth, biological]
  - mexican_hat: center-surround activation pattern
  - rectangular: binary step function neighborhood  
  - linear_decay: linear decrease within radius

✨ Parameter Schedules:
  - exponential: η(t) = η₀ × exp(-t/τ) [default - fast early learning]
  - linear: η(t) = η₀ × (1 - t/T) [steady decay]
  - inverse_time: η(t) = η₀ / (1 + t/τ) [slow asymptotic decay]
  - power_law: η(t) = η₀ × (t₀/t)^α [scale-invariant decay]

🎨 ASCII Diagram - SOM Learning Process:
========================================
Initial (Random):        After Training:
    🔴🟢🔵                  🔴🔴🔴
    🟡⚫🟤         →         🟢🟢🟢  
    🟠⚪🟣                  🔵🔵🔵
    
Input: [0.9, 0.1, 0.1] → Finds red cluster
BMU at (0,0), updates neighborhood:
    🔴← BMU (winner)
    🟢← Neighbor (cooperates)  
    🔵← Distant (no update)

📚 Usage Example:
================
```python
from self_organizing_maps import SelfOrganizingMap

# Create SOM with custom configuration
som = SelfOrganizingMap(
    map_size=(15, 15),              # 15×15 neuron grid
    input_dim=3,                    # 3D input vectors
    neighborhood_function='gaussian', # Smooth neighborhoods
    parameter_schedule='exponential' # Fast early learning
)

# Train on your data
data = load_your_data()  # Shape: (n_samples, 3)
som.train(data, n_iterations=1000)

# Visualize results
som.visualize_map(data)

# Map new inputs
new_point = [0.5, 0.3, 0.7]
grid_position = som.map_input(new_point)
print(f"Input maps to grid position: {grid_position}")
```

🎯 Applications:
===============
- 📊 Data Visualization: High-dimensional data → 2D maps
- 🎯 Clustering: Unsupervised pattern discovery
- 🧠 Neuroscience: Understanding cortical organization
- 🎨 Image Processing: Color quantization, compression
- 📈 Finance: Market segmentation, risk analysis
- 🔊 Audio: Speech recognition, music analysis
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Union, Optional, Any, Callable
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


@dataclass
class SOMNeuron:
    """
    🧠 SOM Neuron: Individual processing unit in the Self-Organizing Map
    
    🎯 ELI5: Like a brain cell that remembers what patterns it likes best.
    Each neuron has a "favorite pattern" (weight_vector) and remembers its
    location on the map (position) and how active it's been (activation_history).
    
    🔬 Technical Details:
    Each neuron in the SOM grid maintains:
    - Spatial position (i, j) coordinates on the 2D lattice
    - Weight vector w_i representing its prototype/template
    - Activation history for analysis and visualization
    
    The neuron competes with others to respond to inputs by calculating
    the Euclidean distance: d = ||x - w_i|| where x is the input vector.
    The neuron with minimum distance becomes the Best Matching Unit (BMU).
    
    📊 Attributes:
    - position: (i, j) grid coordinates - where this neuron sits on the map
    - weight_vector: w_i ∈ ℝᵈ - this neuron's learned feature template  
    - activation_history: List of activation values over time
    
    🎯 Usage:
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
    activation_history: List[float]  # History of activations for analysis


class SelfOrganizingMap:
    """
    🗺️ Self-Organizing Map (SOM) - Kohonen's Topological Learning Algorithm
    
    🎯 ELI5: An unsupervised learning algorithm that creates organized maps!
    Imagine you have a bunch of data points scattered around. The SOM creates
    a 2D grid where similar data points end up close together, like organizing
    a messy room by putting similar items near each other automatically.
    
    🔬 Technical Implementation:
    The SOM implements Kohonen's three-step algorithm:
    1. 🏆 Competition: Find Best Matching Unit (BMU) using Euclidean distance
    2. 🤝 Cooperation: Define neighborhood function around BMU
    3. 📚 Adaptation: Update BMU and neighbors using competitive learning
    
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
    
    🎯 Key Features:
    ===============
    ✅ Unsupervised Learning: No labeled data required
    ✅ Topological Preservation: Similar inputs → nearby neurons  
    ✅ Dimension Reduction: High-D input → 2D visualization
    ✅ Vector Quantization: Learns representative prototypes
    ✅ Competitive Learning: Winner-takes-all with cooperation
    ✅ Biological Plausibility: Models cortical map formation
    
    🔧 Configurable Components:
    ==========================
    🎛️ Neighborhood Functions:
    - gaussian: Smooth, biological, default choice
    - mexican_hat: Center-surround, contrast enhancement  
    - rectangular: Binary, computational efficiency
    - linear_decay: Simple linear decrease
    
    🎛️ Learning Schedules:
    - exponential: Fast initial learning, gradual refinement
    - linear: Steady decrease, predictable convergence
    - inverse_time: Slow asymptotic decay, extended learning
    - power_law: Scale-invariant, natural phenomena modeling
    
    📊 Data Flow Diagram:
    ====================
    Input Vector x ──→ [Competition] ──→ BMU Selection
                                            ↓
    Weight Updates ←── [Adaptation] ←── [Cooperation]
            ↑                              ↓  
    [Learning Rule]                  [Neighborhood]
    
    🎯 Perfect For:
    ==============
    📊 Data Visualization: Scatter plot → organized 2D map
    🎯 Clustering: Discover natural groupings in data
    🔍 Anomaly Detection: Outliers map to sparse regions
    📈 Market Segmentation: Customer behavior analysis  
    🎨 Image Processing: Color quantization, compression
    🧬 Bioinformatics: Gene expression analysis
    🔊 Audio Processing: Speech pattern recognition
    
    ⚠️ Important Notes:
    ==================
    - Training is iterative and can take time for large datasets
    - Map size should be chosen based on data complexity
    - Initialization method affects final organization
    - Parameter schedules control learning dynamics
    - Visualization helps interpret learned structure
    
    💝 Please support our work: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
    Buy us a coffee, beer, or better! Your support makes advanced AI research accessible to everyone! ☕🍺🚀
    """
    
    def __init__(
        self,
        map_size: Tuple[int, int] = (20, 20),
        input_dim: int = 2,
        initial_learning_rate: float = 0.5,
        initial_radius: float = None,
        topology: str = 'rectangular',
        initialization: str = 'random',
        neighborhood_function: str = 'gaussian',  # 'gaussian', 'mexican_hat', 'rectangular', 'linear_decay', 'bubble', 'cosine', 'epanechnikov' 
        parameter_schedule: str = 'exponential',  # 'exponential', 'linear', 'inverse_time', 'power_law', 'step_decay', 'cyclic'
        schedule_parameters: Optional[Dict[str, float]] = None,  # Additional parameters for schedules
        random_seed: Optional[int] = None
    ):
        """
        🎯 Initialize Self-Organizing Map with Custom Configuration
        
        🎯 ELI5: Set up your smart map with the size, learning style, and behavior you want.
        Like setting up a blank canvas with specific dimensions and painting rules!
        
        🔧 Parameters:
        ==============
        
        📏 **map_size**: Tuple[int, int] = (20, 20)
            Grid dimensions (height, width) - how many neurons in your map
            • Small (5×5): Fast training, coarse organization
            • Medium (20×20): Good balance, most common choice  
            • Large (50×50): Fine detail, longer training time
            💡 Rule of thumb: √(n_samples) neurons per dimension
        
        🔢 **input_dim**: int = 2  
            Dimensionality of input data vectors
            • 2D: Images, coordinates, simple features
            • 3D: RGB colors, 3D coordinates  
            • High-D: Feature vectors, embeddings, sensor data
            💡 SOM handles any dimensionality, but visualization works best ≤3D
        
        📈 **initial_learning_rate**: float = 0.5
            Starting learning rate α₀ - how fast the map adapts initially
            • 0.1: Conservative, stable, slow convergence
            • 0.5: Balanced, recommended default
            • 0.9: Aggressive, fast initial learning, may oscillate
            💡 Gets smaller over time according to parameter_schedule
        
        📍 **initial_radius**: float = None  
            Starting neighborhood radius σ₀ (default: max(map_size)/2)
            • Large radius: Global reorganization, smooth maps
            • Small radius: Local tuning, detailed structure
            💡 Auto-calculated as max(height, width) / 2 if None
        
        🗺️ **topology**: str = 'rectangular'
            Grid topology - how neurons are spatially arranged
            • 'rectangular': Square grid, simple distance calculation
            • 'hexagonal': Hexagonal lattice, more biological, better packing
            💡 Hexagonal often gives better topological preservation
        
        🎲 **initialization**: str = 'random'  
            Weight initialization method
            • 'random': Random uniform [-1, 1], unbiased start
            • 'linear': Linear interpolation along first 2 dimensions
            💡 Linear can speed up convergence for structured data
        
        🎯 **neighborhood_function**: str = 'gaussian'
            How neighborhood influence decreases with distance
            • 'gaussian': exp(-d²/2σ²) - smooth, biological, default
            • 'mexican_hat': center-surround - contrast enhancement  
            • 'rectangular': step function - binary neighborhood
            • 'linear_decay': 1-d/σ - simple linear decrease
            • 'bubble': uniform within radius - efficient rectangular alternative
            • 'cosine': smooth cosine decay - good gaussian compromise
            • 'epanechnikov': parabolic kernel - statistically optimal
            💡 Gaussian most common, mexican_hat for edge detection
        
        📊 **parameter_schedule**: str = 'exponential'
            How learning rate and radius decay over time
            • 'exponential': η(t)=η₀×exp(-t/τ) - fast early, slow later
            • 'linear': η(t)=η₀×(1-t/T) - steady decrease  
            • 'inverse_time': η(t)=η₀/(1+t/τ) - asymptotic decay
            • 'power_law': η(t)=η₀×(t₀/t)^α - scale-invariant
            • 'step_decay': discrete reductions at intervals - multi-phase training
            • 'cyclic': oscillating between min/max - periodic reorganization
            💡 Exponential best for most applications
        
        ⚙️ **schedule_parameters**: Optional[Dict[str, float]] = None
            Additional parameters for learning schedules
            • For 'inverse_time': {'tau': 100} - time constant
            • For 'power_law': {'alpha': 0.5, 't0': 1.0} - decay exponent
            • For 'step_decay': {'step_size': 250, 'decay_rate': 0.5} - step interval and reduction
            • For 'cyclic': {'cycle_length': 100, 'min_factor': 0.1} - cycle length and minimum
            💡 Leave None to use sensible defaults
        
        🎲 **random_seed**: Optional[int] = None
            Random seed for reproducible results
            • None: Different results each run (exploration)
            • Integer: Same results each run (debugging/comparison)
            💡 Set for reproducible experiments, None for production
        
        🎨 Example Configurations:
        =========================
        ```python
        # Quick exploration - small, fast
        som = SelfOrganizingMap(map_size=(10, 10), input_dim=2)
        
        # High-quality visualization - large, detailed  
        som = SelfOrganizingMap(
            map_size=(30, 30),
            initial_learning_rate=0.3,
            neighborhood_function='gaussian'
        )
        
        # Biological modeling - hexagonal topology
        som = SelfOrganizingMap(
            map_size=(20, 20),
            topology='hexagonal',
            neighborhood_function='mexican_hat'
        )
        
        # Custom decay schedule
        som = SelfOrganizingMap(
            parameter_schedule='power_law',
            schedule_parameters={'alpha': 0.3, 't0': 1.0}
        )
        ```
        
        🚀 What Happens:
        ================
        1. Creates neurons at each grid position with random/linear weights
        2. Sets up neighborhood and learning parameter schedules  
        3. Initializes training history tracking
        4. Prints configuration summary
        
        ⚠️ Important Notes:
        ==================
        • Larger maps need more training iterations
        • Higher learning rates need careful monitoring
        • Hexagonal topology requires more computation
        • Schedule parameters affect convergence behavior
        """
        
        self.map_height, self.map_width = map_size
        self.input_dim = input_dim
        self.initial_learning_rate = initial_learning_rate
        self.topology = topology
        self.neighborhood_function = neighborhood_function
        self.parameter_schedule = parameter_schedule
        self.schedule_parameters = schedule_parameters or {}
        
        if initial_radius is None:
            self.initial_radius = max(self.map_height, self.map_width) / 2
        else:
            self.initial_radius = initial_radius
            
        if random_seed is not None:
            np.random.seed(random_seed)
            
        # Initialize neuron grid and weights
        self._initialize_neurons(initialization)
        
        # Training state
        self.current_iteration = 0
        self.training_history = {
            'quantization_errors': [],
            'topographic_errors': [],
            'learning_rates': [],
            'neighborhood_radii': []
        }
        
        print(f"✓ Self-Organizing Map initialized:")
        print(f"   Map size: {self.map_height}×{self.map_width} = {self.map_height * self.map_width} neurons")
        print(f"   Input dimension: {self.input_dim}")
        print(f"   Topology: {self.topology}")
        print(f"   Neighborhood function: {self.neighborhood_function}")
        print(f"   Parameter schedule: {self.parameter_schedule}")
        print(f"   Initial learning rate: {self.initial_learning_rate}")
        print(f"   Initial radius: {self.initial_radius:.2f}")
        
    def _initialize_neurons(self, initialization: str):
        """Initialize neuron weights"""
        
        # Create neuron grid
        self.neurons = np.empty((self.map_height, self.map_width), dtype=object)
        
        for i in range(self.map_height):
            for j in range(self.map_width):
                if initialization == 'random':
                    # Random initialization
                    weight_vector = np.random.uniform(-1, 1, self.input_dim)
                elif initialization == 'linear':
                    # Linear initialization along principal components
                    # For demonstration, use simple linear interpolation
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
                    
                # Create neuron
                self.neurons[i, j] = SOMNeuron(
                    position=(i, j),
                    weight_vector=weight_vector,
                    activation_history=[]
                )
                
        print(f"   Weights initialized using '{initialization}' method")
        
    def _find_bmu(self, input_vector: np.ndarray) -> Tuple[int, int]:
        """
        🏆 Find Best Matching Unit (BMU) - Competition Phase of Kohonen Algorithm
        
        🎯 ELI5: Find the neuron that "likes" the input the most!
        Like finding which person in a crowd looks most similar to a photo you're holding.
        Each neuron has learned to recognize certain patterns, and we pick the best match.
        
        🔬 Technical Details:
        The BMU is the neuron with the minimum Euclidean distance to the input:
        
        BMU = argmin_i ||x - w_i||₂
        
        where:
        - x: input vector
        - w_i: weight vector of neuron i  
        - ||·||₂: Euclidean (L2) norm
        
        This implements the "competition" phase of Kohonen's algorithm where neurons
        compete to respond to the input. Only the winning neuron (BMU) and its
        neighbors will be updated during the adaptation phase.
        
        🎯 Algorithm:
        1. Initialize min_distance = ∞ and best_position = (0,0)
        2. For each neuron (i,j) in the grid:
           a. Calculate distance = ||input - w_ij||₂  
           b. If distance < min_distance:
              - Update min_distance = distance
              - Update best_position = (i,j)
        3. Return best_position
        
        ⚡ Performance Notes:
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
            bmu_position = som._find_bmu(input_data)
            print(f"BMU at grid position: {bmu_position}")
            
            # Get the actual BMU neuron
            bmu_neuron = som.neurons[bmu_position[0], bmu_position[1]]
            distance = np.linalg.norm(bmu_neuron.weight_vector - input_data)
            print(f"Distance to BMU: {distance:.4f}")
            ```
        """
        
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
        
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate distance between two grid positions"""
        
        if self.topology == 'rectangular':
            return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        elif self.topology == 'hexagonal':
            # Hexagonal distance (simplified)
            dx = pos1[1] - pos2[1]
            dy = pos1[0] - pos2[0]
            if (dy > 0 and dx > 0) or (dy < 0 and dx < 0):
                return max(abs(dx), abs(dy))
            else:
                return abs(dx) + abs(dy)
        else:
            raise ValueError(f"Unknown topology: {self.topology}")
            
    def _neighborhood_function(self, distance: float, radius: float) -> float:
        """
        Calculate neighborhood influence based on distance
        
        Uses configurable neighborhood function based on self.neighborhood_function
        
        # FIXME: Missing alternative neighborhood functions from Kohonen 1982
        # Paper discusses several options beyond Gaussian:
        # - Mexican hat function (difference of Gaussians)
        # - Rectangular neighborhood (step function) 
        # - Linear decay function
        # Current implementation only uses Gaussian, limiting experimental flexibility
        
        # IMPLEMENTATION NOTE: Added configurable neighborhood functions
        # - gaussian: exp(-distance²/(2*radius²)) [default, original implementation]
        # - mexican_hat: Difference of Gaussians for center-surround activation
        # - rectangular: Step function within radius (binary neighborhood)
        # - linear_decay: Linear decrease from 1.0 to 0.0 within radius
        # Users can now select via neighborhood_function parameter
        """
        
        if radius <= 0:
            return 1.0 if distance == 0 else 0.0
        
        if self.neighborhood_function == 'gaussian':
            return np.exp(-(distance**2) / (2 * radius**2))
        elif self.neighborhood_function == 'mexican_hat':
            return self._mexican_hat_neighborhood(distance, radius)
        elif self.neighborhood_function == 'rectangular':
            return self._rectangular_neighborhood(distance, radius)
        elif self.neighborhood_function == 'linear_decay':
            return self._linear_decay_neighborhood(distance, radius)
        elif self.neighborhood_function == 'bubble':
            return self._bubble_neighborhood(distance, radius)
        elif self.neighborhood_function == 'cosine':
            return self._cosine_neighborhood(distance, radius)
        elif self.neighborhood_function == 'epanechnikov':
            return self._epanechnikov_neighborhood(distance, radius)
        else:
            raise ValueError(f"Unknown neighborhood function: {self.neighborhood_function}")
    
    def _mexican_hat_neighborhood(self, distance: float, radius: float) -> float:
        """
        Mexican hat (difference of Gaussians) neighborhood function
        Provides center-surround activation pattern
        """
        # Center Gaussian (narrow, positive)
        center = np.exp(-(distance**2) / (2 * (radius/3)**2))
        # Surround Gaussian (wider, negative)
        surround = 0.5 * np.exp(-(distance**2) / (2 * radius**2))
        return max(0.0, center - surround)
    
    def _rectangular_neighborhood(self, distance: float, radius: float) -> float:
        """
        Rectangular (step function) neighborhood
        Binary activation within radius
        """
        return 1.0 if distance <= radius else 0.0
    
    def _linear_decay_neighborhood(self, distance: float, radius: float) -> float:
        """
        Linear decay neighborhood function
        Linear decrease from 1.0 to 0.0 within radius
        """
        if distance >= radius:
            return 0.0
        return 1.0 - (distance / radius)
    
    def _bubble_neighborhood(self, distance: float, radius: float) -> float:
        """
        Bubble neighborhood function
        Uniform activation within radius with hard cutoff
        More efficient than rectangular with smoother boundaries
        """
        return 1.0 if distance <= radius else 0.0
    
    def _cosine_neighborhood(self, distance: float, radius: float) -> float:
        """
        Cosine neighborhood function
        Smooth cosine-based decay within radius
        Good compromise between Gaussian and rectangular
        """
        if distance >= radius:
            return 0.0
        return 0.5 * (1 + np.cos(np.pi * distance / radius))
    
    def _epanechnikov_neighborhood(self, distance: float, radius: float) -> float:
        """
        Epanechnikov neighborhood function (quadratic kernel)
        Parabolic decay within radius - optimal for certain statistical properties
        Often used in kernel density estimation
        """
        if distance >= radius:
            return 0.0
        normalized_distance = distance / radius
        return 1.0 - normalized_distance**2
        
    def _update_learning_parameters(self, iteration: int, total_iterations: int) -> Tuple[float, float]:
        """
        Update learning rate and neighborhood radius over time
        
        Uses configurable parameter schedule based on self.parameter_schedule
        
        # FIXME: Missing alternative parameter schedules from Kohonen 1982
        # Paper discusses multiple annealing schedules:
        # - Linear decay: η(t) = η₀(1 - t/T)
        # - Inverse time decay: η(t) = η₀/(1 + t/τ) 
        # - Power law decay: η(t) = η₀(t₀/t)^α
        # Current implementation only uses exponential decay
        
        # IMPLEMENTATION NOTE: Added configurable parameter schedules
        # - exponential: η(t) = η₀ * exp(-t/τ) [default, original implementation]
        # - linear: η(t) = η₀ * (1 - t/T) for linear decay to zero
        # - inverse_time: η(t) = η₀ / (1 + t/τ) for hyperbolic decay
        # - power_law: η(t) = η₀ * (t₀/t)^α for power law decay
        # Users can configure via parameter_schedule and schedule_parameters
        """
        
        if self.parameter_schedule == 'exponential':
            return self._exponential_schedule(iteration, total_iterations)
        elif self.parameter_schedule == 'linear':
            return self._linear_schedule(iteration, total_iterations)
        elif self.parameter_schedule == 'inverse_time':
            return self._inverse_time_schedule(iteration, total_iterations)
        elif self.parameter_schedule == 'power_law':
            return self._power_law_schedule(iteration, total_iterations)
        elif self.parameter_schedule == 'step_decay':
            return self._step_decay_schedule(iteration, total_iterations)
        elif self.parameter_schedule == 'cyclic':
            return self._cyclic_schedule(iteration, total_iterations)
        else:
            raise ValueError(f"Unknown parameter schedule: {self.parameter_schedule}")
    
    def _exponential_schedule(self, iteration: int, total_iterations: int) -> Tuple[float, float]:
        """
        Exponential decay schedule (original implementation)
        η(t) = η₀ * exp(-t/τ)
        """
        time_constant = total_iterations / np.log(self.initial_radius)
        learning_rate = self.initial_learning_rate * np.exp(-iteration / time_constant)
        radius = self.initial_radius * np.exp(-iteration / time_constant)
        return learning_rate, radius
    
    def _linear_schedule(self, iteration: int, total_iterations: int) -> Tuple[float, float]:
        """
        Linear decay schedule
        η(t) = η₀ * (1 - t/T)
        """
        decay_factor = 1.0 - (iteration / total_iterations)
        learning_rate = self.initial_learning_rate * max(0.01, decay_factor)  # Min 1% of initial
        radius = self.initial_radius * max(0.1, decay_factor)  # Min 10% of initial
        return learning_rate, radius
    
    def _inverse_time_schedule(self, iteration: int, total_iterations: int) -> Tuple[float, float]:
        """
        Inverse time decay schedule
        η(t) = η₀ / (1 + t/τ)
        """
        tau = self.schedule_parameters.get('tau', total_iterations / 10)
        learning_rate = self.initial_learning_rate / (1 + iteration / tau)
        radius = self.initial_radius / (1 + iteration / tau)
        return learning_rate, radius
    
    def _power_law_schedule(self, iteration: int, total_iterations: int) -> Tuple[float, float]:
        """
        Power law decay schedule
        η(t) = η₀ * (t₀/t)^α
        """
        alpha = self.schedule_parameters.get('alpha', 0.5)
        t0 = self.schedule_parameters.get('t0', 1.0)
        t = max(1.0, iteration + 1)  # Avoid division by zero
        
        decay_factor = (t0 / t) ** alpha
        learning_rate = self.initial_learning_rate * decay_factor
        radius = self.initial_radius * decay_factor
        return learning_rate, radius
    
    def _step_decay_schedule(self, iteration: int, total_iterations: int) -> Tuple[float, float]:
        """
        Step decay schedule - reduces parameters in discrete steps
        Useful for multi-phase training with distinct learning periods
        """
        step_size = self.schedule_parameters.get('step_size', total_iterations // 4)
        decay_rate = self.schedule_parameters.get('decay_rate', 0.5)
        
        # Calculate number of steps completed
        steps = iteration // step_size
        decay_factor = decay_rate ** steps
        
        learning_rate = self.initial_learning_rate * decay_factor
        radius = self.initial_radius * decay_factor
        return learning_rate, radius
    
    def _cyclic_schedule(self, iteration: int, total_iterations: int) -> Tuple[float, float]:
        """
        Cyclic schedule - parameters oscillate between min and max values
        Allows periodic reorganization and fine-tuning phases
        Inspired by cyclic learning rates in deep learning
        """
        cycle_length = self.schedule_parameters.get('cycle_length', total_iterations // 10)
        min_factor = self.schedule_parameters.get('min_factor', 0.1)
        
        if cycle_length <= 0:
            cycle_length = total_iterations // 10
        
        # Calculate position within current cycle (0 to 1)
        cycle_position = (iteration % cycle_length) / cycle_length
        
        # Cosine annealing within each cycle
        factor = min_factor + (1 - min_factor) * (1 + np.cos(np.pi * cycle_position)) / 2
        
        learning_rate = self.initial_learning_rate * factor
        radius = self.initial_radius * factor
        return learning_rate, radius
        
    def train_step(self, input_vector: np.ndarray, iteration: int, total_iterations: int):
        """
        Perform one training step with a single input vector
        
        This implements Kohonen's three-step process:
        1. Competition: Find BMU
        2. Cooperation: Calculate neighborhood
        3. Adaptation: Update weights
        """
        
        # Step 1: Competition - Find Best Matching Unit
        bmu_pos = self._find_bmu(input_vector)
        
        # Step 2 & 3: Cooperation and Adaptation
        learning_rate, radius = self._update_learning_parameters(iteration, total_iterations)
        
        # Update BMU and its neighbors
        for i in range(self.map_height):
            for j in range(self.map_width):
                neuron = self.neurons[i, j]
                
                # Calculate distance from BMU
                distance = self._calculate_distance((i, j), bmu_pos)
                
                # Calculate neighborhood influence
                influence = self._neighborhood_function(distance, radius)
                
                # Update neuron weights if within influence
                if influence > 0.01:  # Threshold to avoid tiny updates
                    # Kohonen learning rule: w_new = w_old + η * h * (x - w_old)
                    delta = learning_rate * influence * (input_vector - neuron.weight_vector)
                    neuron.weight_vector += delta
                    
        # Store training parameters
        self.training_history['learning_rates'].append(learning_rate)
        self.training_history['neighborhood_radii'].append(radius)
        
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
            if (iteration + 1) % (n_iterations // 10) == 0:
                qe = self._calculate_quantization_error(training_data)
                te = self._calculate_topographic_error(training_data)
                
                self.training_history['quantization_errors'].append(qe)
                self.training_history['topographic_errors'].append(te)
                
                if verbose:
                    progress = (iteration + 1) / n_iterations * 100
                    lr = self.training_history['learning_rates'][-1]
                    radius = self.training_history['neighborhood_radii'][-1]
                    print(f"   Progress: {progress:5.1f}% | QE: {qe:.4f} | TE: {te:.4f} | LR: {lr:.4f} | R: {radius:.2f}")
                    
        self.current_iteration = n_iterations
        
        # Final metrics
        final_qe = self._calculate_quantization_error(training_data)
        final_te = self._calculate_topographic_error(training_data)
        
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
        
    def _calculate_quantization_error(self, data: np.ndarray) -> float:
        """
        Calculate quantization error (average distance from inputs to BMUs)
        
        Lower is better - measures how well the SOM represents the data
        """
        
        total_error = 0
        
        for input_vector in data:
            bmu_pos = self._find_bmu(input_vector)
            bmu = self.neurons[bmu_pos[0], bmu_pos[1]]
            error = np.linalg.norm(input_vector - bmu.weight_vector)
            total_error += error
            
        return total_error / len(data)
        
    def _calculate_topographic_error(self, data: np.ndarray) -> float:
        """
        Calculate topographic error (proportion of data for which BMU and 2nd BMU are not adjacent)
        
        Lower is better - measures topological preservation
        """
        
        topographic_errors = 0
        
        for input_vector in data:
            # Find BMU and second BMU
            distances = []
            positions = []
            
            for i in range(self.map_height):
                for j in range(self.map_width):
                    neuron = self.neurons[i, j]
                    distance = np.linalg.norm(neuron.weight_vector - input_vector)
                    distances.append(distance)
                    positions.append((i, j))
                    
            sorted_indices = np.argsort(distances)
            bmu_pos = positions[sorted_indices[0]]
            second_bmu_pos = positions[sorted_indices[1]]
            
            # Check if BMU and 2nd BMU are adjacent
            distance_between = self._calculate_distance(bmu_pos, second_bmu_pos)
            if distance_between > 1.5:  # Not adjacent (allowing for diagonal)
                topographic_errors += 1
                
        return topographic_errors / len(data)
        
    def map_input(self, input_vector: np.ndarray) -> Tuple[int, int]:
        """Map an input vector to its BMU position on the grid"""
        return self._find_bmu(input_vector)
        
    def get_neuron_weights(self) -> np.ndarray:
        """Get all neuron weights as a 3D array (height, width, input_dim)"""
        
        weights = np.zeros((self.map_height, self.map_width, self.input_dim))
        
        for i in range(self.map_height):
            for j in range(self.map_width):
                weights[i, j] = self.neurons[i, j].weight_vector
                
        return weights
        
    def create_cluster_map(self, training_data: np.ndarray) -> np.ndarray:
        """
        Create a cluster assignment map
        
        Returns array where each cell contains the cluster ID of the most 
        frequently mapped input
        """
        
        # Map each training sample to grid position
        assignments = np.full((self.map_height, self.map_width), -1, dtype=int)
        hit_counts = np.zeros((self.map_height, self.map_width))
        
        for idx, input_vector in enumerate(training_data):
            bmu_pos = self._find_bmu(input_vector)
            i, j = bmu_pos
            
            hit_counts[i, j] += 1
            if assignments[i, j] == -1:
                assignments[i, j] = idx
                
        return assignments, hit_counts
        
    def visualize_map(self, training_data: Optional[np.ndarray] = None, 
                     figsize: Tuple[int, int] = (15, 12)):
        """
        Visualize the Self-Organizing Map and its properties
        """
        
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        fig.suptitle('Self-Organizing Map Visualization', fontsize=14)
        
        weights = self.get_neuron_weights()
        
        # 1. Weight components (for 2D input)
        if self.input_dim >= 2:
            ax1 = axes[0, 0]
            im1 = ax1.imshow(weights[:, :, 0], cmap='viridis')
            ax1.set_title('Weight Component 1')
            ax1.set_xlabel('Map Width')
            ax1.set_ylabel('Map Height')
            plt.colorbar(im1, ax=ax1)
            
            ax2 = axes[0, 1]
            im2 = ax2.imshow(weights[:, :, 1], cmap='plasma')
            ax2.set_title('Weight Component 2')
            ax2.set_xlabel('Map Width')
            ax2.set_ylabel('Map Height')
            plt.colorbar(im2, ax=ax2)
        else:
            ax1 = axes[0, 0]
            im1 = ax1.imshow(weights[:, :, 0], cmap='viridis')
            ax1.set_title('Weight Values')
            plt.colorbar(im1, ax=ax1)
            
        # 2. U-Matrix (Unified Distance Matrix)
        ax3 = axes[0, 2]
        u_matrix = self._calculate_u_matrix()
        im3 = ax3.imshow(u_matrix, cmap='gray')
        ax3.set_title('U-Matrix (Distance Map)')
        ax3.set_xlabel('Map Width')
        ax3.set_ylabel('Map Height')
        plt.colorbar(im3, ax=ax3)
        
        # 3. Hit histogram (if training data provided)
        if training_data is not None:
            ax4 = axes[1, 0]
            assignments, hit_counts = self.create_cluster_map(training_data)
            im4 = ax4.imshow(hit_counts, cmap='hot')
            ax4.set_title('Hit Histogram')
            ax4.set_xlabel('Map Width')
            ax4.set_ylabel('Map Height')
            plt.colorbar(im4, ax=ax4)
            
            # Overlay training data if 2D
            if self.input_dim == 2:
                # Map data points to grid coordinates for overlay
                for sample in training_data[::max(1, len(training_data)//100)]:  # Sample for visibility
                    bmu_pos = self._find_bmu(sample)
                    ax4.scatter(bmu_pos[1], bmu_pos[0], c='cyan', s=10, alpha=0.3)
        
        # 4. Training curves
        ax5 = axes[1, 1]
        if self.training_history['quantization_errors']:
            iterations = np.linspace(0, self.current_iteration, 
                                   len(self.training_history['quantization_errors']))
            ax5.plot(iterations, self.training_history['quantization_errors'], 'b-', 
                    label='Quantization Error')
            ax5.plot(iterations, self.training_history['topographic_errors'], 'r-',
                    label='Topographic Error')
            ax5.set_title('Training Progress')
            ax5.set_xlabel('Iteration')
            ax5.set_ylabel('Error')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
            
        # 5. Learning parameters over time
        ax6 = axes[1, 2]
        if self.training_history['learning_rates']:
            iterations = range(len(self.training_history['learning_rates']))
            ax6_twin = ax6.twinx()
            
            line1 = ax6.plot(iterations, self.training_history['learning_rates'], 'g-', 
                           label='Learning Rate')
            line2 = ax6_twin.plot(iterations, self.training_history['neighborhood_radii'], 'orange', 
                                label='Neighborhood Radius')
            
            ax6.set_xlabel('Iteration')
            ax6.set_ylabel('Learning Rate', color='g')
            ax6_twin.set_ylabel('Neighborhood Radius', color='orange')
            ax6.set_title('Learning Parameters')
            
            # Combine legends
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax6.legend(lines, labels, loc='upper right')
            
        plt.tight_layout()
        plt.show()
        
        # Print map statistics
        self._print_map_statistics(training_data)
        
    def _calculate_u_matrix(self) -> np.ndarray:
        """
        Calculate Unified Distance Matrix (U-Matrix)
        
        Shows average distance between each neuron and its neighbors
        Useful for cluster boundary visualization
        """
        
        u_matrix = np.zeros((self.map_height, self.map_width))
        
        for i in range(self.map_height):
            for j in range(self.map_width):
                current_neuron = self.neurons[i, j]
                distances = []
                
                # Check all neighbors
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue  # Skip self
                            
                        ni, nj = i + di, j + dj
                        if 0 <= ni < self.map_height and 0 <= nj < self.map_width:
                            neighbor = self.neurons[ni, nj]
                            distance = np.linalg.norm(current_neuron.weight_vector - 
                                                    neighbor.weight_vector)
                            distances.append(distance)
                            
                u_matrix[i, j] = np.mean(distances) if distances else 0
                
        return u_matrix
        
    def _print_map_statistics(self, training_data: Optional[np.ndarray]):
        """Print detailed map statistics"""
        
        print(f"\n📊 SOM Statistics:")
        print(f"   • Map size: {self.map_height}×{self.map_width} = {self.map_height * self.map_width} neurons")
        print(f"   • Input dimension: {self.input_dim}")
        print(f"   • Topology: {self.topology}")
        
        if self.training_history['quantization_errors']:
            final_qe = self.training_history['quantization_errors'][-1]
            final_te = self.training_history['topographic_errors'][-1]
            print(f"   • Final quantization error: {final_qe:.4f}")
            print(f"   • Final topographic error: {final_te:.4f}")
            
        if training_data is not None:
            assignments, hit_counts = self.create_cluster_map(training_data)
            active_neurons = np.sum(hit_counts > 0)
            max_hits = np.max(hit_counts)
            avg_hits = np.mean(hit_counts[hit_counts > 0])
            
            print(f"   • Active neurons: {active_neurons}/{self.map_height * self.map_width} ({active_neurons/(self.map_height * self.map_width)*100:.1f}%)")
            print(f"   • Max hits per neuron: {max_hits:.0f}")
            print(f"   • Average hits per active neuron: {avg_hits:.1f}")


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
        self.train(X, n_iterations=1000)
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
        if not hasattr(self, 'neurons') or self.neurons is None:
            raise ValueError("SOM not fitted. Call fit() first.")
        
        predictions = []
        for sample in X:
            bmu_row, bmu_col = self.map_input(sample)
            predictions.append([bmu_row, bmu_col])
        
        return np.array(predictions)
    
    def fit_predict(self, X: np.ndarray, y=None) -> np.ndarray:
        """
        Scikit-learn compatible fit_predict method
        
        Fit the SOM and return BMU coordinates
        
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


# Example usage and demonstration
if __name__ == "__main__":
    print("🗺️  Self-Organizing Map Library - Kohonen (1982)")
    print("=" * 50)
    
    # Create test datasets
    print(f"\n🎲 Generating test datasets...")
    
    # Dataset 1: 2D Gaussian clusters
    np.random.seed(42)
    n_samples = 1000
    
    cluster1 = np.random.multivariate_normal([2, 2], [[0.5, 0.2], [0.2, 0.5]], n_samples//3)
    cluster2 = np.random.multivariate_normal([-1, 3], [[0.3, -0.1], [-0.1, 0.4]], n_samples//3)
    cluster3 = np.random.multivariate_normal([1, -2], [[0.4, 0.1], [0.1, 0.3]], n_samples//3)
    
    gaussian_data = np.vstack([cluster1, cluster2, cluster3])
    
    # Dataset 2: Ring/circle data
    angles = np.random.uniform(0, 2*np.pi, n_samples)
    radius = 3 + np.random.normal(0, 0.3, n_samples)
    ring_data = np.column_stack([
        radius * np.cos(angles),
        radius * np.sin(angles)
    ])
    
    print(f"   Created Gaussian clusters: {len(gaussian_data)} samples")
    print(f"   Created ring data: {len(ring_data)} samples")
    
    # Example 1: Train on Gaussian clusters
    print(f"\n🎯 Example 1: Gaussian Cluster Data")
    
    som1 = SelfOrganizingMap(
        map_size=(15, 15),
        input_dim=2,
        initial_learning_rate=0.5,
        topology='rectangular',
        random_seed=42
    )
    
    results1 = som1.train(gaussian_data, n_iterations=2000, verbose=True)
    som1.visualize_map(gaussian_data, figsize=(15, 10))
    
    # Example 2: Train on ring data  
    print(f"\n🔄 Example 2: Ring Data")
    
    som2 = SelfOrganizingMap(
        map_size=(10, 10),
        input_dim=2,
        initial_learning_rate=0.3,
        topology='rectangular',
        initialization='random',
        random_seed=42
    )
    
    results2 = som2.train(ring_data, n_iterations=1500, verbose=True)
    som2.visualize_map(ring_data, figsize=(15, 10))
    
    # Example 3: High-dimensional data (simplified)
    print(f"\n📊 Example 3: High-Dimensional Data")
    
    # Create 5D test data
    high_dim_data = np.random.multivariate_normal(
        mean=np.zeros(5),
        cov=np.eye(5),
        size=500
    )
    
    som3 = SelfOrganizingMap(
        map_size=(8, 8),
        input_dim=5,
        initial_learning_rate=0.4,
        random_seed=42
    )
    
    results3 = som3.train(high_dim_data, n_iterations=1000, verbose=True)
    som3.visualize_map(high_dim_data, figsize=(15, 10))
    
    # Test mapping functionality
    print(f"\n🔍 Testing input mapping...")
    test_point = np.array([1.5, 1.8])
    bmu_pos = som1.map_input(test_point)
    print(f"   Input {test_point} maps to grid position {bmu_pos}")
    
    print(f"\n💡 Key Innovation:")
    print(f"   • Unsupervised topological learning")
    print(f"   • Competitive and cooperative learning")
    print(f"   • Preserves neighborhood relationships")
    print(f"   • Models biological cortical organization")
    print(f"   • Foundation for visualization and clustering!")