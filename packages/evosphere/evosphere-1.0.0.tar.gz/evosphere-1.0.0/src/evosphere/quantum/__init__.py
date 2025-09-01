"""
Hybrid Quantum-Evolutionary State-Space Engine (HQESE)

Patent-pending quantum computing framework for evolutionary biology.
"""

from .quantum_engine import HQESE
from .state_space import QuantumStateSpace
from .operators import EvolutionaryOperators

__all__ = [
    "HQESE",
    "QuantumStateSpace", 
    "EvolutionaryOperators",
]
