"""
Uncertainty Quantification Engine

Patent-pending system for quantifying and propagating uncertainties
in evolutionary simulations with Bayesian neural networks.
"""

from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np
import logging
from abc import ABC, abstractmethod
import math
from collections import defaultdict
import time
import warnings

try:
    from scipy.stats import (
        norm, gamma, beta, dirichlet, 
        multivariate_normal, gaussian_kde
    )
    from scipy.optimize import minimize
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    
    # Fallback implementations
    class norm:
        @staticmethod
        def pdf(x, loc=0, scale=1):
            return np.exp(-0.5 * ((x - loc) / scale) ** 2) / (scale * np.sqrt(2 * np.pi))
        
        @staticmethod
        def rvs(loc=0, scale=1, size=None):
            if size is None:
                return np.random.normal(loc, scale)
            return np.random.normal(loc, scale, size)

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    
    # Fallback neural network implementations
    class nn:
        class Module:
            def __init__(self):
                pass
        
        class Linear:
            def __init__(self, in_features, out_features):
                self.weight = np.random.randn(out_features, in_features) * 0.1
                self.bias = np.zeros(out_features)
        
        class Dropout:
            def __init__(self, p=0.5):
                self.p = p

logger = logging.getLogger(__name__)


class UncertaintyType(Enum):
    """Types of uncertainty in evolutionary systems."""
    
    ALEATORIC = auto()      # Inherent randomness
    EPISTEMIC = auto()      # Knowledge uncertainty
    MODEL = auto()          # Model uncertainty
    PARAMETER = auto()      # Parameter uncertainty
    MEASUREMENT = auto()    # Measurement uncertainty
    TEMPORAL = auto()       # Temporal uncertainty
    SPATIAL = auto()        # Spatial uncertainty


@dataclass
class UncertaintyDistribution:
    """
    Represents uncertainty as a probability distribution.
    
    Patent Feature: Multi-type uncertainty representation
    with distribution parameters and sampling methods.
    """
    
    distribution_type: str
    parameters: Dict[str, float]
    uncertainty_type: UncertaintyType
    
    # Statistical properties
    mean: float = 0.0
    variance: float = 1.0
    confidence_interval: Tuple[float, float] = field(default_factory=lambda: (-1.0, 1.0))
    
    # Metadata
    timestamp: float = field(default_factory=time.time)
    source: str = "unknown"
    
    def sample(self, num_samples: int = 1) -> np.ndarray:
        """Sample from the uncertainty distribution."""
        
        if self.distribution_type == 'normal':
            loc = self.parameters.get('loc', self.mean)
            scale = self.parameters.get('scale', np.sqrt(self.variance))
            
            if HAS_SCIPY:
                return norm.rvs(loc=loc, scale=scale, size=num_samples)
            else:
                return np.random.normal(loc, scale, num_samples)
        
        elif self.distribution_type == 'gamma':
            shape = self.parameters.get('shape', 2.0)
            scale = self.parameters.get('scale', 1.0)
            
            return np.random.gamma(shape, scale, num_samples)
        
        elif self.distribution_type == 'beta':
            alpha = self.parameters.get('alpha', 1.0)
            beta_param = self.parameters.get('beta', 1.0)
            
            return np.random.beta(alpha, beta_param, num_samples)
        
        elif self.distribution_type == 'uniform':
            low = self.parameters.get('low', 0.0)
            high = self.parameters.get('high', 1.0)
            
            return np.random.uniform(low, high, num_samples)
        
        else:
            # Default to normal distribution
            return np.random.normal(self.mean, np.sqrt(self.variance), num_samples)
    
    def pdf(self, x: np.ndarray) -> np.ndarray:
        """Calculate probability density function."""
        
        if self.distribution_type == 'normal':
            loc = self.parameters.get('loc', self.mean)
            scale = self.parameters.get('scale', np.sqrt(self.variance))
            
            if HAS_SCIPY:
                return norm.pdf(x, loc=loc, scale=scale)
            else:
                return norm.pdf(x, loc, scale)
        
        elif self.distribution_type == 'gamma':
            shape = self.parameters.get('shape', 2.0)
            scale = self.parameters.get('scale', 1.0)
            
            # Simplified gamma PDF
            return np.power(x, shape - 1) * np.exp(-x / scale) / (scale ** shape * math.gamma(shape))
        
        else:
            # Default normal PDF
            loc = self.mean
            scale = np.sqrt(self.variance)
            return np.exp(-0.5 * ((x - loc) / scale) ** 2) / (scale * np.sqrt(2 * np.pi))
    
    def update_parameters(self, new_params: Dict[str, float]):
        """Update distribution parameters."""
        
        self.parameters.update(new_params)
        
        # Update derived properties
        if self.distribution_type == 'normal':
            self.mean = self.parameters.get('loc', self.mean)
            self.variance = self.parameters.get('scale', np.sqrt(self.variance)) ** 2
        
        elif self.distribution_type == 'gamma':
            shape = self.parameters.get('shape', 2.0)
            scale = self.parameters.get('scale', 1.0)
            self.mean = shape * scale
            self.variance = shape * scale ** 2


class BayesianNeuralNetwork:
    """
    Bayesian Neural Network for uncertainty-aware predictions.
    
    Patent Feature: Evolutionary parameter estimation with
    uncertainty propagation through neural architectures.
    """
    
    def __init__(
        self,
        input_dim: int,
        hidden_dims: List[int],
        output_dim: int,
        num_samples: int = 100,
        prior_std: float = 1.0
    ):
        """
        Initialize Bayesian neural network.
        
        Args:
            input_dim: Input dimension
            hidden_dims: Hidden layer dimensions
            output_dim: Output dimension
            num_samples: Number of posterior samples
            prior_std: Prior standard deviation for weights
        """
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.output_dim = output_dim
        self.num_samples = num_samples
        self.prior_std = prior_std
        
        # Network architecture
        self.layers = []
        layer_dims = [input_dim] + hidden_dims + [output_dim]
        
        for i in range(len(layer_dims) - 1):
            layer_info = {
                'input_dim': layer_dims[i],
                'output_dim': layer_dims[i + 1],
                'weight_mean': np.random.randn(layer_dims[i + 1], layer_dims[i]) * 0.1,
                'weight_std': np.ones((layer_dims[i + 1], layer_dims[i])) * prior_std,
                'bias_mean': np.zeros(layer_dims[i + 1]),
                'bias_std': np.ones(layer_dims[i + 1]) * prior_std
            }
            self.layers.append(layer_info)
        
        # Training history
        self.training_history: List[Dict[str, float]] = []
        
        logger.info(f"Bayesian neural network initialized with {len(self.layers)} layers")
    
    def forward_with_uncertainty(
        self, 
        x: np.ndarray, 
        num_samples: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Forward pass with uncertainty quantification.
        
        Args:
            x: Input data
            num_samples: Number of weight samples for uncertainty
            
        Returns:
            (mean_output, uncertainty_output)
        """
        
        if num_samples is None:
            num_samples = self.num_samples
        
        outputs = []
        
        # Sample from posterior and make predictions
        for _ in range(num_samples):
            sample_weights = []
            sample_biases = []
            
            # Sample weights and biases
            for layer in self.layers:
                weight_sample = np.random.normal(
                    layer['weight_mean'], 
                    layer['weight_std']
                )
                bias_sample = np.random.normal(
                    layer['bias_mean'], 
                    layer['bias_std']
                )
                
                sample_weights.append(weight_sample)
                sample_biases.append(bias_sample)
            
            # Forward pass with sampled parameters
            output = self._forward_pass(x, sample_weights, sample_biases)
            outputs.append(output)
        
        outputs = np.array(outputs)
        
        # Calculate statistics
        mean_output = np.mean(outputs, axis=0)
        uncertainty_output = np.std(outputs, axis=0)
        
        return mean_output, uncertainty_output
    
    def _forward_pass(
        self, 
        x: np.ndarray, 
        weights: List[np.ndarray], 
        biases: List[np.ndarray]
    ) -> np.ndarray:
        """Single forward pass with given parameters."""
        
        current_input = x
        
        for i, (weight, bias) in enumerate(zip(weights, biases)):
            # Linear transformation
            current_input = current_input @ weight.T + bias
            
            # Activation function (ReLU for hidden, linear for output)
            if i < len(weights) - 1:
                current_input = np.maximum(0, current_input)  # ReLU
        
        return current_input
    
    def train_variational(
        self, 
        x_train: np.ndarray, 
        y_train: np.ndarray,
        num_epochs: int = 1000,
        learning_rate: float = 0.01
    ):
        """
        Train using variational inference.
        
        Args:
            x_train: Training inputs
            y_train: Training targets
            num_epochs: Number of training epochs
            learning_rate: Learning rate
        """
        
        logger.info("Starting variational training")
        
        for epoch in range(num_epochs):
            # Sample from current posterior
            predictions, uncertainties = self.forward_with_uncertainty(x_train, num_samples=10)
            
            # Calculate loss
            mse_loss = np.mean((predictions - y_train) ** 2)
            kl_loss = self._calculate_kl_divergence()
            total_loss = mse_loss + 0.01 * kl_loss  # Weight KL term
            
            # Update parameters using gradient approximation
            self._update_parameters(x_train, y_train, learning_rate)
            
            # Record training progress
            if epoch % 100 == 0:
                self.training_history.append({
                    'epoch': epoch,
                    'mse_loss': mse_loss,
                    'kl_loss': kl_loss,
                    'total_loss': total_loss,
                    'mean_uncertainty': np.mean(uncertainties)
                })
                
                logger.debug(f"Epoch {epoch}: loss={total_loss:.4f}, uncertainty={np.mean(uncertainties):.4f}")
        
        logger.info("Variational training completed")
    
    def _calculate_kl_divergence(self) -> float:
        """Calculate KL divergence between posterior and prior."""
        
        kl_div = 0.0
        
        for layer in self.layers:
            # KL divergence for weights
            weight_kl = np.sum(
                0.5 * (
                    layer['weight_std'] ** 2 / self.prior_std ** 2 +
                    layer['weight_mean'] ** 2 / self.prior_std ** 2 -
                    1 -
                    2 * np.log(layer['weight_std'] / self.prior_std)
                )
            )
            
            # KL divergence for biases
            bias_kl = np.sum(
                0.5 * (
                    layer['bias_std'] ** 2 / self.prior_std ** 2 +
                    layer['bias_mean'] ** 2 / self.prior_std ** 2 -
                    1 -
                    2 * np.log(layer['bias_std'] / self.prior_std)
                )
            )
            
            kl_div += weight_kl + bias_kl
        
        return kl_div
    
    def _update_parameters(
        self, 
        x_train: np.ndarray, 
        y_train: np.ndarray, 
        learning_rate: float
    ):
        """Update variational parameters using gradient approximation."""
        
        # Simple gradient approximation for parameter updates
        epsilon = 1e-6
        
        for layer_idx, layer in enumerate(self.layers):
            # Update weight means
            for i in range(layer['weight_mean'].shape[0]):
                for j in range(layer['weight_mean'].shape[1]):
                    # Finite difference gradient approximation
                    original_val = layer['weight_mean'][i, j]
                    
                    layer['weight_mean'][i, j] = original_val + epsilon
                    loss_plus, _ = self._evaluate_loss(x_train, y_train)
                    
                    layer['weight_mean'][i, j] = original_val - epsilon
                    loss_minus, _ = self._evaluate_loss(x_train, y_train)
                    
                    gradient = (loss_plus - loss_minus) / (2 * epsilon)
                    
                    # Update
                    layer['weight_mean'][i, j] = original_val - learning_rate * gradient
            
            # Update weight stds (ensure positive)
            layer['weight_std'] = np.maximum(
                layer['weight_std'] * 0.999,  # Slow decay
                0.01  # Minimum std
            )
    
    def _evaluate_loss(self, x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
        """Evaluate loss function."""
        
        predictions, uncertainties = self.forward_with_uncertainty(x, num_samples=5)
        
        mse_loss = np.mean((predictions - y) ** 2)
        kl_loss = self._calculate_kl_divergence()
        
        return mse_loss, kl_loss
    
    def get_parameter_uncertainty(self) -> Dict[str, np.ndarray]:
        """Get uncertainty in network parameters."""
        
        param_uncertainties = {}
        
        for i, layer in enumerate(self.layers):
            param_uncertainties[f'layer_{i}_weight_std'] = layer['weight_std'].copy()
            param_uncertainties[f'layer_{i}_bias_std'] = layer['bias_std'].copy()
        
        return param_uncertainties


class MonteCarloDropout:
    """
    Monte Carlo Dropout for uncertainty estimation.
    
    Patent Feature: Efficient uncertainty estimation using
    dropout variational inference in evolutionary networks.
    """
    
    def __init__(
        self,
        network_architecture: List[int],
        dropout_rate: float = 0.5,
        num_samples: int = 100
    ):
        """
        Initialize Monte Carlo Dropout.
        
        Args:
            network_architecture: List of layer sizes
            dropout_rate: Dropout probability
            num_samples: Number of MC samples
        """
        self.architecture = network_architecture
        self.dropout_rate = dropout_rate
        self.num_samples = num_samples
        
        # Initialize network weights
        self.weights = []
        self.biases = []
        
        for i in range(len(network_architecture) - 1):
            weight = np.random.randn(
                network_architecture[i + 1], 
                network_architecture[i]
            ) * np.sqrt(2.0 / network_architecture[i])
            
            bias = np.zeros(network_architecture[i + 1])
            
            self.weights.append(weight)
            self.biases.append(bias)
        
        logger.info(f"Monte Carlo Dropout initialized with {len(self.weights)} layers")
    
    def forward_with_dropout(self, x: np.ndarray) -> np.ndarray:
        """Forward pass with dropout applied."""
        
        current_input = x
        
        for i, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            # Linear transformation
            current_input = current_input @ weight.T + bias
            
            # Apply dropout (except for output layer)
            if i < len(self.weights) - 1:
                # ReLU activation
                current_input = np.maximum(0, current_input)
                
                # Dropout
                dropout_mask = np.random.binomial(1, 1 - self.dropout_rate, current_input.shape)
                current_input = current_input * dropout_mask / (1 - self.dropout_rate)
        
        return current_input
    
    def predict_with_uncertainty(self, x: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions with uncertainty estimates.
        
        Args:
            x: Input data
            
        Returns:
            (mean_predictions, prediction_uncertainty)
        """
        
        predictions = []
        
        # Multiple forward passes with dropout
        for _ in range(self.num_samples):
            pred = self.forward_with_dropout(x)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # Calculate statistics
        mean_predictions = np.mean(predictions, axis=0)
        prediction_uncertainty = np.std(predictions, axis=0)
        
        return mean_predictions, prediction_uncertainty
    
    def estimate_epistemic_uncertainty(self, x: np.ndarray) -> np.ndarray:
        """Estimate epistemic (model) uncertainty."""
        
        _, total_uncertainty = self.predict_with_uncertainty(x)
        
        # Epistemic uncertainty is related to variance across predictions
        return total_uncertainty
    
    def train_with_uncertainty(
        self, 
        x_train: np.ndarray, 
        y_train: np.ndarray,
        num_epochs: int = 500,
        learning_rate: float = 0.01
    ):
        """
        Train network while tracking uncertainty.
        
        Args:
            x_train: Training inputs
            y_train: Training targets
            num_epochs: Number of training epochs
            learning_rate: Learning rate
        """
        
        training_losses = []
        uncertainty_history = []
        
        for epoch in range(num_epochs):
            # Forward pass with dropout
            predictions = self.forward_with_dropout(x_train)
            
            # Calculate loss
            loss = np.mean((predictions - y_train) ** 2)
            training_losses.append(loss)
            
            # Estimate current uncertainty
            _, uncertainty = self.predict_with_uncertainty(x_train)
            mean_uncertainty = np.mean(uncertainty)
            uncertainty_history.append(mean_uncertainty)
            
            # Simple gradient descent update
            self._update_weights(x_train, y_train, predictions, learning_rate)
            
            if epoch % 100 == 0:
                logger.debug(f"Epoch {epoch}: loss={loss:.4f}, uncertainty={mean_uncertainty:.4f}")
        
        return {
            'training_losses': training_losses,
            'uncertainty_history': uncertainty_history,
            'final_loss': training_losses[-1] if training_losses else float('inf')
        }
    
    def _update_weights(
        self, 
        x: np.ndarray, 
        y: np.ndarray, 
        predictions: np.ndarray, 
        learning_rate: float
    ):
        """Update weights using simplified gradient descent."""
        
        # Simplified weight update (placeholder for full backpropagation)
        error = predictions - y
        
        # Update last layer
        if self.weights:
            last_layer_grad = np.outer(error.mean(axis=0), x.mean(axis=0))
            self.weights[-1] -= learning_rate * last_layer_grad[:self.weights[-1].shape[0], :self.weights[-1].shape[1]]


class UncertaintyPropagator:
    """
    Propagates uncertainties through evolutionary computations.
    
    Patent Feature: Multi-scale uncertainty propagation with
    cross-scale coupling and temporal evolution.
    """
    
    def __init__(self):
        """Initialize uncertainty propagator."""
        
        self.propagation_methods = {
            'monte_carlo': self._monte_carlo_propagation,
            'linear_approximation': self._linear_propagation,
            'unscented_transform': self._unscented_propagation,
            'polynomial_chaos': self._polynomial_chaos_propagation
        }
        
        # Propagation history
        self.propagation_history: List[Dict[str, Any]] = []
        
        logger.info("Uncertainty propagator initialized")
    
    def propagate_uncertainty(
        self,
        input_distributions: List[UncertaintyDistribution],
        computation_function: Callable,
        method: str = 'monte_carlo',
        num_samples: int = 1000
    ) -> UncertaintyDistribution:
        """
        Propagate uncertainties through a computation.
        
        Args:
            input_distributions: Input uncertainty distributions
            computation_function: Function to propagate through
            method: Propagation method
            num_samples: Number of samples for MC methods
            
        Returns:
            Output uncertainty distribution
        """
        
        if method not in self.propagation_methods:
            logger.warning(f"Unknown method '{method}', using monte_carlo")
            method = 'monte_carlo'
        
        start_time = time.time()
        
        propagator = self.propagation_methods[method]
        output_distribution = propagator(
            input_distributions, 
            computation_function, 
            num_samples
        )
        
        propagation_time = time.time() - start_time
        
        # Record propagation
        self.propagation_history.append({
            'method': method,
            'num_inputs': len(input_distributions),
            'num_samples': num_samples,
            'propagation_time': propagation_time,
            'timestamp': time.time()
        })
        
        return output_distribution
    
    def _monte_carlo_propagation(
        self,
        input_distributions: List[UncertaintyDistribution],
        computation_function: Callable,
        num_samples: int
    ) -> UncertaintyDistribution:
        """Monte Carlo uncertainty propagation."""
        
        # Sample from all input distributions
        input_samples = []
        for dist in input_distributions:
            samples = dist.sample(num_samples)
            input_samples.append(samples)
        
        input_samples = np.array(input_samples).T  # Shape: (num_samples, num_inputs)
        
        # Evaluate function for all samples
        output_samples = []
        
        for sample in input_samples:
            try:
                output = computation_function(sample)
                if isinstance(output, (int, float)):
                    output_samples.append(output)
                elif hasattr(output, '__len__'):
                    output_samples.append(np.mean(output))  # Average for vector outputs
                else:
                    output_samples.append(0.0)
                    
            except Exception as e:
                logger.warning(f"Error in computation function: {e}")
                output_samples.append(0.0)
        
        output_samples = np.array(output_samples)
        
        # Create output distribution
        output_mean = np.mean(output_samples)
        output_variance = np.var(output_samples)
        
        # Determine distribution type based on output characteristics
        if np.all(output_samples >= 0):
            if np.all(output_samples <= 1):
                dist_type = 'beta'
                # Estimate beta parameters
                if output_variance > 0:
                    alpha = output_mean * (output_mean * (1 - output_mean) / output_variance - 1)
                    beta_param = (1 - output_mean) * (output_mean * (1 - output_mean) / output_variance - 1)
                    parameters = {'alpha': max(alpha, 0.1), 'beta': max(beta_param, 0.1)}
                else:
                    parameters = {'alpha': 1.0, 'beta': 1.0}
            else:
                dist_type = 'gamma'
                # Estimate gamma parameters
                if output_variance > 0:
                    scale = output_variance / output_mean
                    shape = output_mean / scale
                    parameters = {'shape': max(shape, 0.1), 'scale': max(scale, 0.1)}
                else:
                    parameters = {'shape': 1.0, 'scale': 1.0}
        else:
            dist_type = 'normal'
            parameters = {'loc': output_mean, 'scale': np.sqrt(output_variance)}
        
        output_distribution = UncertaintyDistribution(
            distribution_type=dist_type,
            parameters=parameters,
            uncertainty_type=UncertaintyType.MODEL,
            mean=output_mean,
            variance=output_variance
        )
        
        return output_distribution
    
    def _linear_propagation(
        self,
        input_distributions: List[UncertaintyDistribution],
        computation_function: Callable,
        num_samples: int
    ) -> UncertaintyDistribution:
        """Linear uncertainty propagation using first-order Taylor expansion."""
        
        # Evaluate function at mean values
        input_means = [dist.mean for dist in input_distributions]
        mean_output = computation_function(np.array(input_means))
        
        if not isinstance(mean_output, (int, float)):
            mean_output = np.mean(mean_output) if hasattr(mean_output, '__len__') else 0.0
        
        # Calculate Jacobian numerically
        epsilon = 1e-6
        jacobian = []
        
        for i, dist in enumerate(input_distributions):
            perturbed_input = input_means.copy()
            perturbed_input[i] += epsilon
            
            try:
                perturbed_output = computation_function(np.array(perturbed_input))
                if not isinstance(perturbed_output, (int, float)):
                    perturbed_output = np.mean(perturbed_output) if hasattr(perturbed_output, '__len__') else 0.0
                
                gradient = (perturbed_output - mean_output) / epsilon
                jacobian.append(gradient)
                
            except Exception as e:
                logger.warning(f"Error calculating gradient: {e}")
                jacobian.append(0.0)
        
        jacobian = np.array(jacobian)
        
        # Propagate variance linearly
        input_variances = [dist.variance for dist in input_distributions]
        output_variance = np.sum(jacobian ** 2 * input_variances)
        
        output_distribution = UncertaintyDistribution(
            distribution_type='normal',
            parameters={'loc': mean_output, 'scale': np.sqrt(output_variance)},
            uncertainty_type=UncertaintyType.MODEL,
            mean=mean_output,
            variance=output_variance
        )
        
        return output_distribution
    
    def _unscented_propagation(
        self,
        input_distributions: List[UncertaintyDistribution],
        computation_function: Callable,
        num_samples: int
    ) -> UncertaintyDistribution:
        """Unscented transform for uncertainty propagation."""
        
        n_dims = len(input_distributions)
        
        # Create sigma points
        input_means = np.array([dist.mean for dist in input_distributions])
        input_covariance = np.diag([dist.variance for dist in input_distributions])
        
        # Unscented transform parameters
        alpha = 1e-3
        beta = 2.0
        kappa = 0.0
        lambda_param = alpha ** 2 * (n_dims + kappa) - n_dims
        
        # Generate sigma points
        sigma_points = []
        
        # Central point
        sigma_points.append(input_means)
        
        # Positive and negative sigma points
        try:
            sqrt_matrix = np.linalg.cholesky((n_dims + lambda_param) * input_covariance)
            
            for i in range(n_dims):
                sigma_points.append(input_means + sqrt_matrix[i])
                sigma_points.append(input_means - sqrt_matrix[i])
                
        except np.linalg.LinAlgError:
            # Fallback to diagonal if Cholesky fails
            sqrt_diag = np.sqrt(np.diag(input_covariance) * (n_dims + lambda_param))
            
            for i in range(n_dims):
                perturbation = np.zeros(n_dims)
                perturbation[i] = sqrt_diag[i]
                sigma_points.append(input_means + perturbation)
                sigma_points.append(input_means - perturbation)
        
        # Evaluate function at sigma points
        output_points = []
        for point in sigma_points:
            try:
                output = computation_function(point)
                if isinstance(output, (int, float)):
                    output_points.append(output)
                else:
                    output_points.append(np.mean(output) if hasattr(output, '__len__') else 0.0)
            except Exception as e:
                logger.warning(f"Error evaluating function at sigma point: {e}")
                output_points.append(0.0)
        
        output_points = np.array(output_points)
        
        # Calculate weights
        w_m = np.zeros(2 * n_dims + 1)
        w_c = np.zeros(2 * n_dims + 1)
        
        w_m[0] = lambda_param / (n_dims + lambda_param)
        w_c[0] = lambda_param / (n_dims + lambda_param) + (1 - alpha ** 2 + beta)
        
        for i in range(1, 2 * n_dims + 1):
            w_m[i] = 1.0 / (2 * (n_dims + lambda_param))
            w_c[i] = 1.0 / (2 * (n_dims + lambda_param))
        
        # Calculate output statistics
        output_mean = np.sum(w_m * output_points)
        output_variance = np.sum(w_c * (output_points - output_mean) ** 2)
        
        output_distribution = UncertaintyDistribution(
            distribution_type='normal',
            parameters={'loc': output_mean, 'scale': np.sqrt(output_variance)},
            uncertainty_type=UncertaintyType.MODEL,
            mean=output_mean,
            variance=output_variance
        )
        
        return output_distribution
    
    def _polynomial_chaos_propagation(
        self,
        input_distributions: List[UncertaintyDistribution],
        computation_function: Callable,
        num_samples: int
    ) -> UncertaintyDistribution:
        """Polynomial chaos expansion for uncertainty propagation."""
        
        # Simplified polynomial chaos (quadratic approximation)
        n_dims = len(input_distributions)
        
        # Generate collocation points (using tensor grid)
        collocation_points = []
        
        # Use fewer points for efficiency
        points_per_dim = max(3, min(5, int(num_samples ** (1.0 / n_dims))))
        
        if n_dims == 1:
            # 1D case
            dist = input_distributions[0]
            for i in range(points_per_dim):
                t = i / (points_per_dim - 1) if points_per_dim > 1 else 0.5
                # Use inverse CDF sampling
                if dist.distribution_type == 'normal':
                    from scipy.stats import norm
                    if HAS_SCIPY:
                        point = norm.ppf(0.1 + 0.8 * t, loc=dist.mean, scale=np.sqrt(dist.variance))
                    else:
                        # Approximate inverse normal
                        z = -2 + 4 * t  # Map to approximate normal range
                        point = dist.mean + z * np.sqrt(dist.variance)
                else:
                    # Linear interpolation between bounds
                    low = dist.mean - 2 * np.sqrt(dist.variance)
                    high = dist.mean + 2 * np.sqrt(dist.variance)
                    point = low + t * (high - low)
                
                collocation_points.append([point])
        
        else:
            # Multi-dimensional case (simplified grid)
            for i in range(min(num_samples, 50)):  # Limit for efficiency
                point = []
                for dist in input_distributions:
                    # Random sampling for higher dimensions
                    sample = dist.sample(1)[0]
                    point.append(sample)
                collocation_points.append(point)
        
        # Evaluate function at collocation points
        output_values = []
        for point in collocation_points:
            try:
                output = computation_function(np.array(point))
                if isinstance(output, (int, float)):
                    output_values.append(output)
                else:
                    output_values.append(np.mean(output) if hasattr(output, '__len__') else 0.0)
            except Exception as e:
                logger.warning(f"Error in polynomial chaos evaluation: {e}")
                output_values.append(0.0)
        
        output_values = np.array(output_values)
        
        # Fit polynomial approximation (simplified to mean and variance)
        output_mean = np.mean(output_values)
        output_variance = np.var(output_values)
        
        output_distribution = UncertaintyDistribution(
            distribution_type='normal',
            parameters={'loc': output_mean, 'scale': np.sqrt(output_variance)},
            uncertainty_type=UncertaintyType.MODEL,
            mean=output_mean,
            variance=output_variance
        )
        
        return output_distribution


class EvolutionaryUncertaintyQuantifier:
    """
    Main uncertainty quantification coordinator.
    
    Patent Feature: Comprehensive uncertainty quantification
    for evolutionary systems with adaptive method selection.
    """
    
    def __init__(self):
        """Initialize evolutionary uncertainty quantifier."""
        
        # Components
        self.bayesian_network = None
        self.mc_dropout = None
        self.uncertainty_propagator = UncertaintyPropagator()
        
        # Uncertainty tracking
        self.uncertainty_history: Dict[str, List[float]] = defaultdict(list)
        self.quantification_log: List[Dict[str, Any]] = []
        
        # Method performance
        self.method_performance = defaultdict(list)
        
        logger.info("Evolutionary uncertainty quantifier initialized")
    
    def initialize_networks(
        self,
        input_dim: int,
        hidden_dims: List[int] = None,
        output_dim: int = 1
    ):
        """Initialize neural networks for uncertainty estimation."""
        
        if hidden_dims is None:
            hidden_dims = [64, 32]
        
        # Initialize Bayesian neural network
        self.bayesian_network = BayesianNeuralNetwork(
            input_dim=input_dim,
            hidden_dims=hidden_dims,
            output_dim=output_dim
        )
        
        # Initialize Monte Carlo dropout
        architecture = [input_dim] + hidden_dims + [output_dim]
        self.mc_dropout = MonteCarloDropout(
            network_architecture=architecture,
            dropout_rate=0.3
        )
        
        logger.info("Neural networks initialized for uncertainty quantification")
    
    def quantify_parameter_uncertainty(
        self,
        parameters: Dict[str, float],
        parameter_bounds: Dict[str, Tuple[float, float]],
        prior_knowledge: Optional[Dict[str, Any]] = None
    ) -> Dict[str, UncertaintyDistribution]:
        """
        Quantify uncertainty in evolutionary parameters.
        
        Args:
            parameters: Parameter values
            parameter_bounds: Parameter bounds
            prior_knowledge: Prior knowledge about parameters
            
        Returns:
            Parameter uncertainty distributions
        """
        
        parameter_uncertainties = {}
        
        for param_name, param_value in parameters.items():
            # Get parameter bounds
            if param_name in parameter_bounds:
                lower_bound, upper_bound = parameter_bounds[param_name]
            else:
                # Default bounds
                lower_bound = param_value * 0.1
                upper_bound = param_value * 10.0
            
            # Determine appropriate distribution
            if param_name.startswith('fitness') or param_name.startswith('probability'):
                # Use beta distribution for bounded [0,1] parameters
                mean_normalized = (param_value - lower_bound) / (upper_bound - lower_bound)
                mean_normalized = np.clip(mean_normalized, 0.01, 0.99)
                
                # Estimate beta parameters from mean and variance
                assumed_variance = 0.01  # Conservative assumption
                if assumed_variance > 0:
                    alpha = mean_normalized * (mean_normalized * (1 - mean_normalized) / assumed_variance - 1)
                    beta_param = (1 - mean_normalized) * (mean_normalized * (1 - mean_normalized) / assumed_variance - 1)
                    parameters_dict = {'alpha': max(alpha, 0.1), 'beta': max(beta_param, 0.1)}
                else:
                    parameters_dict = {'alpha': 1.0, 'beta': 1.0}
                
                distribution = UncertaintyDistribution(
                    distribution_type='beta',
                    parameters=parameters_dict,
                    uncertainty_type=UncertaintyType.PARAMETER,
                    mean=mean_normalized,
                    variance=assumed_variance
                )
            
            elif param_value > 0:
                # Use gamma distribution for positive parameters
                shape = 4.0  # Moderate shape
                scale = param_value / shape
                
                distribution = UncertaintyDistribution(
                    distribution_type='gamma',
                    parameters={'shape': shape, 'scale': scale},
                    uncertainty_type=UncertaintyType.PARAMETER,
                    mean=param_value,
                    variance=param_value * scale
                )
            
            else:
                # Use normal distribution for general parameters
                std = (upper_bound - lower_bound) / 6.0  # 3-sigma rule
                
                distribution = UncertaintyDistribution(
                    distribution_type='normal',
                    parameters={'loc': param_value, 'scale': std},
                    uncertainty_type=UncertaintyType.PARAMETER,
                    mean=param_value,
                    variance=std ** 2
                )
            
            parameter_uncertainties[param_name] = distribution
        
        return parameter_uncertainties
    
    def quantify_model_uncertainty(
        self,
        training_data: Tuple[np.ndarray, np.ndarray],
        architecture: Optional[List[int]] = None,
        method: str = 'bayesian'
    ) -> Dict[str, Any]:
        """
        Quantify model uncertainty using neural networks.
        
        Args:
            training_data: (X, y) training data
            architecture: Network architecture
            method: Uncertainty quantification method ('bayesian' or 'dropout')
            
        Returns:
            Model uncertainty results
        """
        
        x_train, y_train = training_data
        
        # Initialize networks if needed
        if self.bayesian_network is None or self.mc_dropout is None:
            input_dim = x_train.shape[1] if len(x_train.shape) > 1 else 1
            output_dim = y_train.shape[1] if len(y_train.shape) > 1 else 1
            
            if architecture is None:
                architecture = [64, 32]
            
            self.initialize_networks(input_dim, architecture, output_dim)
        
        start_time = time.time()
        
        if method == 'bayesian' and self.bayesian_network:
            # Train Bayesian network
            self.bayesian_network.train_variational(x_train, y_train)
            
            # Get uncertainty estimates
            predictions, uncertainties = self.bayesian_network.forward_with_uncertainty(x_train)
            
            method_results = {
                'predictions': predictions,
                'uncertainties': uncertainties,
                'parameter_uncertainty': self.bayesian_network.get_parameter_uncertainty(),
                'method': 'bayesian_neural_network'
            }
        
        elif method == 'dropout' and self.mc_dropout:
            # Train with dropout
            training_results = self.mc_dropout.train_with_uncertainty(x_train, y_train)
            
            # Get uncertainty estimates
            predictions, uncertainties = self.mc_dropout.predict_with_uncertainty(x_train)
            
            method_results = {
                'predictions': predictions,
                'uncertainties': uncertainties,
                'training_history': training_results,
                'method': 'monte_carlo_dropout'
            }
        
        else:
            logger.error(f"Unknown method '{method}' or networks not initialized")
            return {'error': f'Method {method} not available'}
        
        quantification_time = time.time() - start_time
        
        # Record performance
        self.method_performance[method].append(quantification_time)
        
        # Log quantification
        log_entry = {
            'method': method,
            'quantification_time': quantification_time,
            'mean_uncertainty': np.mean(uncertainties) if uncertainties is not None else 0.0,
            'timestamp': time.time()
        }
        
        self.quantification_log.append(log_entry)
        
        method_results['quantification_time'] = quantification_time
        method_results['timestamp'] = time.time()
        
        return method_results
    
    def analyze_uncertainty_sources(
        self,
        total_uncertainty: float,
        component_uncertainties: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Analyze and decompose uncertainty sources.
        
        Args:
            total_uncertainty: Total system uncertainty
            component_uncertainties: Uncertainties from different components
            
        Returns:
            Uncertainty source analysis
        """
        
        uncertainty_breakdown = {}
        
        # Calculate contribution percentages
        total_component_uncertainty = sum(component_uncertainties.values())
        
        if total_component_uncertainty > 0:
            for component, uncertainty in component_uncertainties.items():
                contribution = uncertainty / total_component_uncertainty
                uncertainty_breakdown[component] = {
                    'absolute_uncertainty': uncertainty,
                    'relative_contribution': contribution,
                    'percentage': contribution * 100
                }
        
        # Identify dominant uncertainty sources
        if uncertainty_breakdown:
            dominant_source = max(
                uncertainty_breakdown.items(),
                key=lambda x: x[1]['relative_contribution']
            )
            
            secondary_sources = sorted(
                uncertainty_breakdown.items(),
                key=lambda x: x[1]['relative_contribution'],
                reverse=True
            )[1:3]  # Top 2 secondary sources
        else:
            dominant_source = ('unknown', {'relative_contribution': 1.0})
            secondary_sources = []
        
        # Uncertainty reduction recommendations
        recommendations = self._generate_uncertainty_reduction_recommendations(
            uncertainty_breakdown,
            dominant_source[0]
        )
        
        return {
            'total_uncertainty': total_uncertainty,
            'uncertainty_breakdown': uncertainty_breakdown,
            'dominant_source': {
                'name': dominant_source[0],
                'contribution': dominant_source[1]['relative_contribution']
            },
            'secondary_sources': [
                {'name': name, 'contribution': info['relative_contribution']}
                for name, info in secondary_sources
            ],
            'recommendations': recommendations,
            'analysis_timestamp': time.time()
        }
    
    def _generate_uncertainty_reduction_recommendations(
        self,
        uncertainty_breakdown: Dict[str, Dict[str, float]],
        dominant_source: str
    ) -> List[str]:
        """Generate recommendations for reducing uncertainty."""
        
        recommendations = []
        
        if 'parameter' in dominant_source.lower():
            recommendations.append("Improve parameter estimation through additional experimental data")
            recommendations.append("Use more informative priors based on biological knowledge")
            recommendations.append("Perform sensitivity analysis to identify critical parameters")
        
        elif 'model' in dominant_source.lower():
            recommendations.append("Increase model complexity or use ensemble methods")
            recommendations.append("Collect more diverse training data")
            recommendations.append("Apply regularization techniques to reduce overfitting")
        
        elif 'measurement' in dominant_source.lower():
            recommendations.append("Improve measurement protocols and instrumentation")
            recommendations.append("Increase sample sizes and replication")
            recommendations.append("Use multiple measurement techniques for cross-validation")
        
        elif 'temporal' in dominant_source.lower():
            recommendations.append("Increase temporal resolution of measurements")
            recommendations.append("Use time-series modeling techniques")
            recommendations.append("Account for temporal correlations in the model")
        
        else:
            recommendations.append("Perform systematic uncertainty analysis")
            recommendations.append("Validate model assumptions with experimental data")
            recommendations.append("Use cross-validation to assess model reliability")
        
        return recommendations
    
    def get_uncertainty_summary(self) -> Dict[str, Any]:
        """Get summary of uncertainty quantification operations."""
        
        if not self.quantification_log:
            return {'message': 'No uncertainty quantification performed yet'}
        
        # Performance statistics
        total_operations = len(self.quantification_log)
        avg_quantification_time = np.mean([
            entry['quantification_time'] for entry in self.quantification_log
        ])
        
        avg_uncertainty = np.mean([
            entry['mean_uncertainty'] for entry in self.quantification_log
        ])
        
        # Method usage
        method_counts = defaultdict(int)
        for entry in self.quantification_log:
            method_counts[entry['method']] += 1
        
        return {
            'total_operations': total_operations,
            'average_quantification_time': avg_quantification_time,
            'average_uncertainty': avg_uncertainty,
            'method_usage': dict(method_counts),
            'networks_initialized': {
                'bayesian_network': self.bayesian_network is not None,
                'mc_dropout': self.mc_dropout is not None
            }
        }
