"""
Core Bayesian Network generation functions.
"""

import networkx as nx
import numpy as np

# Compatibility patch for numpy.product deprecation
if not hasattr(np, 'product'):
    np.product = np.prod

import itertools
import random
import time
import matplotlib.pyplot as plt
import warnings
import pandas as pd

# Suppress specific pgmpy deprecation warnings
warnings.filterwarnings("ignore", 
                       message="Passing a DataFrame to DataFrame.from_records is deprecated.*",
                       category=FutureWarning,
                       module="pgmpy.*")

# Also suppress other common pgmpy warnings for cleaner output
warnings.filterwarnings("ignore",
                       message="Probability values don't exactly sum to 1.*",
                       category=UserWarning,
                       module="pgmpy.*")
from functools import wraps
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from scipy.stats import entropy, beta, dirichlet
from datetime import datetime
import os
from pathlib import Path
import logging

try:
    from pgmpy.models import DiscreteBayesianNetwork as BayesianNetwork
except ImportError:
    from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.sampling import BayesianModelSampling

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_noise_to_data(data, noise_level=0.1):
    """
    Add random noise to the data.

    Parameters:
    data (DataFrame): The dataset to which noise is to be added.
    noise_level (float): The proportion of data to be noised, between 0 and 1.

    Returns:
    DataFrame: The dataset with added noise.
    """
    if not 0 <= noise_level <= 1:
        raise ValueError("Noise level must be between 0 and 1")
    
    if data.empty:
        return data
    
    noisy_data = data.copy()
    num_rows, num_cols = noisy_data.shape
    total_values = num_rows * num_cols
    num_noisy_values = int(total_values * noise_level)
    
    for _ in range(num_noisy_values):
        row_index = np.random.randint(num_rows)
        col_index = np.random.randint(num_cols)
        column_name = noisy_data.columns[col_index]
        max_value = noisy_data[column_name].max()
        if pd.notna(max_value):
            noisy_data.iat[row_index, col_index] = np.random.randint(max_value + 1)
    
    return noisy_data

def add_missing_data(data, missing_data_percentage=0.1):
    """
    Add missing data to the dataset.

    Parameters:
    data (DataFrame): The dataset to which missing data is to be added.
    missing_data_percentage (float): The proportion of missing data, between 0 and 1.

    Returns:
    DataFrame: The dataset with added missing data.
    """
    if not 0 <= missing_data_percentage <= 1:
        raise ValueError("Missing data percentage must be between 0 and 1")
    
    if data.empty:
        return data
    
    missing_data = data.copy()
    num_rows, num_cols = missing_data.shape
    total_values = num_rows * num_cols
    num_missing_values = int(total_values * missing_data_percentage)
    
    for _ in range(num_missing_values):
        row_index = np.random.randint(num_rows)
        col_index = np.random.randint(num_cols)
        missing_data.iat[row_index, col_index] = np.nan
    
    return missing_data

def generate_edges(num_nodes, name_of_nodes, max_indegree, density):
    """
    Generate edges for Bayesian Network ensuring DAG property.
    
    Parameters:
    num_nodes (int): Number of nodes
    name_of_nodes (list): List of node names
    max_indegree (int): Maximum in-degree for any node
    density (str): Network density - 'sparse', 'normal', or 'dense'
    
    Returns:
    list: List of edges as tuples
    """
    if not isinstance(num_nodes, int) or num_nodes <= 0:
        raise ValueError("num_nodes must be a positive integer")
    if not isinstance(max_indegree, int) or max_indegree < 1:
        raise ValueError("max_indegree must be a positive integer")
    
    if num_nodes == 1:
        return []
    
    all_possible_edges = list(itertools.permutations(name_of_nodes, 2))
    random.shuffle(all_possible_edges)
    
    graph = nx.DiGraph()
    edges = set()
    
    for edge in all_possible_edges:
        if len([e for e in edges if e[1] == edge[1]]) < max_indegree:
            graph.add_edge(*edge)
            if nx.is_directed_acyclic_graph(graph):
                edges.add(edge)
            else:
                graph.remove_edge(*edge)
    
    max_edges = len(edges)
    edge_count = {
        "normal": max_edges // 2, 
        "sparse": max_edges // 4, 
        "dense": max_edges
    }.get(density, max_edges)
    
    return list(edges)[:edge_count]

def apply_skew(values, max_skew):
    """
    Apply skew to probability values.
    
    Parameters:
    values (numpy.ndarray): Probability values
    max_skew (float): Maximum skew factor
    
    Returns:
    numpy.ndarray: Skewed probability values
    """
    if max_skew is None or max_skew == 0:
        return values

    num_states = values.shape[0]
    if max_skew >= 1:
        random_skew_factors = np.random.uniform(1, max_skew, size=num_states)
    else:
        random_skew_factors = np.random.uniform(max_skew, 1, size=num_states)

    for i in range(num_states):
        values[i, :] *= random_skew_factors[i]

    values /= values.sum(axis=0, keepdims=True)
    return values


def add_duplicate_records(samples, duplicate_rate):
    """
    Add duplicate records to simulate real-world data duplication.
    
    Parameters:
    samples (pandas.DataFrame): Original samples
    duplicate_rate (float): Proportion of records to duplicate (0.0-0.5)
    
    Returns:
    pandas.DataFrame: Samples with duplicates added
    """
    if duplicate_rate <= 0 or duplicate_rate > 0.5:
        return samples
    
    num_samples = len(samples)
    num_duplicates = int(num_samples * duplicate_rate)
    
    # Randomly select records to duplicate
    duplicate_indices = np.random.choice(num_samples, size=num_duplicates, replace=True)
    duplicated_records = samples.iloc[duplicate_indices].copy()
    
    # Concatenate original samples with duplicates
    result = pd.concat([samples, duplicated_records], ignore_index=True)
    
    # Shuffle to mix duplicates throughout the dataset
    result = result.sample(frac=1).reset_index(drop=True)
    
    return result


def apply_temporal_drift(samples, drift_strength):
    """
    Apply temporal distribution drift to simulate data evolution over time.
    
    Parameters:
    samples (pandas.DataFrame): Original samples
    drift_strength (float): Strength of temporal drift (0.0-1.0)
    
    Returns:
    pandas.DataFrame: Samples with temporal drift applied
    """
    if drift_strength <= 0:
        return samples
    
    num_samples = len(samples)
    samples_copy = samples.copy()
    
    # Create time-based drift pattern
    time_factor = np.linspace(0, 1, num_samples)
    
    for col in samples.columns:
        # Check if column is discrete (integer/categorical)
        is_discrete = samples[col].dtype == 'int64' or len(samples[col].unique()) <= 10
        
        if is_discrete:
            # For categorical/discrete columns, gradually change distribution
            unique_vals = samples[col].unique()
            if len(unique_vals) > 1:
                # Create probability shift over time - keep it minimal to preserve structure
                for i in range(num_samples):
                    current_val = samples_copy.iloc[i][col]
                    # Apply time-dependent probability change
                    change_prob = drift_strength * time_factor[i] * 0.05  # Reduced intensity
                    if np.random.random() < change_prob:
                        # Randomly change to a different value
                        other_vals = [v for v in unique_vals if v != current_val]
                        if other_vals:
                            samples_copy.iloc[i, samples_copy.columns.get_loc(col)] = np.random.choice(other_vals)
        else:
            # For continuous columns, apply small gradual shift
            drift_effect = drift_strength * time_factor * np.random.normal(0, 0.01, num_samples)
            samples_copy[col] = samples[col] + drift_effect
    
    return samples_copy


def apply_measurement_bias(samples, bias_strength):
    """
    Apply systematic measurement bias to simulate sensor/collection errors.
    
    Parameters:
    samples (pandas.DataFrame): Original samples
    bias_strength (float): Strength of measurement bias (0.0-1.0)
    
    Returns:
    pandas.DataFrame: Samples with measurement bias applied
    """
    if bias_strength <= 0:
        return samples
    
    samples_copy = samples.copy()
    
    for col in samples.columns:
        # Check if column is discrete (integer/categorical)
        is_discrete = samples[col].dtype == 'int64' or len(samples[col].unique()) <= 10
        
        if is_discrete:
            # For categorical/discrete columns, introduce systematic label bias
            unique_vals = samples[col].unique()
            if len(unique_vals) > 1:
                # Bias toward one particular category
                favored_category = np.random.choice(unique_vals)
                bias_mask = np.random.random(len(samples)) < bias_strength * 0.1  # Reduced intensity
                samples_copy.loc[bias_mask, col] = favored_category
        else:
            # Apply systematic bias to continuous columns
            bias_direction = np.random.choice([-1, 1])  # Random bias direction
            bias_magnitude = bias_strength * samples[col].std() * 0.1  # Reduced magnitude
            samples_copy[col] = samples[col] + (bias_direction * bias_magnitude)
    
    return samples_copy

def generate_cpds(model, node_cardinality, max_skew):
    """
    Generate Conditional Probability Distributions for the network.
    
    Parameters:
    model: Bayesian Network model
    node_cardinality (dict): Node cardinality mapping
    max_skew (float): Maximum skew to apply
    
    Returns:
    dict: Dictionary of CPDs
    """
    if max_skew is not None and not isinstance(max_skew, (float, int)):
        raise ValueError("max_skew must be a float or an integer.")

    if max_skew is not None and max_skew < 0:
        raise ValueError("max_skew must be a positive value greater than 0.")

    cpds = {}
    
    for node in model.nodes():
        try:
            parents = model.get_parents(node)
            variable_card = node_cardinality.get(node, 2)
            parent_cardinalities = [node_cardinality.get(parent, 2) for parent in parents]
            values = np.random.rand(variable_card, np.prod(parent_cardinalities) if parents else 1)

            # Normalize
            values = values / values.sum(axis=0, keepdims=True)
    
            # Apply skew
            if max_skew is not None and max_skew != 1:
                values = apply_skew(values, max_skew)
    
            cpd = TabularCPD(variable=node, variable_card=variable_card, values=values, 
                           evidence=parents, evidence_card=parent_cardinalities)
            cpds[node] = cpd
        except Exception as e:
            logger.error(f"Error while generating CPD for node {node}: {e}")
            raise ValueError(f"Error while generating CPD for node {node}: {e}")

    return cpds

def _prepare_nodes_and_model(num_nodes, node_cardinality, max_indegree, density, topology_type="random"):
    """
    Prepare nodes and model for network generation.
    """
    # Generate node names
    if isinstance(node_cardinality, dict) and len(node_cardinality) > 1:
        existing_names = set(node_cardinality.keys()) - {'default'}
        name_of_nodes = list(existing_names)
        additional_nodes_needed = num_nodes - len(existing_names)

        if additional_nodes_needed > 0:
            additional_names = [f'N{i}' for i in range(len(existing_names), num_nodes)]
            name_of_nodes.extend(additional_names)
    else:
        name_of_nodes = [f'N{i}' for i in range(num_nodes)]

    # Remove 'default' if it accidentally becomes a node name
    if 'default' in name_of_nodes:
        name_of_nodes.remove('default')

    # Generate edges
    edges = generate_edges(num_nodes, name_of_nodes, max_indegree, density)

    # Initialize Bayesian Network model
    model = BayesianNetwork(edges)

    # Setup node cardinality dictionary
    if isinstance(node_cardinality, int):
        node_cardinality_dict = {node: node_cardinality for node in name_of_nodes}
    elif isinstance(node_cardinality, dict):
        default_cardinality = node_cardinality.get('default', 2)
        node_cardinality_dict = {node: node_cardinality.get(node, default_cardinality) 
                               for node in name_of_nodes}
    else:
        raise ValueError("node_cardinality must be an integer or a dictionary")

    # Remove 'default' from node_cardinality dictionary if present
    if 'default' in node_cardinality_dict:
        del node_cardinality_dict['default']

    return name_of_nodes, edges, model, node_cardinality_dict

def _generate_samples(model, sample_size, noise, missing_data_percentage):
    """
    Generate samples from the Bayesian Network.
    """
    sampler = BayesianModelSampling(model)
    samples = sampler.forward_sample(size=sample_size)

    if noise > 0:
        samples = add_noise_to_data(samples, noise_level=noise)

    if missing_data_percentage > 0:
        samples = add_missing_data(samples, missing_data_percentage=missing_data_percentage)

    return samples

def create_pgm(
    num_nodes: int = 3,
    node_cardinality = 2,
    max_indegree: int = 2,
    density: str = "normal",
    topology_type: str = "random",
    distribution_type: str = "uniform",
    skew: float = 1,
    noise: float = 0,
    missing_data_percentage: float = 0,
    sample_size: int = 1000,
    quality_assessment: bool = False,
    # New enhanced data quality parameters
    duplicate_rate: float = 0,
    temporal_drift: float = 0,
    measurement_bias: float = 0
) -> Dict[str, Any]:
    """
    Create a Probabilistic Graphical Model (Bayesian Network).
    
    Parameters:
    num_nodes (int): Number of nodes in the network
    node_cardinality (int or dict): Cardinality of nodes
    max_indegree (int): Maximum in-degree for any node
    density (str): Network density - 'normal', 'sparse', or 'dense'
    topology_type (str): Network topology type
    distribution_type (str): Probability distribution type
    skew (float): Skew to be applied to probabilities
    noise (float): Noise level to be added to the data
    missing_data_percentage (float): Percentage of missing data
    sample_size (int): Number of samples to be generated
    quality_assessment (bool): Whether to perform quality assessment
    duplicate_rate (float): Rate of duplicate records (0.0-0.5)
    temporal_drift (float): Strength of temporal distribution drift (0.0-1.0)
    measurement_bias (float): Strength of systematic measurement bias (0.0-1.0)
    
    Returns:
    dict: Dictionary containing the model, samples, and runtime
    """
    
    start_time = time.time()
    logger.info(f"Starting PGM creation with {num_nodes} nodes")
    
    # Validate parameters
    sample_size = int(sample_size)
    if num_nodes <= 0:
        raise ValueError("num_nodes must be positive")
    
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
    
    if not 0 <= noise <= 1:
        noise = 0
    if not 0 <= missing_data_percentage <= 1:
        missing_data_percentage = 0
    
    try:
        # Prepare nodes and model
        name_of_nodes, edges, model, node_cardinality_dict = _prepare_nodes_and_model(
            num_nodes, node_cardinality, max_indegree, density, topology_type)
        
        logger.info(f'Generated {len(edges)} edges for the Bayesian Network')
        
        # Generate CPDs
        cpds = generate_cpds(model, node_cardinality_dict, skew)
        
        # Add CPDs to model and validate
        for cpd in cpds.values():
            model.add_cpds(cpd)
        
        if not model.check_model():
            raise ValueError("Invalid model configuration")
        
        # Generate samples
        samples = _generate_samples(model, sample_size, noise, missing_data_percentage)
        
        # Apply enhanced data quality issues
        if duplicate_rate > 0:
            samples = add_duplicate_records(samples, duplicate_rate)
            logger.info(f"Applied duplicate records with rate {duplicate_rate}")
        
        if temporal_drift > 0:
            samples = apply_temporal_drift(samples, temporal_drift)
            logger.info(f"Applied temporal drift with strength {temporal_drift}")
        
        if measurement_bias > 0:
            samples = apply_measurement_bias(samples, measurement_bias)
            logger.info(f"Applied measurement bias with strength {measurement_bias}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.info(f"PGM creation completed in {total_time:.3f} seconds")
        
        result = {
            'model': model,
            'samples': samples,
            'runtime': total_time
        }
        
        if quality_assessment:
            from .quality_metrics import NetworkQualityMetrics
            result['quality_metrics'] = NetworkQualityMetrics.assess_network_quality(model, samples)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in PGM creation: {e}")
        raise

# Alias for advanced functionality
def create_comprehensive_pgm(*args, **kwargs):
    """
    Create a comprehensive Bayesian Network with advanced features.
    
    This is an alias for create_pgm with quality_assessment enabled by default.
    """
    kwargs.setdefault('quality_assessment', True)
    return create_pgm(*args, **kwargs)