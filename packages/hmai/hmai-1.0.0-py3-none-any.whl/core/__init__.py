"""
Hyper-Material AI (HMAI) Core Package

A revolutionary AI framework for inventing new classes of matter through
generative quantum field theory, materials-to-quantum bridging, and
entropic assembly optimization.

Author: HMAI Research Team
Date: August 31, 2025
License: Dual License (Research/Commercial)
"""

from .gqft_engine import GenerativeQuantumFieldEngine
from .mqb_compiler import MaterialsQuantumBridge
from .eao_optimizer import EntropicAssemblyOptimizer
from .validation import HyperPropertiesValidator

__version__ = "1.0.0"
__author__ = "HMAI Research Team"

__all__ = [
    "GenerativeQuantumFieldEngine",
    "MaterialsQuantumBridge", 
    "EntropicAssemblyOptimizer",
    "HyperPropertiesValidator"
]
