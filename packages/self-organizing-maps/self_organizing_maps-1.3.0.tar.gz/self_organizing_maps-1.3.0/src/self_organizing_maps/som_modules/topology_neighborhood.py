"""
Topology and Neighborhood Functions Module

This module implements different map topologies (rectangular, hexagonal) and 
various neighborhood functions (Gaussian, Mexican hat, rectangular, etc.) for
Self-Organizing Maps.

Based on: Kohonen (1982) "Self-Organized Formation of Topologically Correct Feature Maps"
"""

import numpy as np
from typing import Tuple, Callable
from abc import ABC, abstractmethod


class TopologyCalculator(ABC):
    """Abstract base class for topology distance calculations"""
    
    @abstractmethod
    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate distance between two grid positions"""
        pass


class RectangularTopology(TopologyCalculator):
    """Rectangular (Euclidean) grid topology"""
    
    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between positions"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


class HexagonalTopology(TopologyCalculator):
    """Hexagonal grid topology with improved packing"""
    
    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Calculate distance in hexagonal topology
        
        Hexagonal grids provide better topological preservation due to 
        more uniform neighbor distances compared to rectangular grids.
        """
        dx = pos1[1] - pos2[1]
        dy = pos1[0] - pos2[0]
        
        if (dy > 0 and dx > 0) or (dy < 0 and dx < 0):
            return max(abs(dx), abs(dy))
        else:
            return abs(dx) + abs(dy)


class NeighborhoodFunction(ABC):
    """Abstract base class for neighborhood functions"""
    
    @abstractmethod
    def calculate_influence(self, distance: float, radius: float) -> float:
        """Calculate neighborhood influence based on distance and radius"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get function name for identification"""
        pass


class GaussianNeighborhood(NeighborhoodFunction):
    """
    Gaussian neighborhood function - smooth, biological, default choice
    
    h(d) = exp(-d²/(2σ²))
    
    This is the classic neighborhood function used in most SOM implementations.
    It provides smooth, biologically-plausible activation patterns.
    """
    
    def calculate_influence(self, distance: float, radius: float) -> float:
        if radius <= 0:
            return 1.0 if distance == 0 else 0.0
        return np.exp(-(distance**2) / (2 * radius**2))
    
    def get_name(self) -> str:
        return "gaussian"


class MexicanHatNeighborhood(NeighborhoodFunction):
    """
    Mexican hat (difference of Gaussians) neighborhood function
    
    Provides center-surround activation pattern useful for edge detection
    and contrast enhancement. Creates excitatory center with inhibitory surround.
    """
    
    def calculate_influence(self, distance: float, radius: float) -> float:
        if radius <= 0:
            return 1.0 if distance == 0 else 0.0
        
        # Center Gaussian (narrow, positive)
        center = np.exp(-(distance**2) / (2 * (radius/3)**2))
        # Surround Gaussian (wider, negative)
        surround = 0.5 * np.exp(-(distance**2) / (2 * radius**2))
        return max(0.0, center - surround)
    
    def get_name(self) -> str:
        return "mexican_hat"


class RectangularNeighborhood(NeighborhoodFunction):
    """
    Rectangular (step function) neighborhood - binary activation within radius
    
    h(d) = 1 if d ≤ σ, 0 otherwise
    
    Simple binary neighborhood with hard cutoff. Computationally efficient
    but can lead to discontinuous learning.
    """
    
    def calculate_influence(self, distance: float, radius: float) -> float:
        return 1.0 if distance <= radius else 0.0
    
    def get_name(self) -> str:
        return "rectangular"


class LinearDecayNeighborhood(NeighborhoodFunction):
    """
    Linear decay neighborhood function
    
    h(d) = 1 - d/σ for d ≤ σ, 0 otherwise
    
    Linear decrease from 1.0 to 0.0 within radius. Provides smooth
    decay without the computational cost of exponential functions.
    """
    
    def calculate_influence(self, distance: float, radius: float) -> float:
        if radius <= 0:
            return 1.0 if distance == 0 else 0.0
        if distance >= radius:
            return 0.0
        return 1.0 - (distance / radius)
    
    def get_name(self) -> str:
        return "linear_decay"


class BubbleNeighborhood(NeighborhoodFunction):
    """
    Bubble neighborhood function - uniform activation within radius
    
    More efficient alternative to rectangular with smoother boundaries.
    Provides uniform influence within neighborhood radius.
    """
    
    def calculate_influence(self, distance: float, radius: float) -> float:
        return 1.0 if distance <= radius else 0.0
    
    def get_name(self) -> str:
        return "bubble"


class CosineNeighborhood(NeighborhoodFunction):
    """
    Cosine neighborhood function - smooth cosine-based decay
    
    h(d) = 0.5 * (1 + cos(πd/σ)) for d ≤ σ, 0 otherwise
    
    Good compromise between Gaussian and rectangular functions.
    Provides smooth decay with finite support.
    """
    
    def calculate_influence(self, distance: float, radius: float) -> float:
        if radius <= 0:
            return 1.0 if distance == 0 else 0.0
        if distance >= radius:
            return 0.0
        return 0.5 * (1 + np.cos(np.pi * distance / radius))
    
    def get_name(self) -> str:
        return "cosine"


class EpanechnikovNeighborhood(NeighborhoodFunction):
    """
    Epanechnikov neighborhood function (quadratic kernel)
    
    h(d) = 1 - (d/σ)² for d ≤ σ, 0 otherwise
    
    Parabolic decay within radius - optimal for certain statistical properties.
    Often used in kernel density estimation with good theoretical properties.
    """
    
    def calculate_influence(self, distance: float, radius: float) -> float:
        if radius <= 0:
            return 1.0 if distance == 0 else 0.0
        if distance >= radius:
            return 0.0
        normalized_distance = distance / radius
        return 1.0 - normalized_distance**2
    
    def get_name(self) -> str:
        return "epanechnikov"


class TopologyNeighborhoodManager:
    """
    Manager class for topology and neighborhood function combinations
    
    This class provides a unified interface for different topology types
    and neighborhood functions, making it easy to experiment with different
    configurations.
    """
    
    def __init__(self, topology: str = 'rectangular', 
                 neighborhood_function: str = 'gaussian'):
        """
        Initialize topology and neighborhood function
        
        Args:
            topology: 'rectangular' or 'hexagonal'
            neighborhood_function: Name of neighborhood function to use
        """
        # Initialize topology calculator
        if topology == 'rectangular':
            self.topology = RectangularTopology()
        elif topology == 'hexagonal':
            self.topology = HexagonalTopology()
        else:
            raise ValueError(f"Unknown topology: {topology}")
        
        # Initialize neighborhood function
        neighborhood_map = {
            'gaussian': GaussianNeighborhood(),
            'mexican_hat': MexicanHatNeighborhood(),
            'rectangular': RectangularNeighborhood(),
            'linear_decay': LinearDecayNeighborhood(),
            'bubble': BubbleNeighborhood(),
            'cosine': CosineNeighborhood(),
            'epanechnikov': EpanechnikovNeighborhood()
        }
        
        if neighborhood_function not in neighborhood_map:
            raise ValueError(f"Unknown neighborhood function: {neighborhood_function}")
        
        self.neighborhood_func = neighborhood_map[neighborhood_function]
        self.topology_name = topology
        self.neighborhood_name = neighborhood_function
    
    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate distance between grid positions using selected topology"""
        return self.topology.calculate_distance(pos1, pos2)
    
    def calculate_neighborhood_influence(self, distance: float, radius: float) -> float:
        """Calculate neighborhood influence using selected function"""
        return self.neighborhood_func.calculate_influence(distance, radius)
    
    def get_configuration(self) -> dict:
        """Get current configuration information"""
        return {
            'topology': self.topology_name,
            'neighborhood_function': self.neighborhood_name,
            'topology_class': self.topology.__class__.__name__,
            'neighborhood_class': self.neighborhood_func.__class__.__name__
        }


def create_topology_calculator(topology: str) -> TopologyCalculator:
    """Factory function to create topology calculators"""
    if topology == 'rectangular':
        return RectangularTopology()
    elif topology == 'hexagonal':
        return HexagonalTopology()
    else:
        raise ValueError(f"Unknown topology: {topology}")


def create_neighborhood_function(function_name: str) -> NeighborhoodFunction:
    """Factory function to create neighborhood functions"""
    function_map = {
        'gaussian': GaussianNeighborhood,
        'mexican_hat': MexicanHatNeighborhood,
        'rectangular': RectangularNeighborhood,
        'linear_decay': LinearDecayNeighborhood,
        'bubble': BubbleNeighborhood,
        'cosine': CosineNeighborhood,
        'epanechnikov': EpanechnikovNeighborhood
    }
    
    if function_name not in function_map:
        available = ', '.join(function_map.keys())
        raise ValueError(f"Unknown neighborhood function: {function_name}. "
                        f"Available functions: {available}")
    
    return function_map[function_name]()


def get_available_topologies() -> list:
    """Get list of available topology types"""
    return ['rectangular', 'hexagonal']


def get_available_neighborhood_functions() -> list:
    """Get list of available neighborhood functions"""
    return ['gaussian', 'mexican_hat', 'rectangular', 'linear_decay', 
            'bubble', 'cosine', 'epanechnikov']