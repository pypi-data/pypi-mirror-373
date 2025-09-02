"""
Network generation classes and utilities.
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
from .core import create_pgm

class NetworkGenerator:
    """
    Advanced Bayesian Network generator with comprehensive configuration options.
    """
    
    def __init__(self):
        self.topology_types = [
            "random", "hierarchical", "small_world", "scale_free", "layered"
        ]
        
        self.distribution_types = [
            "uniform", "dirichlet", "beta", "power_law", "contextual"
        ]
        
        self.cardinality_presets = {
            "binary": 2,
            "ternary": 3,
            "quaternary": 4,
            "mixed_small": {"N0": 2, "N1": 3, "N2": 2, "default": 2},
            "mixed_large": {"N0": 2, "N1": 3, "N2": 4, "N3": 5, "N4": 6, "default": 3},
            "high_cardinality": 8
        }
    
    def generate_network(self, **kwargs) -> Dict[str, Any]:
        """
        Generate a Bayesian Network with specified parameters.
        
        Returns:
        dict: Complete network generation result
        """
        return create_pgm(**kwargs)
    
    def generate_multiple_networks(self, configurations: List[Dict]) -> List[Dict[str, Any]]:
        """
        Generate multiple networks with different configurations.
        
        Parameters:
        configurations (list): List of configuration dictionaries
        
        Returns:
        list: List of generation results
        """
        results = []
        for config in configurations:
            result = self.generate_network(**config)
            results.append(result)
        return results
    
    def get_topology_types(self) -> List[str]:
        """Get available topology types."""
        return self.topology_types.copy()
    
    def get_distribution_types(self) -> List[str]:
        """Get available distribution types."""
        return self.distribution_types.copy()
    
    def get_cardinality_presets(self) -> Dict[str, Any]:
        """Get available cardinality presets."""
        return self.cardinality_presets.copy()
    
    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate generation parameters.
        
        Returns:
        bool: True if parameters are valid
        """
        """
        bool: True if parameters are valid
        """
        num_nodes = kwargs.get('num_nodes', 3)
        if not isinstance(num_nodes, int) or num_nodes < 1:
            raise ValueError("num_nodes must be a positive integer")
        
        # Warning for large networks
        if num_nodes > 50:
            import warnings
            warnings.warn(
                f"Creating a network with {num_nodes} nodes. "
                "Networks with more than 50 nodes may have significantly slower generation times "
                "and higher memory usage. Consider reducing the number of nodes or increasing "
                "available system resources for optimal performance.",
                UserWarning,
                stacklevel=2
            )
        
        sample_size = kwargs.get('sample_size', 1000)
        if not isinstance(sample_size, int) or sample_size < 100:
            raise ValueError("sample_size must be an integer >= 100")
        
        density = kwargs.get('density', 'normal')
        if density not in ['sparse', 'normal', 'dense']:
            raise ValueError("density must be 'sparse', 'normal', or 'dense'")
        
        topology_type = kwargs.get('topology_type', 'random')
        if topology_type not in self.topology_types:
            raise ValueError(f"topology_type must be one of {self.topology_types}")
        
        return True