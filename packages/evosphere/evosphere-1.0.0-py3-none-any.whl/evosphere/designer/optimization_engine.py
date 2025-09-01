"""
Multi-Objective Optimization Engine

Implements genetic algorithms, simulated annealing, and Pareto optimization
for evolutionary pathway design with biological constraints.
"""

from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np
import logging
from abc import ABC, abstractmethod
import math
import random
from collections import defaultdict

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of optimization algorithms."""
    
    GENETIC_ALGORITHM = auto()
    SIMULATED_ANNEALING = auto()
    PARTICLE_SWARM = auto()
    DIFFERENTIAL_EVOLUTION = auto()
    NSGA_II = auto()  # Multi-objective
    SPEA2 = auto()   # Multi-objective


@dataclass
class OptimizationObjective:
    """Single optimization objective."""
    
    name: str
    weight: float
    minimize: bool = False
    target_value: Optional[float] = None
    tolerance: float = 0.01
    constraint_func: Optional[Callable[[Any], bool]] = None
    
    def evaluate(self, value: float) -> float:
        """Evaluate objective value."""
        
        if self.target_value is not None:
            # Distance from target
            distance = abs(value - self.target_value)
            score = max(0.0, 1.0 - distance / max(self.tolerance, 1e-6))
        else:
            # Raw value optimization
            score = value if not self.minimize else 1.0 - value
        
        return self.weight * score


@dataclass
class OptimizationSolution:
    """Single solution in optimization space."""
    
    parameters: Dict[str, Any]
    objectives: Dict[str, float]
    constraints: Dict[str, bool]
    fitness: float = 0.0
    rank: int = 0
    crowding_distance: float = 0.0
    
    def dominates(self, other: 'OptimizationSolution') -> bool:
        """Check if this solution dominates another (Pareto dominance)."""
        
        better_in_any = False
        worse_in_any = False
        
        for obj_name, obj_value in self.objectives.items():
            other_value = other.objectives.get(obj_name, 0.0)
            
            if obj_value > other_value:
                better_in_any = True
            elif obj_value < other_value:
                worse_in_any = True
        
        return better_in_any and not worse_in_any


class PathwayOptimizer(ABC):
    """
    Abstract base class for pathway optimization algorithms.
    
    Patent Feature: Pluggable optimization framework for evolutionary
    pathways with biological constraint integration.
    """
    
    def __init__(self, objectives: List[OptimizationObjective]):
        """Initialize optimizer."""
        
        self.objectives = objectives
        self.optimization_history: List[Dict[str, Any]] = []
        
    @abstractmethod
    def optimize(
        self,
        initial_solution: Dict[str, Any],
        max_iterations: int = 1000,
        convergence_tolerance: float = 1e-6
    ) -> Dict[str, Any]:
        """
        Optimize pathway parameters.
        
        Args:
            initial_solution: Starting parameter values
            max_iterations: Maximum optimization iterations
            convergence_tolerance: Convergence tolerance
            
        Returns:
            Optimization results
        """
        pass
    
    def evaluate_solution(self, parameters: Dict[str, Any]) -> OptimizationSolution:
        """Evaluate single solution."""
        
        solution = OptimizationSolution(
            parameters=parameters.copy(),
            objectives={},
            constraints={}
        )
        
        # Evaluate objectives
        total_fitness = 0.0
        total_weight = sum(obj.weight for obj in self.objectives)
        
        for objective in self.objectives:
            if objective.name in parameters:
                value = parameters[objective.name]
                obj_score = objective.evaluate(value)
                
                solution.objectives[objective.name] = value
                total_fitness += obj_score
            
            # Check constraints
            if objective.constraint_func:
                solution.constraints[objective.name] = objective.constraint_func(parameters)
        
        solution.fitness = total_fitness / max(total_weight, 1e-6)
        
        return solution


class GeneticAlgorithmOptimizer(PathwayOptimizer):
    """
    Genetic algorithm optimizer for evolutionary pathways.
    
    Patent Feature: Specialized GA with biological mutation operators
    and evolutionary constraint handling.
    """
    
    def __init__(
        self,
        objectives: List[OptimizationObjective],
        population_size: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elite_ratio: float = 0.1
    ):
        """Initialize genetic algorithm optimizer."""
        
        super().__init__(objectives)
        
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_ratio = elite_ratio
        
        logger.info("Genetic algorithm optimizer initialized")
    
    def optimize(
        self,
        initial_solution: Dict[str, Any],
        max_iterations: int = 1000,
        convergence_tolerance: float = 1e-6
    ) -> Dict[str, Any]:
        """Optimize using genetic algorithm."""
        
        # Initialize population
        population = self._initialize_population(initial_solution)
        
        best_fitness_history = []
        avg_fitness_history = []
        best_solution = None
        best_fitness = -float('inf')
        
        for generation in range(max_iterations):
            # Evaluate population
            evaluated_pop = [self.evaluate_solution(ind) for ind in population]
            
            # Track statistics
            fitnesses = [sol.fitness for sol in evaluated_pop]
            current_best = max(fitnesses)
            current_avg = np.mean(fitnesses)
            
            best_fitness_history.append(current_best)
            avg_fitness_history.append(current_avg)
            
            # Update best solution
            if current_best > best_fitness:
                best_fitness = current_best
                best_idx = np.argmax(fitnesses)
                best_solution = evaluated_pop[best_idx]
            
            # Check convergence
            if (len(best_fitness_history) > 10 and
                abs(best_fitness_history[-1] - best_fitness_history[-10]) < convergence_tolerance):
                logger.info(f"GA converged at generation {generation}")
                break
            
            # Evolution step
            population = self._evolve_population(evaluated_pop)
            
            if generation % 100 == 0:
                logger.debug(f"GA generation {generation}, best fitness: {current_best:.4f}")
        
        # Prepare results
        results = {
            'best_solution': best_solution.parameters if best_solution else initial_solution,
            'best_fitness': best_fitness,
            'optimization_history': {
                'best_fitness': best_fitness_history,
                'avg_fitness': avg_fitness_history
            },
            'generations': generation + 1,
            'converged': len(best_fitness_history) > 10
        }
        
        self.optimization_history.append(results)
        
        return results
    
    def _initialize_population(self, initial_solution: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Initialize GA population."""
        
        population = [initial_solution.copy()]
        
        # Create variations of initial solution
        for _ in range(self.population_size - 1):
            individual = self._mutate_parameters(initial_solution, self.mutation_rate * 2)
            population.append(individual)
        
        return population
    
    def _evolve_population(
        self, 
        evaluated_population: List[OptimizationSolution]
    ) -> List[Dict[str, Any]]:
        """Evolve population for next generation."""
        
        # Sort by fitness
        evaluated_population.sort(key=lambda x: x.fitness, reverse=True)
        
        # Elite selection
        elite_size = max(1, int(self.population_size * self.elite_ratio))
        elite = [sol.parameters for sol in evaluated_population[:elite_size]]
        
        # Create next generation
        next_population = elite.copy()
        
        # Fill rest with crossover and mutation
        while len(next_population) < self.population_size:
            # Selection for reproduction
            parent1 = self._tournament_selection(evaluated_population)
            parent2 = self._tournament_selection(evaluated_population)
            
            # Crossover
            if np.random.random() < self.crossover_rate:
                child = self._crossover(parent1.parameters, parent2.parameters)
            else:
                child = parent1.parameters.copy()
            
            # Mutation
            if np.random.random() < self.mutation_rate:
                child = self._mutate_parameters(child, self.mutation_rate)
            
            next_population.append(child)
        
        return next_population[:self.population_size]
    
    def _tournament_selection(
        self, 
        population: List[OptimizationSolution],
        tournament_size: int = 3
    ) -> OptimizationSolution:
        """Tournament selection for reproduction."""
        
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness)
    
    def _crossover(
        self, 
        parent1: Dict[str, Any], 
        parent2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crossover two parameter sets."""
        
        child = {}
        
        for param in parent1:
            if param in parent2:
                # Blend crossover for numerical parameters
                if isinstance(parent1[param], (int, float)):
                    alpha = np.random.random()
                    child[param] = alpha * parent1[param] + (1 - alpha) * parent2[param]
                else:
                    # Random choice for non-numerical
                    child[param] = random.choice([parent1[param], parent2[param]])
            else:
                child[param] = parent1[param]
        
        return child
    
    def _mutate_parameters(
        self, 
        parameters: Dict[str, Any], 
        mutation_rate: float
    ) -> Dict[str, Any]:
        """Mutate parameter values."""
        
        mutated = parameters.copy()
        
        for param, value in parameters.items():
            if np.random.random() < mutation_rate:
                if isinstance(value, float):
                    # Gaussian mutation
                    mutated[param] = value + np.random.normal(0, abs(value) * 0.1 + 1e-6)
                elif isinstance(value, int):
                    # Integer mutation
                    mutated[param] = max(1, value + np.random.randint(-2, 3))
                elif isinstance(value, str):
                    # String mutation (for categorical parameters)
                    pass  # Would implement categorical mutation
        
        return mutated


class SimulatedAnnealingOptimizer(PathwayOptimizer):
    """
    Simulated annealing optimizer for pathway design.
    
    Patent Feature: Temperature-controlled optimization with biological
    cooling schedules and constraint-aware acceptance criteria.
    """
    
    def __init__(
        self,
        objectives: List[OptimizationObjective],
        initial_temperature: float = 100.0,
        cooling_rate: float = 0.95,
        min_temperature: float = 1e-6
    ):
        """Initialize simulated annealing optimizer."""
        
        super().__init__(objectives)
        
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature
        
        logger.info("Simulated annealing optimizer initialized")
    
    def optimize(
        self,
        initial_solution: Dict[str, Any],
        max_iterations: int = 1000,
        convergence_tolerance: float = 1e-6
    ) -> Dict[str, Any]:
        """Optimize using simulated annealing."""
        
        current_solution = initial_solution.copy()
        current_eval = self.evaluate_solution(current_solution)
        
        best_solution = current_solution.copy()
        best_fitness = current_eval.fitness
        
        temperature = self.initial_temperature
        
        fitness_history = []
        temperature_history = []
        acceptance_history = []
        
        for iteration in range(max_iterations):
            # Generate neighbor solution
            neighbor = self._generate_neighbor(current_solution, temperature)
            neighbor_eval = self.evaluate_solution(neighbor)
            
            # Calculate acceptance probability
            delta_fitness = neighbor_eval.fitness - current_eval.fitness
            
            if delta_fitness > 0:
                # Better solution - always accept
                acceptance_prob = 1.0
            else:
                # Worse solution - accept with probability
                acceptance_prob = np.exp(delta_fitness / temperature) if temperature > 0 else 0.0
            
            # Accept or reject
            accept = np.random.random() < acceptance_prob
            
            if accept:
                current_solution = neighbor
                current_eval = neighbor_eval
            
            # Update best solution
            if neighbor_eval.fitness > best_fitness:
                best_solution = neighbor.copy()
                best_fitness = neighbor_eval.fitness
            
            # Cool temperature
            temperature *= self.cooling_rate
            temperature = max(temperature, self.min_temperature)
            
            # Record history
            fitness_history.append(current_eval.fitness)
            temperature_history.append(temperature)
            acceptance_history.append(accept)
            
            # Check convergence
            if (len(fitness_history) > 100 and
                np.std(fitness_history[-50:]) < convergence_tolerance):
                logger.info(f"SA converged at iteration {iteration}")
                break
            
            if iteration % 100 == 0:
                logger.debug(f"SA iteration {iteration}, fitness: {current_eval.fitness:.4f}, T: {temperature:.4f}")
        
        # Prepare results
        results = {
            'best_solution': best_solution,
            'best_fitness': best_fitness,
            'optimization_history': {
                'fitness': fitness_history,
                'temperature': temperature_history,
                'acceptance_rate': np.mean(acceptance_history[-100:]) if acceptance_history else 0.0
            },
            'iterations': iteration + 1,
            'final_temperature': temperature
        }
        
        self.optimization_history.append(results)
        
        return results
    
    def _generate_neighbor(
        self, 
        solution: Dict[str, Any], 
        temperature: float
    ) -> Dict[str, Any]:
        """Generate neighbor solution."""
        
        neighbor = solution.copy()
        
        # Choose parameter to modify
        param_names = list(solution.keys())
        if not param_names:
            return neighbor
        
        param_name = random.choice(param_names)
        current_value = solution[param_name]
        
        if isinstance(current_value, float):
            # Gaussian perturbation scaled by temperature
            perturbation_scale = temperature / self.initial_temperature
            noise = np.random.normal(0, abs(current_value) * 0.1 * perturbation_scale + 1e-6)
            neighbor[param_name] = current_value + noise
            
        elif isinstance(current_value, int):
            # Integer perturbation
            max_change = max(1, int(temperature / self.initial_temperature * 5))
            change = np.random.randint(-max_change, max_change + 1)
            neighbor[param_name] = max(1, current_value + change)
        
        return neighbor


class MultiObjectiveOptimizer(PathwayOptimizer):
    """
    Multi-objective optimizer using NSGA-II algorithm.
    
    Patent Feature: Pareto-optimal pathway design with biological
    trade-off analysis and solution diversity maintenance.
    """
    
    def __init__(
        self,
        objectives: List[OptimizationObjective],
        population_size: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.9
    ):
        """Initialize multi-objective optimizer."""
        
        super().__init__(objectives)
        
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
        logger.info("Multi-objective NSGA-II optimizer initialized")
    
    def optimize(
        self,
        initial_solution: Dict[str, Any],
        max_iterations: int = 1000,
        convergence_tolerance: float = 1e-6
    ) -> Dict[str, Any]:
        """Optimize using NSGA-II algorithm."""
        
        # Initialize population
        population = self._initialize_population(initial_solution)
        
        pareto_history = []
        diversity_history = []
        
        for generation in range(max_iterations):
            # Evaluate population
            evaluated_pop = [self.evaluate_solution(ind) for ind in population]
            
            # Fast non-dominated sorting
            fronts = self._fast_non_dominated_sort(evaluated_pop)
            
            # Calculate crowding distances
            for front in fronts:
                self._calculate_crowding_distance(front)
            
            # Track Pareto front
            pareto_front = fronts[0] if fronts else []
            pareto_history.append(len(pareto_front))
            
            # Calculate diversity
            diversity = self._calculate_diversity(evaluated_pop)
            diversity_history.append(diversity)
            
            # Check convergence
            if (len(pareto_history) > 20 and
                np.std(pareto_history[-10:]) < 0.1):
                logger.info(f"NSGA-II converged at generation {generation}")
                break
            
            # Create next generation
            next_population = self._create_next_generation(evaluated_pop)
            population = [sol.parameters for sol in next_population]
            
            if generation % 50 == 0:
                logger.debug(f"NSGA-II generation {generation}, Pareto front size: {len(pareto_front)}")
        
        # Extract Pareto optimal solutions
        final_evaluated = [self.evaluate_solution(ind) for ind in population]
        final_fronts = self._fast_non_dominated_sort(final_evaluated)
        pareto_optimal = final_fronts[0] if final_fronts else []
        
        # Prepare results
        results = {
            'pareto_optimal_solutions': [sol.parameters for sol in pareto_optimal],
            'pareto_front_objectives': [sol.objectives for sol in pareto_optimal],
            'best_solutions': sorted(pareto_optimal, key=lambda x: x.fitness, reverse=True)[:5],
            'optimization_history': {
                'pareto_front_size': pareto_history,
                'diversity': diversity_history
            },
            'generations': generation + 1,
            'final_diversity': diversity_history[-1] if diversity_history else 0.0
        }
        
        self.optimization_history.append(results)
        
        return results
    
    def _initialize_population(self, initial_solution: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Initialize population with diversity."""
        
        population = [initial_solution.copy()]
        
        # Create diverse initial population
        for _ in range(self.population_size - 1):
            individual = {}
            
            for param, value in initial_solution.items():
                if isinstance(value, float):
                    # Random variation around initial value
                    variation = np.random.uniform(0.5, 2.0)
                    individual[param] = value * variation
                elif isinstance(value, int):
                    individual[param] = max(1, int(value * np.random.uniform(0.5, 2.0)))
                else:
                    individual[param] = value
            
            population.append(individual)
        
        return population
    
    def _fast_non_dominated_sort(
        self, 
        population: List[OptimizationSolution]
    ) -> List[List[OptimizationSolution]]:
        """NSGA-II fast non-dominated sorting."""
        
        fronts = []
        
        for solution in population:
            solution.rank = 0
            solution.dominated_solutions = []
            solution.domination_count = 0
            
            for other in population:
                if solution.dominates(other):
                    solution.dominated_solutions.append(other)
                elif other.dominates(solution):
                    solution.domination_count += 1
            
            if solution.domination_count == 0:
                solution.rank = 0
                if not fronts:
                    fronts.append([])
                fronts[0].append(solution)
        
        # Build subsequent fronts
        front_index = 0
        while front_index < len(fronts) and fronts[front_index]:
            next_front = []
            
            for solution in fronts[front_index]:
                for dominated in getattr(solution, 'dominated_solutions', []):
                    dominated.domination_count -= 1
                    
                    if dominated.domination_count == 0:
                        dominated.rank = front_index + 1
                        next_front.append(dominated)
            
            if next_front:
                fronts.append(next_front)
            
            front_index += 1
        
        return fronts
    
    def _calculate_crowding_distance(self, front: List[OptimizationSolution]):
        """Calculate crowding distance for solutions in front."""
        
        if len(front) <= 2:
            for solution in front:
                solution.crowding_distance = float('inf')
            return
        
        # Initialize distances
        for solution in front:
            solution.crowding_distance = 0.0
        
        # Calculate distance for each objective
        for obj in self.objectives:
            obj_name = obj.name
            
            # Sort by objective value
            front.sort(key=lambda x: x.objectives.get(obj_name, 0.0))
            
            # Boundary solutions get infinite distance
            front[0].crowding_distance = float('inf')
            front[-1].crowding_distance = float('inf')
            
            # Calculate normalized distance for middle solutions
            obj_values = [sol.objectives.get(obj_name, 0.0) for sol in front]
            obj_range = max(obj_values) - min(obj_values)
            
            if obj_range > 0:
                for i in range(1, len(front) - 1):
                    distance = (obj_values[i + 1] - obj_values[i - 1]) / obj_range
                    front[i].crowding_distance += distance
    
    def _create_next_generation(
        self, 
        evaluated_population: List[OptimizationSolution]
    ) -> List[OptimizationSolution]:
        """Create next generation using NSGA-II selection."""
        
        # Sort by rank and crowding distance
        evaluated_population.sort(
            key=lambda x: (x.rank, -x.crowding_distance)
        )
        
        # Select top half
        selected = evaluated_population[:self.population_size // 2]
        
        # Create offspring through crossover and mutation
        offspring = []
        
        while len(offspring) < self.population_size - len(selected):
            parent1 = random.choice(selected)
            parent2 = random.choice(selected)
            
            # Crossover
            if np.random.random() < self.crossover_rate:
                child_params = self._crossover(parent1.parameters, parent2.parameters)
            else:
                child_params = parent1.parameters.copy()
            
            # Mutation
            if np.random.random() < self.mutation_rate:
                child_params = self._mutate_parameters(child_params, self.mutation_rate)
            
            child = self.evaluate_solution(child_params)
            offspring.append(child)
        
        return selected + offspring
    
    def _calculate_diversity(self, population: List[OptimizationSolution]) -> float:
        """Calculate population diversity."""
        
        if len(population) <= 1:
            return 0.0
        
        # Calculate pairwise distances in objective space
        distances = []
        
        for i in range(len(population)):
            for j in range(i + 1, len(population)):
                sol1, sol2 = population[i], population[j]
                
                # Euclidean distance in objective space
                distance = 0.0
                obj_count = 0
                
                for obj_name in sol1.objectives:
                    if obj_name in sol2.objectives:
                        diff = sol1.objectives[obj_name] - sol2.objectives[obj_name]
                        distance += diff ** 2
                        obj_count += 1
                
                if obj_count > 0:
                    distance = np.sqrt(distance / obj_count)
                    distances.append(distance)
        
        return np.mean(distances) if distances else 0.0
    
    def _crossover(
        self, 
        parent1: Dict[str, Any], 
        parent2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crossover operation for SA."""
        
        child = {}
        
        for param in parent1:
            if param in parent2:
                # Arithmetic crossover
                if isinstance(parent1[param], (int, float)):
                    alpha = np.random.uniform(0.2, 0.8)
                    child[param] = alpha * parent1[param] + (1 - alpha) * parent2[param]
                else:
                    child[param] = random.choice([parent1[param], parent2[param]])
            else:
                child[param] = parent1[param]
        
        return child
    
    def _mutate_parameters(
        self, 
        parameters: Dict[str, Any], 
        mutation_rate: float
    ) -> Dict[str, Any]:
        """Mutate parameters with SA-specific strategy."""
        
        mutated = parameters.copy()
        
        for param, value in parameters.items():
            if np.random.random() < mutation_rate:
                if isinstance(value, float):
                    # Adaptive mutation based on parameter magnitude
                    scale = max(abs(value) * 0.05, 1e-6)
                    mutated[param] = value + np.random.normal(0, scale)
                elif isinstance(value, int):
                    mutated[param] = max(1, value + np.random.randint(-1, 2))
        
        return mutated


class PathwayOptimizationEngine:
    """
    Main optimization engine coordinating multiple algorithms.
    
    Patent Feature: Hybrid optimization with algorithm selection
    and biological constraint integration.
    """
    
    def __init__(self):
        """Initialize optimization engine."""
        
        self.optimizers: Dict[OptimizationType, PathwayOptimizer] = {}
        self.optimization_results: List[Dict[str, Any]] = []
        
        logger.info("Pathway optimization engine initialized")
    
    def register_optimizer(
        self, 
        opt_type: OptimizationType, 
        optimizer: PathwayOptimizer
    ):
        """Register optimization algorithm."""
        
        self.optimizers[opt_type] = optimizer
        logger.info(f"Registered {opt_type.name} optimizer")
    
    def optimize_pathway(
        self,
        initial_parameters: Dict[str, Any],
        objectives: List[OptimizationObjective],
        algorithm: OptimizationType = OptimizationType.GENETIC_ALGORITHM,
        max_iterations: int = 1000
    ) -> Dict[str, Any]:
        """
        Optimize pathway using specified algorithm.
        
        Args:
            initial_parameters: Starting parameter values
            objectives: Optimization objectives
            algorithm: Optimization algorithm to use
            max_iterations: Maximum iterations
            
        Returns:
            Optimization results
        """
        
        # Get or create optimizer
        if algorithm not in self.optimizers:
            self._create_default_optimizer(algorithm, objectives)
        
        optimizer = self.optimizers[algorithm]
        
        # Run optimization
        results = optimizer.optimize(
            initial_parameters,
            max_iterations=max_iterations
        )
        
        # Add metadata
        results['algorithm'] = algorithm.name
        results['objectives'] = [obj.name for obj in objectives]
        results['initial_parameters'] = initial_parameters.copy()
        
        # Store results
        self.optimization_results.append(results)
        
        logger.info(f"Optimization completed with {algorithm.name}")
        
        return results
    
    def compare_algorithms(
        self,
        initial_parameters: Dict[str, Any],
        objectives: List[OptimizationObjective],
        algorithms: Optional[List[OptimizationType]] = None,
        max_iterations: int = 500
    ) -> Dict[str, Any]:
        """
        Compare multiple optimization algorithms.
        
        Args:
            initial_parameters: Starting parameters
            objectives: Optimization objectives
            algorithms: Algorithms to compare (default: all available)
            max_iterations: Maximum iterations per algorithm
            
        Returns:
            Comparison results
        """
        
        if algorithms is None:
            algorithms = [
                OptimizationType.GENETIC_ALGORITHM,
                OptimizationType.SIMULATED_ANNEALING,
                OptimizationType.NSGA_II
            ]
        
        comparison_results = {}
        
        for algorithm in algorithms:
            try:
                results = self.optimize_pathway(
                    initial_parameters,
                    objectives,
                    algorithm,
                    max_iterations
                )
                
                comparison_results[algorithm.name] = {
                    'best_fitness': results.get('best_fitness', 0.0),
                    'convergence_rate': self._calculate_convergence_rate(results),
                    'solution_quality': self._assess_solution_quality(results),
                    'computational_cost': results.get('iterations', max_iterations),
                    'algorithm_efficiency': results.get('best_fitness', 0.0) / results.get('iterations', 1)
                }
                
            except Exception as e:
                logger.error(f"Error running {algorithm.name}: {e}")
                comparison_results[algorithm.name] = {
                    'error': str(e),
                    'best_fitness': 0.0
                }
        
        # Determine best algorithm
        best_algorithm = max(
            comparison_results.keys(),
            key=lambda alg: comparison_results[alg].get('best_fitness', 0.0)
        )
        
        return {
            'algorithm_results': comparison_results,
            'best_algorithm': best_algorithm,
            'performance_ranking': sorted(
                comparison_results.keys(),
                key=lambda alg: comparison_results[alg].get('best_fitness', 0.0),
                reverse=True
            )
        }
    
    def _create_default_optimizer(
        self, 
        opt_type: OptimizationType, 
        objectives: List[OptimizationObjective]
    ):
        """Create default optimizer for given type."""
        
        if opt_type == OptimizationType.GENETIC_ALGORITHM:
            optimizer = GeneticAlgorithmOptimizer(objectives)
        
        elif opt_type == OptimizationType.SIMULATED_ANNEALING:
            optimizer = SimulatedAnnealingOptimizer(objectives)
        
        elif opt_type == OptimizationType.NSGA_II:
            optimizer = MultiObjectiveOptimizer(objectives)
        
        else:
            # Default to genetic algorithm
            optimizer = GeneticAlgorithmOptimizer(objectives)
        
        self.register_optimizer(opt_type, optimizer)
    
    def _calculate_convergence_rate(self, results: Dict[str, Any]) -> float:
        """Calculate convergence rate from optimization history."""
        
        history = results.get('optimization_history', {})
        
        if 'best_fitness' in history:
            fitness_history = history['best_fitness']
            
            if len(fitness_history) > 10:
                # Calculate improvement rate
                initial_fitness = fitness_history[0]
                final_fitness = fitness_history[-1]
                improvement = final_fitness - initial_fitness
                generations = len(fitness_history)
                
                return improvement / generations
        
        return 0.0
    
    def _assess_solution_quality(self, results: Dict[str, Any]) -> float:
        """Assess overall quality of optimization results."""
        
        # Consider multiple factors
        fitness_score = results.get('best_fitness', 0.0)
        convergence_score = 1.0 if results.get('converged', False) else 0.5
        diversity_score = results.get('final_diversity', 0.0)
        
        # Weighted combination
        quality_score = (
            0.6 * fitness_score +
            0.3 * convergence_score +
            0.1 * min(1.0, diversity_score)
        )
        
        return quality_score
    
    def generate_optimization_report(self) -> str:
        """Generate comprehensive optimization report."""
        
        if not self.optimization_results:
            return "No optimization results available."
        
        report_lines = [
            "# EvoSphere Pathway Optimization Report",
            "",
            f"Total optimizations performed: {len(self.optimization_results)}",
            ""
        ]
        
        # Algorithm performance summary
        algorithm_stats = defaultdict(list)
        
        for result in self.optimization_results:
            algorithm = result.get('algorithm', 'Unknown')
            fitness = result.get('best_fitness', 0.0)
            algorithm_stats[algorithm].append(fitness)
        
        report_lines.append("## Algorithm Performance")
        
        for algorithm, fitnesses in algorithm_stats.items():
            avg_fitness = np.mean(fitnesses)
            std_fitness = np.std(fitnesses)
            
            report_lines.append(f"- {algorithm}: {avg_fitness:.4f} ± {std_fitness:.4f}")
        
        report_lines.extend([
            "",
            "## Best Solutions",
            ""
        ])
        
        # Best solutions
        best_results = sorted(
            self.optimization_results,
            key=lambda x: x.get('best_fitness', 0.0),
            reverse=True
        )[:3]
        
        for i, result in enumerate(best_results, 1):
            algorithm = result.get('algorithm', 'Unknown')
            fitness = result.get('best_fitness', 0.0)
            
            report_lines.append(f"{i}. {algorithm}: {fitness:.4f}")
            
            if 'best_solution' in result:
                for param, value in result['best_solution'].items():
                    if isinstance(value, float):
                        report_lines.append(f"   - {param}: {value:.6f}")
                    else:
                        report_lines.append(f"   - {param}: {value}")
        
        return '\n'.join(report_lines)
