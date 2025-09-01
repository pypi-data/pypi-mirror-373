"""
Cross-Scale Evolutionary Coupling Engine

Patent-pending system for modeling evolutionary processes across
multiple scales with dynamic coupling mechanisms.
"""

from typing import Dict, List, Any, Optional, Tuple, Union, Callable
import numpy as np
import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

class ScaleLevel(Enum):
    """Biological scale levels for evolutionary modeling."""
    
    MOLECULAR = "molecular"
    CELLULAR = "cellular"
    TISSUE = "tissue"
    ORGANISMAL = "organismal"
    POPULATION = "population"
    COMMUNITY = "community"
    ECOSYSTEM = "ecosystem"
    BIOSPHERE = "biosphere"

class CouplingType(Enum):
    """Types of cross-scale couplings."""
    
    UPWARD_CAUSATION = "upward_causation"        # Lower scale influences higher scale
    DOWNWARD_CAUSATION = "downward_causation"    # Higher scale constrains lower scale
    LATERAL_COUPLING = "lateral_coupling"        # Same-scale interactions
    EMERGENT_COUPLING = "emergent_coupling"      # Emergent properties coupling
    FEEDBACK_COUPLING = "feedback_coupling"      # Bidirectional feedback loops
    CONSTRAINT_COUPLING = "constraint_coupling"  # Constraint propagation

class CouplingStrength(Enum):
    """Predefined coupling strength levels."""
    
    WEAK = 0.1
    MODERATE = 0.3
    STRONG = 0.6
    VERY_STRONG = 0.9

@dataclass
class CrossScaleCoupling:
    """Represents a coupling between two scales."""
    
    coupling_id: str
    source_scale: ScaleLevel
    target_scale: ScaleLevel
    coupling_type: CouplingType
    strength: float
    coupling_function: Optional[Callable] = None
    is_active: bool = True
    creation_time: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if self.coupling_function is None:
            self.coupling_function = self._default_coupling_function
    
    def _default_coupling_function(self, source_state: Any, target_state: Any) -> Any:
        """Default linear coupling function."""
        try:
            if isinstance(source_state, dict) and isinstance(target_state, dict):
                # Simple state influence
                influence = {}
                for key in target_state:
                    if key in source_state:
                        try:
                            source_val = float(source_state[key])
                            target_val = float(target_state[key])
                            
                            # Apply coupling based on type
                            if self.coupling_type == CouplingType.UPWARD_CAUSATION:
                                influence[key] = target_val + self.strength * source_val * 0.1
                            elif self.coupling_type == CouplingType.DOWNWARD_CAUSATION:
                                influence[key] = target_val * (1 - self.strength * 0.1)
                            else:
                                influence[key] = target_val + self.strength * (source_val - target_val) * 0.1
                        except (ValueError, TypeError):
                            influence[key] = target_state[key]
                    else:
                        influence[key] = target_state[key]
                
                return influence
            
            return target_state
        
        except Exception:
            return target_state

@dataclass
class ScaleSpecificModel:
    """Model for a specific biological scale."""
    
    scale: ScaleLevel
    model_id: str
    state_dimension: int
    current_state: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, float] = field(default_factory=dict)
    evolution_function: Optional[Callable] = None
    is_active: bool = True
    creation_time: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if self.evolution_function is None:
            self.evolution_function = self._default_evolution_function
        
        # Initialize default state if empty
        if not self.current_state:
            self.current_state = self._initialize_default_state()
    
    def _initialize_default_state(self) -> Dict[str, Any]:
        """Initialize default state for the scale."""
        
        base_state = {
            'fitness': np.random.uniform(0.5, 1.0),
            'diversity': np.random.uniform(0.3, 0.8),
            'adaptation_rate': np.random.uniform(0.01, 0.1),
            'mutation_rate': np.random.uniform(0.001, 0.01),
            'population_size': np.random.randint(100, 10000),
            'energy_level': np.random.uniform(0.4, 0.9),
            'complexity': np.random.uniform(0.2, 0.7)
        }
        
        # Scale-specific additions
        if self.scale == ScaleLevel.MOLECULAR:
            base_state.update({
                'gene_expression': np.random.uniform(0.1, 1.0),
                'protein_concentration': np.random.uniform(0.2, 0.8),
                'metabolite_levels': np.random.uniform(0.1, 0.9)
            })
        elif self.scale == ScaleLevel.ORGANISMAL:
            base_state.update({
                'phenotype_score': np.random.uniform(0.3, 0.9),
                'developmental_stage': np.random.uniform(0.0, 1.0),
                'stress_response': np.random.uniform(0.1, 0.6)
            })
        elif self.scale == ScaleLevel.POPULATION:
            base_state.update({
                'allele_frequency': np.random.uniform(0.1, 0.9),
                'effective_population_size': np.random.randint(50, 5000),
                'migration_rate': np.random.uniform(0.001, 0.05)
            })
        elif self.scale == ScaleLevel.ECOSYSTEM:
            base_state.update({
                'species_richness': np.random.randint(10, 200),
                'resource_availability': np.random.uniform(0.2, 0.8),
                'environmental_stress': np.random.uniform(0.0, 0.5)
            })
        
        return base_state
    
    def _default_evolution_function(self, dt: float, external_influences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Default evolution function for the scale."""
        
        try:
            new_state = self.current_state.copy()
            
            # Basic evolutionary dynamics
            fitness = new_state.get('fitness', 0.5)
            diversity = new_state.get('diversity', 0.5)
            mutation_rate = new_state.get('mutation_rate', 0.01)
            
            # Apply basic evolution
            fitness_change = (np.random.normal(0, 0.01) + 
                            diversity * 0.02 - 
                            abs(fitness - 0.7) * 0.01) * dt
            
            new_state['fitness'] = max(0.0, min(1.0, fitness + fitness_change))
            
            # Diversity evolution
            diversity_change = (mutation_rate * 0.5 - 
                              diversity * 0.01 + 
                              np.random.normal(0, 0.005)) * dt
            
            new_state['diversity'] = max(0.0, min(1.0, diversity + diversity_change))
            
            # Apply external influences
            if external_influences:
                for key, influence in external_influences.items():
                    if key in new_state:
                        try:
                            current_val = float(new_state[key])
                            influence_val = float(influence)
                            new_state[key] = current_val + influence_val * dt
                        except (ValueError, TypeError):
                            continue
            
            return new_state
        
        except Exception as e:
            print(f"Warning: Error in evolution function: {e}")
            return self.current_state
    
    def evolve_step(self, dt: float, external_influences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Evolve the model by one time step."""
        
        try:
            new_state = self.evolution_function(dt, external_influences)
            self.current_state = new_state
            return new_state
        
        except Exception as e:
            print(f"Error evolving {self.scale} model: {e}")
            return self.current_state

class CouplingValidator:
    """Validates coupling configurations and stability."""
    
    def __init__(self):
        self.validation_rules = {
            'max_coupling_strength': 1.0,
            'min_coupling_strength': 0.0,
            'max_couplings_per_scale': 10,
            'forbidden_self_loops': True
        }
    
    def validate_coupling(self, coupling: CrossScaleCoupling) -> Dict[str, Any]:
        """Validate a single coupling configuration."""
        
        validation = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        try:
            # Check coupling strength
            if coupling.strength > self.validation_rules['max_coupling_strength']:
                validation['errors'].append(
                    f"Coupling strength {coupling.strength} exceeds maximum"
                )
                validation['is_valid'] = False
            
            if coupling.strength < self.validation_rules['min_coupling_strength']:
                validation['errors'].append(
                    f"Coupling strength {coupling.strength} below minimum"
                )
                validation['is_valid'] = False
            
            # Check for self-loops
            if (self.validation_rules['forbidden_self_loops'] and 
                coupling.source_scale == coupling.target_scale):
                validation['errors'].append(
                    "Self-loop couplings are forbidden"
                )
                validation['is_valid'] = False
            
            # Type-specific validations
            if coupling.coupling_type == CouplingType.UPWARD_CAUSATION:
                if coupling.source_scale.value >= coupling.target_scale.value:
                    validation['warnings'].append(
                        "Upward causation should go from lower to higher scales"
                    )
            
            elif coupling.coupling_type == CouplingType.DOWNWARD_CAUSATION:
                if coupling.source_scale.value <= coupling.target_scale.value:
                    validation['warnings'].append(
                        "Downward causation should go from higher to lower scales"
                    )
        
        except Exception as e:
            validation['errors'].append(f"Validation error: {e}")
            validation['is_valid'] = False
        
        return validation
    
    def validate_coupling_network(self, couplings: List[CrossScaleCoupling]) -> Dict[str, Any]:
        """Validate entire coupling network."""
        
        network_validation = {
            'is_stable': True,
            'coupling_count': len(couplings),
            'scale_degrees': {},
            'warnings': [],
            'errors': []
        }
        
        try:
            # Count couplings per scale
            scale_counts = {}
            for coupling in couplings:
                source = coupling.source_scale.value
                target = coupling.target_scale.value
                
                scale_counts[source] = scale_counts.get(source, 0) + 1
                scale_counts[target] = scale_counts.get(target, 0) + 1
            
            network_validation['scale_degrees'] = scale_counts
            
            # Check for over-coupled scales
            max_couplings = self.validation_rules['max_couplings_per_scale']
            for scale, count in scale_counts.items():
                if count > max_couplings:
                    network_validation['warnings'].append(
                        f"Scale {scale} has {count} couplings (max recommended: {max_couplings})"
                    )
            
            # Check for isolated scales
            all_scales = set(scale.value for scale in ScaleLevel)
            coupled_scales = set(scale_counts.keys())
            isolated_scales = all_scales - coupled_scales
            
            if isolated_scales:
                network_validation['warnings'].append(
                    f"Isolated scales detected: {isolated_scales}"
                )
            
            # Stability analysis (simplified)
            total_coupling_strength = sum(c.strength for c in couplings)
            avg_coupling_strength = total_coupling_strength / len(couplings) if couplings else 0
            
            if avg_coupling_strength > 0.8:
                network_validation['warnings'].append(
                    "High average coupling strength may cause instability"
                )
                network_validation['is_stable'] = False
        
        except Exception as e:
            network_validation['errors'].append(f"Network validation error: {e}")
            network_validation['is_stable'] = False
        
        return network_validation

class CrossScaleEvolutionaryCouplingEngine:
    """
    Patent Feature: Advanced coupling engine for multi-scale evolutionary modeling.
    
    Implements dynamic cross-scale couplings with adaptive strength,
    emergence detection, and stability control for biological systems.
    """
    
    def __init__(
        self,
        scales: List[str] = None,
        default_coupling_strength: float = 0.5,
        enable_adaptive_coupling: bool = True,
        stability_threshold: float = 0.8
    ):
        """
        Initialize the cross-scale coupling engine.
        
        Args:
            scales: List of scale names to couple
            default_coupling_strength: Default strength for new couplings
            enable_adaptive_coupling: Enable adaptive coupling strength
            stability_threshold: Threshold for stability warnings
        """
        self.scales = scales or ['molecular', 'organismal', 'population', 'ecosystem']
        self.default_coupling_strength = default_coupling_strength
        self.enable_adaptive_coupling = enable_adaptive_coupling
        self.stability_threshold = stability_threshold
        
        # Core components
        self.scale_models: Dict[str, ScaleSpecificModel] = {}
        self.couplings: List[CrossScaleCoupling] = []
        self.coupling_validator = CouplingValidator()
        
        # System state
        self.is_active = False
        self.evolution_step_count = 0
        self.total_evolution_time = 0.0
        self.coupling_history = []
        
        # Thread safety
        self._lock = threading.Lock()
        
        print(f"CrossScaleEvolutionaryCouplingEngine initialized for scales: {self.scales}")
    
    def register_scale_model(
        self,
        scale_name: str,
        initial_state: Dict[str, Any],
        evolution_function: Optional[Callable] = None
    ) -> bool:
        """
        Register a model for a specific scale.
        
        Args:
            scale_name: Name of the scale
            initial_state: Initial state for the scale
            evolution_function: Custom evolution function
            
        Returns:
            Success status
        """
        
        try:
            # Map scale name to ScaleLevel
            scale_level = None
            for level in ScaleLevel:
                if level.value == scale_name.lower():
                    scale_level = level
                    break
            
            if scale_level is None:
                print(f"Warning: Unknown scale level {scale_name}, using molecular")
                scale_level = ScaleLevel.MOLECULAR
            
            # Create scale model
            model = ScaleSpecificModel(
                scale=scale_level,
                model_id=f"{scale_name}_model",
                state_dimension=len(initial_state),
                current_state=initial_state.copy(),
                evolution_function=evolution_function
            )
            
            with self._lock:
                self.scale_models[scale_name] = model
            
            print(f"Registered {scale_name} scale model with {len(initial_state)} state variables")
            return True
        
        except Exception as e:
            print(f"Error registering scale model for {scale_name}: {e}")
            return False
    
    def add_coupling(
        self,
        source_scale: str,
        target_scale: str,
        strength: float,
        coupling_type: str = 'upward_causation',
        coupling_function: Optional[Callable] = None
    ) -> str:
        """
        Add a coupling between two scales.
        
        Args:
            source_scale: Source scale name
            target_scale: Target scale name
            strength: Coupling strength (0.0 to 1.0)
            coupling_type: Type of coupling
            coupling_function: Custom coupling function
            
        Returns:
            Coupling ID
        """
        
        try:
            # Map coupling type
            coupling_type_enum = CouplingType.UPWARD_CAUSATION
            for ct in CouplingType:
                if ct.value == coupling_type.lower():
                    coupling_type_enum = ct
                    break
            
            # Map scale names
            source_level = ScaleLevel.MOLECULAR
            target_level = ScaleLevel.ORGANISMAL
            
            for level in ScaleLevel:
                if level.value == source_scale.lower():
                    source_level = level
                if level.value == target_scale.lower():
                    target_level = level
            
            # Create coupling
            coupling_id = f"{source_scale}_{target_scale}_{coupling_type}_{time.time()}"
            
            coupling = CrossScaleCoupling(
                coupling_id=coupling_id,
                source_scale=source_level,
                target_scale=target_level,
                coupling_type=coupling_type_enum,
                strength=strength,
                coupling_function=coupling_function
            )
            
            # Validate coupling
            validation = self.coupling_validator.validate_coupling(coupling)
            if not validation['is_valid']:
                print(f"Warning: Invalid coupling: {validation['errors']}")
                return ""
            
            with self._lock:
                self.couplings.append(coupling)
            
            print(f"Added {coupling_type} coupling: {source_scale} -> {target_scale} (strength: {strength})")
            return coupling_id
        
        except Exception as e:
            print(f"Error adding coupling: {e}")
            return ""
    
    def configure_couplings(self, configuration: Dict[str, Any]) -> bool:
        """
        Configure multiple couplings from a configuration dictionary.
        
        Args:
            configuration: Coupling configuration
            
        Returns:
            Success status
        """
        
        try:
            couplings_added = 0
            
            for coupling_config in configuration.get('couplings', []):
                coupling_id = self.add_coupling(
                    source_scale=coupling_config['source'],
                    target_scale=coupling_config['target'],
                    strength=coupling_config.get('strength', self.default_coupling_strength),
                    coupling_type=coupling_config.get('type', 'upward_causation')
                )
                
                if coupling_id:
                    couplings_added += 1
            
            print(f"Configured {couplings_added} couplings from configuration")
            return couplings_added > 0
        
        except Exception as e:
            print(f"Error configuring couplings: {e}")
            return False
    
    def activate_couplings(self) -> Dict[str, Any]:
        """Activate all registered couplings."""
        
        try:
            activation_results = {
                'activation_time': time.time(),
                'total_couplings': len(self.couplings),
                'active_couplings': 0,
                'failed_couplings': 0,
                'scale_models': len(self.scale_models)
            }
            
            # Validate coupling network
            network_validation = self.coupling_validator.validate_coupling_network(self.couplings)
            activation_results['network_validation'] = network_validation
            
            if not network_validation['is_stable']:
                print("Warning: Coupling network may be unstable")
            
            # Activate individual couplings
            for coupling in self.couplings:
                if coupling.is_active:
                    activation_results['active_couplings'] += 1
                else:
                    activation_results['failed_couplings'] += 1
            
            self.is_active = True
            activation_results['system_active'] = True
            
            print(f"Activated {activation_results['active_couplings']} couplings across {len(self.scale_models)} scales")
            return activation_results
        
        except Exception as e:
            print(f"Error activating couplings: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def evolve_step(self, dt: float) -> Dict[str, Any]:
        """
        Evolve all coupled scales by one time step.
        
        Args:
            dt: Time step size
            
        Returns:
            Evolution step results
        """
        
        if not self.is_active:
            return {
                'success': False,
                'error': 'Coupling engine not activated'
            }
        
        step_results = {
            'step': self.evolution_step_count,
            'dt': dt,
            'timestamp': time.time()
        }
        
        try:
            with self._lock:
                # Calculate cross-scale influences
                scale_influences = {}
                for scale_name in self.scale_models:
                    scale_influences[scale_name] = {}
                
                # Apply couplings
                for coupling in self.couplings:
                    if not coupling.is_active:
                        continue
                    
                    source_scale_name = coupling.source_scale.value
                    target_scale_name = coupling.target_scale.value
                    
                    # Find corresponding models
                    source_model = None
                    target_model = None
                    
                    for name, model in self.scale_models.items():
                        if model.scale.value == source_scale_name:
                            source_model = model
                        if model.scale.value == target_scale_name:
                            target_model = model
                    
                    if source_model and target_model:
                        # Calculate coupling influence
                        influence = coupling.coupling_function(
                            source_model.current_state,
                            target_model.current_state
                        )
                        
                        # Accumulate influences
                        target_name = target_scale_name
                        for model_name, model in self.scale_models.items():
                            if model.scale.value == target_scale_name:
                                target_name = model_name
                                break
                        
                        if target_name not in scale_influences:
                            scale_influences[target_name] = {}
                        
                        # Merge influences
                        for key, value in influence.items():
                            if key in scale_influences[target_name]:
                                scale_influences[target_name][key] += value
                            else:
                                scale_influences[target_name][key] = value
                
                # Evolve each scale with influences
                scale_states = {}
                for scale_name, model in self.scale_models.items():
                    influences = scale_influences.get(scale_name, {})
                    new_state = model.evolve_step(dt, influences)
                    scale_states[scale_name] = new_state
                
                step_results['scale_states'] = scale_states
                step_results['influences_applied'] = len([
                    name for name, influences in scale_influences.items() 
                    if influences
                ])
            
            # Update step counter
            self.evolution_step_count += 1
            self.total_evolution_time += dt
            
            # Adaptive coupling adjustment
            if self.enable_adaptive_coupling and self.evolution_step_count % 10 == 0:
                adaptation_results = self._adapt_coupling_strengths()
                step_results['coupling_adaptation'] = adaptation_results
            
            step_results['success'] = True
            
        except Exception as e:
            step_results['success'] = False
            step_results['error'] = str(e)
            print(f"Error in coupling evolution step: {e}")
        
        return step_results
    
    def _adapt_coupling_strengths(self) -> Dict[str, Any]:
        """Adapt coupling strengths based on system behavior."""
        
        adaptation = {
            'adaptations_made': 0,
            'strength_changes': {}
        }
        
        try:
            # Simple adaptation: reduce strength if system becomes unstable
            # In production, this would be much more sophisticated
            
            for coupling in self.couplings:
                if not coupling.is_active:
                    continue
                
                # Get source and target model states
                source_model = None
                target_model = None
                
                for model in self.scale_models.values():
                    if model.scale == coupling.source_scale:
                        source_model = model
                    if model.scale == coupling.target_scale:
                        target_model = model
                
                if source_model and target_model:
                    # Check for instability indicators
                    source_fitness = source_model.current_state.get('fitness', 0.5)
                    target_fitness = target_model.current_state.get('fitness', 0.5)
                    
                    # If either scale has very low fitness, reduce coupling
                    if source_fitness < 0.1 or target_fitness < 0.1:
                        old_strength = coupling.strength
                        coupling.strength *= 0.95  # Reduce by 5%
                        coupling.strength = max(0.01, coupling.strength)  # Minimum strength
                        
                        adaptation['adaptations_made'] += 1
                        adaptation['strength_changes'][coupling.coupling_id] = {
                            'old_strength': old_strength,
                            'new_strength': coupling.strength,
                            'reason': 'low_fitness_stabilization'
                        }
                        
                        coupling.last_update = time.time()
        
        except Exception as e:
            adaptation['error'] = str(e)
        
        return adaptation
    
    def apply_scale_perturbation(
        self,
        scale_name: str,
        perturbation_magnitude: float = 0.1
    ) -> Dict[str, Any]:
        """
        Apply a perturbation to a specific scale.
        
        Args:
            scale_name: Name of scale to perturb
            perturbation_magnitude: Magnitude of perturbation
            
        Returns:
            Perturbation results
        """
        
        results = {
            'perturbation_time': time.time(),
            'target_scale': scale_name,
            'magnitude': perturbation_magnitude
        }
        
        try:
            if scale_name not in self.scale_models:
                results['success'] = False
                results['error'] = f"Scale {scale_name} not found"
                return results
            
            model = self.scale_models[scale_name]
            
            # Apply random perturbations to state variables
            perturbed_state = model.current_state.copy()
            perturbations_applied = {}
            
            for key, value in perturbed_state.items():
                try:
                    numeric_value = float(value)
                    perturbation = np.random.normal(0, perturbation_magnitude)
                    new_value = numeric_value + perturbation
                    
                    # Keep values in reasonable bounds
                    if key in ['fitness', 'diversity']:
                        new_value = max(0.0, min(1.0, new_value))
                    elif key in ['mutation_rate', 'adaptation_rate']:
                        new_value = max(0.001, min(0.1, new_value))
                    elif key.endswith('_size'):
                        new_value = max(1, int(new_value))
                    
                    perturbed_state[key] = new_value
                    perturbations_applied[key] = {
                        'original': numeric_value,
                        'perturbation': perturbation,
                        'new_value': new_value
                    }
                
                except (ValueError, TypeError):
                    continue
            
            # Update model state
            model.current_state = perturbed_state
            
            results['perturbations_applied'] = perturbations_applied
            results['success'] = True
            
        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            print(f"Error applying perturbation to {scale_name}: {e}")
        
        return results
    
    def get_scale_state(self, scale_name: str) -> Dict[str, Any]:
        """Get current state of a specific scale."""
        
        try:
            if scale_name in self.scale_models:
                model = self.scale_models[scale_name]
                return {
                    'scale': scale_name,
                    'state': model.current_state.copy(),
                    'model_id': model.model_id,
                    'is_active': model.is_active,
                    'state_dimension': model.state_dimension
                }
            else:
                return {
                    'scale': scale_name,
                    'error': 'Scale not found'
                }
        
        except Exception as e:
            return {
                'scale': scale_name,
                'error': str(e)
            }
    
    def get_active_couplings(self) -> List[Dict[str, Any]]:
        """Get information about all active couplings."""
        
        try:
            active_couplings = []
            
            for coupling in self.couplings:
                if coupling.is_active:
                    coupling_info = {
                        'coupling_id': coupling.coupling_id,
                        'source_scale': coupling.source_scale.value,
                        'target_scale': coupling.target_scale.value,
                        'coupling_type': coupling.coupling_type.value,
                        'strength': coupling.strength,
                        'age': time.time() - coupling.creation_time,
                        'last_update': coupling.last_update
                    }
                    active_couplings.append(coupling_info)
            
            return active_couplings
        
        except Exception as e:
            print(f"Error getting active couplings: {e}")
            return []
    
    def get_coupling_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of the coupling system."""
        
        summary = {
            'timestamp': time.time(),
            'system_active': self.is_active,
            'evolution_steps': self.evolution_step_count,
            'total_evolution_time': self.total_evolution_time,
            'statistics': {}
        }
        
        try:
            # Coupling statistics
            total_couplings = len(self.couplings)
            active_couplings = len([c for c in self.couplings if c.is_active])
            
            summary['statistics'] = {
                'total_couplings': total_couplings,
                'active_couplings': active_couplings,
                'registered_scales': len(self.scale_models),
                'avg_coupling_strength': np.mean([c.strength for c in self.couplings]) if self.couplings else 0.0
            }
            
            # Scale model summary
            scale_summary = {}
            for name, model in self.scale_models.items():
                scale_summary[name] = {
                    'state_dimension': model.state_dimension,
                    'is_active': model.is_active,
                    'current_fitness': model.current_state.get('fitness', 'unknown')
                }
            
            summary['scale_models'] = scale_summary
            
            # Coupling type distribution
            coupling_types = {}
            for coupling in self.couplings:
                ct = coupling.coupling_type.value
                coupling_types[ct] = coupling_types.get(ct, 0) + 1
            
            summary['coupling_type_distribution'] = coupling_types
            
        except Exception as e:
            summary['error'] = str(e)
        
        return summary

# Export main classes
__all__ = [
    'CrossScaleEvolutionaryCouplingEngine',
    'ScaleLevel',
    'CouplingType',
    'CouplingStrength',
    'CrossScaleCoupling',
    'ScaleSpecificModel',
    'CouplingValidator'
]
