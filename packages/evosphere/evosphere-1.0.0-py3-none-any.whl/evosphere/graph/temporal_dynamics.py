"""
Temporal Graph Dynamics Engine

Implements temporal evolution and dynamics for MRAEG graph networks.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from dataclasses import dataclass, field
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class TemporalState:
    """Represents temporal state of graph evolution."""
    
    timestamp: datetime
    node_states: torch.Tensor
    edge_weights: torch.Tensor
    fitness_score: float
    generation: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TemporalConfig:
    """Configuration for temporal graph dynamics."""
    
    time_window: int = 100
    decay_rate: float = 0.95
    adaptation_rate: float = 0.01
    memory_capacity: int = 1000
    prediction_horizon: int = 10

class TemporalGraphEngine(nn.Module):
    """
    Temporal Graph Dynamics Engine for evolutionary processes.
    
    Patent Feature: Time-aware graph evolution with temporal
    pattern recognition and predictive dynamics modeling.
    """
    
    def __init__(
        self,
        node_dim: int,
        edge_dim: int = 32,
        hidden_dim: int = 128,
        num_temporal_layers: int = 3,
        config: Optional[TemporalConfig] = None
    ):
        super().__init__()
        
        self.node_dim = node_dim
        self.edge_dim = edge_dim
        self.hidden_dim = hidden_dim
        self.num_temporal_layers = num_temporal_layers
        self.config = config or TemporalConfig()
        
        # Temporal memory for storing graph states
        self.temporal_memory: List[TemporalState] = []
        self.current_generation = 0
        
        # Temporal encoding layers
        self.temporal_encoder = nn.ModuleList([
            nn.LSTM(node_dim, hidden_dim, batch_first=True)
            for _ in range(num_temporal_layers)
        ])
        
        # Graph state prediction layers
        self.state_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, node_dim)
        )
        
        # Edge evolution predictor
        self.edge_predictor = nn.Sequential(
            nn.Linear(hidden_dim + edge_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, edge_dim)
        )
        
        # Fitness trend predictor
        self.fitness_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
        
        # Adaptation mechanism
        self.adaptation_weights = nn.Parameter(torch.ones(num_temporal_layers))
    
    def add_temporal_state(
        self,
        node_states: torch.Tensor,
        edge_weights: torch.Tensor,
        fitness_score: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add new temporal state to memory."""
        
        state = TemporalState(
            timestamp=datetime.now(),
            node_states=node_states.clone().detach(),
            edge_weights=edge_weights.clone().detach(),
            fitness_score=fitness_score,
            generation=self.current_generation,
            metadata=metadata or {}
        )
        
        self.temporal_memory.append(state)
        self.current_generation += 1
        
        # Maintain memory capacity
        if len(self.temporal_memory) > self.config.memory_capacity:
            self.temporal_memory.pop(0)
    
    def get_temporal_sequence(
        self,
        sequence_length: Optional[int] = None
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Get temporal sequence for training/prediction."""
        
        if not self.temporal_memory:
            return None, None, None
        
        seq_len = sequence_length or min(self.config.time_window, len(self.temporal_memory))
        
        if len(self.temporal_memory) < seq_len:
            seq_len = len(self.temporal_memory)
        
        recent_states = self.temporal_memory[-seq_len:]
        
        # Extract sequences
        node_sequence = torch.stack([state.node_states for state in recent_states])
        edge_sequence = torch.stack([state.edge_weights for state in recent_states])
        fitness_sequence = torch.tensor([state.fitness_score for state in recent_states])
        
        return node_sequence, edge_sequence, fitness_sequence
    
    def predict_next_state(
        self,
        current_nodes: torch.Tensor,
        current_edges: torch.Tensor,
        steps_ahead: int = 1
    ) -> Tuple[torch.Tensor, torch.Tensor, float]:
        """
        Predict future graph state using temporal patterns.
        
        Args:
            current_nodes: Current node states [num_nodes, node_dim]
            current_edges: Current edge weights [num_edges, edge_dim]
            steps_ahead: Number of time steps to predict
            
        Returns:
            Predicted node states, edge weights, and fitness score
        """
        
        # Get temporal context
        node_seq, edge_seq, fitness_seq = self.get_temporal_sequence()
        
        if node_seq is None:
            # No temporal history - return current state
            return current_nodes, current_edges, 0.5
        
        # Prepare input for temporal prediction
        batch_size = 1
        seq_len = node_seq.size(0)
        
        # Encode temporal patterns
        temporal_features = []
        for layer_idx, lstm in enumerate(self.temporal_encoder):
            lstm_input = node_seq.unsqueeze(0)  # [1, seq_len, node_dim]
            lstm_output, (hidden, cell) = lstm(lstm_input)
            
            # Use final hidden state as temporal feature
            temporal_features.append(hidden[-1])  # [1, hidden_dim]
        
        # Aggregate temporal features
        if len(temporal_features) > 1:
            temporal_repr = torch.cat(temporal_features, dim=-1)
            temporal_repr = F.linear(
                temporal_repr, 
                torch.ones(temporal_repr.size(-1), self.hidden_dim) / len(temporal_features)
            )
        else:
            temporal_repr = temporal_features[0]
        
        # Multi-step prediction
        predicted_nodes = current_nodes
        predicted_edges = current_edges
        predicted_fitness = 0.5
        
        for step in range(steps_ahead):
            # Predict node state changes
            node_delta = self.state_predictor(temporal_repr.squeeze(0))
            predicted_nodes = predicted_nodes + node_delta * self.config.adaptation_rate
            
            # Predict edge weight changes
            edge_temporal_input = torch.cat([
                temporal_repr.squeeze(0).mean(dim=0, keepdim=True).expand(predicted_edges.size(0), -1),
                predicted_edges
            ], dim=-1)
            edge_delta = self.edge_predictor(edge_temporal_input)
            predicted_edges = predicted_edges + edge_delta * self.config.adaptation_rate
            
            # Predict fitness trend
            fitness_input = temporal_repr.mean(dim=-1, keepdim=True)
            fitness_delta = self.fitness_predictor(temporal_repr.squeeze(0))
            predicted_fitness = float(fitness_delta.item())
        
        return predicted_nodes, predicted_edges, predicted_fitness
    
    def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in graph evolution."""
        
        if len(self.temporal_memory) < 2:
            return {'status': 'insufficient_data'}
        
        # Extract time series data
        timestamps = [state.timestamp for state in self.temporal_memory]
        fitness_scores = [state.fitness_score for state in self.temporal_memory]
        generations = [state.generation for state in self.temporal_memory]
        
        # Calculate temporal statistics
        time_deltas = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                      for i in range(1, len(timestamps))]
        
        fitness_trend = np.polyfit(generations, fitness_scores, 1)[0] if len(fitness_scores) > 1 else 0
        fitness_variance = np.var(fitness_scores) if len(fitness_scores) > 1 else 0
        avg_time_step = np.mean(time_deltas) if time_deltas else 0
        
        # Analyze convergence
        recent_window = min(10, len(fitness_scores))
        recent_scores = fitness_scores[-recent_window:]
        convergence_rate = np.std(recent_scores) if len(recent_scores) > 1 else 1.0
        
        return {
            'total_generations': len(self.temporal_memory),
            'current_generation': self.current_generation,
            'fitness_trend': fitness_trend,
            'fitness_variance': fitness_variance,
            'avg_time_per_generation': avg_time_step,
            'convergence_rate': convergence_rate,
            'is_converging': convergence_rate < 0.01,
            'memory_usage': len(self.temporal_memory) / self.config.memory_capacity
        }
    
    def reset_temporal_memory(self):
        """Reset temporal memory and generation counter."""
        
        self.temporal_memory.clear()
        self.current_generation = 0
        logger.info("Temporal memory reset")
    
    def export_temporal_data(self) -> Dict[str, Any]:
        """Export temporal data for analysis."""
        
        return {
            'config': {
                'time_window': self.config.time_window,
                'decay_rate': self.config.decay_rate,
                'adaptation_rate': self.config.adaptation_rate,
                'memory_capacity': self.config.memory_capacity
            },
            'states': [
                {
                    'timestamp': state.timestamp.isoformat(),
                    'generation': state.generation,
                    'fitness_score': state.fitness_score,
                    'node_dim': state.node_states.shape,
                    'edge_dim': state.edge_weights.shape,
                    'metadata': state.metadata
                }
                for state in self.temporal_memory
            ],
            'statistics': self.analyze_temporal_patterns()
        }

class TemporalPatternDetector(nn.Module):
    """
    Detects recurring patterns in temporal graph evolution.
    
    Patent Feature: Pattern recognition in evolutionary dynamics
    with cycle detection and trend analysis.
    """
    
    def __init__(
        self,
        pattern_length: int = 10,
        min_pattern_strength: float = 0.7
    ):
        super().__init__()
        
        self.pattern_length = pattern_length
        self.min_pattern_strength = min_pattern_strength
        
        # Pattern detection network
        self.pattern_encoder = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(pattern_length),
            nn.Flatten(),
            nn.Linear(64 * pattern_length, 128),
            nn.ReLU(),
            nn.Linear(128, pattern_length)
        )
    
    def detect_patterns(self, fitness_sequence: torch.Tensor) -> Dict[str, Any]:
        """Detect patterns in fitness evolution."""
        
        if len(fitness_sequence) < self.pattern_length:
            return {'patterns': [], 'confidence': 0.0}
        
        # Normalize sequence
        normalized_seq = (fitness_sequence - fitness_sequence.mean()) / (fitness_sequence.std() + 1e-8)
        
        # Detect patterns using sliding window
        patterns = []
        
        for i in range(len(normalized_seq) - self.pattern_length + 1):
            window = normalized_seq[i:i + self.pattern_length]
            
            # Encode pattern
            pattern_encoding = self.pattern_encoder(window.unsqueeze(0).unsqueeze(0))
            pattern_strength = torch.sigmoid(pattern_encoding.mean()).item()
            
            if pattern_strength > self.min_pattern_strength:
                patterns.append({
                    'start_index': i,
                    'length': self.pattern_length,
                    'strength': pattern_strength,
                    'pattern_type': self._classify_pattern(window)
                })
        
        return {
            'patterns': patterns,
            'confidence': np.mean([p['strength'] for p in patterns]) if patterns else 0.0,
            'num_patterns': len(patterns)
        }
    
    def _classify_pattern(self, pattern: torch.Tensor) -> str:
        """Classify the type of temporal pattern."""
        
        # Calculate pattern characteristics
        trend = torch.polyfit(torch.arange(len(pattern), dtype=torch.float), pattern, 1)[0]
        variance = torch.var(pattern)
        
        if abs(trend) < 0.01 and variance < 0.01:
            return "stable"
        elif trend > 0.05:
            return "increasing"
        elif trend < -0.05:
            return "decreasing"
        elif variance > 0.1:
            return "oscillating"
        else:
            return "complex"

class GraphEvolutionTracker:
    """
    Tracks evolutionary changes in graph structure over time.
    
    Patent Feature: Real-time monitoring of graph topology
    evolution with automated adaptation detection.
    """
    
    def __init__(self, tracking_window: int = 50):
        self.tracking_window = tracking_window
        self.evolution_history = []
        self.topology_changes = []
        
    def track_evolution(
        self,
        graph_state: Dict[str, torch.Tensor],
        generation: int
    ):
        """Track graph evolution at current generation."""
        
        evolution_record = {
            'generation': generation,
            'timestamp': datetime.now(),
            'num_nodes': graph_state.get('nodes', torch.tensor([])).size(0),
            'num_edges': graph_state.get('edges', torch.tensor([])).size(0) if graph_state.get('edges', torch.tensor([])).dim() > 1 else 0,
            'avg_node_degree': self._calculate_avg_degree(graph_state),
            'clustering_coefficient': self._calculate_clustering(graph_state),
            'graph_density': self._calculate_density(graph_state)
        }
        
        self.evolution_history.append(evolution_record)
        
        # Maintain window size
        if len(self.evolution_history) > self.tracking_window:
            self.evolution_history.pop(0)
        
        # Detect topology changes
        if len(self.evolution_history) > 1:
            self._detect_topology_changes()
    
    def _calculate_avg_degree(self, graph_state: Dict[str, torch.Tensor]) -> float:
        """Calculate average node degree."""
        
        edges = graph_state.get('edges', torch.tensor([]))
        nodes = graph_state.get('nodes', torch.tensor([]))
        
        if edges.numel() == 0 or nodes.numel() == 0:
            return 0.0
        
        if edges.dim() == 2 and edges.size(0) >= 2:
            num_edges = edges.size(1)
            num_nodes = nodes.size(0)
            return (2 * num_edges) / max(num_nodes, 1)
        
        return 0.0
    
    def _calculate_clustering(self, graph_state: Dict[str, torch.Tensor]) -> float:
        """Calculate clustering coefficient."""
        
        # Simplified clustering calculation
        edges = graph_state.get('edges', torch.tensor([]))
        
        if edges.numel() == 0:
            return 0.0
        
        # Approximate clustering based on edge density
        if edges.dim() == 2 and edges.size(1) > 0:
            edge_density = self._calculate_density(graph_state)
            return min(edge_density * 2, 1.0)  # Rough approximation
        
        return 0.0
    
    def _calculate_density(self, graph_state: Dict[str, torch.Tensor]) -> float:
        """Calculate graph density."""
        
        edges = graph_state.get('edges', torch.tensor([]))
        nodes = graph_state.get('nodes', torch.tensor([]))
        
        if edges.numel() == 0 or nodes.numel() == 0:
            return 0.0
        
        num_nodes = nodes.size(0)
        if num_nodes < 2:
            return 0.0
        
        max_edges = num_nodes * (num_nodes - 1) / 2
        actual_edges = edges.size(1) if edges.dim() == 2 else 0
        
        return actual_edges / max_edges if max_edges > 0 else 0.0
    
    def _detect_topology_changes(self):
        """Detect significant topology changes."""
        
        if len(self.evolution_history) < 2:
            return
        
        current = self.evolution_history[-1]
        previous = self.evolution_history[-2]
        
        # Calculate change metrics
        node_change = abs(current['num_nodes'] - previous['num_nodes'])
        edge_change = abs(current['num_edges'] - previous['num_edges'])
        density_change = abs(current['graph_density'] - previous['graph_density'])
        
        # Detect significant changes
        if node_change > 0 or edge_change > 2 or density_change > 0.1:
            change_record = {
                'generation': current['generation'],
                'timestamp': current['timestamp'],
                'change_type': self._classify_change(node_change, edge_change, density_change),
                'magnitude': max(node_change, edge_change, density_change * 10),
                'details': {
                    'node_change': node_change,
                    'edge_change': edge_change,
                    'density_change': density_change
                }
            }
            
            self.topology_changes.append(change_record)
    
    def _classify_change(
        self, 
        node_change: float, 
        edge_change: float, 
        density_change: float
    ) -> str:
        """Classify the type of topology change."""
        
        if node_change > 0:
            return "structural_growth" if node_change > 0 else "structural_pruning"
        elif edge_change > 2:
            return "connectivity_change"
        elif density_change > 0.1:
            return "density_shift"
        else:
            return "minor_adaptation"
    
    def get_evolution_summary(self) -> Dict[str, Any]:
        """Get summary of graph evolution."""
        
        if not self.evolution_history:
            return {'status': 'no_data'}
        
        # Calculate trends
        generations = [record['generation'] for record in self.evolution_history]
        densities = [record['graph_density'] for record in self.evolution_history]
        clustering = [record['clustering_coefficient'] for record in self.evolution_history]
        
        return {
            'total_generations_tracked': len(self.evolution_history),
            'topology_changes': len(self.topology_changes),
            'current_density': densities[-1] if densities else 0.0,
            'density_trend': np.polyfit(generations, densities, 1)[0] if len(densities) > 1 else 0,
            'avg_clustering': np.mean(clustering) if clustering else 0.0,
            'evolution_stability': 1.0 - (len(self.topology_changes) / max(len(self.evolution_history), 1)),
            'recent_changes': self.topology_changes[-5:] if self.topology_changes else []
        }
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for PyTorch compatibility."""
        return x  # Pass-through for tracking functionality
