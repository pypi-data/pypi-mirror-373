"""
Quality assessment metrics for Bayesian Networks.
"""

import numpy as np
import pandas as pd
import networkx as nx
from typing import Dict, Any
from scipy.stats import entropy

class NetworkQualityMetrics:
    """Comprehensive quality assessment for generated networks."""
    
    @staticmethod
    def assess_network_quality(model, samples: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive quality assessment.
        
        Parameters:
        model: Bayesian Network model
        samples (DataFrame): Generated samples
        
        Returns:
        dict: Quality metrics
        """
        metrics = {}
        
        # Structural metrics
        metrics['structural'] = NetworkQualityMetrics._assess_structure(model)
        
        # Statistical metrics
        metrics['statistical'] = NetworkQualityMetrics._assess_statistics(samples)
        
        # Information theoretic metrics
        metrics['information'] = NetworkQualityMetrics._assess_information_content(samples)
        
        return metrics
    
    @staticmethod
    def _assess_structure(model) -> Dict[str, Any]:
        """Assess structural properties of the network."""
        G = nx.DiGraph(model.edges())
        
        structural_metrics = {
            'num_nodes': G.number_of_nodes(),
            'num_edges': G.number_of_edges(),
            'density': nx.density(G) if G.number_of_nodes() > 1 else 0,
            'is_dag': nx.is_directed_acyclic_graph(G),
        }
        
        try:
            if G.number_of_nodes() > 0:
                structural_metrics['avg_clustering'] = nx.average_clustering(G.to_undirected())
            else:
                structural_metrics['avg_clustering'] = 0
        except:
            structural_metrics['avg_clustering'] = 0
        
        try:
            if nx.is_connected(G.to_undirected()) and G.number_of_nodes() > 1:
                structural_metrics['avg_path_length'] = nx.average_shortest_path_length(G)
            else:
                structural_metrics['avg_path_length'] = None
        except:
            structural_metrics['avg_path_length'] = None
        
        try:
            if nx.is_directed_acyclic_graph(G) and G.number_of_edges() > 0:
                structural_metrics['longest_path'] = len(nx.dag_longest_path(G))
            else:
                structural_metrics['longest_path'] = 0
        except:
            structural_metrics['longest_path'] = 0
        
        return structural_metrics
    
    @staticmethod
    def _assess_statistics(samples: pd.DataFrame) -> Dict[str, Any]:
        """Assess statistical properties of generated samples."""
        if samples.empty:
            return {'error': 'Empty samples'}
        
        try:
            completeness = 1 - samples.isnull().sum().sum() / (len(samples) * len(samples.columns))
            
            # Calculate correlations safely
            numeric_samples = samples.select_dtypes(include=[np.number])
            if not numeric_samples.empty and len(numeric_samples.columns) > 1:
                corr_matrix = numeric_samples.corr()
                avg_correlation = corr_matrix.abs().mean().mean()
            else:
                avg_correlation = 0
            
            # Calculate entropy per column
            entropy_per_column = {}
            for col in samples.columns:
                try:
                    value_counts = samples[col].value_counts()
                    if len(value_counts) > 1:
                        entropy_per_column[col] = entropy(value_counts)
                    else:
                        entropy_per_column[col] = 0
                except:
                    entropy_per_column[col] = 0
            
            # Calculate class balance
            class_balance = {}
            for col in samples.columns:
                try:
                    normalized_counts = samples[col].value_counts(normalize=True)
                    if len(normalized_counts) > 0:
                        class_balance[col] = normalized_counts.min()
                    else:
                        class_balance[col] = 0
                except:
                    class_balance[col] = 0
            
            return {
                'sample_size': len(samples),
                'completeness': completeness,
                'avg_correlation': avg_correlation,
                'entropy_per_column': entropy_per_column,
                'class_balance': class_balance,
                'avg_entropy': np.mean(list(entropy_per_column.values())),
                'avg_class_balance': np.mean(list(class_balance.values()))
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def _assess_information_content(samples: pd.DataFrame) -> Dict[str, Any]:
        """Assess information theoretic properties."""
        try:
            info_metrics = {}
            
            # Mutual information between columns
            mutual_info_sum = 0
            pair_count = 0
            
            for i, col1 in enumerate(samples.columns):
                for j, col2 in enumerate(samples.columns[i+1:], i+1):
                    try:
                        # Simple mutual information approximation
                        joint_counts = pd.crosstab(samples[col1], samples[col2])
                        if joint_counts.size > 1:
                            joint_probs = joint_counts / joint_counts.sum().sum()
                            marginal1 = joint_probs.sum(axis=1)
                            marginal2 = joint_probs.sum(axis=0)
                            
                            mi = 0
                            for r in joint_probs.index:
                                for c in joint_probs.columns:
                                    if joint_probs.loc[r, c] > 0:
                                        mi += joint_probs.loc[r, c] * np.log2(
                                            joint_probs.loc[r, c] / (marginal1[r] * marginal2[c])
                                        )
                            
                            mutual_info_sum += mi
                            pair_count += 1
                    except:
                        continue
            
            info_metrics['avg_mutual_information'] = mutual_info_sum / max(1, pair_count)
            
            return info_metrics
        except Exception as e:
            return {'error': str(e)}