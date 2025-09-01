"""
Evolutionary Feedback Controller

Advanced feedback control system for maintaining stability and
directing evolution in multi-scale biological systems.
"""

from typing import Dict, List, Any, Optional, Tuple, Union, Callable
import numpy as np
import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

class FeedbackType(Enum):
    """Types of feedback control."""
    
    NEGATIVE_FEEDBACK = "negative_feedback"      # Stabilizing feedback
    POSITIVE_FEEDBACK = "positive_feedback"      # Amplifying feedback
    ADAPTIVE_FEEDBACK = "adaptive_feedback"      # Self-adjusting feedback
    PREDICTIVE_FEEDBACK = "predictive_feedback"  # Model-predictive control
    HOMEOSTATIC_FEEDBACK = "homeostatic_feedback" # Homeostasis maintenance

@dataclass
class ControlSignal:
    """Control signal for feedback loops."""
    
    signal_id: str
    source_scale: str
    target_scale: str
    signal_type: str
    magnitude: float
    direction: str  # 'increase', 'decrease', 'maintain'
    timestamp: float = field(default_factory=time.time)
    priority: int = 1  # 1 = low, 5 = high priority

@dataclass
class FeedbackGain:
    """Gain parameters for feedback control."""
    
    proportional_gain: float = 1.0      # P gain
    integral_gain: float = 0.1          # I gain  
    derivative_gain: float = 0.01       # D gain
    adaptive_gain: float = 0.05         # Adaptive component
    saturation_limit: float = 10.0      # Anti-windup limit

@dataclass
class FeedbackLoop:
    """Represents a feedback control loop."""
    
    loop_id: str
    feedback_type: FeedbackType
    source_scale: str
    target_scale: str
    control_variable: str
    reference_value: float
    gains: FeedbackGain = field(default_factory=FeedbackGain)
    is_active: bool = True
    creation_time: float = field(default_factory=time.time)
    
    # Control history for integral and derivative terms
    error_history: List[float] = field(default_factory=list)
    control_history: List[float] = field(default_factory=list)
    integral_sum: float = 0.0
    last_error: float = 0.0
    last_update: float = field(default_factory=time.time)

class StabilityAnalyzer:
    """Analyzes system stability and provides control recommendations."""
    
    def __init__(self):
        self.stability_metrics = {}
        self.stability_history = []
        self.analysis_window = 50  # Number of time steps to analyze
    
    def analyze_stability(
        self,
        system_states: Dict[str, Dict[str, Any]],
        time_window: int = None
    ) -> Dict[str, Any]:
        """
        Analyze system stability across scales.
        
        Args:
            system_states: Current states of all scales
            time_window: Number of previous states to analyze
            
        Returns:
            Stability analysis results
        """
        
        analysis = {
            'timestamp': time.time(),
            'overall_stability': 'unknown',
            'scale_stability': {},
            'recommendations': []
        }
        
        try:
            window = time_window or self.analysis_window
            
            # Analyze each scale
            total_stability_score = 0.0
            scale_count = 0
            
            for scale_name, state in system_states.items():
                stability_metrics = self._analyze_scale_stability(scale_name, state)
                analysis['scale_stability'][scale_name] = stability_metrics
                
                if 'stability_score' in stability_metrics:
                    total_stability_score += stability_metrics['stability_score']
                    scale_count += 1
            
            # Overall stability assessment
            if scale_count > 0:
                overall_score = total_stability_score / scale_count
                
                if overall_score > 0.8:
                    analysis['overall_stability'] = 'stable'
                elif overall_score > 0.6:
                    analysis['overall_stability'] = 'moderately_stable'
                elif overall_score > 0.4:
                    analysis['overall_stability'] = 'unstable'
                else:
                    analysis['overall_stability'] = 'highly_unstable'
                    analysis['recommendations'].append('Reduce coupling strengths')
                    analysis['recommendations'].append('Increase stabilizing feedback')
                
                analysis['overall_stability_score'] = overall_score
            
            # Add to history
            self.stability_history.append({
                'time': time.time(),
                'overall_score': analysis.get('overall_stability_score', 0.0),
                'scale_scores': {
                    name: metrics.get('stability_score', 0.0)
                    for name, metrics in analysis['scale_stability'].items()
                }
            })
            
            # Limit history size
            if len(self.stability_history) > window:
                self.stability_history = self.stability_history[-window:]
        
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_scale_stability(self, scale_name: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stability of a single scale."""
        
        metrics = {
            'scale': scale_name,
            'analysis_time': time.time()
        }
        
        try:
            # Key stability indicators
            fitness = state.get('fitness', 0.5)
            diversity = state.get('diversity', 0.5)
            mutation_rate = state.get('mutation_rate', 0.01)
            
            # Stability score calculation
            stability_factors = []
            
            # Fitness stability (should be moderate, not too high or low)
            fitness_stability = 1.0 - abs(fitness - 0.7)  # Optimal around 0.7
            stability_factors.append(fitness_stability)
            
            # Diversity stability (should maintain reasonable diversity)
            diversity_stability = min(diversity * 2, 1.0)  # Higher diversity = more stable
            stability_factors.append(diversity_stability)
            
            # Mutation rate stability (moderate mutation rates preferred)
            if mutation_rate > 0:
                mutation_stability = 1.0 - abs(np.log10(mutation_rate) + 2.0) / 2.0  # Optimal around 0.01
                stability_factors.append(max(0.0, mutation_stability))
            
            # Overall stability score
            stability_score = np.mean(stability_factors)
            metrics['stability_score'] = stability_score
            
            # Individual factor scores
            metrics['fitness_stability'] = fitness_stability
            metrics['diversity_stability'] = diversity_stability
            
            if mutation_rate > 0:
                metrics['mutation_stability'] = mutation_stability
            
            # Stability classification
            if stability_score > 0.8:
                metrics['classification'] = 'stable'
            elif stability_score > 0.6:
                metrics['classification'] = 'moderately_stable'
            elif stability_score > 0.4:
                metrics['classification'] = 'unstable'
            else:
                metrics['classification'] = 'highly_unstable'
        
        except Exception as e:
            metrics['error'] = str(e)
            metrics['stability_score'] = 0.0
        
        return metrics

class EvolutionaryFeedbackController:
    """
    Patent Feature: Advanced feedback controller for evolutionary systems.
    
    Implements PID control, adaptive feedback, and stability maintenance
    for multi-scale evolutionary processes with homeostatic regulation.
    """
    
    def __init__(
        self,
        enable_adaptive_gains: bool = True,
        stability_threshold: float = 0.6,
        max_control_effort: float = 1.0
    ):
        """
        Initialize evolutionary feedback controller.
        
        Args:
            enable_adaptive_gains: Enable adaptive gain adjustment
            stability_threshold: Minimum stability score to maintain
            max_control_effort: Maximum control signal magnitude
        """
        self.enable_adaptive_gains = enable_adaptive_gains
        self.stability_threshold = stability_threshold
        self.max_control_effort = max_control_effort
        
        # Control components
        self.feedback_loops: List[FeedbackLoop] = []
        self.control_signals: List[ControlSignal] = []
        self.stability_analyzer = StabilityAnalyzer()
        
        # Control state
        self.is_active = False
        self.control_step_count = 0
        self.total_control_time = 0.0
        
        # Thread safety
        self._lock = threading.Lock()
        
        print("EvolutionaryFeedbackController initialized")
    
    def initialize_feedback_loops(
        self,
        scales: List[str],
        initial_states: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Initialize feedback loops for the given scales.
        
        Args:
            scales: List of scale names
            initial_states: Initial states for each scale
            
        Returns:
            Initialization results
        """
        
        results = {
            'initialization_time': time.time(),
            'scales': scales,
            'loops_created': 0
        }
        
        try:
            # Create homeostatic feedback loops for each scale
            for scale in scales:
                if scale in initial_states:
                    state = initial_states[scale]
                    
                    # Create feedback loops for key variables
                    key_variables = ['fitness', 'diversity', 'mutation_rate']
                    
                    for variable in key_variables:
                        if variable in state:
                            loop_id = self._create_homeostatic_loop(
                                scale, variable, state[variable]
                            )
                            if loop_id:
                                results['loops_created'] += 1
            
            # Create cross-scale feedback loops
            cross_scale_loops = self._create_cross_scale_loops(scales, initial_states)
            results['cross_scale_loops'] = cross_scale_loops
            results['loops_created'] += cross_scale_loops
            
            self.is_active = True
            results['success'] = True
            
            print(f"Initialized {results['loops_created']} feedback loops across {len(scales)} scales")
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            print(f"Error initializing feedback loops: {e}")
        
        return results
    
    def _create_homeostatic_loop(
        self,
        scale: str,
        variable: str,
        target_value: float
    ) -> str:
        """Create a homeostatic feedback loop for a variable."""
        
        try:
            loop_id = f"homeostatic_{scale}_{variable}_{time.time()}"
            
            # Set appropriate gains based on variable type
            gains = FeedbackGain()
            
            if variable == 'fitness':
                gains.proportional_gain = 0.5
                gains.integral_gain = 0.05
                gains.derivative_gain = 0.01
            elif variable == 'diversity':
                gains.proportional_gain = 0.3
                gains.integral_gain = 0.03
                gains.derivative_gain = 0.005
            elif variable == 'mutation_rate':
                gains.proportional_gain = 0.1
                gains.integral_gain = 0.01
                gains.derivative_gain = 0.001
            
            feedback_loop = FeedbackLoop(
                loop_id=loop_id,
                feedback_type=FeedbackType.HOMEOSTATIC_FEEDBACK,
                source_scale=scale,
                target_scale=scale,
                control_variable=variable,
                reference_value=target_value,
                gains=gains
            )
            
            self.feedback_loops.append(feedback_loop)
            
            print(f"Created homeostatic loop for {scale}.{variable} (target: {target_value})")
            return loop_id
        
        except Exception as e:
            print(f"Error creating homeostatic loop: {e}")
            return ""
    
    def _create_cross_scale_loops(
        self,
        scales: List[str],
        initial_states: Dict[str, Any]
    ) -> int:
        """Create feedback loops between different scales."""
        
        loops_created = 0
        
        try:
            # Population -> Organismal feedback (selection pressure)
            if 'population' in scales and 'organismal' in scales:
                loop_id = f"cross_scale_population_organismal_{time.time()}"
                
                feedback_loop = FeedbackLoop(
                    loop_id=loop_id,
                    feedback_type=FeedbackType.ADAPTIVE_FEEDBACK,
                    source_scale='population',
                    target_scale='organismal',
                    control_variable='fitness',
                    reference_value=0.7,  # Target fitness
                    gains=FeedbackGain(
                        proportional_gain=0.2,
                        integral_gain=0.02,
                        derivative_gain=0.005
                    )
                )
                
                self.feedback_loops.append(feedback_loop)
                loops_created += 1
            
            # Ecosystem -> Population feedback (environmental pressure)
            if 'ecosystem' in scales and 'population' in scales:
                loop_id = f"cross_scale_ecosystem_population_{time.time()}"
                
                feedback_loop = FeedbackLoop(
                    loop_id=loop_id,
                    feedback_type=FeedbackType.NEGATIVE_FEEDBACK,
                    source_scale='ecosystem',
                    target_scale='population',
                    control_variable='population_size',
                    reference_value=1000.0,  # Target population size
                    gains=FeedbackGain(
                        proportional_gain=0.1,
                        integral_gain=0.01,
                        derivative_gain=0.002
                    )
                )
                
                self.feedback_loops.append(feedback_loop)
                loops_created += 1
            
            # Molecular -> Organismal feedback (gene expression)
            if 'molecular' in scales and 'organismal' in scales:
                loop_id = f"cross_scale_molecular_organismal_{time.time()}"
                
                feedback_loop = FeedbackLoop(
                    loop_id=loop_id,
                    feedback_type=FeedbackType.PREDICTIVE_FEEDBACK,
                    source_scale='molecular',
                    target_scale='organismal',
                    control_variable='gene_expression',
                    reference_value=0.5,  # Target expression level
                    gains=FeedbackGain(
                        proportional_gain=0.3,
                        integral_gain=0.03,
                        derivative_gain=0.01
                    )
                )
                
                self.feedback_loops.append(feedback_loop)
                loops_created += 1
        
        except Exception as e:
            print(f"Error creating cross-scale loops: {e}")
        
        return loops_created
    
    def apply_feedback(self, current_time: float, dt: float) -> Dict[str, Any]:
        """
        Apply feedback control to all active loops.
        
        Args:
            current_time: Current simulation time
            dt: Time step size
            
        Returns:
            Feedback application results
        """
        
        if not self.is_active:
            return {
                'success': False,
                'error': 'Feedback controller not active'
            }
        
        results = {
            'control_time': current_time,
            'dt': dt,
            'loops_processed': 0,
            'signals_generated': 0
        }
        
        try:
            with self._lock:
                new_control_signals = []
                
                for loop in self.feedback_loops:
                    if not loop.is_active:
                        continue
                    
                    # Calculate control signal
                    control_signal = self._calculate_control_signal(
                        loop, current_time, dt
                    )
                    
                    if control_signal:
                        new_control_signals.append(control_signal)
                        results['signals_generated'] += 1
                    
                    results['loops_processed'] += 1
                
                # Add new control signals
                self.control_signals.extend(new_control_signals)
                
                # Clean up old signals (keep only recent ones)
                cutoff_time = current_time - 10.0  # Keep signals from last 10 time units
                self.control_signals = [
                    signal for signal in self.control_signals
                    if signal.timestamp > cutoff_time
                ]
                
                # Adaptive gain adjustment
                if self.enable_adaptive_gains and self.control_step_count % 20 == 0:
                    adaptation_results = self._adapt_feedback_gains()
                    results['gain_adaptation'] = adaptation_results
            
            self.control_step_count += 1
            self.total_control_time += dt
            
            results['success'] = True
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            print(f"Error applying feedback: {e}")
        
        return results
    
    def _calculate_control_signal(
        self,
        loop: FeedbackLoop,
        current_time: float,
        dt: float
    ) -> Optional[ControlSignal]:
        """Calculate control signal for a feedback loop."""
        
        try:
            # For now, generate a mock control signal
            # In production, this would access actual system states
            
            # Mock current value (would come from actual system state)
            current_value = np.random.normal(loop.reference_value, 0.1)
            
            # Calculate error
            error = loop.reference_value - current_value
            
            # PID control calculation
            proportional = loop.gains.proportional_gain * error
            
            # Integral term
            loop.integral_sum += error * dt
            # Anti-windup
            loop.integral_sum = np.clip(
                loop.integral_sum,
                -loop.gains.saturation_limit,
                loop.gains.saturation_limit
            )
            integral = loop.gains.integral_gain * loop.integral_sum
            
            # Derivative term
            derivative = 0.0
            if loop.error_history:
                derivative = loop.gains.derivative_gain * (error - loop.last_error) / dt
            
            # Adaptive term
            adaptive = 0.0
            if len(loop.error_history) > 5:
                recent_errors = loop.error_history[-5:]
                error_trend = np.polyfit(range(5), recent_errors, 1)[0]
                adaptive = loop.gains.adaptive_gain * error_trend
            
            # Total control effort
            control_effort = proportional + integral + derivative + adaptive
            
            # Clamp control effort
            control_effort = np.clip(control_effort, -self.max_control_effort, self.max_control_effort)
            
            # Update loop history
            loop.error_history.append(error)
            loop.control_history.append(control_effort)
            loop.last_error = error
            loop.last_update = current_time
            
            # Limit history size
            if len(loop.error_history) > 100:
                loop.error_history = loop.error_history[-100:]
                loop.control_history = loop.control_history[-100:]
            
            # Create control signal
            direction = 'increase' if control_effort > 0 else 'decrease'
            if abs(control_effort) < 0.01:
                direction = 'maintain'
            
            control_signal = ControlSignal(
                signal_id=f"control_{loop.loop_id}_{current_time}",
                source_scale=loop.source_scale,
                target_scale=loop.target_scale,
                signal_type=loop.feedback_type.value,
                magnitude=abs(control_effort),
                direction=direction,
                priority=3 if abs(error) > 0.2 else 1  # High priority for large errors
            )
            
            return control_signal
        
        except Exception as e:
            print(f"Error calculating control signal for loop {loop.loop_id}: {e}")
            return None
    
    def _adapt_feedback_gains(self) -> Dict[str, Any]:
        """Adapt feedback gains based on control performance."""
        
        adaptation = {
            'adaptations_made': 0,
            'gain_changes': {}
        }
        
        try:
            for loop in self.feedback_loops:
                if len(loop.error_history) < 10:
                    continue
                
                # Analyze recent performance
                recent_errors = loop.error_history[-10:]
                recent_controls = loop.control_history[-10:]
                
                # Calculate performance metrics
                error_variance = np.var(recent_errors)
                control_variance = np.var(recent_controls)
                mean_abs_error = np.mean(np.abs(recent_errors))
                
                old_gains = {
                    'proportional': loop.gains.proportional_gain,
                    'integral': loop.gains.integral_gain,
                    'derivative': loop.gains.derivative_gain
                }
                
                # Adaptation rules
                adapted = False
                
                # If high error variance, reduce gains for stability
                if error_variance > 0.1:
                    loop.gains.proportional_gain *= 0.95
                    loop.gains.derivative_gain *= 0.9
                    adapted = True
                
                # If high control variance, reduce integral gain
                if control_variance > 0.5:
                    loop.gains.integral_gain *= 0.9
                    adapted = True
                
                # If persistent error, increase integral gain
                if mean_abs_error > 0.1 and error_variance < 0.05:
                    loop.gains.integral_gain *= 1.05
                    adapted = True
                
                # If oscillations detected, increase derivative gain
                if len(recent_errors) >= 6:
                    oscillation_score = self._detect_oscillations(recent_errors)
                    if oscillation_score > 0.7:
                        loop.gains.derivative_gain *= 1.1
                        adapted = True
                
                if adapted:
                    adaptation['adaptations_made'] += 1
                    adaptation['gain_changes'][loop.loop_id] = {
                        'old_gains': old_gains,
                        'new_gains': {
                            'proportional': loop.gains.proportional_gain,
                            'integral': loop.gains.integral_gain,
                            'derivative': loop.gains.derivative_gain
                        },
                        'performance_metrics': {
                            'error_variance': error_variance,
                            'control_variance': control_variance,
                            'mean_abs_error': mean_abs_error
                        }
                    }
        
        except Exception as e:
            adaptation['error'] = str(e)
        
        return adaptation
    
    def _detect_oscillations(self, error_sequence: List[float]) -> float:
        """Detect oscillations in error sequence."""
        
        try:
            if len(error_sequence) < 4:
                return 0.0
            
            # Simple oscillation detection: count sign changes
            sign_changes = 0
            for i in range(1, len(error_sequence)):
                if (error_sequence[i] > 0) != (error_sequence[i-1] > 0):
                    sign_changes += 1
            
            # Normalize by sequence length
            oscillation_score = sign_changes / (len(error_sequence) - 1)
            return oscillation_score
        
        except Exception:
            return 0.0
    
    def analyze_stability(self) -> Dict[str, Any]:
        """Analyze overall system stability."""
        
        if not self.is_active:
            return {
                'success': False,
                'error': 'Controller not active'
            }
        
        # Mock system states for stability analysis
        # In production, this would access actual system states
        mock_states = {}
        for scale in ['molecular', 'organismal', 'population', 'ecosystem']:
            mock_states[scale] = {
                'fitness': np.random.uniform(0.4, 0.9),
                'diversity': np.random.uniform(0.3, 0.8),
                'mutation_rate': np.random.uniform(0.005, 0.02)
            }
        
        return self.stability_analyzer.analyze_stability(mock_states)
    
    def get_controller_status(self) -> Dict[str, Any]:
        """Get comprehensive controller status."""
        
        status = {
            'timestamp': time.time(),
            'is_active': self.is_active,
            'control_steps': self.control_step_count,
            'total_control_time': self.total_control_time,
            'configuration': {
                'adaptive_gains_enabled': self.enable_adaptive_gains,
                'stability_threshold': self.stability_threshold,
                'max_control_effort': self.max_control_effort
            }
        }
        
        try:
            # Feedback loop statistics
            total_loops = len(self.feedback_loops)
            active_loops = len([loop for loop in self.feedback_loops if loop.is_active])
            
            status['feedback_loops'] = {
                'total': total_loops,
                'active': active_loops,
                'loop_types': {}
            }
            
            # Count loop types
            for loop in self.feedback_loops:
                loop_type = loop.feedback_type.value
                if loop_type not in status['feedback_loops']['loop_types']:
                    status['feedback_loops']['loop_types'][loop_type] = 0
                status['feedback_loops']['loop_types'][loop_type] += 1
            
            # Control signal statistics
            recent_signals = [
                signal for signal in self.control_signals
                if signal.timestamp > (time.time() - 5.0)  # Last 5 seconds
            ]
            
            status['control_signals'] = {
                'total_signals': len(self.control_signals),
                'recent_signals': len(recent_signals),
                'signal_types': {}
            }
            
            for signal in recent_signals:
                signal_type = signal.signal_type
                if signal_type not in status['control_signals']['signal_types']:
                    status['control_signals']['signal_types'][signal_type] = 0
                status['control_signals']['signal_types'][signal_type] += 1
            
            # Performance metrics
            if self.feedback_loops:
                # Average loop performance
                total_error = 0.0
                loops_with_history = 0
                
                for loop in self.feedback_loops:
                    if loop.error_history:
                        recent_error = np.mean(np.abs(loop.error_history[-5:]))
                        total_error += recent_error
                        loops_with_history += 1
                
                if loops_with_history > 0:
                    status['performance'] = {
                        'average_tracking_error': total_error / loops_with_history,
                        'loops_analyzed': loops_with_history
                    }
        
        except Exception as e:
            status['error'] = str(e)
        
        return status
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of feedback control system."""
        
        summary = {
            'timestamp': time.time(),
            'system_active': self.is_active,
            'total_loops': len(self.feedback_loops),
            'total_signals': len(self.control_signals)
        }
        
        try:
            # Loop summary by type
            loop_summary = {}
            for loop in self.feedback_loops:
                loop_type = loop.feedback_type.value
                if loop_type not in loop_summary:
                    loop_summary[loop_type] = {
                        'count': 0,
                        'active': 0,
                        'avg_error': 0.0
                    }
                
                loop_summary[loop_type]['count'] += 1
                
                if loop.is_active:
                    loop_summary[loop_type]['active'] += 1
                
                if loop.error_history:
                    recent_error = np.mean(np.abs(loop.error_history[-5:]))
                    loop_summary[loop_type]['avg_error'] += recent_error
            
            # Average errors
            for loop_type, data in loop_summary.items():
                if data['count'] > 0:
                    data['avg_error'] /= data['count']
            
            summary['loop_summary'] = loop_summary
            
            # Recent control activity
            recent_signals = [
                signal for signal in self.control_signals
                if signal.timestamp > (time.time() - 1.0)
            ]
            
            summary['recent_activity'] = {
                'signals_last_second': len(recent_signals),
                'control_intensity': np.mean([s.magnitude for s in recent_signals]) if recent_signals else 0.0
            }
        
        except Exception as e:
            summary['error'] = str(e)
        
        return summary

# Export main classes
__all__ = [
    'EvolutionaryFeedbackController',
    'FeedbackLoop',
    'FeedbackType',
    'ControlSignal',
    'FeedbackGain',
    'StabilityAnalyzer'
]
