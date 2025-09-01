"""
Quantum State Space for Evolutionary Computation

Implements quantum state space representation for genomic and evolutionary data.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from dataclasses import dataclass
import logging

try:
    from qiskit.quantum_info import Statevector, DensityMatrix, SparsePauliOp
    from qiskit import QuantumCircuit
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class QuantumStateSpace:
    """
    Quantum state space for evolutionary computation.
    
    Patent Feature: Novel quantum state space encoding for biological
    sequences with evolutionary operator algebra.
    """
    
    dimension: int
    basis_states: List[str]
    hamiltonian: Optional[SparsePauliOp] = None
    ground_state: Optional[Statevector] = None
    eigenvalues: Optional[np.ndarray] = None
    eigenvectors: Optional[np.ndarray] = None
    
    def __post_init__(self):
        """Initialize quantum state space after creation."""
        if not QISKIT_AVAILABLE:
            logger.warning("Quantum state space requires Qiskit")
            return
        
        # Initialize ground state if not provided
        if self.ground_state is None:
            self.ground_state = Statevector.from_label('0' * int(np.log2(self.dimension)))
    
    def add_basis_state(self, state_label: str, genome_sequence: str):
        """Add new basis state to the quantum space."""
        
        if state_label not in self.basis_states:
            self.basis_states.append(state_label)
            
            # Expand dimension if needed
            if len(self.basis_states) > self.dimension:
                self.dimension = 2 ** int(np.ceil(np.log2(len(self.basis_states))))
    
    def create_superposition(
        self, 
        state_weights: Dict[str, complex]
    ) -> Statevector:
        """
        Create quantum superposition of genomic states.
        
        Patent Feature: Biological sequence superposition with
        evolutionary amplitude weighting.
        """
        
        if not QISKIT_AVAILABLE:
            raise RuntimeError("Quantum superposition requires Qiskit")
        
        # Create amplitude vector
        amplitudes = np.zeros(self.dimension, dtype=complex)
        
        for state_label, weight in state_weights.items():
            if state_label in self.basis_states:
                state_index = self.basis_states.index(state_label)
                if state_index < self.dimension:
                    amplitudes[state_index] = weight
        
        # Normalize amplitudes
        norm = np.linalg.norm(amplitudes)
        if norm > 0:
            amplitudes /= norm
        else:
            amplitudes[0] = 1.0  # Default to ground state
        
        return Statevector(amplitudes)
    
    def evolve_state(
        self, 
        initial_state: Statevector, 
        evolution_time: float,
        hamiltonian: Optional[SparsePauliOp] = None
    ) -> Statevector:
        """
        Evolve quantum state under Hamiltonian dynamics.
        
        Patent Feature: Quantum time evolution for biological systems
        with evolutionary Hamiltonian dynamics.
        """
        
        if not QISKIT_AVAILABLE:
            raise RuntimeError("Quantum evolution requires Qiskit")
        
        if hamiltonian is None:
            hamiltonian = self.hamiltonian
        
        if hamiltonian is None:
            logger.warning("No Hamiltonian specified, returning initial state")
            return initial_state
        
        # Time evolution operator: exp(-i * H * t)
        evolution_operator = (-1j * evolution_time * hamiltonian).exp_i()
        
        # Apply evolution
        evolved_state = evolution_operator @ initial_state
        
        return evolved_state
    
    def measure_observable(
        self, 
        state: Statevector, 
        observable: SparsePauliOp
    ) -> float:
        """
        Measure quantum observable on evolutionary state.
        
        Patent Feature: Quantum measurement protocol for biological
        observables (fitness, diversity, adaptation rate).
        """
        
        if not QISKIT_AVAILABLE:
            return 0.0
        
        # Calculate expectation value
        expectation = state.expectation_value(observable)
        
        return float(np.real(expectation))
    
    def calculate_quantum_fitness(
        self, 
        state: Statevector,
        fitness_operator: Optional[SparsePauliOp] = None
    ) -> float:
        """Calculate quantum fitness without state collapse."""
        
        if fitness_operator is None:
            # Default fitness operator (sum of Z measurements)
            num_qubits = int(np.log2(len(state)))
            fitness_operator = self._create_default_fitness_operator(num_qubits)
        
        return self.measure_observable(state, fitness_operator)
    
    def _create_default_fitness_operator(self, num_qubits: int) -> SparsePauliOp:
        """Create default fitness measurement operator."""
        
        pauli_list = []
        coefficients = []
        
        # Fitness as weighted sum of qubit measurements
        for i in range(num_qubits):
            z_pauli = ['I'] * num_qubits
            z_pauli[i] = 'Z'
            pauli_list.append(''.join(z_pauli))
            coefficients.append(1.0 / num_qubits)
        
        return SparsePauliOp(pauli_list, coefficients)
    
    def entanglement_entropy(self, state: Statevector, subsystem_qubits: List[int]) -> float:
        """
        Calculate entanglement entropy of subsystem.
        
        Patent Feature: Quantum entanglement measures for biological
        interaction network analysis.
        """
        
        if not QISKIT_AVAILABLE:
            return 0.0
        
        # Get reduced density matrix for subsystem
        try:
            rho_sub = state.trace_out(subsystem_qubits)
            
            # Calculate von Neumann entropy
            eigenvalues = np.linalg.eigvals(rho_sub.data)
            eigenvalues = eigenvalues[eigenvalues > 1e-12]  # Remove numerical zeros
            
            entropy = -np.sum(eigenvalues * np.log2(eigenvalues))
            return float(entropy)
            
        except Exception as e:
            logger.warning(f"Error calculating entanglement entropy: {e}")
            return 0.0
    
    def quantum_mutation_circuit(
        self, 
        num_qubits: int, 
        mutation_rate: float
    ) -> QuantumCircuit:
        """
        Create quantum circuit for evolutionary mutations.
        
        Patent Feature: Quantum mutation operators with biological
        mutation rate encoding and error correction.
        """
        
        circuit = QuantumCircuit(num_qubits)
        
        # Single-qubit mutation operators
        for i in range(num_qubits):
            # Rotation angle proportional to mutation rate
            theta = 2 * np.pi * mutation_rate
            
            # X rotation for bit flips (point mutations)
            circuit.rx(theta, i)
            
            # Z rotation for phase mutations (epigenetic changes)
            circuit.rz(theta * 0.5, i)
        
        # Add quantum error correction if mutation rate is low
        if mutation_rate < 0.01:
            circuit = self._add_quantum_error_correction(circuit)
        
        return circuit
    
    def quantum_recombination_circuit(
        self, 
        num_qubits: int, 
        recombination_rate: float
    ) -> QuantumCircuit:
        """
        Create quantum circuit for evolutionary recombination.
        
        Patent Feature: Quantum recombination operators using
        controlled entanglement with biological crossover patterns.
        """
        
        circuit = QuantumCircuit(num_qubits)
        
        # Two-qubit recombination operators
        for i in range(0, num_qubits - 1, 2):
            # Controlled rotation for recombination
            theta = np.pi * recombination_rate
            circuit.cry(theta, i, i + 1)
            
            # Swap test for crossover probability
            circuit.fredkin(i, i + 1, (i + 2) % num_qubits)
        
        # Global entanglement for population-level recombination
        if recombination_rate > 0.1:
            for i in range(num_qubits):
                circuit.h(i)
            
            for i in range(num_qubits - 1):
                circuit.cnot(i, i + 1)
        
        return circuit
    
    def _add_quantum_error_correction(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Add quantum error correction for low mutation rates."""
        
        num_qubits = circuit.num_qubits
        
        # Simple repetition code for demonstration
        if num_qubits >= 3:
            # Encode logical qubit using first three physical qubits
            circuit.cnot(0, 1)
            circuit.cnot(0, 2)
            
            # Error syndrome detection
            circuit.cnot(0, 1)
            circuit.cnot(0, 2)
            
            # Error correction (simplified)
            circuit.ccx(1, 2, 0)  # Correct if both ancillas are 1
        
        return circuit
    
    def quantum_selection_circuit(
        self, 
        num_qubits: int, 
        selection_pressure: float
    ) -> QuantumCircuit:
        """
        Create quantum circuit for evolutionary selection.
        
        Patent Feature: Quantum selection operators using amplitude
        amplification with fitness-dependent selection probabilities.
        """
        
        circuit = QuantumCircuit(num_qubits)
        
        # Grover-like amplitude amplification for high-fitness states
        if selection_pressure > 0:
            # Oracle marking high-fitness states
            oracle = self._create_fitness_oracle(num_qubits, selection_pressure)
            circuit = circuit.compose(oracle)
            
            # Diffusion operator for amplitude amplification
            diffusion = self._create_diffusion_operator(num_qubits)
            circuit = circuit.compose(diffusion)
        
        return circuit
    
    def _create_fitness_oracle(
        self, 
        num_qubits: int, 
        selection_pressure: float
    ) -> QuantumCircuit:
        """Create oracle circuit for fitness-based selection."""
        
        oracle = QuantumCircuit(num_qubits)
        
        # Mark states with high fitness (simplified)
        # In practice, this would encode complex fitness functions
        
        # Multi-controlled Z gate on high-fitness states
        if num_qubits > 2:
            # Create target state pattern (e.g., alternating 01010...)
            target_pattern = [i % 2 for i in range(num_qubits)]
            
            # Add X gates to create control pattern
            for i, bit in enumerate(target_pattern):
                if bit == 0:
                    oracle.x(i)
            
            # Multi-controlled Z
            oracle.mcz(list(range(num_qubits - 1)), num_qubits - 1)
            
            # Uncompute X gates
            for i, bit in enumerate(target_pattern):
                if bit == 0:
                    oracle.x(i)
        
        return oracle
    
    def _create_diffusion_operator(self, num_qubits: int) -> QuantumCircuit:
        """Create diffusion operator for amplitude amplification."""
        
        diffusion = QuantumCircuit(num_qubits)
        
        # Hadamard gates
        for i in range(num_qubits):
            diffusion.h(i)
        
        # Conditional phase flip about |00...0>
        for i in range(num_qubits):
            diffusion.x(i)
        
        # Multi-controlled Z
        if num_qubits > 1:
            diffusion.mcz(list(range(num_qubits - 1)), num_qubits - 1)
        
        # Uncompute X gates
        for i in range(num_qubits):
            diffusion.x(i)
        
        # Hadamard gates
        for i in range(num_qubits):
            diffusion.h(i)
        
        return diffusion
    
    def get_state_statistics(self) -> Dict[str, Any]:
        """Get comprehensive quantum state space statistics."""
        
        stats = {
            'dimension': self.dimension,
            'num_basis_states': len(self.basis_states),
            'has_hamiltonian': self.hamiltonian is not None,
            'has_ground_state': self.ground_state is not None,
            'is_quantum_available': QISKIT_AVAILABLE
        }
        
        if QISKIT_AVAILABLE and self.ground_state is not None:
            stats.update({
                'ground_state_norm': float(np.linalg.norm(self.ground_state.data)),
                'ground_state_purity': float(self.ground_state.purity()),
                'ground_state_entropy': float(self.ground_state.entropy())
            })
            
            if self.eigenvalues is not None:
                stats.update({
                    'spectrum_gap': float(self.eigenvalues[1] - self.eigenvalues[0]) if len(self.eigenvalues) > 1 else 0.0,
                    'ground_state_energy': float(self.eigenvalues[0]) if len(self.eigenvalues) > 0 else 0.0
                })
        
        return stats
