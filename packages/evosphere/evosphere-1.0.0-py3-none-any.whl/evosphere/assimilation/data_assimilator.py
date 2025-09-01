"""
Evolutionary Data Assimilator

Patent-pending system for integrating real-world biological data
with evolutionary simulations using advanced filtering techniques.
"""

from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np
import logging
from abc import ABC, abstractmethod
import math
from collections import defaultdict, deque
import time

try:
    from scipy import linalg
    from scipy.stats import multivariate_normal
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    # Fallback implementations
    class linalg:
        @staticmethod
        def inv(matrix):
            return np.linalg.inv(matrix)
        
        @staticmethod
        def cholesky(matrix):
            return np.linalg.cholesky(matrix)

logger = logging.getLogger(__name__)


class DataType(Enum):
    """Types of biological data for assimilation."""
    
    GENOMIC = auto()
    TRANSCRIPTOMIC = auto()
    PROTEOMIC = auto()
    PHENOTYPIC = auto()
    ENVIRONMENTAL = auto()
    TEMPORAL = auto()
    SPATIAL = auto()
    METABOLOMIC = auto()


@dataclass
class BiologicalObservation:
    """
    Single biological observation for data assimilation.
    
    Patent Feature: Standardized biological data representation
    with uncertainty quantification and temporal tracking.
    """
    
    observation_id: str
    data_type: DataType
    timestamp: float
    location: Optional[Tuple[float, float, float]] = None
    
    # Core data
    values: Dict[str, Any] = field(default_factory=dict)
    uncertainties: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    source: str = "unknown"
    quality_score: float = 1.0
    measurement_noise: float = 0.01
    
    # Contextual information
    experimental_conditions: Dict[str, Any] = field(default_factory=dict)
    organism_info: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate observation after creation."""
        
        # Ensure uncertainties exist for all values
        for key in self.values:
            if key not in self.uncertainties:
                self.uncertainties[key] = self.measurement_noise
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get observation value with default."""
        
        return self.values.get(key, default)
    
    def get_uncertainty(self, key: str, default: float = 0.01) -> float:
        """Get uncertainty for value."""
        
        return self.uncertainties.get(key, default)


class EvolutionaryState:
    """
    State representation for evolutionary system.
    
    Patent Feature: Multi-scale evolutionary state with
    hierarchical organization and uncertainty propagation.
    """
    
    def __init__(self, state_dim: int):
        """
        Initialize evolutionary state.
        
        Args:
            state_dim: Dimension of state vector
        """
        self.state_dim = state_dim
        
        # State vectors
        self.mean_state = np.zeros(state_dim)
        self.covariance = np.eye(state_dim)
        
        # Hierarchical states
        self.molecular_state = {}
        self.cellular_state = {}
        self.organismal_state = {}
        self.population_state = {}
        
        # Temporal information
        self.timestamp = time.time()
        self.generation = 0
        
        # Metadata
        self.confidence = 1.0
        self.last_update = self.timestamp
    
    def update_state(self, new_mean: np.ndarray, new_covariance: np.ndarray):
        """Update state with new estimates."""
        
        self.mean_state = new_mean.copy()
        self.covariance = new_covariance.copy()
        self.last_update = time.time()
    
    def get_uncertainty(self) -> float:
        """Get overall state uncertainty."""
        
        return np.trace(self.covariance) / self.state_dim
    
    def predict_forward(self, time_delta: float, evolution_model: Callable) -> 'EvolutionaryState':
        """Predict state forward in time."""
        
        predicted_state = EvolutionaryState(self.state_dim)
        
        # Apply evolution model
        predicted_mean, predicted_cov = evolution_model(
            self.mean_state, 
            self.covariance, 
            time_delta
        )
        
        predicted_state.update_state(predicted_mean, predicted_cov)
        predicted_state.timestamp = self.timestamp + time_delta
        predicted_state.generation = self.generation + int(time_delta)
        
        return predicted_state


class KalmanEvolutionFilter:
    """
    Extended Kalman Filter for evolutionary state estimation.
    
    Patent Feature: Evolutionary dynamics-aware Kalman filtering
    with biological process models and adaptive noise estimation.
    """
    
    def __init__(
        self,
        state_dim: int,
        observation_dim: int,
        process_noise: float = 1e-4,
        measurement_noise: float = 1e-3
    ):
        """
        Initialize Kalman evolution filter.
        
        Args:
            state_dim: Dimension of evolutionary state
            observation_dim: Dimension of observations
            process_noise: Process noise variance
            measurement_noise: Measurement noise variance
        """
        self.state_dim = state_dim
        self.observation_dim = observation_dim
        
        # Current state estimate
        self.state = EvolutionaryState(state_dim)
        
        # Noise parameters
        self.Q = np.eye(state_dim) * process_noise  # Process noise
        self.R = np.eye(observation_dim) * measurement_noise  # Measurement noise
        
        # Evolution model parameters
        self.mutation_rate = 1e-6
        self.selection_strength = 1.0
        self.drift_coefficient = 1e-4
        
        # Filter history
        self.state_history: List[EvolutionaryState] = []
        self.innovation_history: List[np.ndarray] = []
        
        logger.info("Kalman evolution filter initialized")
    
    def predict(self, time_delta: float) -> EvolutionaryState:
        """
        Predict evolutionary state forward in time.
        
        Args:
            time_delta: Time step for prediction
            
        Returns:
            Predicted evolutionary state
        """
        
        # Evolution transition model
        F = self._get_transition_matrix(time_delta)
        
        # Predict state
        predicted_mean = F @ self.state.mean_state
        predicted_covariance = F @ self.state.covariance @ F.T + self.Q
        
        # Create predicted state
        predicted_state = EvolutionaryState(self.state_dim)
        predicted_state.update_state(predicted_mean, predicted_covariance)
        predicted_state.timestamp = self.state.timestamp + time_delta
        predicted_state.generation = self.state.generation + int(time_delta)
        
        return predicted_state
    
    def update(
        self, 
        observation: BiologicalObservation,
        prediction: Optional[EvolutionaryState] = None
    ) -> EvolutionaryState:
        """
        Update state estimate with new observation.
        
        Args:
            observation: New biological observation
            prediction: Optional predicted state (if None, will predict)
            
        Returns:
            Updated evolutionary state
        """
        
        if prediction is None:
            time_delta = observation.timestamp - self.state.timestamp
            prediction = self.predict(time_delta)
        
        # Convert observation to measurement vector
        measurement_vector, measurement_noise = self._observation_to_vector(observation)
        
        # Observation model
        H = self._get_observation_matrix(observation)
        
        # Kalman update equations
        innovation = measurement_vector - H @ prediction.mean_state
        innovation_covariance = H @ prediction.covariance @ H.T + measurement_noise
        
        # Kalman gain
        try:
            if HAS_SCIPY:
                kalman_gain = prediction.covariance @ H.T @ linalg.inv(innovation_covariance)
            else:
                kalman_gain = prediction.covariance @ H.T @ np.linalg.inv(innovation_covariance)
        except np.linalg.LinAlgError:
            logger.warning("Singular innovation covariance, using pseudoinverse")
            kalman_gain = prediction.covariance @ H.T @ np.linalg.pinv(innovation_covariance)
        
        # Update state
        updated_mean = prediction.mean_state + kalman_gain @ innovation
        updated_covariance = (np.eye(self.state_dim) - kalman_gain @ H) @ prediction.covariance
        
        # Create updated state
        updated_state = EvolutionaryState(self.state_dim)
        updated_state.update_state(updated_mean, updated_covariance)
        updated_state.timestamp = observation.timestamp
        updated_state.generation = prediction.generation
        
        # Update internal state
        self.state = updated_state
        
        # Record history
        self.state_history.append(updated_state)
        self.innovation_history.append(innovation)
        
        # Adaptive noise estimation
        self._update_noise_estimates(innovation, innovation_covariance)
        
        return updated_state
    
    def _get_transition_matrix(self, time_delta: float) -> np.ndarray:
        """Get evolution transition matrix F."""
        
        # Simple linear evolution model
        F = np.eye(self.state_dim)
        
        # Add evolutionary dynamics
        if self.state_dim >= 3:
            # [fitness, diversity, population_size, ...]
            
            # Fitness evolution (selection + drift)
            F[0, 0] = 1.0 + self.selection_strength * time_delta
            F[0, 1] = -0.1 * time_delta  # Diversity affects fitness
            
            # Diversity evolution (mutation + selection)
            F[1, 1] = 1.0 - 0.1 * self.selection_strength * time_delta
            F[1, 0] = -0.05 * time_delta  # Selection reduces diversity
            
            # Population size evolution
            if self.state_dim >= 3:
                F[2, 2] = 1.0  # Assume constant population
                F[2, 0] = 0.1 * time_delta  # Fitness affects population
        
        return F
    
    def _get_observation_matrix(self, observation: BiologicalObservation) -> np.ndarray:
        """Get observation matrix H mapping state to observations."""
        
        H = np.zeros((self.observation_dim, self.state_dim))
        
        # Map state components to observations based on data type
        if observation.data_type == DataType.GENOMIC:
            # Genomic data observes molecular state
            H[0, 0] = 1.0  # Fitness from genomic diversity
            if self.state_dim > 1:
                H[1, 1] = 1.0  # Diversity directly observable
        
        elif observation.data_type == DataType.PHENOTYPIC:
            # Phenotypic data observes organismal state
            H[0, 0] = 1.0  # Fitness from phenotype
            if self.observation_dim > 1 and self.state_dim > 2:
                H[1, 2] = 1.0  # Population size affects phenotype
        
        elif observation.data_type == DataType.ENVIRONMENTAL:
            # Environmental data affects all levels
            H[0, :] = 0.1  # Environmental pressure affects all state components
        
        else:
            # Default identity mapping
            min_dim = min(self.observation_dim, self.state_dim)
            H[:min_dim, :min_dim] = np.eye(min_dim)
        
        return H
    
    def _observation_to_vector(
        self, 
        observation: BiologicalObservation
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convert biological observation to measurement vector."""
        
        measurement_vector = np.zeros(self.observation_dim)
        measurement_noise = np.eye(self.observation_dim) * observation.measurement_noise
        
        # Extract values based on data type
        if observation.data_type == DataType.GENOMIC:
            # Extract genomic features
            if 'snp_frequency' in observation.values:
                measurement_vector[0] = observation.values['snp_frequency']
            if 'heterozygosity' in observation.values:
                measurement_vector[1] = observation.values['heterozygosity']
        
        elif observation.data_type == DataType.PHENOTYPIC:
            # Extract phenotypic measurements
            if 'fitness_proxy' in observation.values:
                measurement_vector[0] = observation.values['fitness_proxy']
            if 'population_count' in observation.values:
                measurement_vector[1] = np.log10(observation.values['population_count'] + 1)
        
        elif observation.data_type == DataType.ENVIRONMENTAL:
            # Extract environmental parameters
            if 'temperature' in observation.values:
                measurement_vector[0] = (observation.values['temperature'] - 273.15) / 100  # Normalize
            if 'drug_concentration' in observation.values:
                measurement_vector[1] = np.log10(observation.values['drug_concentration'] + 1e-12)
        
        # Update noise based on observation uncertainties
        for i, key in enumerate(['primary', 'secondary']):
            if i < self.observation_dim and key in observation.uncertainties:
                measurement_noise[i, i] = observation.uncertainties[key] ** 2
        
        return measurement_vector, measurement_noise
    
    def _update_noise_estimates(
        self, 
        innovation: np.ndarray, 
        innovation_covariance: np.ndarray
    ):
        """Adaptively update noise estimates based on innovations."""
        
        # Innovation-based adaptive estimation
        if len(self.innovation_history) > 10:
            recent_innovations = np.array(self.innovation_history[-10:])
            
            # Estimate actual innovation covariance
            empirical_cov = np.cov(recent_innovations.T)
            
            # Update process noise (simplified)
            alpha = 0.05  # Learning rate
            
            if empirical_cov.shape == innovation_covariance.shape:
                adjustment = alpha * (empirical_cov - innovation_covariance)
                
                # Update Q (process noise) - ensure positive definite
                try:
                    self.Q += adjustment[:self.state_dim, :self.state_dim]
                    
                    # Ensure positive definiteness
                    eigenvals = np.linalg.eigvals(self.Q)
                    if np.any(eigenvals <= 0):
                        self.Q = np.eye(self.state_dim) * 1e-4
                
                except Exception as e:
                    logger.warning(f"Error updating process noise: {e}")
    
    def get_state_estimate(self) -> Dict[str, Any]:
        """Get current state estimate with uncertainties."""
        
        return {
            'mean_state': self.state.mean_state.copy(),
            'covariance': self.state.covariance.copy(),
            'uncertainty': self.state.get_uncertainty(),
            'timestamp': self.state.timestamp,
            'generation': self.state.generation,
            'confidence': self.state.confidence
        }
    
    def reset_filter(self, initial_state: Optional[EvolutionaryState] = None):
        """Reset filter to initial conditions."""
        
        if initial_state:
            self.state = initial_state
        else:
            self.state = EvolutionaryState(self.state_dim)
        
        self.state_history.clear()
        self.innovation_history.clear()
        
        logger.info("Kalman evolution filter reset")


class ParticleEvolutionFilter:
    """
    Particle filter for non-linear evolutionary dynamics.
    
    Patent Feature: Particle-based state estimation for complex
    evolutionary systems with non-Gaussian distributions.
    """
    
    def __init__(
        self,
        state_dim: int,
        num_particles: int = 1000,
        resampling_threshold: float = 0.5
    ):
        """
        Initialize particle evolution filter.
        
        Args:
            state_dim: Dimension of evolutionary state
            num_particles: Number of particles
            resampling_threshold: Effective sample size threshold for resampling
        """
        self.state_dim = state_dim
        self.num_particles = num_particles
        self.resampling_threshold = resampling_threshold
        
        # Particle representation
        self.particles = np.random.randn(num_particles, state_dim)
        self.weights = np.ones(num_particles) / num_particles
        
        # Filter parameters
        self.process_noise_std = 0.1
        self.measurement_noise_std = 0.05
        
        # History
        self.particle_history: List[np.ndarray] = []
        self.weight_history: List[np.ndarray] = []
        
        logger.info(f"Particle evolution filter initialized with {num_particles} particles")
    
    def predict(self, time_delta: float) -> np.ndarray:
        """
        Predict particles forward using evolutionary dynamics.
        
        Args:
            time_delta: Time step for prediction
            
        Returns:
            Predicted particles
        """
        
        predicted_particles = np.zeros_like(self.particles)
        
        for i in range(self.num_particles):
            particle = self.particles[i]
            
            # Apply evolutionary dynamics model
            predicted_particle = self._evolve_particle(particle, time_delta)
            
            # Add process noise
            noise = np.random.normal(0, self.process_noise_std, self.state_dim)
            predicted_particles[i] = predicted_particle + noise
        
        self.particles = predicted_particles
        
        return predicted_particles
    
    def update(self, observation: BiologicalObservation) -> np.ndarray:
        """
        Update particle weights based on observation.
        
        Args:
            observation: New biological observation
            
        Returns:
            Updated particle weights
        """
        
        # Convert observation to measurement
        measurement_vector, measurement_noise = self._observation_to_measurement(observation)
        
        # Update weights based on likelihood
        for i in range(self.num_particles):
            particle = self.particles[i]
            
            # Calculate predicted observation
            predicted_obs = self._particle_to_observation(particle, observation.data_type)
            
            # Calculate likelihood
            likelihood = self._calculate_likelihood(
                measurement_vector, 
                predicted_obs, 
                measurement_noise
            )
            
            self.weights[i] *= likelihood
        
        # Normalize weights
        weight_sum = np.sum(self.weights)
        if weight_sum > 0:
            self.weights /= weight_sum
        else:
            # Reset to uniform if all weights are zero
            self.weights = np.ones(self.num_particles) / self.num_particles
        
        # Check effective sample size
        effective_sample_size = 1.0 / np.sum(self.weights ** 2)
        
        if effective_sample_size < self.resampling_threshold * self.num_particles:
            self._resample()
        
        # Record history
        self.particle_history.append(self.particles.copy())
        self.weight_history.append(self.weights.copy())
        
        return self.weights.copy()
    
    def _evolve_particle(self, particle: np.ndarray, time_delta: float) -> np.ndarray:
        """Evolve single particle using evolutionary dynamics."""
        
        evolved = particle.copy()
        
        if len(particle) >= 3:
            # [fitness, diversity, population_size, ...]
            
            # Fitness evolution with selection
            fitness_change = self.selection_strength * particle[0] * time_delta
            fitness_change += np.random.normal(0, 0.01)  # Stochastic component
            evolved[0] = np.clip(particle[0] + fitness_change, 0, 1)
            
            # Diversity evolution with mutation and drift
            mutation_increase = self.mutation_rate * 1000 * time_delta
            selection_decrease = self.selection_strength * particle[1] * 0.1 * time_delta
            diversity_change = mutation_increase - selection_decrease
            evolved[1] = np.clip(particle[1] + diversity_change, 0, 1)
            
            # Population dynamics
            carrying_capacity = 10000
            growth_rate = 0.1 * particle[0]  # Fitness-dependent growth
            pop_change = growth_rate * particle[2] * (1 - particle[2] / carrying_capacity) * time_delta
            evolved[2] = max(1, particle[2] + pop_change)
        
        return evolved
    
    def _particle_to_observation(
        self, 
        particle: np.ndarray, 
        data_type: DataType
    ) -> np.ndarray:
        """Convert particle state to predicted observation."""
        
        observation = np.zeros(self.observation_dim)
        
        if data_type == DataType.GENOMIC:
            # Genomic observations
            if len(particle) >= 2:
                observation[0] = particle[1]  # Diversity -> heterozygosity
                if self.observation_dim > 1:
                    observation[1] = particle[0]  # Fitness -> allele frequency change
        
        elif data_type == DataType.PHENOTYPIC:
            # Phenotypic observations
            observation[0] = particle[0]  # Fitness directly observable
            if self.observation_dim > 1 and len(particle) >= 3:
                observation[1] = np.log10(particle[2] + 1)  # Log population size
        
        elif data_type == DataType.ENVIRONMENTAL:
            # Environmental observations affect all components
            observation[:] = np.mean(particle) * 0.5  # Simplified mapping
        
        return observation
    
    def _observation_to_measurement(
        self, 
        observation: BiologicalObservation
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convert biological observation to measurement vector."""
        
        measurement = np.zeros(self.observation_dim)
        noise_matrix = np.eye(self.observation_dim) * observation.measurement_noise
        
        # Extract relevant values
        if observation.data_type == DataType.GENOMIC:
            values = [
                observation.get_value('heterozygosity', 0.5),
                observation.get_value('allele_frequency_change', 0.0)
            ]
        elif observation.data_type == DataType.PHENOTYPIC:
            values = [
                observation.get_value('fitness_proxy', 0.5),
                observation.get_value('population_size', 1000)
            ]
        else:
            values = [
                observation.get_value('primary_measurement', 0.5),
                observation.get_value('secondary_measurement', 0.0)
            ]
        
        # Fill measurement vector
        for i, value in enumerate(values[:self.observation_dim]):
            measurement[i] = value
            
            # Update noise matrix with observation uncertainties
            uncertainty_key = ['heterozygosity', 'allele_frequency_change', 'fitness_proxy', 'population_size'][i]
            uncertainty = observation.get_uncertainty(uncertainty_key, observation.measurement_noise)
            noise_matrix[i, i] = uncertainty ** 2
        
        return measurement, noise_matrix
    
    def _calculate_likelihood(
        self, 
        measurement: np.ndarray, 
        predicted: np.ndarray,
        noise_covariance: np.ndarray
    ) -> float:
        """Calculate observation likelihood for particle."""
        
        try:
            residual = measurement - predicted
            
            if HAS_SCIPY:
                # Use scipy multivariate normal
                likelihood = multivariate_normal.pdf(
                    residual, 
                    mean=np.zeros_like(residual),
                    cov=noise_covariance
                )
            else:
                # Fallback: Gaussian likelihood
                inv_cov = np.linalg.inv(noise_covariance + np.eye(len(noise_covariance)) * 1e-12)
                exponent = -0.5 * residual.T @ inv_cov @ residual
                normalization = 1.0 / np.sqrt((2 * np.pi) ** len(residual) * np.linalg.det(noise_covariance))
                likelihood = normalization * np.exp(exponent)
            
            return max(likelihood, 1e-12)  # Avoid zero likelihood
            
        except Exception as e:
            logger.warning(f"Error calculating likelihood: {e}")
            return 1e-6
    
    def _resample(self):
        """Resample particles using systematic resampling."""
        
        # Systematic resampling
        cumulative_weights = np.cumsum(self.weights)
        
        # Generate systematic samples
        u = np.random.random() / self.num_particles
        samples = [(u + i / self.num_particles) for i in range(self.num_particles)]
        
        # Resample particles
        resampled_particles = np.zeros_like(self.particles)
        
        i = 0
        for j, sample in enumerate(samples):
            while cumulative_weights[i] < sample:
                i += 1
            resampled_particles[j] = self.particles[i]
        
        self.particles = resampled_particles
        self.weights = np.ones(self.num_particles) / self.num_particles
    
    def get_state_estimate(self) -> Dict[str, Any]:
        """Get weighted state estimate from particles."""
        
        # Weighted mean and covariance
        mean_state = np.average(self.particles, weights=self.weights, axis=0)
        
        # Weighted covariance
        deviations = self.particles - mean_state
        weighted_deviations = deviations * self.weights[:, np.newaxis]
        covariance = weighted_deviations.T @ deviations
        
        # Effective sample size
        effective_sample_size = 1.0 / np.sum(self.weights ** 2)
        
        return {
            'mean_state': mean_state,
            'covariance': covariance,
            'uncertainty': np.trace(covariance) / self.state_dim,
            'effective_sample_size': effective_sample_size,
            'particles': self.particles.copy(),
            'weights': self.weights.copy()
        }


class EnsembleEvolutionFilter:
    """
    Ensemble filter combining multiple filtering approaches.
    
    Patent Feature: Multi-algorithm ensemble with adaptive
    weight adjustment and cross-validation.
    """
    
    def __init__(
        self,
        state_dim: int,
        observation_dim: int,
        ensemble_size: int = 5
    ):
        """
        Initialize ensemble evolution filter.
        
        Args:
            state_dim: Dimension of evolutionary state
            observation_dim: Dimension of observations
            ensemble_size: Number of ensemble members
        """
        self.state_dim = state_dim
        self.observation_dim = observation_dim
        self.ensemble_size = ensemble_size
        
        # Create ensemble of filters
        self.kalman_filters = []
        self.particle_filters = []
        
        for i in range(ensemble_size):
            # Kalman filters with different noise parameters
            process_noise = 1e-4 * (0.5 + i * 0.5)
            measurement_noise = 1e-3 * (0.5 + i * 0.5)
            
            kf = KalmanEvolutionFilter(
                state_dim, observation_dim, 
                process_noise, measurement_noise
            )
            self.kalman_filters.append(kf)
            
            # Particle filters with different particle counts
            num_particles = 500 + i * 200
            pf = ParticleEvolutionFilter(state_dim, num_particles)
            self.particle_filters.append(pf)
        
        # Ensemble weights
        self.kalman_weights = np.ones(ensemble_size) / ensemble_size
        self.particle_weights = np.ones(ensemble_size) / ensemble_size
        
        # Performance tracking
        self.performance_history = {
            'kalman': defaultdict(list),
            'particle': defaultdict(list)
        }
        
        logger.info(f"Ensemble evolution filter initialized with {ensemble_size} members")
    
    def predict(self, time_delta: float) -> Dict[str, Any]:
        """Predict using ensemble of filters."""
        
        kalman_predictions = []
        particle_predictions = []
        
        # Get predictions from all ensemble members
        for i in range(self.ensemble_size):
            # Kalman predictions
            kf_pred = self.kalman_filters[i].predict(time_delta)
            kalman_predictions.append(kf_pred)
            
            # Particle predictions
            pf_pred = self.particle_filters[i].predict(time_delta)
            particle_predictions.append(pf_pred)
        
        # Combine predictions
        ensemble_prediction = self._combine_predictions(
            kalman_predictions, 
            particle_predictions
        )
        
        return ensemble_prediction
    
    def update(self, observation: BiologicalObservation) -> Dict[str, Any]:
        """Update ensemble with new observation."""
        
        kalman_updates = []
        particle_updates = []
        
        # Update all ensemble members
        for i in range(self.ensemble_size):
            try:
                # Kalman update
                kf_update = self.kalman_filters[i].update(observation)
                kalman_updates.append(kf_update)
                
                # Particle update
                pf_weights = self.particle_filters[i].update(observation)
                pf_estimate = self.particle_filters[i].get_state_estimate()
                particle_updates.append(pf_estimate)
                
            except Exception as e:
                logger.warning(f"Error updating ensemble member {i}: {e}")
        
        # Evaluate filter performance
        self._evaluate_filter_performance(observation, kalman_updates, particle_updates)
        
        # Update ensemble weights
        self._update_ensemble_weights()
        
        # Combine updates
        ensemble_update = self._combine_updates(kalman_updates, particle_updates)
        
        return ensemble_update
    
    def _combine_predictions(
        self, 
        kalman_preds: List[EvolutionaryState],
        particle_preds: List[np.ndarray]
    ) -> Dict[str, Any]:
        """Combine predictions from ensemble members."""
        
        # Weighted combination of Kalman predictions
        kalman_mean = np.zeros(self.state_dim)
        kalman_cov = np.zeros((self.state_dim, self.state_dim))
        
        for i, pred in enumerate(kalman_preds):
            weight = self.kalman_weights[i]
            kalman_mean += weight * pred.mean_state
            kalman_cov += weight * pred.covariance
        
        # Weighted combination of particle predictions
        all_particles = []
        all_weights = []
        
        for i, pred in enumerate(particle_preds):
            pf_estimate = self.particle_filters[i].get_state_estimate()
            particles = pf_estimate['particles']
            weights = pf_estimate['weights'] * self.particle_weights[i]
            
            all_particles.extend(particles)
            all_weights.extend(weights)
        
        # Normalize particle weights
        all_weights = np.array(all_weights)
        all_weights /= np.sum(all_weights)
        
        # Particle-based estimate
        particle_mean = np.average(all_particles, weights=all_weights, axis=0)
        
        # Combine Kalman and particle estimates
        final_mean = 0.6 * kalman_mean + 0.4 * particle_mean
        final_cov = kalman_cov  # Use Kalman covariance for stability
        
        return {
            'mean_state': final_mean,
            'covariance': final_cov,
            'kalman_estimate': kalman_mean,
            'particle_estimate': particle_mean,
            'ensemble_uncertainty': np.trace(final_cov) / self.state_dim
        }
    
    def _combine_updates(
        self, 
        kalman_updates: List[EvolutionaryState],
        particle_updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Combine state updates from ensemble members."""
        
        # Similar to combine_predictions but for updates
        return self._combine_predictions(kalman_updates, [])
    
    def _evaluate_filter_performance(
        self,
        observation: BiologicalObservation,
        kalman_updates: List[EvolutionaryState],
        particle_updates: List[Dict[str, Any]]
    ):
        """Evaluate performance of individual filters."""
        
        # Extract true measurement
        true_measurement, _ = self._observation_to_measurement(observation)
        
        # Evaluate Kalman filters
        for i, update in enumerate(kalman_updates):
            predicted_obs = self._state_to_observation(update.mean_state, observation.data_type)
            error = np.linalg.norm(true_measurement - predicted_obs)
            
            self.performance_history['kalman'][i].append(error)
        
        # Evaluate particle filters
        for i, update in enumerate(particle_updates):
            predicted_obs = self._state_to_observation(update['mean_state'], observation.data_type)
            error = np.linalg.norm(true_measurement - predicted_obs)
            
            self.performance_history['particle'][i].append(error)
    
    def _update_ensemble_weights(self):
        """Update ensemble weights based on recent performance."""
        
        if not self.performance_history['kalman']:
            return
        
        # Update Kalman weights
        kalman_errors = []
        for i in range(self.ensemble_size):
            if self.performance_history['kalman'][i]:
                recent_error = np.mean(self.performance_history['kalman'][i][-10:])
                kalman_errors.append(recent_error)
            else:
                kalman_errors.append(1.0)
        
        # Convert errors to weights (inverse relationship)
        kalman_errors = np.array(kalman_errors)
        self.kalman_weights = 1.0 / (kalman_errors + 1e-6)
        self.kalman_weights /= np.sum(self.kalman_weights)
        
        # Update particle weights similarly
        particle_errors = []
        for i in range(self.ensemble_size):
            if self.performance_history['particle'][i]:
                recent_error = np.mean(self.performance_history['particle'][i][-10:])
                particle_errors.append(recent_error)
            else:
                particle_errors.append(1.0)
        
        particle_errors = np.array(particle_errors)
        self.particle_weights = 1.0 / (particle_errors + 1e-6)
        self.particle_weights /= np.sum(self.particle_weights)
    
    def _observation_to_measurement(
        self, 
        observation: BiologicalObservation
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convert observation to measurement (delegate to Kalman filter)."""
        
        if self.kalman_filters:
            return self.kalman_filters[0]._observation_to_vector(observation)
        else:
            measurement = np.zeros(self.observation_dim)
            noise = np.eye(self.observation_dim) * observation.measurement_noise
            return measurement, noise
    
    def _state_to_observation(
        self, 
        state: np.ndarray, 
        data_type: DataType
    ) -> np.ndarray:
        """Convert state to predicted observation."""
        
        observation = np.zeros(self.observation_dim)
        
        if data_type == DataType.GENOMIC:
            if len(state) >= 2:
                observation[0] = state[1]  # Diversity
                if self.observation_dim > 1:
                    observation[1] = state[0]  # Fitness
        
        elif data_type == DataType.PHENOTYPIC:
            observation[0] = state[0] if len(state) > 0 else 0.5
            if self.observation_dim > 1 and len(state) >= 3:
                observation[1] = np.log10(state[2] + 1)
        
        return observation
    
    def get_ensemble_statistics(self) -> Dict[str, Any]:
        """Get ensemble performance statistics."""
        
        stats = {
            'kalman_weights': self.kalman_weights.copy(),
            'particle_weights': self.particle_weights.copy(),
            'performance_summary': {}
        }
        
        # Kalman performance summary
        if self.performance_history['kalman']:
            kalman_performances = []
            for i in range(self.ensemble_size):
                if self.performance_history['kalman'][i]:
                    avg_error = np.mean(self.performance_history['kalman'][i])
                    kalman_performances.append(avg_error)
            
            stats['performance_summary']['kalman'] = {
                'mean_error': np.mean(kalman_performances) if kalman_performances else 0.0,
                'std_error': np.std(kalman_performances) if kalman_performances else 0.0,
                'best_member': np.argmin(kalman_performances) if kalman_performances else 0
            }
        
        # Particle performance summary
        if self.performance_history['particle']:
            particle_performances = []
            for i in range(self.ensemble_size):
                if self.performance_history['particle'][i]:
                    avg_error = np.mean(self.performance_history['particle'][i])
                    particle_performances.append(avg_error)
            
            stats['performance_summary']['particle'] = {
                'mean_error': np.mean(particle_performances) if particle_performances else 0.0,
                'std_error': np.std(particle_performances) if particle_performances else 0.0,
                'best_member': np.argmin(particle_performances) if particle_performances else 0
            }
        
        return stats


class EvolutionaryDataAssimilator:
    """
    Main data assimilation coordinator.
    
    Patent Feature: Intelligent data assimilation with automatic
    filter selection and biological knowledge integration.
    """
    
    def __init__(
        self,
        state_dim: int = 10,
        observation_dim: int = 5,
        use_ensemble: bool = True
    ):
        """
        Initialize evolutionary data assimilator.
        
        Args:
            state_dim: Dimension of evolutionary state
            observation_dim: Dimension of observations
            use_ensemble: Whether to use ensemble filtering
        """
        self.state_dim = state_dim
        self.observation_dim = observation_dim
        self.use_ensemble = use_ensemble
        
        # Initialize filters
        if use_ensemble:
            self.primary_filter = EnsembleEvolutionFilter(state_dim, observation_dim)
        else:
            self.primary_filter = KalmanEvolutionFilter(state_dim, observation_dim)
        
        # Data management
        self.observation_buffer: deque = deque(maxlen=1000)
        self.assimilation_log: List[Dict[str, Any]] = []
        
        # Performance metrics
        self.prediction_errors: List[float] = []
        self.assimilation_times: List[float] = []
        
        logger.info("Evolutionary data assimilator initialized")
    
    def add_observation(self, observation: BiologicalObservation):
        """Add new biological observation to buffer."""
        
        self.observation_buffer.append(observation)
        logger.debug(f"Added {observation.data_type.name} observation at t={observation.timestamp}")
    
    def assimilate_data(
        self, 
        batch_size: Optional[int] = None,
        real_time: bool = False
    ) -> Dict[str, Any]:
        """
        Assimilate buffered observations into evolutionary state.
        
        Args:
            batch_size: Number of observations to process (None for all)
            real_time: Whether to process in real-time mode
            
        Returns:
            Assimilation results
        """
        
        if not self.observation_buffer:
            logger.warning("No observations to assimilate")
            return {'state_estimate': self.primary_filter.get_state_estimate()}
        
        start_time = time.time()
        
        # Process observations
        observations_to_process = list(self.observation_buffer)
        if batch_size:
            observations_to_process = observations_to_process[:batch_size]
        
        # Sort by timestamp
        observations_to_process.sort(key=lambda obs: obs.timestamp)
        
        assimilation_results = []
        
        for i, observation in enumerate(observations_to_process):
            try:
                # Predict forward if needed
                if i == 0 or not real_time:
                    time_delta = 1.0  # Default time step
                else:
                    time_delta = observation.timestamp - observations_to_process[i-1].timestamp
                
                prediction = self.primary_filter.predict(time_delta)
                
                # Update with observation
                update = self.primary_filter.update(observation, prediction)
                
                # Record results
                result = {
                    'observation_id': observation.observation_id,
                    'timestamp': observation.timestamp,
                    'data_type': observation.data_type.name,
                    'prediction': prediction if hasattr(prediction, 'mean_state') else None,
                    'update': update if hasattr(update, 'mean_state') else None,
                    'innovation': self._calculate_innovation(observation, prediction)
                }
                
                assimilation_results.append(result)
                
            except Exception as e:
                logger.error(f"Error assimilating observation {observation.observation_id}: {e}")
        
        # Clear processed observations
        for _ in range(len(observations_to_process)):
            if self.observation_buffer:
                self.observation_buffer.popleft()
        
        # Calculate performance metrics
        assimilation_time = time.time() - start_time
        self.assimilation_times.append(assimilation_time)
        
        # Get final state estimate
        final_state = self.primary_filter.get_state_estimate()
        
        # Log assimilation
        log_entry = {
            'timestamp': time.time(),
            'observations_processed': len(observations_to_process),
            'assimilation_time': assimilation_time,
            'final_uncertainty': final_state.get('uncertainty', 0.0),
            'filter_type': type(self.primary_filter).__name__
        }
        
        self.assimilation_log.append(log_entry)
        
        return {
            'state_estimate': final_state,
            'assimilation_results': assimilation_results,
            'performance_metrics': {
                'assimilation_time': assimilation_time,
                'observations_processed': len(observations_to_process),
                'final_uncertainty': final_state.get('uncertainty', 0.0)
            }
        }
    
    def _calculate_innovation(
        self, 
        observation: BiologicalObservation, 
        prediction: Any
    ) -> Optional[np.ndarray]:
        """Calculate innovation (observation - prediction)."""
        
        try:
            if hasattr(self.primary_filter, '_observation_to_vector'):
                obs_vector, _ = self.primary_filter._observation_to_vector(observation)
                
                if hasattr(prediction, 'mean_state'):
                    pred_obs = self._state_to_observation(prediction.mean_state, observation.data_type)
                    return obs_vector - pred_obs
            
            return None
            
        except Exception as e:
            logger.warning(f"Error calculating innovation: {e}")
            return None
    
    def _state_to_observation(self, state: np.ndarray, data_type: DataType) -> np.ndarray:
        """Convert state to predicted observation."""
        
        observation = np.zeros(self.observation_dim)
        
        # Simple mapping based on data type
        if data_type == DataType.GENOMIC and len(state) >= 2:
            observation[0] = state[1]  # Diversity
            if self.observation_dim > 1:
                observation[1] = state[0]  # Fitness
        
        elif data_type == DataType.PHENOTYPIC and len(state) >= 1:
            observation[0] = state[0]  # Fitness
            if self.observation_dim > 1 and len(state) >= 3:
                observation[1] = np.log10(state[2] + 1)  # Population size
        
        return observation
    
    def get_assimilation_summary(self) -> Dict[str, Any]:
        """Get summary of data assimilation performance."""
        
        if not self.assimilation_log:
            return {'message': 'No assimilation performed yet'}
        
        total_observations = sum(entry['observations_processed'] for entry in self.assimilation_log)
        total_time = sum(entry['assimilation_time'] for entry in self.assimilation_log)
        
        avg_uncertainty = np.mean([
            entry['final_uncertainty'] for entry in self.assimilation_log
        ])
        
        return {
            'total_observations_processed': total_observations,
            'total_assimilation_time': total_time,
            'average_uncertainty': avg_uncertainty,
            'observations_per_second': total_observations / total_time if total_time > 0 else 0,
            'assimilation_sessions': len(self.assimilation_log),
            'filter_type': self.assimilation_log[-1]['filter_type'] if self.assimilation_log else 'Unknown'
        }
