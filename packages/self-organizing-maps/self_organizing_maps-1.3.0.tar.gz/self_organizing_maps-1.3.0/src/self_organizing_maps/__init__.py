"""
Self-Organizing Maps Package - Modular Implementation

A comprehensive, modular implementation of Kohonen's Self-Organizing Maps 
with extensive visualization, analysis, and configuration options.

This package provides both the modular components for advanced users and
a unified interface maintaining backward compatibility with the original
monolithic implementation.

Main Classes:
- SelfOrganizingMap: Main SOM class (backward compatible)
- ModularSelfOrganizingMap: Explicit modular version

Key Features:
- Multiple neighborhood functions (Gaussian, Mexican hat, etc.)
- Various parameter schedules (exponential, linear, power law, etc.) 
- Comprehensive visualization and analysis tools
- Quality metrics (quantization error, topographic error, etc.)
- Scikit-learn compatible interface
- Extensive customization options

Based on: Kohonen (1982) "Self-Organized Formation of Topologically Correct Feature Maps"

Author: Benedict Chen (benedict@benedictchen.com)
Support: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Example Usage:
```python
from self_organizing_maps import SelfOrganizingMap
import numpy as np

# Create sample data
data = np.random.rand(1000, 3)

# Create and train SOM
som = SelfOrganizingMap(
    map_size=(15, 15),
    input_dim=3,
    neighborhood_function='gaussian',
    parameter_schedule='exponential'
)

som.train(data, n_iterations=1000)
som.visualize_map(data)

# Map new inputs
new_input = np.array([0.5, 0.3, 0.8])
grid_position = som.map_input(new_input)
```
"""

# Import main classes and functions from modular components
from .som_modules import (
    # Main SOM implementations
    SelfOrganizingMap,
    ModularSelfOrganizingMap,
    
    # Core components for advanced users
    SOMCoreAlgorithm,
    SOMNeuron,
    TopologyNeighborhoodManager,
    ParameterScheduleManager,
    SOMVisualizer,
    SOMMetrics,
    SOMUtils,
    
    # Utility functions
    get_available_topologies,
    get_available_neighborhood_functions,
    get_available_schedules,
    get_schedule_default_parameters,
    
    # Factory functions
    create_topology_calculator,
    create_neighborhood_function,
    create_parameter_schedule,
    create_som_visualizer,
    create_som_metrics
)

# Package metadata
__version__ = '2.0.0'
__author__ = 'Benedict Chen'
__email__ = 'benedict@benedictchen.com'

# Public API - what gets imported with "from self_organizing_maps import *"
__all__ = [
    # Main classes (most users will only need these)
    'SelfOrganizingMap',
    'ModularSelfOrganizingMap',
    
    # Advanced components
    'SOMCoreAlgorithm',
    'SOMNeuron', 
    'TopologyNeighborhoodManager',
    'ParameterScheduleManager',
    'SOMVisualizer',
    'SOMMetrics',
    'SOMUtils',
    
    # Discovery functions
    'get_available_topologies',
    'get_available_neighborhood_functions', 
    'get_available_schedules',
    'get_schedule_default_parameters',
    
    # Factory functions
    'create_topology_calculator',
    'create_neighborhood_function',
    'create_parameter_schedule',
    'create_som_visualizer',
    'create_som_metrics'
]

# Package information
def get_package_info():
    """Get package information"""
    return {
        'name': 'self_organizing_maps',
        'version': __version__,
        'author': __author__,
        'email': __email__,
        'description': 'Modular Self-Organizing Maps implementation',
        'components': [
            'Core Algorithm (Competition, Cooperation, Adaptation)',
            'Topology & Neighborhood Functions', 
            'Parameter Scheduling',
            'Visualization & Analysis',
            'Quality Metrics & Utilities'
        ],
        'supported_topologies': get_available_topologies(),
        'supported_neighborhoods': get_available_neighborhood_functions(),
        'supported_schedules': get_available_schedules()
    }

def print_package_info():
    """Print comprehensive package information"""
    info = get_package_info()
    
    print(f"📦 {info['name']} v{info['version']}")
    print(f"👤 Author: {info['author']} <{info['email']}>")
    print(f"📝 Description: {info['description']}")
    print("\n🧩 Modular Components:")
    for component in info['components']:
        print(f"   • {component}")
    
    print(f"\n🗺️  Supported Topologies: {', '.join(info['supported_topologies'])}")
    print(f"🎯 Neighborhood Functions: {', '.join(info['supported_neighborhoods'])}")  
    print(f"📈 Parameter Schedules: {', '.join(info['supported_schedules'])}")
    
    print(f"\n💝 Support this work: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")
    print("Your support makes advanced AI research accessible to everyone! ☕🍺🚀")

# Print info on import (can be disabled by setting environment variable)
import os
if not os.environ.get('SOM_SILENT_IMPORT', False):
    print("✓ Self-Organizing Maps package loaded (modular implementation)")
    print("  Run som.print_package_info() for detailed information")
    print("  Set SOM_SILENT_IMPORT=1 to disable this message")