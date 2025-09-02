"""
Self-Organizing Maps Modular Components

This package contains the modular components of the Self-Organizing Map implementation:

- core_algorithm: Core SOM learning algorithm (competition, cooperation, adaptation)
- topology_neighborhood: Topology calculation and neighborhood functions  
- parameter_schedules: Learning rate and radius decay schedules
- visualization: Comprehensive visualization and analysis tools
- metrics_utils: Quality metrics and utility functions
- modular_som: Main modular SOM class integrating all components

Based on: Kohonen (1982) "Self-Organized Formation of Topologically Correct Feature Maps"
"""

from .core_algorithm import SOMCoreAlgorithm, SOMNeuron
from .topology_neighborhood import (
    TopologyNeighborhoodManager,
    RectangularTopology, HexagonalTopology,
    GaussianNeighborhood, MexicanHatNeighborhood, RectangularNeighborhood,
    LinearDecayNeighborhood, BubbleNeighborhood, CosineNeighborhood,
    EpanechnikovNeighborhood,
    create_topology_calculator, create_neighborhood_function,
    get_available_topologies, get_available_neighborhood_functions
)
from .parameter_schedules import (
    ParameterScheduleManager,
    ExponentialSchedule, LinearSchedule, InverseTimeSchedule,
    PowerLawSchedule, StepDecaySchedule, CyclicSchedule,
    create_parameter_schedule, get_available_schedules,
    get_schedule_default_parameters
)
from .visualization import SOMVisualizer, create_som_visualizer
from .metrics_utils import SOMMetrics, SOMUtils, create_som_metrics
from .modular_som import ModularSelfOrganizingMap, SelfOrganizingMap

# Main exports for public API
__all__ = [
    # Main SOM class
    'ModularSelfOrganizingMap',
    'SelfOrganizingMap',  # Backward compatibility alias
    
    # Core components
    'SOMCoreAlgorithm',
    'SOMNeuron',
    
    # Topology and neighborhood
    'TopologyNeighborhoodManager',
    'get_available_topologies',
    'get_available_neighborhood_functions',
    
    # Parameter scheduling
    'ParameterScheduleManager',
    'get_available_schedules',
    'get_schedule_default_parameters',
    
    # Visualization and metrics
    'SOMVisualizer',
    'SOMMetrics',
    'SOMUtils',
    
    # Factory functions
    'create_topology_calculator',
    'create_neighborhood_function',
    'create_parameter_schedule',
    'create_som_visualizer',
    'create_som_metrics'
]

# Version info
__version__ = '2.0.0'
__author__ = 'Benedict Chen'
__email__ = 'benedict@benedictchen.com'