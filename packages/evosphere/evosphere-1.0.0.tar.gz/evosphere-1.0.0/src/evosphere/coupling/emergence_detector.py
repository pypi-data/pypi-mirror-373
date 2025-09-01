"""
Emergence Detector for Multi-Scale Evolutionary Systems

Advanced system for detecting emergent properties, phase transitions,
and critical phenomena in evolutionary biological systems.
"""

from typing import Dict, List, Any, Optional, Tuple, Union, Callable
import numpy as np
import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

class EmergenceMetric(Enum):
    """Metrics for detecting emergence."""
    
    COMPLEXITY_INCREASE = "complexity_increase"
    PHASE_TRANSITION = "phase_transition"
    CRITICAL_SLOWING_DOWN = "critical_slowing_down"
    SYNCHRONIZATION = "synchronization"
    PATTERN_FORMATION = "pattern_formation"
    INFORMATION_INTEGRATION = "information_integration"
    CAUSAL_EMERGENCE = "causal_emergence"
    DOWNWARD_CAUSATION = "downward_causation"

@dataclass
class EmergentProperty:
    """Represents a detected emergent property."""
    
    property_id: str
    property_type: EmergenceMetric
    emergence_scale: str
    source_scales: List[str]
    emergence_strength: float
    detection_time: float
    duration: float = 0.0
    properties: Dict[str, Any] = field(default_factory=dict)
    is_persistent: bool = False

@dataclass
class ComplexityMeasure:
    """Complexity measurement for emergence detection."""
    
    measure_id: str
    scale: str
    complexity_type: str  # 'logical_depth', 'effective_complexity', 'thermodynamic_depth'
    value: float
    timestamp: float = field(default_factory=time.time)
    computation_method: str = "default"

class PhaseTransitionDetector:
    """Detects phase transitions in evolutionary systems."""
    
    def __init__(self):
        self.transition_history = []
        self.critical_indicators = {}
        self.analysis_window = 30
    
    def detect_phase_transition(
        self,
        system_states: Dict[str, Dict[str, Any]],
        time_series: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect phase transitions across scales.
        
        Args:
            system_states: Current states of all scales
            time_series: Historical time series data
            
        Returns:
            Phase transition detection results
        """
        
        detection = {
            'detection_time': time.time(),
            'transitions_detected': [],
            'critical_indicators': {},
            'analysis_method': 'variance_based'
        }
        
        try:
            # Analyze each scale for phase transitions
            for scale, state in system_states.items():
                transition_indicators = self._analyze_scale_transition(scale, state, time_series)
                detection['critical_indicators'][scale] = transition_indicators
                
                # Check for transition signatures
                if self._is_phase_transition(transition_indicators):
                    transition = {
                        'scale': scale,
                        'transition_type': transition_indicators.get('transition_type', 'unknown'),
                        'strength': transition_indicators.get('transition_strength', 0.0),
                        'critical_parameter': transition_indicators.get('critical_parameter', 'unknown')
                    }
                    detection['transitions_detected'].append(transition)
            
            # Cross-scale transition analysis
            cross_scale_transitions = self._detect_cross_scale_transitions(system_states)
            detection['cross_scale_transitions'] = cross_scale_transitions
            
        except Exception as e:
            detection['error'] = str(e)
        
        return detection
    
    def _analyze_scale_transition(
        self,
        scale: str,
        state: Dict[str, Any],
        time_series: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze a single scale for phase transition indicators."""
        
        indicators = {
            'scale': scale,
            'analysis_time': time.time()
        }
        
        try:
            # Key variables for transition detection
            fitness = state.get('fitness', 0.5)
            diversity = state.get('diversity', 0.5)
            mutation_rate = state.get('mutation_rate', 0.01)
            
            # Variance analysis (critical slowing down indicator)
            if time_series and len(time_series) > 10:
                # Extract fitness time series
                fitness_series = []
                for ts_point in time_series[-self.analysis_window:]:
                    if scale in ts_point and 'fitness' in ts_point[scale]:
                        fitness_series.append(float(ts_point[scale]['fitness']))
                
                if len(fitness_series) > 5:
                    # Calculate variance and autocorrelation
                    fitness_variance = np.var(fitness_series)
                    autocorr = self._calculate_autocorrelation(fitness_series)
                    
                    indicators['fitness_variance'] = fitness_variance
                    indicators['autocorrelation'] = autocorr
                    
                    # Critical slowing down detection
                    if autocorr > 0.8 and fitness_variance > 0.01:
                        indicators['critical_slowing_down'] = True
                        indicators['transition_strength'] = autocorr * fitness_variance
                        indicators['transition_type'] = 'critical_transition'
                    else:
                        indicators['critical_slowing_down'] = False
            
            # Bistability detection
            if 0.45 < fitness < 0.55:  # Near critical fitness value
                indicators['near_critical_point'] = True
                indicators['critical_parameter'] = 'fitness'
            
            # Diversity collapse detection
            if diversity < 0.1:
                indicators['diversity_collapse'] = True
                indicators['transition_type'] = 'diversity_collapse'
                indicators['transition_strength'] = 1.0 - diversity * 10
            
            # Mutation rate criticality
            if mutation_rate > 0.05 or mutation_rate < 0.001:
                indicators['mutation_criticality'] = True
                indicators['critical_parameter'] = 'mutation_rate'
        
        except Exception as e:
            indicators['error'] = str(e)
        
        return indicators
    
    def _is_phase_transition(self, indicators: Dict[str, Any]) -> bool:
        """Determine if indicators suggest a phase transition."""
        
        try:
            # Check for multiple transition indicators
            transition_signals = 0
            
            if indicators.get('critical_slowing_down', False):
                transition_signals += 1
            
            if indicators.get('near_critical_point', False):
                transition_signals += 1
            
            if indicators.get('diversity_collapse', False):
                transition_signals += 1
            
            if indicators.get('mutation_criticality', False):
                transition_signals += 1
            
            # Transition detected if multiple signals present
            return transition_signals >= 2
        
        except Exception:
            return False
    
    def _detect_cross_scale_transitions(self, system_states: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect transitions that span multiple scales."""
        
        transitions = []
        
        try:
            # Look for synchronized changes across scales
            scale_fitnesses = {}
            for scale, state in system_states.items():
                if 'fitness' in state:
                    scale_fitnesses[scale] = float(state['fitness'])
            
            if len(scale_fitnesses) >= 2:
                # Calculate fitness correlation across scales
                fitness_values = list(scale_fitnesses.values())
                fitness_variance = np.var(fitness_values)
                
                # Low variance indicates synchronization
                if fitness_variance < 0.01:
                    transition = {
                        'transition_type': 'synchronization',
                        'involved_scales': list(scale_fitnesses.keys()),
                        'synchronization_strength': 1.0 - fitness_variance * 100,
                        'detection_time': time.time()
                    }
                    transitions.append(transition)
                
                # High variance indicates critical fluctuations
                elif fitness_variance > 0.1:
                    transition = {
                        'transition_type': 'critical_fluctuations',
                        'involved_scales': list(scale_fitnesses.keys()),
                        'fluctuation_strength': fitness_variance,
                        'detection_time': time.time()
                    }
                    transitions.append(transition)
        
        except Exception as e:
            transitions.append({
                'error': str(e),
                'detection_time': time.time()
            })
        
        return transitions
    
    def _calculate_autocorrelation(self, series: List[float], lag: int = 1) -> float:
        """Calculate autocorrelation of a time series."""
        
        try:
            if len(series) <= lag:
                return 0.0
            
            series_array = np.array(series)
            mean_series = np.mean(series_array)
            
            # Calculate autocorrelation at given lag
            numerator = 0.0
            denominator = 0.0
            
            for i in range(len(series) - lag):
                numerator += (series_array[i] - mean_series) * (series_array[i + lag] - mean_series)
                denominator += (series_array[i] - mean_series) ** 2
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
        
        except Exception:
            return 0.0

class CriticalityAnalyzer:
    """Analyzes criticality and self-organized criticality in evolutionary systems."""
    
    def __init__(self):
        self.criticality_history = []
        self.power_law_exponents = {}
    
    def analyze_criticality(
        self,
        system_states: Dict[str, Dict[str, Any]],
        time_series: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze system for criticality indicators.
        
        Args:
            system_states: Current system states
            time_series: Historical time series
            
        Returns:
            Criticality analysis results
        """
        
        analysis = {
            'analysis_time': time.time(),
            'criticality_detected': False,
            'criticality_indicators': {},
            'power_law_analysis': {}
        }
        
        try:
            # Analyze each scale for criticality
            for scale, state in system_states.items():
                criticality_metrics = self._analyze_scale_criticality(scale, state, time_series)
                analysis['criticality_indicators'][scale] = criticality_metrics
                
                if criticality_metrics.get('is_critical', False):
                    analysis['criticality_detected'] = True
            
            # Power law analysis
            if time_series and len(time_series) > 20:
                power_law_results = self._analyze_power_laws(time_series)
                analysis['power_law_analysis'] = power_law_results
            
            # Self-organized criticality detection
            soc_analysis = self._detect_self_organized_criticality(system_states, time_series)
            analysis['self_organized_criticality'] = soc_analysis
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_scale_criticality(
        self,
        scale: str,
        state: Dict[str, Any],
        time_series: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze criticality for a single scale."""
        
        metrics = {
            'scale': scale,
            'is_critical': False,
            'criticality_score': 0.0
        }
        
        try:
            fitness = state.get('fitness', 0.5)
            diversity = state.get('diversity', 0.5)
            
            # Criticality indicators
            criticality_factors = []
            
            # Near-critical fitness
            if 0.45 < fitness < 0.55:
                criticality_factors.append(0.8)
            elif 0.4 < fitness < 0.6:
                criticality_factors.append(0.4)
            else:
                criticality_factors.append(0.0)
            
            # Low diversity (near extinction)
            if diversity < 0.2:
                criticality_factors.append(0.9)
            elif diversity < 0.4:
                criticality_factors.append(0.5)
            else:
                criticality_factors.append(0.0)
            
            # Time series analysis
            if time_series and len(time_series) > 10:
                # Extract recent fitness values
                recent_fitness = []
                for ts_point in time_series[-10:]:
                    if scale in ts_point and 'fitness' in ts_point[scale]:
                        recent_fitness.append(float(ts_point[scale]['fitness']))
                
                if len(recent_fitness) > 5:
                    # Large fluctuations indicate criticality
                    fitness_std = np.std(recent_fitness)
                    if fitness_std > 0.1:
                        criticality_factors.append(fitness_std * 5)  # Scale to 0-1 range
                    else:
                        criticality_factors.append(0.0)
            
            # Calculate overall criticality score
            if criticality_factors:
                metrics['criticality_score'] = np.mean(criticality_factors)
                metrics['is_critical'] = metrics['criticality_score'] > 0.6
                metrics['individual_factors'] = criticality_factors
        
        except Exception as e:
            metrics['error'] = str(e)
        
        return metrics
    
    def _analyze_power_laws(self, time_series: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze time series for power law distributions."""
        
        analysis = {
            'power_laws_detected': [],
            'exponents': {}
        }
        
        try:
            # Extract fitness fluctuations across all scales
            all_fluctuations = []
            
            for i in range(1, len(time_series)):
                current = time_series[i]
                previous = time_series[i-1]
                
                for scale in current:
                    if (scale in previous and 
                        isinstance(current[scale], dict) and 
                        isinstance(previous[scale], dict)):
                        
                        if 'fitness' in current[scale] and 'fitness' in previous[scale]:
                            try:
                                curr_fitness = float(current[scale]['fitness'])
                                prev_fitness = float(previous[scale]['fitness'])
                                fluctuation = abs(curr_fitness - prev_fitness)
                                
                                if fluctuation > 0:
                                    all_fluctuations.append(fluctuation)
                            
                            except (ValueError, TypeError):
                                continue
            
            # Power law analysis on fluctuation sizes
            if len(all_fluctuations) > 20:
                # Create histogram
                fluctuations_array = np.array(all_fluctuations)
                hist, bins = np.histogram(fluctuations_array, bins=20)
                
                # Remove zeros
                nonzero_mask = hist > 0
                hist_nonzero = hist[nonzero_mask]
                bins_nonzero = bins[:-1][nonzero_mask]
                
                if len(hist_nonzero) > 5:
                    # Fit power law: P(x) ~ x^(-alpha)
                    log_hist = np.log(hist_nonzero)
                    log_bins = np.log(bins_nonzero)
                    
                    # Linear regression in log space
                    coeffs = np.polyfit(log_bins, log_hist, 1)
                    exponent = -coeffs[0]  # Negative slope gives positive exponent
                    
                    analysis['exponents']['fluctuation_sizes'] = exponent
                    
                    # Power law detected if exponent in reasonable range
                    if 1.0 < exponent < 4.0:
                        analysis['power_laws_detected'].append({
                            'variable': 'fitness_fluctuations',
                            'exponent': exponent,
                            'quality_score': abs(coeffs[1])  # R-squared approximation
                        })
        
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _detect_self_organized_criticality(
        self,
        system_states: Dict[str, Dict[str, Any]],
        time_series: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Detect self-organized criticality patterns."""
        
        soc_analysis = {
            'soc_detected': False,
            'soc_indicators': {},
            'analysis_method': 'avalanche_detection'
        }
        
        try:
            # SOC indicators
            soc_indicators = []
            
            # 1. Power law distributions
            if time_series:
                power_law_analysis = self._analyze_power_laws(time_series)
                if power_law_analysis['power_laws_detected']:
                    soc_indicators.append('power_law_distributions')
                    soc_analysis['soc_indicators']['power_laws'] = power_law_analysis
            
            # 2. Long-range correlations
            correlation_analysis = self._analyze_long_range_correlations(system_states, time_series)
            if correlation_analysis.get('long_range_detected', False):
                soc_indicators.append('long_range_correlations')
                soc_analysis['soc_indicators']['correlations'] = correlation_analysis
            
            # 3. Scale invariance
            scale_invariance = self._detect_scale_invariance(system_states)
            if scale_invariance.get('scale_invariant', False):
                soc_indicators.append('scale_invariance')
                soc_analysis['soc_indicators']['scale_invariance'] = scale_invariance
            
            # SOC detected if multiple indicators present
            soc_analysis['soc_detected'] = len(soc_indicators) >= 2
            soc_analysis['detected_indicators'] = soc_indicators
        
        except Exception as e:
            soc_analysis['error'] = str(e)
        
        return soc_analysis
    
    def _analyze_long_range_correlations(
        self,
        system_states: Dict[str, Dict[str, Any]],
        time_series: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze for long-range temporal correlations."""
        
        correlation_analysis = {
            'long_range_detected': False,
            'correlation_lengths': {}
        }
        
        try:
            if not time_series or len(time_series) < 20:
                return correlation_analysis
            
            # Analyze fitness correlations
            for scale in system_states.keys():
                fitness_series = []
                
                for ts_point in time_series:
                    if scale in ts_point and 'fitness' in ts_point[scale]:
                        try:
                            fitness_series.append(float(ts_point[scale]['fitness']))
                        except (ValueError, TypeError):
                            continue
                
                if len(fitness_series) > 10:
                    # Calculate correlations at different lags
                    max_lag = min(len(fitness_series) // 3, 10)
                    correlations = []
                    
                    for lag in range(1, max_lag + 1):
                        corr = self._calculate_autocorrelation(fitness_series, lag)
                        correlations.append((lag, corr))
                    
                    # Find correlation length (where correlation drops below 1/e)
                    correlation_length = 1
                    for lag, corr in correlations:
                        if corr < 1.0/np.e:
                            correlation_length = lag
                            break
                        correlation_length = lag
                    
                    correlation_analysis['correlation_lengths'][scale] = correlation_length
                    
                    # Long-range if correlation length > 5
                    if correlation_length > 5:
                        correlation_analysis['long_range_detected'] = True
        
        except Exception as e:
            correlation_analysis['error'] = str(e)
        
        return correlation_analysis
    
    def _detect_scale_invariance(self, system_states: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Detect scale-invariant patterns across biological scales."""
        
        invariance = {
            'scale_invariant': False,
            'invariant_properties': []
        }
        
        try:
            # Check if similar patterns exist across scales
            fitness_values = []
            diversity_values = []
            
            for scale, state in system_states.items():
                if 'fitness' in state:
                    fitness_values.append(float(state['fitness']))
                if 'diversity' in state:
                    diversity_values.append(float(state['diversity']))
            
            # Scale invariance detected if values are similar across scales
            if len(fitness_values) >= 2:
                fitness_cv = np.std(fitness_values) / np.mean(fitness_values) if np.mean(fitness_values) > 0 else 1.0
                if fitness_cv < 0.2:  # Low coefficient of variation
                    invariance['invariant_properties'].append('fitness')
            
            if len(diversity_values) >= 2:
                diversity_cv = np.std(diversity_values) / np.mean(diversity_values) if np.mean(diversity_values) > 0 else 1.0
                if diversity_cv < 0.2:
                    invariance['invariant_properties'].append('diversity')
            
            invariance['scale_invariant'] = len(invariance['invariant_properties']) > 0
        
        except Exception as e:
            invariance['error'] = str(e)
        
        return invariance
    
    def _calculate_autocorrelation(self, series: List[float], lag: int = 1) -> float:
        """Calculate autocorrelation at specified lag."""
        
        try:
            if len(series) <= lag:
                return 0.0
            
            series_array = np.array(series)
            mean_series = np.mean(series_array)
            
            numerator = 0.0
            denominator = 0.0
            
            for i in range(len(series) - lag):
                numerator += (series_array[i] - mean_series) * (series_array[i + lag] - mean_series)
                denominator += (series_array[i] - mean_series) ** 2
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
        
        except Exception:
            return 0.0

class EmergenceDetector:
    """
    Patent Feature: Advanced emergence detection for evolutionary systems.
    
    Detects emergent properties, phase transitions, self-organized criticality,
    and other complex phenomena arising from multi-scale interactions.
    """
    
    def __init__(
        self,
        detection_threshold: float = 0.7,
        monitoring_window: int = 50,
        enable_criticality_analysis: bool = True
    ):
        """
        Initialize emergence detector.
        
        Args:
            detection_threshold: Threshold for emergence detection
            monitoring_window: Number of time steps to analyze
            enable_criticality_analysis: Enable criticality detection
        """
        self.detection_threshold = detection_threshold
        self.monitoring_window = monitoring_window
        self.enable_criticality_analysis = enable_criticality_analysis
        
        # Detection components
        self.phase_transition_detector = PhaseTransitionDetector()
        self.criticality_analyzer = CriticalityAnalyzer()
        
        # Detection state
        self.emergent_properties: List[EmergentProperty] = []
        self.complexity_measures: List[ComplexityMeasure] = []
        self.monitoring_history = []
        self.is_monitoring = False
        
        # Thread safety
        self._lock = threading.Lock()
        
        print("EmergenceDetector initialized")
    
    def start_monitoring(
        self,
        scales: List[str],
        initial_states: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Start monitoring for emergent properties.
        
        Args:
            scales: List of scales to monitor
            initial_states: Initial states of scales
            
        Returns:
            Monitoring initialization results
        """
        
        results = {
            'monitoring_start': time.time(),
            'monitored_scales': scales,
            'baseline_complexity': {}
        }
        
        try:
            # Calculate baseline complexity for each scale
            for scale in scales:
                if scale in initial_states:
                    complexity = self._calculate_complexity(initial_states[scale], scale)
                    self.complexity_measures.append(complexity)
                    results['baseline_complexity'][scale] = complexity.value
            
            # Initialize monitoring history
            self.monitoring_history = [{
                'time': 0.0,
                'states': initial_states.copy(),
                'complexity_measures': [cm.value for cm in self.complexity_measures]
            }]
            
            self.is_monitoring = True
            results['success'] = True
            
            print(f"Started emergence monitoring for {len(scales)} scales")
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            print(f"Error starting monitoring: {e}")
        
        return results
    
    def detect_emergence(self, current_time: float) -> Dict[str, Any]:
        """
        Detect emergent properties at current time.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            Emergence detection results
        """
        
        if not self.is_monitoring:
            return {
                'success': False,
                'error': 'Emergence monitoring not started'
            }
        
        detection_results = {
            'detection_time': current_time,
            'emergent_properties': [],
            'complexity_changes': {},
            'phase_transitions': []
        }
        
        try:
            with self._lock:
                # Mock current system states (in production, would be passed as parameter)
                current_states = self._generate_mock_states()
                
                # Add to monitoring history
                self.monitoring_history.append({
                    'time': current_time,
                    'states': current_states,
                    'complexity_measures': []
                })
                
                # Limit history size
                if len(self.monitoring_history) > self.monitoring_window:
                    self.monitoring_history = self.monitoring_history[-self.monitoring_window:]
                
                # 1. Complexity-based emergence detection
                complexity_results = self._detect_complexity_emergence(current_states, current_time)
                detection_results['complexity_changes'] = complexity_results
                
                if complexity_results.get('emergence_detected', False):
                    detection_results['emergent_properties'].extend(
                        complexity_results['emergent_properties']
                    )
                
                # 2. Phase transition detection
                transition_results = self.phase_transition_detector.detect_phase_transition(
                    current_states, self.monitoring_history
                )
                detection_results['phase_transitions'] = transition_results['transitions_detected']
                
                # Convert phase transitions to emergent properties
                for transition in transition_results['transitions_detected']:
                    emergent_prop = EmergentProperty(
                        property_id=f"phase_transition_{transition['scale']}_{current_time}",
                        property_type=EmergenceMetric.PHASE_TRANSITION,
                        emergence_scale=transition['scale'],
                        source_scales=[transition['scale']],
                        emergence_strength=transition['strength'],
                        detection_time=current_time,
                        properties=transition
                    )
                    self.emergent_properties.append(emergent_prop)
                    detection_results['emergent_properties'].append(emergent_prop)
                
                # 3. Criticality analysis (if enabled)
                if self.enable_criticality_analysis:
                    criticality_results = self.criticality_analyzer.analyze_criticality(
                        current_states, self.monitoring_history
                    )
                    detection_results['criticality'] = criticality_results
                
                # 4. Pattern formation detection
                pattern_results = self._detect_pattern_formation(current_states)
                detection_results['patterns'] = pattern_results
                
                if pattern_results.get('patterns_detected', False):
                    detection_results['emergent_properties'].extend(
                        pattern_results['emergent_patterns']
                    )
                
                # 5. Information integration detection
                integration_results = self._detect_information_integration(current_states)
                detection_results['information_integration'] = integration_results
                
                detection_results['total_emergent_properties'] = len(detection_results['emergent_properties'])
                detection_results['success'] = True
        
        except Exception as e:
            detection_results['success'] = False
            detection_results['error'] = str(e)
            print(f"Error in emergence detection: {e}")
        
        return detection_results
    
    def _generate_mock_states(self) -> Dict[str, Dict[str, Any]]:
        """Generate mock system states for testing."""
        
        mock_states = {}
        
        scales = ['molecular', 'organismal', 'population', 'ecosystem']
        
        for scale in scales:
            mock_states[scale] = {
                'fitness': np.random.uniform(0.3, 0.9),
                'diversity': np.random.uniform(0.2, 0.8),
                'mutation_rate': np.random.uniform(0.005, 0.03),
                'adaptation_rate': np.random.uniform(0.01, 0.05),
                'complexity': np.random.uniform(0.1, 0.8)
            }
        
        return mock_states
    
    def _calculate_complexity(self, state: Dict[str, Any], scale: str) -> ComplexityMeasure:
        """Calculate complexity measure for a given state."""
        
        try:
            # Simple complexity calculation based on entropy
            values = []
            for key, value in state.items():
                try:
                    values.append(float(value))
                except (ValueError, TypeError):
                    continue
            
            if values:
                # Normalize values
                values_array = np.array(values)
                if np.std(values_array) > 0:
                    normalized = (values_array - np.mean(values_array)) / np.std(values_array)
                else:
                    normalized = values_array
                
                # Calculate entropy as complexity measure
                hist, _ = np.histogram(normalized, bins=10, density=True)
                hist = hist[hist > 0]  # Remove zeros
                entropy = -np.sum(hist * np.log(hist + 1e-10))
                
                complexity_value = min(entropy / np.log(len(values)), 1.0)  # Normalize
            else:
                complexity_value = 0.0
            
            return ComplexityMeasure(
                measure_id=f"complexity_{scale}_{time.time()}",
                scale=scale,
                complexity_type='entropy_based',
                value=complexity_value
            )
        
        except Exception as e:
            print(f"Error calculating complexity for {scale}: {e}")
            return ComplexityMeasure(
                measure_id=f"complexity_{scale}_{time.time()}",
                scale=scale,
                complexity_type='entropy_based',
                value=0.0
            )
    
    def _detect_complexity_emergence(
        self,
        current_states: Dict[str, Dict[str, Any]],
        current_time: float
    ) -> Dict[str, Any]:
        """Detect emergence through complexity changes."""
        
        results = {
            'emergence_detected': False,
            'emergent_properties': [],
            'complexity_deltas': {}
        }
        
        try:
            # Calculate current complexities
            current_complexities = {}
            for scale, state in current_states.items():
                complexity = self._calculate_complexity(state, scale)
                current_complexities[scale] = complexity.value
                self.complexity_measures.append(complexity)
            
            # Compare with baseline (first measurement)
            if len(self.complexity_measures) > len(current_states):
                baseline_complexities = {}
                
                # Find baseline complexities
                for measure in self.complexity_measures[:len(current_states)]:
                    baseline_complexities[measure.scale] = measure.value
                
                # Calculate complexity changes
                for scale in current_complexities:
                    if scale in baseline_complexities:
                        delta = current_complexities[scale] - baseline_complexities[scale]
                        results['complexity_deltas'][scale] = {
                            'baseline': baseline_complexities[scale],
                            'current': current_complexities[scale],
                            'delta': delta,
                            'relative_change': delta / max(baseline_complexities[scale], 1e-6)
                        }
                        
                        # Emergence detected if significant complexity increase
                        if delta > self.detection_threshold * baseline_complexities[scale]:
                            emergent_prop = EmergentProperty(
                                property_id=f"complexity_emergence_{scale}_{current_time}",
                                property_type=EmergenceMetric.COMPLEXITY_INCREASE,
                                emergence_scale=scale,
                                source_scales=[scale],
                                emergence_strength=delta,
                                detection_time=current_time,
                                properties={
                                    'complexity_delta': delta,
                                    'baseline_complexity': baseline_complexities[scale],
                                    'current_complexity': current_complexities[scale]
                                }
                            )
                            
                            results['emergent_properties'].append(emergent_prop)
                            results['emergence_detected'] = True
        
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _detect_pattern_formation(self, system_states: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Detect spatial or temporal pattern formation."""
        
        pattern_results = {
            'patterns_detected': False,
            'emergent_patterns': [],
            'pattern_types': []
        }
        
        try:
            # Look for coordinated behavior across scales
            fitness_values = []
            scales_with_fitness = []
            
            for scale, state in system_states.items():
                if 'fitness' in state:
                    fitness_values.append(float(state['fitness']))
                    scales_with_fitness.append(scale)
            
            if len(fitness_values) >= 3:
                # Check for patterns in fitness values
                
                # 1. Monotonic patterns (increasing or decreasing across scales)
                if self._is_monotonic(fitness_values):
                    pattern_results['pattern_types'].append('monotonic_fitness')
                    
                    emergent_pattern = EmergentProperty(
                        property_id=f"monotonic_pattern_{time.time()}",
                        property_type=EmergenceMetric.PATTERN_FORMATION,
                        emergence_scale='multi_scale',
                        source_scales=scales_with_fitness,
                        emergence_strength=0.8,
                        detection_time=time.time(),
                        properties={
                            'pattern_type': 'monotonic',
                            'fitness_values': fitness_values,
                            'involved_scales': scales_with_fitness
                        }
                    )
                    pattern_results['emergent_patterns'].append(emergent_pattern)
                
                # 2. Oscillatory patterns
                if len(fitness_values) >= 4 and self._detect_oscillation(fitness_values):
                    pattern_results['pattern_types'].append('oscillatory_fitness')
                    
                    emergent_pattern = EmergentProperty(
                        property_id=f"oscillatory_pattern_{time.time()}",
                        property_type=EmergenceMetric.PATTERN_FORMATION,
                        emergence_scale='multi_scale',
                        source_scales=scales_with_fitness,
                        emergence_strength=0.6,
                        detection_time=time.time(),
                        properties={
                            'pattern_type': 'oscillatory',
                            'fitness_values': fitness_values,
                            'involved_scales': scales_with_fitness
                        }
                    )
                    pattern_results['emergent_patterns'].append(emergent_pattern)
                
                pattern_results['patterns_detected'] = len(pattern_results['emergent_patterns']) > 0
        
        except Exception as e:
            pattern_results['error'] = str(e)
        
        return pattern_results
    
    def _is_monotonic(self, values: List[float]) -> bool:
        """Check if values form a monotonic sequence."""
        
        try:
            if len(values) < 2:
                return False
            
            increasing = all(values[i] <= values[i+1] for i in range(len(values)-1))
            decreasing = all(values[i] >= values[i+1] for i in range(len(values)-1))
            
            return increasing or decreasing
        
        except Exception:
            return False
    
    def _detect_oscillation(self, values: List[float]) -> bool:
        """Detect oscillatory patterns in values."""
        
        try:
            if len(values) < 4:
                return False
            
            # Simple oscillation detection: count direction changes
            direction_changes = 0
            
            for i in range(2, len(values)):
                # Check if direction changed
                prev_diff = values[i-1] - values[i-2]
                curr_diff = values[i] - values[i-1]
                
                if prev_diff * curr_diff < 0:  # Sign change
                    direction_changes += 1
            
            # Oscillation if direction changes frequently
            return direction_changes >= len(values) // 2
        
        except Exception:
            return False
    
    def _detect_information_integration(self, system_states: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Detect information integration across scales."""
        
        integration = {
            'integration_detected': False,
            'integration_strength': 0.0,
            'integrated_scales': []
        }
        
        try:
            # Calculate mutual information between scales (simplified)
            scale_names = list(system_states.keys())
            
            if len(scale_names) >= 2:
                # Extract fitness values for mutual information calculation
                fitness_data = {}
                for scale, state in system_states.items():
                    if 'fitness' in state:
                        fitness_data[scale] = float(state['fitness'])
                
                if len(fitness_data) >= 2:
                    # Simple correlation as mutual information proxy
                    fitness_values = list(fitness_data.values())
                    
                    if len(fitness_values) == 2:
                        # For two scales, calculate correlation
                        correlation = abs(np.corrcoef([fitness_values[0], fitness_values[1]])[0, 1])
                        
                        if not np.isnan(correlation) and correlation > 0.7:
                            integration['integration_detected'] = True
                            integration['integration_strength'] = correlation
                            integration['integrated_scales'] = list(fitness_data.keys())
                    
                    else:
                        # For multiple scales, calculate average pairwise correlation
                        correlations = []
                        for i in range(len(fitness_values)):
                            for j in range(i+1, len(fitness_values)):
                                try:
                                    corr = abs(np.corrcoef([fitness_values[i], fitness_values[j]])[0, 1])
                                    if not np.isnan(corr):
                                        correlations.append(corr)
                                except Exception:
                                    continue
                        
                        if correlations:
                            avg_correlation = np.mean(correlations)
                            if avg_correlation > 0.6:
                                integration['integration_detected'] = True
                                integration['integration_strength'] = avg_correlation
                                integration['integrated_scales'] = list(fitness_data.keys())
        
        except Exception as e:
            integration['error'] = str(e)
        
        return integration
    
    def get_emergence_summary(self) -> Dict[str, Any]:
        """Get comprehensive emergence detection summary."""
        
        summary = {
            'timestamp': time.time(),
            'is_monitoring': self.is_monitoring,
            'configuration': {
                'detection_threshold': self.detection_threshold,
                'monitoring_window': self.monitoring_window,
                'criticality_analysis_enabled': self.enable_criticality_analysis
            }
        }
        
        try:
            # Emergent properties summary
            total_properties = len(self.emergent_properties)
            recent_properties = [
                prop for prop in self.emergent_properties
                if prop.detection_time > (time.time() - 10.0)
            ]
            
            summary['emergent_properties'] = {
                'total_detected': total_properties,
                'recent_detected': len(recent_properties),
                'property_types': {}
            }
            
            # Count by type
            for prop in self.emergent_properties:
                prop_type = prop.property_type.value
                if prop_type not in summary['emergent_properties']['property_types']:
                    summary['emergent_properties']['property_types'][prop_type] = 0
                summary['emergent_properties']['property_types'][prop_type] += 1
            
            # Complexity evolution
            if self.complexity_measures:
                recent_complexities = self.complexity_measures[-len(self.scales):]
                avg_complexity = np.mean([cm.value for cm in recent_complexities])
                
                summary['complexity_evolution'] = {
                    'current_avg_complexity': avg_complexity,
                    'total_complexity_measures': len(self.complexity_measures)
                }
            
            # Monitoring statistics
            summary['monitoring_statistics'] = {
                'monitoring_history_length': len(self.monitoring_history),
                'monitoring_duration': len(self.monitoring_history) * 0.1 if self.monitoring_history else 0.0
            }
        
        except Exception as e:
            summary['error'] = str(e)
        
        return summary

# Export main classes
__all__ = [
    'EmergenceDetector',
    'EmergentProperty',
    'EmergenceMetric',
    'ComplexityMeasure',
    'PhaseTransitionDetector',
    'CriticalityAnalyzer'
]
