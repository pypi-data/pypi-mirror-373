"""
EvoSphere - The Evolutionary Bio-Compiler

A quantum-enhanced evolutionary system for biological design and optimization.
Integrates six patent-pending innovations for comprehensive biological modeling.

Patent Innovations:
1. HQESE - Hybrid Quantum-Evolutionary State-Space Engine
2. MRAEG - Multi-Resolution Adaptive Evolutionary Graphs
3. EvoByte - Evolutionary Bio-Compilation System
4. SEPD - Smart Evolutionary Pathway Designer
5. EDAL - Evolutionary Data Assimilation Layer
6. CECE - Cross-Scale Evolutionary Coupling Engine

Authors: Krishna Bajpai and Vedanshi Gupta
License: Patent Pending
"""

__version__ = "1.0.0"
__authors__ = ["Krishna Bajpai", "Vedanshi Gupta"]
__email__ = ["krishna@krishnabajpai.me", "vedanshigupta158@gmail.com"]
__license__ = "Patent Pending"

# Core components
from .core.engine import EvoSphere
from .quantum.quantum_engine import QuantumEvolutionEngine
from .quantum.state_space import QuantumStateSpace
from .quantum.operators import QuantumEvolutionOperators
from .graph.adaptive_graph import AdaptiveEvolutionaryGraph
from .compiler.compiler import EvoCompiler
from .compiler.language import EvoLanguage, EvoLanguageParser
from .designer.pathway_designer import SmartEvolutionaryPathwayDesigner
from .designer.constraint_engine import ConstraintEngine
from .designer.optimization_engine import OptimizationEngine
from .assimilation import EDAL
from .coupling import CECE

# Patent systems (aliases for convenience)
HQESE = QuantumEvolutionEngine
MRAEG = AdaptiveEvolutionaryGraph
EvolutionaryBioCompiler = EvoCompiler  # Alias for compatibility
EvoByte = EvoCompiler
EvoByte = EvolutionaryBioCompiler
SEPD = SmartEvolutionaryPathwayDesigner

__all__ = [
    # Core system
    'EvoSphere',
    
    # Quantum components (HQESE)
    'QuantumEvolutionEngine',
    'QuantumStateSpace', 
    'QuantumEvolutionOperators',
    'HQESE',
    
    # Graph components (MRAEG)
    'AdaptiveEvolutionaryGraph',
    'MRAEG',
    
    # Compiler components (EvoByte)
    'EvoCompiler',
    'EvolutionaryBioCompiler',  # Alias
    'EvoLanguage',
    'EvoLanguageParser',
    'EvoByte',
    
    # Designer components (SEPD)
    'SmartEvolutionaryPathwayDesigner',
    'ConstraintEngine',
    'OptimizationEngine',
    'SEPD',
    
    # Assimilation system (EDAL)
    'EDAL',
    
    # Coupling system (CECE)
    'CECE',
    
    # Package info
    '__version__',
    '__authors__',
    '__email__',
    '__license__'
]

# Patent information
PATENT_INFO = {
    'filing_date': '2024',
    'inventors': ['Krishna Bajpai', 'Vedanshi Gupta'],
    'title': 'Quantum-Enhanced Evolutionary Bio-Compiler System',
    'innovations': [
        'HQESE - Hybrid Quantum-Evolutionary State-Space Engine',
        'MRAEG - Multi-Resolution Adaptive Evolutionary Graphs', 
        'EvoByte - Evolutionary Bio-Compilation System',
        'SEPD - Smart Evolutionary Pathway Designer',
        'EDAL - Evolutionary Data Assimilation Layer',
        'CECE - Cross-Scale Evolutionary Coupling Engine'
    ],
    'status': 'Patent Pending'
}

def get_patent_info():
    """Return patent information for EvoSphere."""
    return PATENT_INFO

def get_system_info():
    """Return comprehensive system information."""
    return {
        'name': 'EvoSphere',
        'version': __version__,
        'description': 'Quantum-Enhanced Evolutionary Bio-Compiler',
        'authors': __authors__,
        'license': __license__,
        'patent_info': PATENT_INFO,
        'components': {
            'core': 'Main evolutionary engine',
            'quantum': 'HQESE quantum evolution engine',
            'graph': 'MRAEG adaptive graph networks',
            'compiler': 'EvoByte bio-compilation system',
            'designer': 'SEPD pathway designer',
            'assimilation': 'EDAL data assimilation layer',
            'coupling': 'CECE cross-scale coupling engine'
        }
    }
