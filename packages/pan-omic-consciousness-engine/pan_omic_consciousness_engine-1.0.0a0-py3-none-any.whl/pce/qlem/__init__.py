"""Q-LEM: Quantum-Latent Entropy Minimizer.

Implements bio-quantum entropy functional: F = H(S) - αE + βC
Where:
- H(S) is von Neumann entropy of system state
- E is energy functional (metabolic cost)
- C is consciousness correlation term
- α, β are tunable parameters
"""

import numpy as np
import logging
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

try:
    from scipy.optimize import minimize
    from scipy.linalg import logm, expm
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from ..core.datatypes import LatentEmbedding, HyperGraph
from ..core.config import get_config
from ..utils.logging import get_logger, timer_context
from ..utils.metrics import compute_biological_metrics

logger = get_logger(__name__)


@dataclass
class QuantumState:
    """Quantum state representation for biological system."""
    density_matrix: np.ndarray
    energy: float
    entropy: float
    coherence: float
    timestamp: float
    system_size: int
    
    def __post_init__(self) -> None:
        """Validate quantum state properties."""
        # Check for NaN or infinite values
        if not np.isfinite(self.density_matrix).all():
            logger.error("Density matrix contains NaN or infinite values, resetting to maximally mixed state")
            n = self.density_matrix.shape[0]
            self.density_matrix = np.eye(n) / n
        
        # Ensure density matrix is properly normalized
        trace = np.trace(self.density_matrix)
        if np.isnan(trace) or np.isinf(trace) or trace <= 0:
            logger.warning(f"Density matrix trace is {trace}, renormalizing")
            n = self.density_matrix.shape[0]
            self.density_matrix = np.eye(n) / n
        elif not np.isclose(trace, 1.0, atol=1e-6):
            logger.warning(f"Density matrix trace is {trace}, renormalizing")
            self.density_matrix = self.density_matrix / trace
    
    @property
    def purity(self) -> float:
        """Compute purity of quantum state."""
        return np.trace(self.density_matrix @ self.density_matrix).real
    
    @property
    def von_neumann_entropy(self) -> float:
        """Compute von Neumann entropy."""
        try:
            # Check if density matrix is valid
            if not np.isfinite(self.density_matrix).all():
                logger.warning("Density matrix contains invalid values, returning 0 entropy")
                return 0.0
                
            eigenvals = np.linalg.eigvals(self.density_matrix)
            eigenvals = eigenvals.real  # Take real part
            eigenvals = eigenvals[eigenvals > 1e-10]  # Remove numerical zeros
            
            if len(eigenvals) == 0:
                return 0.0
                
            log_eigenvals = np.log(eigenvals)
            if not np.isfinite(log_eigenvals).all():
                logger.warning("Log eigenvalues contain invalid values, returning 0 entropy")
                return 0.0
                
            entropy = -np.sum(eigenvals * log_eigenvals)
            return entropy if np.isfinite(entropy) else 0.0
        except Exception as e:
            logger.warning(f"Error computing von Neumann entropy: {e}, returning 0")
            return 0.0
    
    def evolve(self, hamiltonian: np.ndarray, time_step: float) -> 'QuantumState':
        """Evolve quantum state under Hamiltonian."""
        if SCIPY_AVAILABLE:
            # Unitary evolution: U = exp(-iHt)
            unitary = expm(-1j * hamiltonian * time_step)
            new_density = unitary @ self.density_matrix @ unitary.conj().T
            
            return QuantumState(
                density_matrix=new_density,
                energy=self.energy + np.trace(hamiltonian @ new_density).real,
                entropy=self.von_neumann_entropy,
                coherence=self.coherence * np.exp(-time_step * 0.1),  # Decoherence
                timestamp=self.timestamp + time_step,
                system_size=self.system_size
            )
        else:
            logger.warning("SciPy not available, returning current state")
            return self


@dataclass
class BioQuantumParameters:
    """Parameters for bio-quantum entropy functional."""
    alpha: float = 1.0          # Energy weight
    beta: float = 0.5           # Consciousness weight
    gamma: float = 0.1          # Decoherence rate
    temperature: float = 310.0  # Body temperature (K)
    coupling_strength: float = 0.01
    metabolic_efficiency: float = 0.25
    coherence_time: float = 1e-12  # Picoseconds


class QuantumHamiltonian:
    """Biological quantum Hamiltonian generator."""
    
    def __init__(
        self,
        system_size: int,
        parameters: BioQuantumParameters,
        interaction_type: str = "neural_inspired"
    ) -> None:
        self.system_size = system_size
        self.parameters = parameters
        self.interaction_type = interaction_type
    
    def generate_hamiltonian(
        self,
        embedding: LatentEmbedding,
        biological_context: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """Generate Hamiltonian matrix from biological embedding."""
        embeddings_matrix = np.array(list(embedding.embeddings.values()))
        
        # Create base Hamiltonian from embedding similarities
        hamiltonian = self._create_interaction_hamiltonian(embeddings_matrix)
        
        # Add biological terms
        hamiltonian += self._add_biological_terms(embeddings_matrix, biological_context)
        
        # Ensure Hermitian
        hamiltonian = 0.5 * (hamiltonian + hamiltonian.conj().T)
        
        return hamiltonian
    
    def _create_interaction_hamiltonian(self, embeddings: np.ndarray) -> np.ndarray:
        """Create interaction Hamiltonian from embeddings."""
        n = embeddings.shape[0]
        hamiltonian = np.zeros((n, n), dtype=complex)
        
        if self.interaction_type == "neural_inspired":
            # Neural-inspired interactions
            for i in range(n):
                for j in range(i + 1, n):
                    # Compute similarity-based coupling
                    similarity = np.dot(embeddings[i], embeddings[j])
                    similarity /= (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]) + 1e-8)
                    
                    # Convert to quantum coupling strength
                    coupling = self.parameters.coupling_strength * similarity
                    
                    # Add to Hamiltonian
                    hamiltonian[i, j] = coupling
                    hamiltonian[j, i] = coupling.conj()
        
        elif self.interaction_type == "metabolic":
            # Metabolic network inspired
            # Implementation would include metabolic pathway information
            pass
        
        return hamiltonian
    
    def _add_biological_terms(
        self,
        embeddings: np.ndarray,
        context: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """Add biological constraint terms."""
        n = embeddings.shape[0]
        bio_terms = np.zeros((n, n), dtype=complex)
        
        if context:
            # Add context-specific biological constraints
            # This would include pathway information, regulatory networks, etc.
            pass
        
        # Add diagonal energy terms (site energies)
        for i in range(n):
            energy = np.linalg.norm(embeddings[i]) * self.parameters.alpha
            bio_terms[i, i] = energy
        
        return bio_terms


class EntropyFunctional:
    """Bio-quantum entropy functional F = H(S) - αE + βC."""
    
    def __init__(self, parameters: BioQuantumParameters) -> None:
        self.parameters = parameters
    
    def compute_functional(
        self,
        quantum_state: QuantumState,
        consciousness_measure: Optional[float] = None
    ) -> float:
        """Compute bio-quantum entropy functional."""
        # von Neumann entropy term
        entropy_term = quantum_state.von_neumann_entropy
        
        # Energy term
        energy_term = self.parameters.alpha * quantum_state.energy
        
        # Consciousness correlation term
        if consciousness_measure is None:
            consciousness_measure = self._estimate_consciousness_measure(quantum_state)
        
        consciousness_term = self.parameters.beta * consciousness_measure
        
        # Total functional
        functional = entropy_term - energy_term + consciousness_term
        
        return functional
    
    def compute_gradient(
        self,
        quantum_state: QuantumState,
        hamiltonian: np.ndarray
    ) -> np.ndarray:
        """Compute gradient of functional with respect to density matrix."""
        rho = quantum_state.density_matrix
        
        # Entropy gradient: -log(ρ) - I
        if SCIPY_AVAILABLE:
            entropy_grad = -logm(rho + 1e-10 * np.eye(rho.shape[0])) - np.eye(rho.shape[0])
        else:
            # Approximate gradient
            eigenvals, eigenvecs = np.linalg.eigh(rho)
            log_eigenvals = np.log(eigenvals + 1e-10)
            entropy_grad = -eigenvecs @ np.diag(log_eigenvals) @ eigenvecs.conj().T - np.eye(rho.shape[0])
        
        # Energy gradient
        energy_grad = -self.parameters.alpha * hamiltonian
        
        # Consciousness gradient (placeholder)
        consciousness_grad = self.parameters.beta * np.eye(rho.shape[0]) * 0.1
        
        total_grad = entropy_grad + energy_grad + consciousness_grad
        return total_grad
    
    def _estimate_consciousness_measure(self, quantum_state: QuantumState) -> float:
        """Estimate consciousness measure from quantum state."""
        # Integrated Information Theory inspired measure
        purity = quantum_state.purity
        entropy = quantum_state.von_neumann_entropy
        coherence = quantum_state.coherence
        
        # Combine measures with empirical weights
        consciousness_estimate = (
            0.4 * (1.0 - purity) +      # Mixed states
            0.3 * entropy +             # Entropy
            0.3 * coherence             # Quantum coherence
        )
        
        return consciousness_estimate


class QLEMOptimizer:
    """Quantum-Latent Entropy Minimizer optimizer."""
    
    def __init__(
        self,
        parameters: BioQuantumParameters,
        max_iterations: int = 1000,
        tolerance: float = 1e-6
    ) -> None:
        self.parameters = parameters
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        
        self.functional = EntropyFunctional(parameters)
        self.optimization_history: List[Dict[str, float]] = []
    
    def optimize(
        self,
        initial_state: QuantumState,
        hamiltonian: np.ndarray,
        constraints: Optional[List[Callable]] = None
    ) -> QuantumState:
        """Optimize quantum state to minimize entropy functional."""
        with timer_context("Q-LEM optimization"):
            current_state = initial_state
            
            for iteration in range(self.max_iterations):
                # Compute functional and gradient
                functional_value = self.functional.compute_functional(current_state)
                gradient = self.functional.compute_gradient(current_state, hamiltonian)
                
                # Record iteration
                self.optimization_history.append({
                    "iteration": iteration,
                    "functional": functional_value,
                    "entropy": current_state.von_neumann_entropy,
                    "energy": current_state.energy,
                    "purity": current_state.purity
                })
                
                # Check convergence
                if iteration > 0:
                    prev_functional = self.optimization_history[-2]["functional"]
                    if abs(functional_value - prev_functional) < self.tolerance:
                        logger.info(f"Q-LEM converged at iteration {iteration}")
                        break
                
                # Gradient descent step
                current_state = self._gradient_step(current_state, gradient, hamiltonian)
                
                # Apply constraints
                if constraints:
                    current_state = self._apply_constraints(current_state, constraints)
            
            logger.info(f"Q-LEM optimization completed: {len(self.optimization_history)} iterations")
            return current_state
    
    def _gradient_step(
        self,
        state: QuantumState,
        gradient: np.ndarray,
        hamiltonian: np.ndarray,
        step_size: float = 0.01
    ) -> QuantumState:
        """Perform gradient descent step."""
        # Update density matrix
        new_density = state.density_matrix - step_size * gradient
        
        # Ensure positive semi-definite and trace 1
        new_density = self._project_to_valid_density_matrix(new_density)
        
        # Update other properties
        new_energy = np.trace(hamiltonian @ new_density).real
        new_state = QuantumState(
            density_matrix=new_density,
            energy=new_energy,
            entropy=0.0,  # Will be computed in __post_init__
            coherence=state.coherence * 0.99,  # Slight decoherence
            timestamp=state.timestamp + 0.01,
            system_size=state.system_size
        )
        
        # Update entropy
        new_state.entropy = new_state.von_neumann_entropy
        
        return new_state
    
    def _project_to_valid_density_matrix(self, matrix: np.ndarray) -> np.ndarray:
        """Project matrix to valid density matrix (positive semi-definite, trace 1)."""
        # Ensure Hermitian
        matrix = 0.5 * (matrix + matrix.conj().T)
        
        # Eigendecomposition
        eigenvals, eigenvecs = np.linalg.eigh(matrix)
        
        # Clamp negative eigenvalues to small positive values
        eigenvals = np.maximum(eigenvals, 1e-10)
        
        # Reconstruct matrix
        matrix = eigenvecs @ np.diag(eigenvals) @ eigenvecs.conj().T
        
        # Normalize trace
        trace = np.trace(matrix)
        if trace > 1e-10:
            matrix = matrix / trace
        else:
            # Fallback to maximally mixed state
            matrix = np.eye(matrix.shape[0]) / matrix.shape[0]
        
        return matrix
    
    def _apply_constraints(
        self,
        state: QuantumState,
        constraints: List[Callable]
    ) -> QuantumState:
        """Apply constraints to quantum state."""
        # Apply each constraint function
        for constraint in constraints:
            state = constraint(state)
        
        return state


class QLEM:
    """Quantum-Latent Entropy Minimizer main class."""
    
    def __init__(
        self,
        parameters: Optional[BioQuantumParameters] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize Q-LEM system."""
        self.config = config or get_config().qlem
        
        if parameters is None:
            parameters = BioQuantumParameters(
                alpha=self.config.get("alpha", 1.0),
                beta=self.config.get("beta", 0.5),
                gamma=self.config.get("gamma", 0.1),
                temperature=self.config.get("temperature", 310.0)
            )
        
        self.parameters = parameters
        self.optimizer = QLEMOptimizer(parameters)
        self.current_state: Optional[QuantumState] = None
        
        logger.info(f"Initialized Q-LEM with parameters: {parameters}")
    
    def create_quantum_state(
        self,
        embedding: LatentEmbedding,
        initial_state_type: str = "thermal"
    ) -> QuantumState:
        """Create initial quantum state from latent embedding."""
        with timer_context("Creating quantum state"):
            embeddings_matrix = np.array(list(embedding.embeddings.values()))
            n = embeddings_matrix.shape[0]
            
            # Check for NaN or infinite values in embeddings
            if not np.isfinite(embeddings_matrix).all():
                logger.warning("Embeddings contain NaN or infinite values, using random embeddings")
                embeddings_matrix = np.random.normal(0, 1, embeddings_matrix.shape)
            
            if initial_state_type == "thermal":
                # Thermal state based on embedding energies
                energies = np.linalg.norm(embeddings_matrix, axis=1)
                # Ensure energies are finite and positive
                energies = np.where(np.isfinite(energies) & (energies > 0), energies, 1.0)
                
                beta = 1.0 / (self.parameters.temperature * 8.617e-5)  # Boltzmann constant
                
                # Create thermal density matrix
                hamiltonian_diag = np.diag(energies)
                if SCIPY_AVAILABLE:
                    try:
                        density_matrix = expm(-beta * hamiltonian_diag)
                        if not np.isfinite(density_matrix).all():
                            logger.warning("Thermal density matrix contains invalid values, using mixed state")
                            density_matrix = np.eye(n) / n
                    except:
                        logger.warning("Failed to compute thermal state, using mixed state")
                        density_matrix = np.eye(n) / n
                else:
                    density_matrix = np.eye(n) / n
                    
                # Normalize
                trace = np.trace(density_matrix)
                if trace > 0 and np.isfinite(trace):
                    density_matrix = density_matrix / trace
                else:
                    density_matrix = np.eye(n) / n
                
            elif initial_state_type == "mixed":
                # Maximally mixed state
                density_matrix = np.eye(n) / n
                
            elif initial_state_type == "coherent":
                # Coherent superposition
                psi = np.ones(n, dtype=complex) / np.sqrt(n)
                density_matrix = np.outer(psi, psi.conj())
                
            else:
                raise ValueError(f"Unknown initial state type: {initial_state_type}")
            
            # Compute initial properties
            try:
                initial_energy = np.trace(np.diag(np.linalg.norm(embeddings_matrix, axis=1)) @ density_matrix).real
                if not np.isfinite(initial_energy):
                    initial_energy = 1.0
            except:
                initial_energy = 1.0
            
            quantum_state = QuantumState(
                density_matrix=density_matrix,
                energy=initial_energy,
                entropy=0.0,  # Computed in __post_init__
                coherence=1.0,
                timestamp=0.0,
                system_size=n
            )
            
            self.current_state = quantum_state
            logger.info(f"Created quantum state: {n}x{n}, entropy={quantum_state.von_neumann_entropy:.4f}")
            
            return quantum_state
    
    def minimize_entropy(
        self,
        embedding: LatentEmbedding,
        quantum_state: Optional[QuantumState] = None,
        biological_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[QuantumState, Dict[str, Any]]:
        """Minimize bio-quantum entropy functional."""
        with timer_context("Q-LEM entropy minimization"):
            # Create quantum state if not provided
            if quantum_state is None:
                quantum_state = self.create_quantum_state(embedding)
            
            # Generate Hamiltonian
            hamiltonian_generator = QuantumHamiltonian(
                quantum_state.system_size,
                self.parameters,
                interaction_type="neural_inspired"
            )
            
            hamiltonian = hamiltonian_generator.generate_hamiltonian(
                embedding, biological_context
            )
            
            # Optimize
            optimized_state = self.optimizer.optimize(
                quantum_state,
                hamiltonian
            )
            
            # Compute final metrics
            metrics = self._compute_optimization_metrics(optimized_state)
            
            self.current_state = optimized_state
            
            logger.info(f"Q-LEM optimization completed: {metrics}")
            return optimized_state, metrics
    
    def analyze_quantum_consciousness(
        self,
        quantum_state: Optional[QuantumState] = None
    ) -> Dict[str, Any]:
        """Analyze quantum consciousness properties."""
        if quantum_state is None:
            quantum_state = self.current_state
        
        if quantum_state is None:
            raise ValueError("No quantum state available")
        
        with timer_context("Quantum consciousness analysis"):
            analysis = {
                "von_neumann_entropy": quantum_state.von_neumann_entropy,
                "purity": quantum_state.purity,
                "coherence": quantum_state.coherence,
                "energy": quantum_state.energy,
                "system_size": quantum_state.system_size,
                "entanglement_measure": self._compute_entanglement_measure(quantum_state),
                "information_integration": self._compute_information_integration(quantum_state),
                "consciousness_potential": self._compute_consciousness_potential(quantum_state),
                "decoherence_time": self._estimate_decoherence_time(quantum_state)
            }
            
            logger.info(f"Quantum consciousness analysis: {analysis}")
            return analysis
    
    def evolve_quantum_state(
        self,
        time_steps: int,
        time_step: float = 0.01,
        hamiltonian: Optional[np.ndarray] = None
    ) -> List[QuantumState]:
        """Evolve quantum state over time."""
        if self.current_state is None:
            raise ValueError("No quantum state available")
        
        if hamiltonian is None:
            # Create default Hamiltonian
            n = self.current_state.system_size
            hamiltonian = np.random.random((n, n)) * 0.1
            hamiltonian = 0.5 * (hamiltonian + hamiltonian.T)
        
        states = [self.current_state]
        current = self.current_state
        
        for _ in range(time_steps):
            current = current.evolve(hamiltonian, time_step)
            states.append(current)
        
        self.current_state = current
        return states
    
    def _compute_optimization_metrics(self, state: QuantumState) -> Dict[str, float]:
        """Compute metrics for optimization results."""
        return {
            "final_entropy": state.von_neumann_entropy,
            "final_energy": state.energy,
            "final_purity": state.purity,
            "final_coherence": state.coherence,
            "iterations": len(self.optimizer.optimization_history),
            "convergence": self.optimizer.optimization_history[-1]["functional"] if self.optimizer.optimization_history else 0.0
        }
    
    def _compute_entanglement_measure(self, state: QuantumState) -> float:
        """Compute entanglement measure (placeholder)."""
        # This would require bipartite decomposition
        return 1.0 - state.purity
    
    def _compute_information_integration(self, state: QuantumState) -> float:
        """Compute information integration measure."""
        # IIT-inspired measure
        return state.von_neumann_entropy * (1.0 - state.purity)
    
    def _compute_consciousness_potential(self, state: QuantumState) -> float:
        """Compute consciousness potential from quantum state."""
        entropy_factor = state.von_neumann_entropy / np.log(state.system_size)
        coherence_factor = state.coherence
        complexity_factor = 1.0 - state.purity
        
        potential = (entropy_factor + coherence_factor + complexity_factor) / 3.0
        return potential
    
    def _estimate_decoherence_time(self, state: QuantumState) -> float:
        """Estimate decoherence time scale."""
        # Based on system size and temperature
        size_factor = np.log(state.system_size)
        temp_factor = self.parameters.temperature / 300.0
        
        decoherence_time = self.parameters.coherence_time / (size_factor * temp_factor)
        return decoherence_time
    
    def __repr__(self) -> str:
        """String representation of Q-LEM."""
        if self.current_state:
            return f"QLEM(state={self.current_state.system_size}x{self.current_state.system_size}, entropy={self.current_state.von_neumann_entropy:.3f})"
        return "QLEM(no state)"
