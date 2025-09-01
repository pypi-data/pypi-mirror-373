"""
Multi-Modal Data Fusion Engine

Patent-pending system for fusing diverse biological data sources
with intelligent conflict resolution and temporal alignment.
"""

from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np
import logging
from abc import ABC, abstractmethod
from collections import defaultdict, OrderedDict
import time
import json

try:
    from scipy.optimize import minimize
    from scipy.stats import entropy
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    
    # Fallback optimization
    def minimize(func, x0, method='BFGS', **kwargs):
        """Simple gradient descent fallback."""
        x = np.array(x0)
        for _ in range(100):
            grad = np.array([
                (func(x + 1e-6 * np.eye(len(x))[i]) - func(x)) / 1e-6
                for i in range(len(x))
            ])
            x -= 0.01 * grad
        return type('Result', (), {'x': x, 'success': True})()

logger = logging.getLogger(__name__)


class FusionStrategy(Enum):
    """Data fusion strategies for multi-modal integration."""
    
    WEIGHTED_AVERAGE = auto()
    BAYESIAN_FUSION = auto()
    INFORMATION_THEORETIC = auto()
    CONFIDENCE_BASED = auto()
    TEMPORAL_PRIORITY = auto()
    CONSENSUS_VOTING = auto()
    ADAPTIVE_ENSEMBLE = auto()


class DataModality(Enum):
    """Different modalities of biological data."""
    
    SEQUENCE_DATA = auto()      # DNA, RNA, protein sequences
    EXPRESSION_DATA = auto()    # Gene/protein expression levels
    STRUCTURAL_DATA = auto()    # 3D structures, conformations
    INTERACTION_DATA = auto()   # Protein-protein, gene networks
    PHENOTYPE_DATA = auto()     # Observable traits, fitness
    ENVIRONMENTAL_DATA = auto() # External conditions
    TEMPORAL_DATA = auto()      # Time series measurements
    SPATIAL_DATA = auto()       # Spatial distributions


@dataclass
class DataSource:
    """
    Represents a single data source for fusion.
    
    Patent Feature: Standardized data source representation
    with quality metrics and fusion compatibility.
    """
    
    source_id: str
    modality: DataModality
    data_type: str
    
    # Data content
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Quality metrics
    reliability: float = 1.0
    completeness: float = 1.0
    temporal_resolution: float = 1.0
    spatial_resolution: float = 1.0
    
    # Temporal information
    timestamp: float = field(default_factory=time.time)
    time_range: Optional[Tuple[float, float]] = None
    
    # Fusion parameters
    fusion_weight: float = 1.0
    conflict_penalty: float = 0.0
    
    def __post_init__(self):
        """Validate data source after creation."""
        
        # Ensure metadata includes required fields
        if 'source_type' not in self.metadata:
            self.metadata['source_type'] = self.modality.name
        
        if 'creation_time' not in self.metadata:
            self.metadata['creation_time'] = self.timestamp
    
    def calculate_quality_score(self) -> float:
        """Calculate overall quality score for this data source."""
        
        quality_components = [
            self.reliability,
            self.completeness,
            self.temporal_resolution,
            self.spatial_resolution
        ]
        
        # Geometric mean for balanced quality assessment
        quality_score = np.power(np.prod(quality_components), 1.0 / len(quality_components))
        
        # Apply conflict penalty
        final_score = quality_score * (1.0 - self.conflict_penalty)
        
        return np.clip(final_score, 0.0, 1.0)
    
    def is_compatible(self, other: 'DataSource') -> bool:
        """Check if this data source is compatible with another."""
        
        # Temporal compatibility
        temporal_compatible = True
        if self.time_range and other.time_range:
            # Check for temporal overlap
            start1, end1 = self.time_range
            start2, end2 = other.time_range
            temporal_compatible = not (end1 < start2 or end2 < start1)
        
        # Modality compatibility (some combinations work better)
        compatible_modalities = {
            DataModality.SEQUENCE_DATA: {
                DataModality.EXPRESSION_DATA, 
                DataModality.STRUCTURAL_DATA,
                DataModality.PHENOTYPE_DATA
            },
            DataModality.EXPRESSION_DATA: {
                DataModality.SEQUENCE_DATA,
                DataModality.PHENOTYPE_DATA,
                DataModality.ENVIRONMENTAL_DATA
            },
            DataModality.PHENOTYPE_DATA: {
                DataModality.SEQUENCE_DATA,
                DataModality.EXPRESSION_DATA,
                DataModality.ENVIRONMENTAL_DATA,
                DataModality.TEMPORAL_DATA
            }
        }
        
        modality_compatible = (
            self.modality == other.modality or
            other.modality in compatible_modalities.get(self.modality, set()) or
            self.modality in compatible_modalities.get(other.modality, set())
        )
        
        return temporal_compatible and modality_compatible


class FusionConflictResolver:
    """
    Resolves conflicts between different data sources.
    
    Patent Feature: Intelligent conflict resolution using
    biological knowledge and trust metrics.
    """
    
    def __init__(self):
        """Initialize conflict resolver."""
        
        self.conflict_history: List[Dict[str, Any]] = []
        self.resolution_strategies = {
            'trust_based': self._resolve_by_trust,
            'temporal_priority': self._resolve_by_time,
            'quality_weighted': self._resolve_by_quality,
            'biological_consistency': self._resolve_by_biology,
            'ensemble_voting': self._resolve_by_voting
        }
        
        # Biological knowledge base
        self.biological_constraints = {
            'protein_expression_bounds': (0.0, 1000.0),
            'gene_expression_correlation': 0.8,
            'fitness_monotonicity': True,
            'population_growth_limits': (1, 1e6)
        }
    
    def detect_conflicts(
        self, 
        data_sources: List[DataSource],
        fusion_key: str
    ) -> List[Dict[str, Any]]:
        """
        Detect conflicts between data sources for a specific key.
        
        Args:
            data_sources: List of data sources to check
            fusion_key: Key to check for conflicts
            
        Returns:
            List of detected conflicts
        """
        
        conflicts = []
        
        # Get values for the key from all sources
        source_values = []
        for source in data_sources:
            if fusion_key in source.data:
                source_values.append({
                    'source_id': source.source_id,
                    'value': source.data[fusion_key],
                    'quality': source.calculate_quality_score(),
                    'timestamp': source.timestamp,
                    'modality': source.modality
                })
        
        if len(source_values) < 2:
            return conflicts  # No conflict possible
        
        # Statistical conflict detection
        values = [sv['value'] for sv in source_values if isinstance(sv['value'], (int, float))]
        
        if len(values) >= 2:
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            # Detect outliers (values > 2 standard deviations from mean)
            for sv in source_values:
                if isinstance(sv['value'], (int, float)):
                    if abs(sv['value'] - mean_val) > 2 * std_val:
                        conflicts.append({
                            'type': 'statistical_outlier',
                            'source_id': sv['source_id'],
                            'value': sv['value'],
                            'expected_range': (mean_val - 2*std_val, mean_val + 2*std_val),
                            'severity': abs(sv['value'] - mean_val) / (std_val + 1e-12)
                        })
        
        # Biological constraint conflicts
        biological_conflicts = self._check_biological_constraints(source_values, fusion_key)
        conflicts.extend(biological_conflicts)
        
        # Temporal consistency conflicts
        temporal_conflicts = self._check_temporal_consistency(source_values)
        conflicts.extend(temporal_conflicts)
        
        return conflicts
    
    def resolve_conflicts(
        self,
        data_sources: List[DataSource],
        conflicts: List[Dict[str, Any]],
        strategy: str = 'quality_weighted'
    ) -> Dict[str, Any]:
        """
        Resolve detected conflicts using specified strategy.
        
        Args:
            data_sources: Conflicting data sources
            conflicts: List of detected conflicts
            strategy: Resolution strategy to use
            
        Returns:
            Resolution results
        """
        
        if strategy not in self.resolution_strategies:
            logger.warning(f"Unknown strategy '{strategy}', using quality_weighted")
            strategy = 'quality_weighted'
        
        resolver_func = self.resolution_strategies[strategy]
        resolution = resolver_func(data_sources, conflicts)
        
        # Record conflict resolution
        resolution_record = {
            'timestamp': time.time(),
            'strategy': strategy,
            'num_conflicts': len(conflicts),
            'num_sources': len(data_sources),
            'resolution': resolution
        }
        
        self.conflict_history.append(resolution_record)
        
        return resolution
    
    def _resolve_by_trust(
        self, 
        data_sources: List[DataSource], 
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Resolve conflicts based on source reliability."""
        
        # Calculate trust scores
        trust_scores = {}
        for source in data_sources:
            base_trust = source.reliability * source.calculate_quality_score()
            
            # Penalize sources involved in conflicts
            conflict_penalty = 0.0
            for conflict in conflicts:
                if conflict.get('source_id') == source.source_id:
                    conflict_penalty += conflict.get('severity', 0.1) * 0.2
            
            trust_scores[source.source_id] = max(0.1, base_trust - conflict_penalty)
        
        # Select highest trust source for each key
        resolved_data = {}
        resolution_weights = {}
        
        for source in data_sources:
            weight = trust_scores[source.source_id]
            
            for key, value in source.data.items():
                if key not in resolved_data or weight > resolution_weights[key]:
                    resolved_data[key] = value
                    resolution_weights[key] = weight
        
        return {
            'fused_data': resolved_data,
            'trust_scores': trust_scores,
            'resolution_method': 'trust_based'
        }
    
    def _resolve_by_time(
        self, 
        data_sources: List[DataSource], 
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Resolve conflicts by temporal priority (most recent wins)."""
        
        # Sort sources by timestamp (most recent first)
        sorted_sources = sorted(data_sources, key=lambda s: s.timestamp, reverse=True)
        
        resolved_data = {}
        
        # Take most recent value for each key
        for source in sorted_sources:
            for key, value in source.data.items():
                if key not in resolved_data:
                    resolved_data[key] = value
        
        return {
            'fused_data': resolved_data,
            'temporal_order': [s.source_id for s in sorted_sources],
            'resolution_method': 'temporal_priority'
        }
    
    def _resolve_by_quality(
        self, 
        data_sources: List[DataSource], 
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Resolve conflicts using quality-weighted averaging."""
        
        resolved_data = {}
        
        # Group sources by data keys
        key_sources = defaultdict(list)
        for source in data_sources:
            for key in source.data:
                key_sources[key].append(source)
        
        # Quality-weighted fusion for each key
        for key, sources in key_sources.items():
            numeric_values = []
            weights = []
            non_numeric_candidates = []
            
            for source in sources:
                value = source.data[key]
                quality = source.calculate_quality_score()
                
                if isinstance(value, (int, float)):
                    numeric_values.append(value)
                    weights.append(quality)
                else:
                    non_numeric_candidates.append((value, quality, source.source_id))
            
            if numeric_values:
                # Weighted average for numeric values
                weights = np.array(weights)
                weights /= np.sum(weights)  # Normalize
                
                fused_value = np.average(numeric_values, weights=weights)
                resolved_data[key] = fused_value
                
            elif non_numeric_candidates:
                # Select highest quality for non-numeric
                best_candidate = max(non_numeric_candidates, key=lambda x: x[1])
                resolved_data[key] = best_candidate[0]
        
        return {
            'fused_data': resolved_data,
            'resolution_method': 'quality_weighted'
        }
    
    def _resolve_by_biology(
        self, 
        data_sources: List[DataSource], 
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Resolve conflicts using biological consistency checks."""
        
        resolved_data = {}
        
        # Apply biological constraints
        for source in data_sources:
            for key, value in source.data.items():
                
                # Check biological plausibility
                is_plausible = self._check_biological_plausibility(key, value, source.modality)
                
                if is_plausible:
                    if key not in resolved_data:
                        resolved_data[key] = value
                    else:
                        # Keep more biologically plausible value
                        current_plausibility = self._get_plausibility_score(
                            key, resolved_data[key], source.modality
                        )
                        new_plausibility = self._get_plausibility_score(
                            key, value, source.modality
                        )
                        
                        if new_plausibility > current_plausibility:
                            resolved_data[key] = value
        
        return {
            'fused_data': resolved_data,
            'resolution_method': 'biological_consistency'
        }
    
    def _resolve_by_voting(
        self, 
        data_sources: List[DataSource], 
        conflicts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Resolve conflicts using ensemble voting."""
        
        resolved_data = {}
        
        # Group similar values and vote
        key_value_groups = defaultdict(lambda: defaultdict(list))
        
        for source in data_sources:
            for key, value in source.data.items():
                if isinstance(value, (int, float)):
                    # Group numeric values by proximity
                    value_group = round(value * 10) / 10  # Group to 1 decimal
                    key_value_groups[key][value_group].append((value, source))
                else:
                    # Group non-numeric values exactly
                    key_value_groups[key][str(value)].append((value, source))
        
        # Vote for each key
        for key, value_groups in key_value_groups.items():
            best_group = None
            best_vote_strength = 0
            
            for group_key, value_source_pairs in value_groups.items():
                # Calculate vote strength (weighted by quality)
                vote_strength = sum(
                    source.calculate_quality_score() 
                    for _, source in value_source_pairs
                )
                
                if vote_strength > best_vote_strength:
                    best_vote_strength = vote_strength
                    best_group = value_source_pairs
            
            if best_group:
                # Use average of winning group for numeric, first for non-numeric
                values = [value for value, _ in best_group]
                if all(isinstance(v, (int, float)) for v in values):
                    resolved_data[key] = np.mean(values)
                else:
                    resolved_data[key] = values[0]
        
        return {
            'fused_data': resolved_data,
            'resolution_method': 'ensemble_voting'
        }
    
    def _check_biological_constraints(
        self, 
        source_values: List[Dict[str, Any]], 
        key: str
    ) -> List[Dict[str, Any]]:
        """Check for violations of biological constraints."""
        
        conflicts = []
        
        for sv in source_values:
            value = sv['value']
            
            # Check against biological constraints
            if key.startswith('protein_expression') and isinstance(value, (int, float)):
                bounds = self.biological_constraints['protein_expression_bounds']
                if value < bounds[0] or value > bounds[1]:
                    conflicts.append({
                        'type': 'biological_constraint_violation',
                        'source_id': sv['source_id'],
                        'constraint': 'protein_expression_bounds',
                        'value': value,
                        'valid_range': bounds,
                        'severity': min(abs(value - bounds[0]), abs(value - bounds[1])) / (bounds[1] - bounds[0])
                    })
            
            elif key.startswith('population') and isinstance(value, (int, float)):
                bounds = self.biological_constraints['population_growth_limits']
                if value < bounds[0] or value > bounds[1]:
                    conflicts.append({
                        'type': 'biological_constraint_violation',
                        'source_id': sv['source_id'],
                        'constraint': 'population_growth_limits',
                        'value': value,
                        'valid_range': bounds,
                        'severity': 0.8  # High severity for population bounds
                    })
        
        return conflicts
    
    def _check_temporal_consistency(self, source_values: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for temporal inconsistencies."""
        
        conflicts = []
        
        # Sort by timestamp
        sorted_values = sorted(source_values, key=lambda sv: sv['timestamp'])
        
        # Check for non-monotonic trends where biology expects monotonicity
        if len(sorted_values) >= 3:
            for i in range(len(sorted_values) - 2):
                prev_val = sorted_values[i]['value']
                curr_val = sorted_values[i+1]['value']
                next_val = sorted_values[i+2]['value']
                
                if all(isinstance(v, (int, float)) for v in [prev_val, curr_val, next_val]):
                    # Check for excessive oscillation
                    if (prev_val < curr_val < next_val) or (prev_val > curr_val > next_val):
                        continue  # Monotonic, good
                    
                    if abs(curr_val - prev_val) > 0.5 * abs(next_val - curr_val):
                        conflicts.append({
                            'type': 'temporal_inconsistency',
                            'source_id': sorted_values[i+1]['source_id'],
                            'inconsistency': 'excessive_oscillation',
                            'severity': 0.6
                        })
        
        return conflicts
    
    def _check_biological_plausibility(
        self, 
        key: str, 
        value: Any, 
        modality: DataModality
    ) -> bool:
        """Check if value is biologically plausible."""
        
        if not isinstance(value, (int, float)):
            return True  # Assume non-numeric values are plausible
        
        # Key-specific checks
        if 'fitness' in key.lower():
            return 0.0 <= value <= 1.0
        
        elif 'expression' in key.lower():
            return value >= 0.0  # Expression levels must be non-negative
        
        elif 'population' in key.lower():
            return value >= 1.0  # Population must be at least 1
        
        elif 'diversity' in key.lower():
            return 0.0 <= value <= 1.0
        
        elif 'temperature' in key.lower():
            return 200.0 <= value <= 400.0  # Reasonable temperature range in Kelvin
        
        # Default: accept all values
        return True
    
    def _get_plausibility_score(
        self, 
        key: str, 
        value: Any, 
        modality: DataModality
    ) -> float:
        """Get plausibility score for a value."""
        
        if not self._check_biological_plausibility(key, value, modality):
            return 0.0
        
        # Calculate detailed plausibility score
        if isinstance(value, (int, float)):
            if 'fitness' in key.lower():
                # Fitness should be in reasonable range with preference for middle values
                if 0.0 <= value <= 1.0:
                    return 1.0 - abs(value - 0.5)  # Prefer values around 0.5
                else:
                    return 0.0
            
            elif 'diversity' in key.lower():
                # Diversity should be positive with preference for moderate levels
                if 0.0 <= value <= 1.0:
                    return min(value * 2, (1.0 - value) * 2, 1.0)
                else:
                    return 0.0
        
        return 0.8  # Default moderate plausibility


class MultiModalFusionEngine:
    """
    Main engine for multi-modal data fusion.
    
    Patent Feature: Adaptive multi-modal fusion with temporal
    alignment and intelligent conflict resolution.
    """
    
    def __init__(self, default_strategy: FusionStrategy = FusionStrategy.ADAPTIVE_ENSEMBLE):
        """
        Initialize multi-modal fusion engine.
        
        Args:
            default_strategy: Default fusion strategy
        """
        self.default_strategy = default_strategy
        
        # Components
        self.conflict_resolver = FusionConflictResolver()
        
        # Data management
        self.data_sources: Dict[str, DataSource] = {}
        self.fusion_cache: Dict[str, Dict[str, Any]] = {}
        
        # Fusion history
        self.fusion_history: List[Dict[str, Any]] = []
        
        # Strategy performance tracking
        self.strategy_performance = defaultdict(list)
        
        logger.info("Multi-modal fusion engine initialized")
    
    def register_data_source(self, data_source: DataSource):
        """Register a new data source for fusion."""
        
        self.data_sources[data_source.source_id] = data_source
        
        # Clear relevant cache entries
        self._invalidate_cache(data_source.modality)
        
        logger.info(f"Registered data source: {data_source.source_id} ({data_source.modality.name})")
    
    def fuse_data(
        self,
        source_ids: Optional[List[str]] = None,
        strategy: Optional[FusionStrategy] = None,
        temporal_window: Optional[Tuple[float, float]] = None
    ) -> Dict[str, Any]:
        """
        Fuse data from multiple sources.
        
        Args:
            source_ids: Specific sources to fuse (None for all)
            strategy: Fusion strategy to use
            temporal_window: Time window for temporal filtering
            
        Returns:
            Fused data results
        """
        
        if strategy is None:
            strategy = self.default_strategy
        
        # Select data sources
        if source_ids:
            sources = [self.data_sources[sid] for sid in source_ids if sid in self.data_sources]
        else:
            sources = list(self.data_sources.values())
        
        if not sources:
            logger.warning("No data sources available for fusion")
            return {'fused_data': {}, 'error': 'No sources available'}
        
        # Apply temporal filtering
        if temporal_window:
            sources = [
                s for s in sources 
                if temporal_window[0] <= s.timestamp <= temporal_window[1]
            ]
        
        # Filter compatible sources
        compatible_sources = self._filter_compatible_sources(sources)
        
        start_time = time.time()
        
        # Perform fusion based on strategy
        if strategy == FusionStrategy.WEIGHTED_AVERAGE:
            result = self._weighted_average_fusion(compatible_sources)
        
        elif strategy == FusionStrategy.BAYESIAN_FUSION:
            result = self._bayesian_fusion(compatible_sources)
        
        elif strategy == FusionStrategy.INFORMATION_THEORETIC:
            result = self._information_theoretic_fusion(compatible_sources)
        
        elif strategy == FusionStrategy.CONFIDENCE_BASED:
            result = self._confidence_based_fusion(compatible_sources)
        
        elif strategy == FusionStrategy.TEMPORAL_PRIORITY:
            result = self._temporal_priority_fusion(compatible_sources)
        
        elif strategy == FusionStrategy.CONSENSUS_VOTING:
            result = self._consensus_voting_fusion(compatible_sources)
        
        elif strategy == FusionStrategy.ADAPTIVE_ENSEMBLE:
            result = self._adaptive_ensemble_fusion(compatible_sources)
        
        else:
            logger.error(f"Unknown fusion strategy: {strategy}")
            result = self._weighted_average_fusion(compatible_sources)
        
        fusion_time = time.time() - start_time
        
        # Add metadata to result
        result.update({
            'fusion_strategy': strategy.name,
            'sources_used': [s.source_id for s in compatible_sources],
            'fusion_time': fusion_time,
            'timestamp': time.time()
        })
        
        # Record fusion history
        self.fusion_history.append(result)
        
        # Update strategy performance
        self.strategy_performance[strategy.name].append(fusion_time)
        
        return result
    
    def _filter_compatible_sources(self, sources: List[DataSource]) -> List[DataSource]:
        """Filter sources for compatibility."""
        
        if len(sources) <= 1:
            return sources
        
        compatible_groups = []
        
        for source in sources:
            # Find compatible group
            placed = False
            for group in compatible_groups:
                if all(source.is_compatible(other) for other in group):
                    group.append(source)
                    placed = True
                    break
            
            if not placed:
                compatible_groups.append([source])
        
        # Return largest compatible group
        if compatible_groups:
            largest_group = max(compatible_groups, key=len)
            return largest_group
        
        return sources
    
    def _weighted_average_fusion(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Perform weighted average fusion."""
        
        if not sources:
            return {'fused_data': {}}
        
        # Detect and resolve conflicts
        all_keys = set()
        for source in sources:
            all_keys.update(source.data.keys())
        
        conflicts = []
        for key in all_keys:
            key_conflicts = self.conflict_resolver.detect_conflicts(sources, key)
            conflicts.extend(key_conflicts)
        
        # Resolve conflicts if any
        if conflicts:
            resolution = self.conflict_resolver.resolve_conflicts(
                sources, conflicts, 'quality_weighted'
            )
            return resolution
        
        # No conflicts, proceed with weighted average
        fused_data = {}
        
        for key in all_keys:
            numeric_values = []
            weights = []
            non_numeric_candidates = []
            
            for source in sources:
                if key in source.data:
                    value = source.data[key]
                    weight = source.fusion_weight * source.calculate_quality_score()
                    
                    if isinstance(value, (int, float)):
                        numeric_values.append(value)
                        weights.append(weight)
                    else:
                        non_numeric_candidates.append((value, weight, source.source_id))
            
            if numeric_values:
                weights = np.array(weights)
                weights /= np.sum(weights)
                fused_data[key] = np.average(numeric_values, weights=weights)
            elif non_numeric_candidates:
                best_candidate = max(non_numeric_candidates, key=lambda x: x[1])
                fused_data[key] = best_candidate[0]
        
        return {
            'fused_data': fused_data,
            'conflicts_detected': len(conflicts),
            'sources_fused': len(sources)
        }
    
    def _bayesian_fusion(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Perform Bayesian data fusion."""
        
        fused_data = {}
        
        # Group data by keys
        key_data = defaultdict(list)
        for source in sources:
            for key, value in source.data.items():
                if isinstance(value, (int, float)):
                    key_data[key].append({
                        'value': value,
                        'uncertainty': source.metadata.get('uncertainty', 0.1),
                        'prior_weight': source.calculate_quality_score()
                    })
        
        # Bayesian fusion for each key
        for key, data_list in key_data.items():
            if len(data_list) == 1:
                fused_data[key] = data_list[0]['value']
                continue
            
            # Bayesian update
            prior_mean = np.mean([d['value'] for d in data_list])
            prior_variance = np.var([d['value'] for d in data_list]) + 1e-6
            
            posterior_precision = 1.0 / prior_variance
            posterior_mean_numerator = prior_mean / prior_variance
            
            for data_point in data_list:
                likelihood_precision = 1.0 / (data_point['uncertainty'] ** 2 + 1e-6)
                posterior_precision += likelihood_precision
                posterior_mean_numerator += data_point['value'] * likelihood_precision
            
            posterior_mean = posterior_mean_numerator / posterior_precision
            fused_data[key] = posterior_mean
        
        return {
            'fused_data': fused_data,
            'fusion_method': 'bayesian'
        }
    
    def _information_theoretic_fusion(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Perform information-theoretic fusion."""
        
        fused_data = {}
        
        # Calculate information content for each source
        source_entropies = {}
        for source in sources:
            entropy_sum = 0
            value_count = 0
            
            for key, value in source.data.items():
                if isinstance(value, (int, float)):
                    # Approximate entropy using value distribution
                    normalized_value = np.clip(value, 0.01, 0.99)
                    value_entropy = -normalized_value * np.log2(normalized_value) - (1 - normalized_value) * np.log2(1 - normalized_value)
                    entropy_sum += value_entropy
                    value_count += 1
            
            source_entropies[source.source_id] = entropy_sum / max(value_count, 1)
        
        # Weight sources by information content (lower entropy = higher weight)
        max_entropy = max(source_entropies.values()) if source_entropies else 1.0
        
        for source in sources:
            source_entropy = source_entropies.get(source.source_id, max_entropy)
            information_weight = (max_entropy - source_entropy + 0.1) / (max_entropy + 0.1)
            
            for key, value in source.data.items():
                if key not in fused_data:
                    fused_data[key] = value * information_weight
                else:
                    if isinstance(fused_data[key], (int, float)) and isinstance(value, (int, float)):
                        fused_data[key] += value * information_weight
        
        return {
            'fused_data': fused_data,
            'source_entropies': source_entropies,
            'fusion_method': 'information_theoretic'
        }
    
    def _confidence_based_fusion(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Perform confidence-based fusion."""
        
        return self._weighted_average_fusion(sources)  # Similar to weighted average
    
    def _temporal_priority_fusion(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Perform temporal priority fusion (most recent wins)."""
        
        # Sort by timestamp (most recent first)
        sorted_sources = sorted(sources, key=lambda s: s.timestamp, reverse=True)
        
        fused_data = {}
        
        for source in sorted_sources:
            for key, value in source.data.items():
                if key not in fused_data:
                    fused_data[key] = value
        
        return {
            'fused_data': fused_data,
            'temporal_order': [s.source_id for s in sorted_sources],
            'fusion_method': 'temporal_priority'
        }
    
    def _consensus_voting_fusion(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Perform consensus voting fusion."""
        
        conflicts = []
        for key in set().union(*(s.data.keys() for s in sources)):
            key_conflicts = self.conflict_resolver.detect_conflicts(sources, key)
            conflicts.extend(key_conflicts)
        
        if conflicts:
            return self.conflict_resolver.resolve_conflicts(sources, conflicts, 'ensemble_voting')
        else:
            return self._weighted_average_fusion(sources)
    
    def _adaptive_ensemble_fusion(self, sources: List[DataSource]) -> Dict[str, Any]:
        """Perform adaptive ensemble fusion using multiple strategies."""
        
        # Try multiple strategies
        strategies = [
            FusionStrategy.WEIGHTED_AVERAGE,
            FusionStrategy.BAYESIAN_FUSION,
            FusionStrategy.CONFIDENCE_BASED
        ]
        
        strategy_results = {}
        
        for strategy in strategies:
            try:
                if strategy == FusionStrategy.WEIGHTED_AVERAGE:
                    result = self._weighted_average_fusion(sources)
                elif strategy == FusionStrategy.BAYESIAN_FUSION:
                    result = self._bayesian_fusion(sources)
                else:
                    result = self._confidence_based_fusion(sources)
                
                strategy_results[strategy.name] = result
                
            except Exception as e:
                logger.warning(f"Error with strategy {strategy.name}: {e}")
        
        # Combine results from multiple strategies
        if strategy_results:
            combined_data = {}
            
            # Get all keys
            all_keys = set()
            for result in strategy_results.values():
                all_keys.update(result.get('fused_data', {}).keys())
            
            # Ensemble fusion of strategy results
            for key in all_keys:
                strategy_values = []
                strategy_weights = []
                
                for strategy_name, result in strategy_results.items():
                    if key in result.get('fused_data', {}):
                        value = result['fused_data'][key]
                        # Weight based on historical performance
                        weight = 1.0 / (np.mean(self.strategy_performance.get(strategy_name, [1.0])) + 0.1)
                        
                        if isinstance(value, (int, float)):
                            strategy_values.append(value)
                            strategy_weights.append(weight)
                
                if strategy_values:
                    strategy_weights = np.array(strategy_weights)
                    strategy_weights /= np.sum(strategy_weights)
                    combined_data[key] = np.average(strategy_values, weights=strategy_weights)
            
            return {
                'fused_data': combined_data,
                'strategy_results': strategy_results,
                'fusion_method': 'adaptive_ensemble'
            }
        
        # Fallback to weighted average
        return self._weighted_average_fusion(sources)
    
    def _invalidate_cache(self, modality: DataModality):
        """Invalidate cache entries related to a modality."""
        
        keys_to_remove = []
        for cache_key in self.fusion_cache:
            if modality.name.lower() in cache_key.lower():
                keys_to_remove.append(cache_key)
        
        for key in keys_to_remove:
            del self.fusion_cache[key]
    
    def get_fusion_summary(self) -> Dict[str, Any]:
        """Get summary of fusion operations."""
        
        if not self.fusion_history:
            return {'message': 'No fusion operations performed yet'}
        
        total_operations = len(self.fusion_history)
        avg_fusion_time = np.mean([
            entry.get('fusion_time', 0) for entry in self.fusion_history
        ])
        
        # Strategy usage statistics
        strategy_counts = defaultdict(int)
        for entry in self.fusion_history:
            strategy = entry.get('fusion_strategy', 'unknown')
            strategy_counts[strategy] += 1
        
        # Data source usage
        source_usage = defaultdict(int)
        for entry in self.fusion_history:
            for source_id in entry.get('sources_used', []):
                source_usage[source_id] += 1
        
        return {
            'total_fusion_operations': total_operations,
            'average_fusion_time': avg_fusion_time,
            'strategy_usage': dict(strategy_counts),
            'source_usage': dict(source_usage),
            'registered_sources': len(self.data_sources),
            'cache_entries': len(self.fusion_cache)
        }
    
    def temporal_alignment(
        self, 
        sources: List[DataSource], 
        target_timestamps: List[float]
    ) -> List[DataSource]:
        """
        Align data sources to target timestamps using interpolation.
        
        Args:
            sources: Data sources to align
            target_timestamps: Target time points for alignment
            
        Returns:
            Temporally aligned data sources
        """
        
        aligned_sources = []
        
        for target_time in target_timestamps:
            # Find sources closest in time
            time_distances = []
            for source in sources:
                time_dist = abs(source.timestamp - target_time)
                time_distances.append((time_dist, source))
            
            # Sort by time distance
            time_distances.sort(key=lambda x: x[0])
            
            if time_distances:
                closest_source = time_distances[0][1]
                
                # Create aligned source
                aligned_source = DataSource(
                    source_id=f"{closest_source.source_id}_aligned_{target_time}",
                    modality=closest_source.modality,
                    data_type=closest_source.data_type,
                    data=closest_source.data.copy(),
                    metadata=closest_source.metadata.copy(),
                    reliability=closest_source.reliability,
                    timestamp=target_time
                )
                
                # Adjust reliability based on temporal distance
                time_penalty = min(time_distances[0][0] / 3600.0, 0.5)  # Max 50% penalty for 1 hour
                aligned_source.reliability *= (1.0 - time_penalty)
                
                aligned_sources.append(aligned_source)
        
        return aligned_sources
    
    def validate_fusion_result(self, fusion_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate fusion result for biological consistency.
        
        Args:
            fusion_result: Result from fusion operation
            
        Returns:
            Validation report
        """
        
        fused_data = fusion_result.get('fused_data', {})
        validation_report = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'biological_consistency_score': 1.0
        }
        
        # Check biological constraints
        for key, value in fused_data.items():
            if isinstance(value, (int, float)):
                
                # Fitness values
                if 'fitness' in key.lower():
                    if not (0.0 <= value <= 1.0):
                        validation_report['errors'].append(
                            f"Invalid fitness value {value} for key {key} (must be 0-1)"
                        )
                        validation_report['is_valid'] = False
                
                # Expression levels
                elif 'expression' in key.lower():
                    if value < 0:
                        validation_report['errors'].append(
                            f"Negative expression value {value} for key {key}"
                        )
                        validation_report['is_valid'] = False
                
                # Population sizes
                elif 'population' in key.lower():
                    if value < 1:
                        validation_report['errors'].append(
                            f"Invalid population size {value} for key {key} (must be >= 1)"
                        )
                        validation_report['is_valid'] = False
        
        # Calculate biological consistency score
        error_count = len(validation_report['errors'])
        warning_count = len(validation_report['warnings'])
        
        consistency_penalty = error_count * 0.3 + warning_count * 0.1
        validation_report['biological_consistency_score'] = max(0.0, 1.0 - consistency_penalty)
        
        return validation_report
