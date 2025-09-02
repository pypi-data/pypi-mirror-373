"""
Parameter Scheduling Module

This module implements various parameter decay schedules for learning rate and
neighborhood radius in Self-Organizing Maps. Different schedules provide different
learning dynamics and convergence properties.

Based on: Kohonen (1982) "Self-Organized Formation of Topologically Correct Feature Maps"
"""

import numpy as np
from typing import Tuple, Dict, Optional
from abc import ABC, abstractmethod


class ParameterSchedule(ABC):
    """Abstract base class for parameter scheduling"""
    
    @abstractmethod
    def calculate_parameters(self, iteration: int, total_iterations: int,
                           initial_learning_rate: float, initial_radius: float,
                           schedule_params: Dict) -> Tuple[float, float]:
        """Calculate learning rate and radius for given iteration"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get schedule name for identification"""
        pass


class ExponentialSchedule(ParameterSchedule):
    """
    Exponential decay schedule - fast early learning, gradual refinement
    
    η(t) = η₀ × exp(-t/τ)
    σ(t) = σ₀ × exp(-t/τ)
    
    This is the classic schedule used in most SOM implementations.
    Provides rapid initial organization followed by fine-tuning.
    """
    
    def calculate_parameters(self, iteration: int, total_iterations: int,
                           initial_learning_rate: float, initial_radius: float,
                           schedule_params: Dict) -> Tuple[float, float]:
        # Calculate time constant based on radius decay requirement
        time_constant = total_iterations / np.log(max(initial_radius, 1.0))
        
        learning_rate = initial_learning_rate * np.exp(-iteration / time_constant)
        radius = initial_radius * np.exp(-iteration / time_constant)
        
        return learning_rate, radius
    
    def get_name(self) -> str:
        return "exponential"


class LinearSchedule(ParameterSchedule):
    """
    Linear decay schedule - steady decrease, predictable convergence
    
    η(t) = η₀ × (1 - t/T)
    σ(t) = σ₀ × (1 - t/T)
    
    Provides predictable linear decrease to zero. Maintains higher learning
    rates longer than exponential, then drops more rapidly.
    """
    
    def calculate_parameters(self, iteration: int, total_iterations: int,
                           initial_learning_rate: float, initial_radius: float,
                           schedule_params: Dict) -> Tuple[float, float]:
        decay_factor = 1.0 - (iteration / total_iterations)
        
        # Ensure minimum values to prevent complete shutdown
        learning_rate = initial_learning_rate * max(0.01, decay_factor)
        radius = initial_radius * max(0.1, decay_factor)
        
        return learning_rate, radius
    
    def get_name(self) -> str:
        return "linear"


class InverseTimeSchedule(ParameterSchedule):
    """
    Inverse time decay schedule - slow asymptotic decay, extended learning
    
    η(t) = η₀ / (1 + t/τ)
    σ(t) = σ₀ / (1 + t/τ)
    
    Provides slower decay than exponential, maintaining learning capacity
    for longer periods. Good for fine-grained optimization.
    """
    
    def calculate_parameters(self, iteration: int, total_iterations: int,
                           initial_learning_rate: float, initial_radius: float,
                           schedule_params: Dict) -> Tuple[float, float]:
        tau = schedule_params.get('tau', total_iterations / 10)
        
        learning_rate = initial_learning_rate / (1 + iteration / tau)
        radius = initial_radius / (1 + iteration / tau)
        
        return learning_rate, radius
    
    def get_name(self) -> str:
        return "inverse_time"


class PowerLawSchedule(ParameterSchedule):
    """
    Power law decay schedule - scale-invariant, natural phenomena modeling
    
    η(t) = η₀ × (t₀/t)^α
    σ(t) = σ₀ × (t₀/t)^α
    
    Models power-law relationships common in natural systems.
    The decay exponent α controls the decay rate.
    """
    
    def calculate_parameters(self, iteration: int, total_iterations: int,
                           initial_learning_rate: float, initial_radius: float,
                           schedule_params: Dict) -> Tuple[float, float]:
        alpha = schedule_params.get('alpha', 0.5)
        t0 = schedule_params.get('t0', 1.0)
        t = max(1.0, iteration + 1)  # Avoid division by zero
        
        decay_factor = (t0 / t) ** alpha
        learning_rate = initial_learning_rate * decay_factor
        radius = initial_radius * decay_factor
        
        return learning_rate, radius
    
    def get_name(self) -> str:
        return "power_law"


class StepDecaySchedule(ParameterSchedule):
    """
    Step decay schedule - discrete reductions at intervals, multi-phase training
    
    Parameters are reduced by a factor at regular intervals.
    Useful for multi-phase training with distinct learning periods.
    """
    
    def calculate_parameters(self, iteration: int, total_iterations: int,
                           initial_learning_rate: float, initial_radius: float,
                           schedule_params: Dict) -> Tuple[float, float]:
        step_size = schedule_params.get('step_size', total_iterations // 4)
        decay_rate = schedule_params.get('decay_rate', 0.5)
        
        # Calculate number of steps completed
        steps = iteration // step_size if step_size > 0 else 0
        decay_factor = decay_rate ** steps
        
        learning_rate = initial_learning_rate * decay_factor
        radius = initial_radius * decay_factor
        
        return learning_rate, radius
    
    def get_name(self) -> str:
        return "step_decay"


class CyclicSchedule(ParameterSchedule):
    """
    Cyclic schedule - parameters oscillate between min and max values
    
    Allows periodic reorganization and fine-tuning phases.
    Inspired by cyclic learning rates in deep learning.
    Can help escape local minima and improve final organization.
    """
    
    def calculate_parameters(self, iteration: int, total_iterations: int,
                           initial_learning_rate: float, initial_radius: float,
                           schedule_params: Dict) -> Tuple[float, float]:
        cycle_length = schedule_params.get('cycle_length', total_iterations // 10)
        min_factor = schedule_params.get('min_factor', 0.1)
        
        if cycle_length <= 0:
            cycle_length = max(1, total_iterations // 10)
        
        # Calculate position within current cycle (0 to 1)
        cycle_position = (iteration % cycle_length) / cycle_length
        
        # Cosine annealing within each cycle
        factor = min_factor + (1 - min_factor) * (1 + np.cos(np.pi * cycle_position)) / 2
        
        learning_rate = initial_learning_rate * factor
        radius = initial_radius * factor
        
        return learning_rate, radius
    
    def get_name(self) -> str:
        return "cyclic"


class ParameterScheduleManager:
    """
    Manager class for parameter scheduling
    
    Provides a unified interface for different parameter decay schedules,
    making it easy to experiment with different learning dynamics.
    """
    
    def __init__(self, schedule_type: str = 'exponential', 
                 schedule_parameters: Optional[Dict] = None):
        """
        Initialize parameter scheduler
        
        Args:
            schedule_type: Type of schedule to use
            schedule_parameters: Additional parameters for the schedule
        """
        self.schedule_parameters = schedule_parameters or {}
        
        # Create schedule instance
        schedule_map = {
            'exponential': ExponentialSchedule(),
            'linear': LinearSchedule(),
            'inverse_time': InverseTimeSchedule(),
            'power_law': PowerLawSchedule(),
            'step_decay': StepDecaySchedule(),
            'cyclic': CyclicSchedule()
        }
        
        if schedule_type not in schedule_map:
            available = ', '.join(schedule_map.keys())
            raise ValueError(f"Unknown schedule type: {schedule_type}. "
                           f"Available schedules: {available}")
        
        self.schedule = schedule_map[schedule_type]
        self.schedule_type = schedule_type
    
    def get_parameters(self, iteration: int, total_iterations: int,
                      initial_learning_rate: float, initial_radius: float) -> Tuple[float, float]:
        """
        Get learning rate and neighborhood radius for current iteration
        
        Args:
            iteration: Current training iteration
            total_iterations: Total number of training iterations
            initial_learning_rate: Starting learning rate
            initial_radius: Starting neighborhood radius
            
        Returns:
            Tuple of (learning_rate, radius) for current iteration
        """
        return self.schedule.calculate_parameters(
            iteration, total_iterations, initial_learning_rate, 
            initial_radius, self.schedule_parameters
        )
    
    def get_configuration(self) -> Dict:
        """Get current configuration information"""
        return {
            'schedule_type': self.schedule_type,
            'schedule_class': self.schedule.__class__.__name__,
            'schedule_parameters': self.schedule_parameters.copy()
        }
    
    def get_parameter_trajectory(self, total_iterations: int,
                               initial_learning_rate: float, 
                               initial_radius: float) -> Dict:
        """
        Generate parameter trajectory over all iterations
        
        Useful for visualization and analysis of parameter schedules.
        
        Returns:
            Dictionary with 'iterations', 'learning_rates', and 'radii' arrays
        """
        iterations = np.arange(total_iterations)
        learning_rates = []
        radii = []
        
        for iteration in iterations:
            lr, radius = self.get_parameters(
                iteration, total_iterations, initial_learning_rate, initial_radius
            )
            learning_rates.append(lr)
            radii.append(radius)
        
        return {
            'iterations': iterations,
            'learning_rates': np.array(learning_rates),
            'radii': np.array(radii)
        }


def create_parameter_schedule(schedule_type: str, 
                            schedule_parameters: Optional[Dict] = None) -> ParameterScheduleManager:
    """
    Factory function to create parameter schedule managers
    
    Args:
        schedule_type: Type of schedule ('exponential', 'linear', etc.)
        schedule_parameters: Optional parameters for the schedule
        
    Returns:
        ParameterScheduleManager instance
    """
    return ParameterScheduleManager(schedule_type, schedule_parameters)


def get_available_schedules() -> list:
    """Get list of available parameter schedules"""
    return ['exponential', 'linear', 'inverse_time', 'power_law', 'step_decay', 'cyclic']


def get_schedule_default_parameters(schedule_type: str) -> Dict:
    """
    Get default parameters for each schedule type
    
    Args:
        schedule_type: Type of schedule
        
    Returns:
        Dictionary of default parameters
    """
    defaults = {
        'exponential': {},
        'linear': {},
        'inverse_time': {'tau': 100},
        'power_law': {'alpha': 0.5, 't0': 1.0},
        'step_decay': {'step_size': 250, 'decay_rate': 0.5},
        'cyclic': {'cycle_length': 100, 'min_factor': 0.1}
    }
    
    return defaults.get(schedule_type, {})