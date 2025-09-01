"""
Multi-Resolution Adaptive Evolutionary Graph (MRAEG)

Patent-pending graph neural network framework for evolutionary biology.
"""

from .adaptive_graph import MRAEG
from .graph_layers import MultiScaleGNN, EvolutionaryGAT
from .temporal_dynamics import TemporalGraphEngine

__all__ = [
    "MRAEG",
    "MultiScaleGNN",
    "EvolutionaryGAT", 
    "TemporalGraphEngine",
]
