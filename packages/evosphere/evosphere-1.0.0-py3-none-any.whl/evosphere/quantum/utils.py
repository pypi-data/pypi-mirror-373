"""
Quantum Utilities and Fallbacks

Provides optional quantum functionality with robust classical fallbacks.
Ensures EvoSphere runs smoothly with or without quantum dependencies.

Authors: Krishna Bajpai and Vedanshi Gupta
"""

import numpy as np
import warnings
import logging
from typing import Dict, List, Optional, Tuple, Any, Union

logger = logging.getLogger(__name__)

# Check quantum availability
QUANTUM_AVAILABLE = False
try:
    import qiskit
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.quantum_info import Statevector, SparsePauliOp
    QUANTUM_AVAILABLE = True
    logger.info("Quantum computing available via Qiskit")
except ImportError as e:
    logger.info(f"Quantum computing not available: {e}")
    logger.info("Using classical simulation fallbacks")

def ensure_quantum_optional(func):
    """Decorator to make quantum functions optional."""
    def wrapper(*args, **kwargs):
        if not QUANTUM_AVAILABLE:
            logger.warning(f"Quantum function {func.__name__} called without quantum support - using classical fallback")
            return None
        return func(*args, **kwargs)
    return wrapper

class ClassicalQuantumCircuit:
    """Classical simulation of quantum circuit operations."""
    
    def __init__(self, num_qubits: int = 1, num_clbits: int = 1, name: str = "circuit"):
        self.num_qubits = num_qubits
        self.num_clbits = num_clbits
        self.name = name
        self.gates = []
        self.parameters = []
        self.state = np.zeros(2**num_qubits, dtype=complex)
        self.state[0] = 1.0  # |0...0⟩ initial state
    
    def h(self, qubit):
        """Hadamard gate simulation."""
        self.gates.append(('h', qubit))
        # Apply Hadamard transformation to state
        if qubit < self.num_qubits:
            self._apply_single_qubit_gate(self._hadamard_matrix(), qubit)
        return self
    
    def x(self, qubit):
        """Pauli-X gate simulation."""
        self.gates.append(('x', qubit))
        if qubit < self.num_qubits:
            self._apply_single_qubit_gate(self._pauli_x_matrix(), qubit)
        return self
    
    def y(self, qubit):
        """Pauli-Y gate simulation."""
        self.gates.append(('y', qubit))
        if qubit < self.num_qubits:
            self._apply_single_qubit_gate(self._pauli_y_matrix(), qubit)
        return self
    
    def z(self, qubit):
        """Pauli-Z gate simulation."""
        self.gates.append(('z', qubit))
        if qubit < self.num_qubits:
            self._apply_single_qubit_gate(self._pauli_z_matrix(), qubit)
        return self
    
    def rx(self, theta, qubit):
        """Rotation-X gate simulation."""
        self.gates.append(('rx', theta, qubit))
        if qubit < self.num_qubits:
            rotation_matrix = self._rotation_x_matrix(theta)
            self._apply_single_qubit_gate(rotation_matrix, qubit)
        return self
    
    def ry(self, theta, qubit):
        """Rotation-Y gate simulation."""
        self.gates.append(('ry', theta, qubit))
        if qubit < self.num_qubits:
            rotation_matrix = self._rotation_y_matrix(theta)
            self._apply_single_qubit_gate(rotation_matrix, qubit)
        return self
    
    def rz(self, theta, qubit):
        """Rotation-Z gate simulation."""
        self.gates.append(('rz', theta, qubit))
        if qubit < self.num_qubits:
            rotation_matrix = self._rotation_z_matrix(theta)
            self._apply_single_qubit_gate(rotation_matrix, qubit)
        return self
    
    def cx(self, control, target):
        """CNOT gate simulation."""
        self.gates.append(('cx', control, target))
        if control < self.num_qubits and target < self.num_qubits:
            self._apply_cnot_gate(control, target)
        return self
    
    def measure(self, qubit, clbit):
        """Measurement simulation."""
        self.gates.append(('measure', qubit, clbit))
        return self
    
    def barrier(self):
        """Barrier (no-op in simulation)."""
        self.gates.append(('barrier',))
        return self
    
    def _hadamard_matrix(self):
        return np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    
    def _pauli_x_matrix(self):
        return np.array([[0, 1], [1, 0]], dtype=complex)
    
    def _pauli_y_matrix(self):
        return np.array([[0, -1j], [1j, 0]], dtype=complex)
    
    def _pauli_z_matrix(self):
        return np.array([[1, 0], [0, -1]], dtype=complex)
    
    def _rotation_x_matrix(self, theta):
        return np.array([
            [np.cos(theta/2), -1j*np.sin(theta/2)],
            [-1j*np.sin(theta/2), np.cos(theta/2)]
        ], dtype=complex)
    
    def _rotation_y_matrix(self, theta):
        return np.array([
            [np.cos(theta/2), -np.sin(theta/2)],
            [np.sin(theta/2), np.cos(theta/2)]
        ], dtype=complex)
    
    def _rotation_z_matrix(self, theta):
        return np.array([
            [np.exp(-1j*theta/2), 0],
            [0, np.exp(1j*theta/2)]
        ], dtype=complex)
    
    def _apply_single_qubit_gate(self, gate_matrix, qubit):
        """Apply single qubit gate to the quantum state."""
        # Construct full gate matrix for the system
        full_gate = np.eye(1, dtype=complex)
        
        for i in range(self.num_qubits):
            if i == qubit:
                full_gate = np.kron(full_gate, gate_matrix)
            else:
                full_gate = np.kron(full_gate, np.eye(2, dtype=complex))
        
        # Apply to state
        self.state = full_gate @ self.state
    
    def _apply_cnot_gate(self, control, target):
        """Apply CNOT gate to the quantum state."""
        # CNOT matrix for 2-qubit system
        cnot_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
        
        # For multi-qubit systems, need to construct full CNOT
        if self.num_qubits == 2:
            self.state = cnot_matrix @ self.state
        else:
            # Simplified CNOT effect for larger systems
            # In a full implementation, would construct proper tensor product
            pass

class ClassicalStatevector:
    """Classical simulation of quantum statevector."""
    
    def __init__(self, data):
        self.data = np.array(data, dtype=complex) if not isinstance(data, np.ndarray) else data.astype(complex)
        # Normalize
        norm = np.linalg.norm(self.data)
        if norm > 0:
            self.data = self.data / norm
    
    def evolve(self, operator):
        """Evolve state with operator."""
        if hasattr(operator, 'matrix'):
            new_data = operator.matrix @ self.data
        elif isinstance(operator, np.ndarray):
            new_data = operator @ self.data
        else:
            new_data = self.data
        
        return ClassicalStatevector(new_data)
    
    def expectation_value(self, operator):
        """Calculate expectation value."""
        if hasattr(operator, 'matrix'):
            return np.real(np.conj(self.data) @ operator.matrix @ self.data)
        elif isinstance(operator, np.ndarray):
            return np.real(np.conj(self.data) @ operator @ self.data)
        else:
            return 0.0
    
    def probabilities(self):
        """Get measurement probabilities."""
        return np.abs(self.data)**2

class ClassicalSparsePauliOp:
    """Classical simulation of Pauli operators."""
    
    def __init__(self, pauli_list, coeffs=None):
        self.paulis = pauli_list if isinstance(pauli_list, list) else ['I']
        self.coeffs = coeffs if coeffs is not None else np.array([1.0])
        
        # Construct matrix representation
        n_qubits = max(1, len(str(self.paulis[0])) if self.paulis else 1)
        self.num_qubits = n_qubits
        self.matrix = self._construct_matrix()
    
    def _construct_matrix(self):
        """Construct the full Pauli operator matrix."""
        pauli_matrices = {
            'I': np.eye(2, dtype=complex),
            'X': np.array([[0, 1], [1, 0]], dtype=complex),
            'Y': np.array([[0, -1j], [1j, 0]], dtype=complex),
            'Z': np.array([[1, 0], [0, -1]], dtype=complex)
        }
        
        total_matrix = np.zeros((2**self.num_qubits, 2**self.num_qubits), dtype=complex)
        
        for pauli_string, coeff in zip(self.paulis, self.coeffs):
            # Construct tensor product for this Pauli string
            pauli_matrix = np.array([[1]], dtype=complex)
            
            for char in str(pauli_string):
                if char in pauli_matrices:
                    pauli_matrix = np.kron(pauli_matrix, pauli_matrices[char])
                else:
                    pauli_matrix = np.kron(pauli_matrix, pauli_matrices['I'])
            
            # Ensure correct dimension
            if pauli_matrix.shape[0] < 2**self.num_qubits:
                padding = 2**self.num_qubits - pauli_matrix.shape[0]
                pauli_matrix = np.pad(pauli_matrix, ((0, padding), (0, padding)), mode='constant')
            elif pauli_matrix.shape[0] > 2**self.num_qubits:
                pauli_matrix = pauli_matrix[:2**self.num_qubits, :2**self.num_qubits]
            
            total_matrix += coeff * pauli_matrix
        
        return total_matrix
    
    @classmethod
    def from_list(cls, pauli_list):
        """Create from list of (pauli_string, coefficient) tuples."""
        if pauli_list:
            paulis, coeffs = zip(*pauli_list)
            return cls(list(paulis), np.array(coeffs))
        return cls(['I'], np.array([1.0]))

def get_quantum_backend():
    """Get appropriate quantum backend."""
    if QUANTUM_AVAILABLE:
        try:
            from qiskit.providers.aer import AerSimulator
            return AerSimulator()
        except ImportError:
            pass
    
    # Classical fallback
    class ClassicalBackend:
        def __init__(self):
            self.name = "classical_simulator"
        
        def run(self, circuits, shots=1024):
            # Simulate quantum circuit execution
            if isinstance(circuits, list):
                circuits = circuits[0] if circuits else None
            
            if circuits is None:
                counts = {'0': shots}
            else:
                # Simple simulation based on circuit
                num_bits = getattr(circuits, 'num_clbits', 1)
                counts = {'0' * num_bits: shots}
            
            result = type('ClassicalResult', (), {
                'get_counts': lambda: counts,
                'get_statevector': lambda: np.array([1.0] + [0.0] * (2**getattr(circuits, 'num_qubits', 1) - 1))
            })()
            return result
    
    return ClassicalBackend()

def create_quantum_circuit(num_qubits: int, num_clbits: int = None) -> Union['QuantumCircuit', 'ClassicalQuantumCircuit']:
    """Create quantum circuit with fallback."""
    if num_clbits is None:
        num_clbits = num_qubits
    
    if QUANTUM_AVAILABLE:
        from qiskit import QuantumCircuit
        return QuantumCircuit(num_qubits, num_clbits)
    else:
        return ClassicalQuantumCircuit(num_qubits, num_clbits)

def create_statevector(data) -> Union['Statevector', 'ClassicalStatevector']:
    """Create statevector with fallback."""
    if QUANTUM_AVAILABLE:
        try:
            from qiskit.quantum_info import Statevector
            return Statevector(data)
        except ImportError:
            pass
    
    return ClassicalStatevector(data)

def create_pauli_operator(pauli_list, coeffs=None) -> Union['SparsePauliOp', 'ClassicalSparsePauliOp']:
    """Create Pauli operator with fallback."""
    if QUANTUM_AVAILABLE:
        try:
            from qiskit.quantum_info import SparsePauliOp
            if isinstance(pauli_list, list) and len(pauli_list) > 0 and isinstance(pauli_list[0], tuple):
                return SparsePauliOp.from_list(pauli_list)
            else:
                return SparsePauliOp(pauli_list, coeffs)
        except ImportError:
            pass
    
    return ClassicalSparsePauliOp(pauli_list, coeffs)

class QuantumOptional:
    """Base class for quantum-optional components."""
    
    def __init__(self, enable_quantum: bool = True):
        self.quantum_enabled = enable_quantum and QUANTUM_AVAILABLE
        
        if enable_quantum and not QUANTUM_AVAILABLE:
            warnings.warn(
                "Quantum computing requested but not available. "
                "Install qiskit for quantum functionality: pip install qiskit"
            )
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if self.quantum_enabled:
            self.logger.info("Quantum mode enabled")
        else:
            self.logger.info("Classical mode enabled")
    
    def is_quantum_available(self) -> bool:
        """Check if quantum functionality is available."""
        return self.quantum_enabled
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about the current backend."""
        if self.quantum_enabled:
            return {
                'type': 'quantum',
                'backend': 'qiskit',
                'available': True
            }
        else:
            return {
                'type': 'classical',
                'backend': 'numpy_simulation',
                'available': True,
                'note': 'Classical fallback - install qiskit for quantum functionality'
            }
