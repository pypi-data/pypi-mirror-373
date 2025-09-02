"""
SNP: Stepwise Noise Peeling for Nadaraya-Watson Regression

This package implements the Stepwise Noise Peeling algorithm for efficient bandwidth 
selection in Nadaraya-Watson regression with Gaussian kernels. SNP provides a scalable 
alternative to Direct Generalized Cross-Validation (DGCV) by converting continuous 
bandwidth optimization into discrete iteration selection, dramatically reducing 
computational cost while maintaining statistical equivalence.

Key Features:
- Fast: Orders of magnitude faster than DGCV for large datasets
- Accurate: Statistically equivalent results to DGCV  
- Adaptive: Automatically adjusts bandwidth through iterative process
- Robust: Handles edge cases and various data sizes
"""

from .core import SNP, DGCV, construct_W
from .examples import example_stepwise, example_wavy, example_california_housing

__version__ = "0.1.0"
__author__ = "Bistoon Hosseini"
__email__ = "bistoon.hosseini@gmail.com"

__all__ = ["SNP", "DGCV", "construct_W", "example_stepwise", "example_wavy", "example_california_housing"]