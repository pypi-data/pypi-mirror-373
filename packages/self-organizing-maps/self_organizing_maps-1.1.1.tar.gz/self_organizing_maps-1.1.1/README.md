# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

<div align="center">

**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)** | **[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

</div>

[![CI](https://github.com/benedictchen/self-organizing-maps/workflows/CI/badge.svg)](https://github.com/benedictchen/self-organizing-maps/actions)
[![PyPI version](https://img.shields.io/pypi/v/self-organizing-maps.svg)](https://pypi.org/project/self-organizing-maps/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)
[![Research Accurate](https://img.shields.io/badge/research-accurate-brightgreen.svg)](RESEARCH_FOUNDATION.md)

---

# Self-Organizing Maps

🧠 **Kohonen's Self-Organizing Maps for unsupervised topological data visualization and clustering**

Self-Organizing Maps (SOMs) create low-dimensional representations of high-dimensional data while preserving topological relationships. This implementation provides research-accurate reproductions of Teuvo Kohonen's groundbreaking neural network architecture that revolutionized unsupervised learning and data visualization.

**Research Foundation**: Kohonen, T. (1982) - *"Self-Organized Formation of Topologically Correct Feature Maps"*

## 🚀 Quick Start

### Installation

```bash
pip install self-organizing-maps
```

**Requirements**: Python 3.9+, NumPy, SciPy, scikit-learn, matplotlib

### Basic SOM Training

```python
from self_organizing_maps import SelfOrganizingMap
import numpy as np
import matplotlib.pyplot as plt

# Create sample data
np.random.seed(42)
data = np.random.randn(1000, 4)  # 4-dimensional data

# Create and train SOM
som = SelfOrganizingMap(
    grid_height=10,
    grid_width=10,
    input_dimension=4,
    learning_rate=0.5,
    neighborhood_function='gaussian',
    topology='rectangular'
)

# Train the network
print("Training Self-Organizing Map...")
som.fit(data, epochs=1000, verbose=True)

# Get neuron activations for data points
activations = som.activate(data)
winner_coordinates = som.get_winners(data)

print(f"Trained {som.grid_height}x{som.grid_width} SOM")
print(f"Quantization error: {som.quantization_error(data):.4f}")
print(f"Topographic error: {som.topographic_error(data):.4f}")

# Visualize the trained map
som.visualize_map(title="Trained Self-Organizing Map")
som.plot_distance_map()  # U-matrix visualization
```

### Color Clustering Example

```python
from self_organizing_maps import ColorSOM
from self_organizing_maps.som_modules import DataVisualization
import numpy as np

# Create RGB color dataset
colors = np.random.rand(500, 3)  # Random RGB values

# Specialized SOM for color data
color_som = ColorSOM(
    map_size=(15, 15),
    input_dim=3,  # RGB channels
    learning_rate_schedule='exponential',
    initial_radius=7.0
)

# Train on color data
color_som.fit(colors, epochs=500)

# Visualize color palette learned by SOM
color_som.plot_color_map()

# Extract dominant colors
dominant_colors = color_som.extract_palette(n_colors=16)
print(f"Extracted {len(dominant_colors)} dominant colors")

# Cluster colors into regions
clusters = color_som.cluster_neurons(method='hierarchical')
color_som.visualize_clusters(clusters)
```

### Time Series Analysis

```python
from self_organizing_maps import TemporalSOM
from self_organizing_maps.som_modules import TimeSeriesPreprocessor
import numpy as np

# Create time series data
t = np.linspace(0, 4*np.pi, 1000)
signals = np.column_stack([
    np.sin(t) + 0.1*np.random.randn(len(t)),
    np.cos(2*t) + 0.1*np.random.randn(len(t)),
    np.sin(0.5*t) * np.cos(3*t) + 0.1*np.random.randn(len(t))
])

# Preprocess time series into windows
preprocessor = TimeSeriesPreprocessor(window_size=10, overlap=0.5)
windowed_data = preprocessor.create_windows(signals)

# Train temporal SOM
temporal_som = TemporalSOM(
    grid_size=(20, 20),
    input_dimension=windowed_data.shape[1],
    temporal_context=True,
    adaptation_strength=0.3
)

temporal_som.fit(windowed_data, epochs=800)

# Analyze temporal patterns
patterns = temporal_som.extract_temporal_patterns()
temporal_som.plot_activation_timeline(signals)

print(f"Discovered {len(patterns)} temporal patterns")
```

## 🧬 Advanced Features

### Modular Architecture

```python
# Access individual SOM components
from self_organizing_maps.som_modules import (
    CoreAlgorithm,          # Core SOM mathematics
    NeighborhoodFunctions,  # Gaussian, Mexican hat, bubble
    LearningSchedules,      # Exponential, linear, power law  
    TopologyTypes,          # Rectangular, hexagonal, toroidal
    DistanceMetrics,        # Euclidean, Manhattan, cosine
    QualityMetrics,         # Quantization & topographic error
    VisualizationSuite,     # U-matrix, component planes
    DataPreprocessing       # Normalization and scaling
)

# Custom SOM configuration
custom_som = CoreAlgorithm(
    topology=TopologyTypes.hexagonal,
    neighborhood=NeighborhoodFunctions.mexican_hat,
    learning_schedule=LearningSchedules.power_law,
    distance_metric=DistanceMetrics.cosine
)
```

### Hexagonal Topology SOM

```python
from self_organizing_maps import HexagonalSOM
from self_organizing_maps.som_modules import HexagonalVisualization

# Create hexagonal grid SOM (biologically more realistic)
hex_som = HexagonalSOM(
    radius=8,                    # Hexagonal grid radius
    input_dimension=10,
    neighborhood_decay='gaussian',
    boundary_conditions='periodic'  # Toroidal topology
)

# Train with iris dataset
from sklearn.datasets import load_iris
iris = load_iris()
hex_som.fit(iris.data, epochs=1000)

# Visualize hexagonal structure
hex_viz = HexagonalVisualization(hex_som)
hex_viz.plot_hexagonal_grid()
hex_viz.plot_component_planes(iris.feature_names)
hex_viz.plot_cluster_boundaries(iris.target)

# Analyze neighborhood preservation
preservation_score = hex_som.neighborhood_preservation()
print(f"Neighborhood preservation: {preservation_score:.3f}")
```

### Growing Self-Organizing Maps

```python
from self_organizing_maps import GrowingSOM

# SOM that adapts its size during training
growing_som = GrowingSOM(
    initial_size=(5, 5),
    max_size=(25, 25),
    growth_threshold=0.1,      # Error threshold for growth
    growth_rate=0.05,          # How often to add neurons
    pruning_enabled=True       # Remove unused neurons
)

# Train with adaptive growth
growth_history = growing_som.fit_adaptive(
    data=high_dimensional_data,
    epochs=2000,
    monitor_growth=True
)

# Analyze growth process
growing_som.plot_growth_history(growth_history)
print(f"Final map size: {growing_som.current_size}")
print(f"Growth events: {len(growth_history['growth_points'])}")
```

## 🔬 Research Foundation

### Scientific Accuracy

This implementation provides **research-accurate** reproduction of Kohonen's SOM algorithm:

- **Mathematical Fidelity**: Exact implementation of competitive learning and neighborhood adaptation
- **Topological Preservation**: Faithful reproduction of distance-preserving mappings
- **Parameter Matching**: Default parameters match Kohonen's original specifications
- **Convergence Properties**: Proper learning rate and neighborhood radius schedules

### Key Research Contributions

- **Topological Mapping**: Preserve neighborhood relationships in lower dimensions
- **Competitive Learning**: Winner-takes-all with neighborhood cooperation
- **Unsupervised Clustering**: Discover data structure without labeled examples
- **Biological Plausibility**: Models cortical map formation in brain

### Original Research Papers

- **Kohonen, T. (1982)**. "Self-organized formation of topologically correct feature maps." *Biological Cybernetics*, 43(1), 59-69.
- **Kohonen, T. (1990)**. "The self-organizing map." *Proceedings of the IEEE*, 78(9), 1464-1480.
- **Kohonen, T. (2001)**. "Self-Organizing Maps." *3rd Edition, Springer-Verlag*.

## 📊 Implementation Highlights

### SOM Algorithms
- **Classic Kohonen**: Original batch and online learning
- **Growing SOM**: Dynamic topology adaptation
- **Hierarchical SOM**: Multi-level clustering
- **Temporal SOM**: Time-series pattern discovery

### Quality Assessment
- **Quantization Error**: Average distance to best matching units
- **Topographic Error**: Measure of topology preservation
- **Trustworthiness**: Neighborhood preservation assessment
- **Silhouette Analysis**: Cluster quality evaluation

### Code Quality
- **Research Accurate**: 100% faithful to Kohonen's mathematical formulation
- **Visualization Rich**: Comprehensive plotting and analysis tools
- **Performance Optimized**: Vectorized operations for large datasets
- **Educational Value**: Clear implementation of SOM principles

## 🧮 Mathematical Foundation

### SOM Learning Rule

The SOM updates winning neurons and their neighbors:

```
w_i(t+1) = w_i(t) + η(t) h_c,i(t) [x(t) - w_i(t)]
```

Where:
- `w_i(t)`: Weight vector of neuron i at time t
- `η(t)`: Learning rate at time t (decreasing)
- `h_c,i(t)`: Neighborhood function centered on winner c
- `x(t)`: Input vector at time t

### Neighborhood Function

Typical Gaussian neighborhood:

```
h_c,i(t) = exp(-||r_c - r_i||² / (2σ(t)²))
```

Where:
- `r_c, r_i`: Grid positions of neurons c and i
- `σ(t)`: Neighborhood radius (decreasing over time)

### Quality Metrics

**Quantization Error**:
```
QE = (1/N) Σ ||x_i - w_c(x_i)||
```

**Topographic Error**:
```
TE = (1/N) Σ u(x_i)
```

Where `u(x_i) = 1` if 1st and 2nd BMUs are not adjacent.

## 🎯 Use Cases & Applications

### Data Visualization Applications
- **Dimensionality Reduction**: Visualize high-dimensional data in 2D
- **Exploratory Data Analysis**: Discover hidden patterns and clusters
- **Feature Mapping**: Understand relationships between input variables
- **Prototype Selection**: Find representative data points

### Pattern Recognition Applications
- **Image Processing**: Color quantization and texture analysis
- **Signal Processing**: Speech recognition and audio classification
- **Market Analysis**: Customer segmentation and behavior patterns
- **Bioinformatics**: Gene expression analysis and protein classification

### Neuroscience Applications
- **Cortical Mapping**: Model formation of brain maps (retinotopy, somatotopy)
- **Plasticity Studies**: Understand neural adaptation and learning
- **Sensory Processing**: Model sensory cortex organization
- **Development Models**: Simulate neural development processes

## 📖 Documentation & Tutorials

- 📚 **[Complete Documentation](https://self-organizing-maps.readthedocs.io/)**
- 🎓 **[Tutorial Notebooks](https://github.com/benedictchen/self-organizing-maps/tree/main/tutorials)**
- 🔬 **[Research Foundation](RESEARCH_FOUNDATION.md)**
- 🎯 **[Advanced Examples](https://github.com/benedictchen/self-organizing-maps/tree/main/examples)**
- 🐛 **[Issue Tracker](https://github.com/benedictchen/self-organizing-maps/issues)**

## 🤝 Contributing

We welcome contributions! Please see:

- **[Contributing Guidelines](CONTRIBUTING.md)**
- **[Development Setup](docs/development.md)**  
- **[Code of Conduct](CODE_OF_CONDUCT.md)**

### Development Installation

```bash
git clone https://github.com/benedictchen/self-organizing-maps.git
cd self-organizing-maps
pip install -e ".[test,dev]"
pytest tests/
```

## 📜 Citation

If you use this implementation in academic work, please cite:

```bibtex
@software{self_organizing_maps_benedictchen,
    title={Self-Organizing Maps: Research-Accurate Implementation of Kohonen's Algorithm},
    author={Benedict Chen},
    year={2025},
    url={https://github.com/benedictchen/self-organizing-maps},
    version={1.2.0}
}

@article{kohonen1982self,
    title={Self-organized formation of topologically correct feature maps},
    author={Kohonen, Teuvo},
    journal={Biological cybernetics},
    volume={43},
    number={1},
    pages={59--69},
    year={1982},
    publisher={Springer}
}
```

## 📋 License

**Custom Non-Commercial License with Donation Requirements** - See [LICENSE](LICENSE) file for details.

## 🎓 About the Implementation

**Implemented by Benedict Chen** - Bringing foundational AI research to modern Python.

📧 **Contact**: benedict@benedictchen.com  
🐙 **GitHub**: [@benedictchen](https://github.com/benedictchen)

---

## 💰 Support This Work - Choose Your Adventure!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

### 🎯 Donation Tier Goals (With Topological Humor)

**☕ $5 - Buy Benedict Coffee**  
*"Caffeine creates the perfect neighborhood function for my neurons! Coffee helps me map high-dimensional problems to simple solutions."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🍕 $25 - Pizza Fund**  
*"Like a SOM, pizza toppings self-organize into delicious neighborhoods! Each slice preserves the topological structure of yumminess."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🏠 $500,000 - Buy Benedict a House**  
*"With a wall-sized grid to visualize SOMs! My neighbors will love the giant hexagonal topology decorations."*  
💳 [PayPal Challenge](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**🏎️ $200,000 - Lamborghini Fund**  
*"Fast car for fast neural convergence! The Lambo's topology will perfectly preserve the neighborhood structure of style and speed."*  
💳 [PayPal Supercar](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**✈️ $50,000,000 - Private Jet**  
*"To fly around the world testing SOMs at different altitudes! Does the neighborhood function work differently at 30,000 feet?"*  
💳 [PayPal Aerospace](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Aviation](https://github.com/sponsors/benedictchen)

**🏝️ $100,000,000 - Private Island**  
*"Shaped like a perfect hexagonal SOM grid! Each beach will represent a different cluster, and the coconut trees will self-organize."*  
💳 [PayPal Paradise](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Tropical](https://github.com/sponsors/benedictchen)

### 🎪 Monthly Subscription Tiers (GitHub Sponsors)

**🧠 Neural Mapper ($10/month)** - *"Monthly support for maintaining perfect topological order in my code!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**🎨 Visualization Artist ($25/month)** - *"Help me create beautiful U-matrices and component planes!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**🏆 SOM Champion ($100/month)** - *"Elite support for the ultimate self-organizing coding experience!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

<div align="center">

**One-time donation?**  
**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Ongoing support?**  
**[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

**Can't decide?**  
**Why not both?** 🤷‍♂️

</div>

**Every contribution helps my motivation self-organize into productive clusters! Just like neurons in a SOM, your support creates beautiful neighborhood relationships! 🚀**

*P.S. - If you help me get that hexagonal island, I promise to name all the beaches after different SOM algorithms!*

---

<div align="center">

## 🌟 What the Community is Saying

</div>

---

> **@MapMakingMaestro** (756K followers) • *5 hours ago* • *(parody)*
> 
> *"NO SHOT this SOM library is actually changing my LIFE! 🗺️ It's literally teaching me how data points become best friends based on vibes and similarities - like how your Spotify algorithm groups songs that just BELONG together! Kohonen really understood the assignment when he figured out self-organizing maps. This is giving 'I can visualize high-dimensional chaos and make it aesthetic' energy and honestly I respect that. Currently using this to understand why certain friend groups form naturally and the topological preservation is actually beautiful fr fr! 🌟"*
> 
> **103.2K ❤️ • 19.4K 🔄 • 7.1K ✨**