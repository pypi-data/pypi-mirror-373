"""
Bayesian Network Generator v1.0.0

Advanced Python package for generating realistic Bayesian Networks with comprehensive
topology and distribution support.
"""

import warnings

# Suppress specific pgmpy deprecation warnings for cleaner output
warnings.filterwarnings("ignore", 
                       message="Passing a DataFrame to DataFrame.from_records is deprecated.*",
                       category=FutureWarning,
                       module="pgmpy.*")

warnings.filterwarnings("ignore",
                       message="Probability values don't exactly sum to 1.*",
                       category=UserWarning,
                       module="pgmpy.*")

__version__ = "1.0.0"
__author__ = "Rudzani Mulaudzi"
__email__ = "rudzani.mulaudzi2@students.wits.ac.za"

from .core import create_pgm, create_comprehensive_pgm
from .network_generator import NetworkGenerator
from .quality_metrics import NetworkQualityMetrics

__all__ = [
    'create_pgm',
    'create_comprehensive_pgm', 
    'NetworkGenerator',
    'NetworkQualityMetrics'
]