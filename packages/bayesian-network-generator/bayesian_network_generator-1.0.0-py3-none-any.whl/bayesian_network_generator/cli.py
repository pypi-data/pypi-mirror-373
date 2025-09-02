"""
Command-line interface for Bayesian Network Generator.
"""

import argparse
import json
import sys
import warnings
from pathlib import Path
from typing import Dict, Any

# Suppress specific pgmpy deprecation warnings
warnings.filterwarnings("ignore", 
                       message="Passing a DataFrame to DataFrame.from_records is deprecated.*",
                       category=FutureWarning,
                       module="pgmpy.*")

warnings.filterwarnings("ignore",
                       message="Probability values don't exactly sum to 1.*",
                       category=UserWarning,
                       module="pgmpy.*")

from .network_generator import NetworkGenerator

def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description='Generate synthetic Bayesian Networks with various configurations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a simple 5-node network
  bayesian-network-generator --num_vars 5 --num_samples 1000
  
  # Generate multiple networks with custom parameters
  bayesian-network-generator --num_vars 10 --num_samples 2000 --num_networks 5 \\
                           --topology_type polytree --distribution_type beta \\
                           --output_dir my_networks
  
  # Generate network with comprehensive data quality issues
  bayesian-network-generator --num_vars 8 --noise_type missing --noise_level 0.1 --skew 2.5 \\
                           --duplicate_rate 0.15 --temporal_drift 0.05 --measurement_bias 0.1
  
  # Use custom cardinalities
  bayesian-network-generator --num_vars 5 --cardinalities 2,3,4,2,3
        """
    )
    
    # Basic parameters
    parser.add_argument('--num_vars', type=int, default=5,
                       help='Number of variables/nodes in the network (default: 5)')
    parser.add_argument('--num_samples', type=int, default=1000,
                       help='Number of samples to generate (default: 1000)')
    parser.add_argument('--num_networks', type=int, default=1,
                       help='Number of networks to generate (default: 1)')
    
    # Network structure
    parser.add_argument('--topology_type', choices=['tree', 'polytree', 'dag'], 
                       default='dag', help='Network topology type (default: dag)')
    parser.add_argument('--max_parents', type=int, default=3,
                       help='Maximum number of parents per node (default: 3)')
    parser.add_argument('--cardinalities', type=str,
                       help='Comma-separated cardinalities for variables (e.g., "2,3,4,2,3")')
    
    # Distribution parameters
    parser.add_argument('--distribution_type', 
                       choices=['uniform', 'dirichlet', 'beta'], 
                       default='dirichlet',
                       help='Distribution type for CPDs (default: dirichlet)')
    parser.add_argument('--alpha', type=float, default=1.0,
                       help='Alpha parameter for distribution (default: 1.0)')
    parser.add_argument('--beta', type=float, default=1.0,
                       help='Beta parameter for Beta distribution (default: 1.0)')
    
    # Data deterioration
    parser.add_argument('--noise_type', 
                       choices=['missing', 'outliers', 'mislabeling', 'mixed', 'none'], 
                       default='none',
                       help='Type of data deterioration to apply (default: none)')
    parser.add_argument('--noise_level', type=float, default=0.0,
                       help='Level of data deterioration (0.0-1.0, default: 0.0)')
    parser.add_argument('--skew', type=float, default=1.0,
                       help='Variable skew for feature imbalance (data deterioration). 1.0=no skew, >1.0=positive skew, <1.0=negative skew (default: 1.0)')
    
    # Advanced data quality issues
    parser.add_argument('--duplicate_rate', type=float, default=0.0,
                       help='Rate of duplicate records to introduce (0.0-0.5, default: 0.0)')
    parser.add_argument('--temporal_drift', type=float, default=0.0,
                       help='Temporal distribution drift strength (0.0-1.0, default: 0.0)')
    parser.add_argument('--measurement_bias', type=float, default=0.0,
                       help='Systematic measurement bias level (0.0-1.0, default: 0.0)')
    
    # Output options
    parser.add_argument('--output_dir', type=str, default='bn_output',
                       help='Output directory (default: bn_output)')
    parser.add_argument('--save_samples', action='store_true',
                       help='Save generated samples to CSV')
    parser.add_argument('--save_network', action='store_true',
                       help='Save network structure')
    parser.add_argument('--create_visualizations', action='store_true',
                       help='Create network visualizations')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    # Configuration file
    parser.add_argument('--config', type=str,
                       help='Path to JSON configuration file')
    
    return parser

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)

def parse_cardinalities(cardinalities_str: str) -> list:
    """Parse cardinalities string into list of integers."""
    try:
        return [int(x.strip()) for x in cardinalities_str.split(',')]
    except ValueError:
        print("Error: Cardinalities must be comma-separated integers")
        sys.exit(1)

def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Load configuration file if provided
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Override config with command line arguments
    params = {
        'num_vars': args.num_vars,
        'num_samples': args.num_samples,
        'topology_type': args.topology_type,
        'max_parents': args.max_parents,
        'distribution_type': args.distribution_type,
        'alpha': args.alpha,
        'beta': args.beta,
        'noise_type': args.noise_type,
        'noise_level': args.noise_level,
        'skew': args.skew,
        'duplicate_rate': args.duplicate_rate,
        'temporal_drift': args.temporal_drift,
        'measurement_bias': args.measurement_bias,
        'output_dir': args.output_dir,
        'save_samples': args.save_samples,
        'save_network': args.save_network,
        'create_visualizations': args.create_visualizations,
        'verbose': args.verbose
    }
    
    # Parse cardinalities if provided
    if args.cardinalities:
        cardinalities = parse_cardinalities(args.cardinalities)
        if len(cardinalities) != args.num_vars:
            print(f"Error: Number of cardinalities ({len(cardinalities)}) must match num_vars ({args.num_vars})")
            sys.exit(1)
        params['cardinalities'] = cardinalities
    
    # Update with config file values (command line takes precedence)
    for key, value in config.items():
        if key not in params or params[key] == parser.get_default(key):
            params[key] = value
    
    try:
        # Create generator
        generator = NetworkGenerator()
        
        if args.verbose:
            print(f"Generating {args.num_networks} network(s) with parameters:")
            for key, value in params.items():
                if key not in ['output_dir', 'save_samples', 'save_network', 'create_visualizations', 'verbose']:
                    print(f"  {key}: {value}")
            print()
        
        # Prepare generation parameters (map CLI params to core function params)
        gen_params = {
            'num_nodes': params['num_vars'],
            'sample_size': params['num_samples'],
            'topology_type': params['topology_type'],
            'max_indegree': params['max_parents'],
            'distribution_type': params['distribution_type'],
            'skew': params['skew'],
            'duplicate_rate': params['duplicate_rate'],
            'temporal_drift': params['temporal_drift'],
            'measurement_bias': params['measurement_bias'],
            'quality_assessment': True
        }
        
        # Handle data deterioration based on noise_type
        if params['noise_type'] == 'missing':
            gen_params['missing_data_percentage'] = params['noise_level']
            gen_params['noise'] = 0.0
        elif params['noise_type'] in ['outliers', 'mislabeling', 'mixed']:
            gen_params['noise'] = params['noise_level']
            gen_params['missing_data_percentage'] = 0.0
        else:  # noise_type == 'none'
            gen_params['noise'] = 0.0
            gen_params['missing_data_percentage'] = 0.0
        
        # Add cardinalities if specified
        if 'cardinalities' in params:
            if len(params['cardinalities']) == params['num_vars']:
                # Create cardinality dict
                cardinality_dict = {f"N{i}": card for i, card in enumerate(params['cardinalities'])}
                gen_params['node_cardinality'] = cardinality_dict
            else:
                gen_params['node_cardinality'] = params['cardinalities'][0] if params['cardinalities'] else 2
        else:
            gen_params['node_cardinality'] = 2
        
        # Generate networks
        results = []
        for i in range(args.num_networks):
            if args.verbose and args.num_networks > 1:
                print(f"Generating network {i+1}/{args.num_networks}...")
            result = generator.generate_network(**gen_params)
            
            # Handle output saving
            if args.save_samples or args.save_network or args.create_visualizations:
                output_dir = Path(args.output_dir)
                if args.num_networks > 1:
                    network_dir = output_dir / f"network_{i+1}"
                else:
                    network_dir = output_dir
                network_dir.mkdir(parents=True, exist_ok=True)
                
                # Save samples
                if args.save_samples and 'samples' in result and result['samples'] is not None:
                    samples_file = network_dir / "samples.csv"
                    result['samples'].to_csv(samples_file, index=False)
                    if args.verbose:
                        print(f"  Saved samples to: {samples_file}")
                
                # Save network structure
                if args.save_network and 'model' in result:
                    import json
                    network_file = network_dir / "network_structure.json"
                    network_info = {
                        'nodes': list(result['model'].nodes()),
                        'edges': list(result['model'].edges()),
                        'parameters': gen_params
                    }
                    with open(network_file, 'w') as f:
                        json.dump(network_info, f, indent=2)
                    if args.verbose:
                        print(f"  Saved network structure to: {network_file}")
                
                # Create visualizations
                if args.create_visualizations and 'model' in result:
                    try:
                        import matplotlib.pyplot as plt
                        import networkx as nx
                        
                        fig, ax = plt.subplots(figsize=(10, 8))
                        G = nx.DiGraph()
                        G.add_edges_from(result['model'].edges())
                        pos = nx.spring_layout(G)
                        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                               node_size=1000, font_size=12, ax=ax)
                        ax.set_title("Bayesian Network Structure")
                        
                        viz_file = network_dir / "network_visualization.png"
                        plt.savefig(viz_file, dpi=300, bbox_inches='tight')
                        plt.close()
                        if args.verbose:
                            print(f"  Saved visualization to: {viz_file}")
                    except Exception as e:
                        if args.verbose:
                            print(f"  Warning: Could not create visualization: {e}")
            
            results.append(result)
        
        print(f"Successfully generated {len(results)} network(s)")
        print(f"Output saved to: {args.output_dir}")
        
        # Print summary statistics
        if args.verbose and results:
            sample_result = results[0]
            if 'samples' in sample_result and sample_result['samples'] is not None:
                print(f"Sample statistics for first network:")
                print(f"  Samples shape: {sample_result['samples'].shape}")
                print(f"  Variables: {list(sample_result['samples'].columns)}")
                if 'quality_metrics' in sample_result:
                    print(f"  Structural metrics: {sample_result['quality_metrics'].get('structural', {})}")
        
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()