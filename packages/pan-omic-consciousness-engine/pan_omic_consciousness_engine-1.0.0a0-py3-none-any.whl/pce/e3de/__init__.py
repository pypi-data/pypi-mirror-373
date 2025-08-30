"""E³DE: Entropic Evolutionary Dynamics Engine.

Implements physics-based evolutionary dynamics with:
- Entropy-driven selection pressure
- Fitness landscapes based on thermodynamic principles
- Multi-scale evolutionary simulation (molecular → organism → population)
- Consciousness emergence through complexity gradients
- Adaptive mutation rates based on environmental entropy
"""

import numpy as np
import logging
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import random
from collections import defaultdict

from ..core.datatypes import LatentEmbedding, HyperGraph, OmicsData
from ..core.config import get_config
from ..utils.logging import get_logger, timer_context
from ..utils.metrics import compute_biological_metrics

logger = get_logger(__name__)


class EvolutionScale(Enum):
    """Scales of evolutionary dynamics."""
    MOLECULAR = "molecular"      # Protein folding, metabolic networks
    CELLULAR = "cellular"        # Cell division, differentiation
    TISSUE = "tissue"           # Tissue organization, morphogenesis
    ORGANISM = "organism"       # Individual development, behavior
    POPULATION = "population"   # Population genetics, speciation
    ECOSYSTEM = "ecosystem"     # Ecological interactions, coevolution


@dataclass
class EvolutionaryParameters:
    """Parameters for evolutionary dynamics."""
    selection_pressure: float = 1.0
    mutation_rate: float = 0.01
    crossover_rate: float = 0.7
    population_size: int = 100
    elite_fraction: float = 0.1
    entropy_weight: float = 0.5
    complexity_reward: float = 0.3
    stability_penalty: float = 0.2
    temperature: float = 310.0      # Physiological temperature
    boltzmann_constant: float = 8.617e-5  # eV/K
    
    # Consciousness-specific parameters
    consciousness_threshold: float = 0.7
    complexity_gradient: float = 0.1
    integration_bonus: float = 0.2


@dataclass
class Organism:
    """Evolutionary organism representation."""
    id: str
    genotype: np.ndarray           # Genetic representation
    phenotype: Dict[str, Any]      # Expressed traits
    fitness: float = 0.0
    entropy: float = 0.0
    complexity: float = 0.0
    consciousness_level: float = 0.0
    metabolic_cost: float = 0.0
    age: int = 0
    generation: int = 0
    lineage: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Initialize derived properties."""
        if self.lineage is None:
            self.lineage = [self.id]
    
    def mutate(self, mutation_rate: float, environmental_entropy: float = 0.0) -> 'Organism':
        """Create mutated offspring."""
        # Adaptive mutation rate based on environmental entropy
        adaptive_rate = mutation_rate * (1.0 + environmental_entropy)
        
        # Apply mutations
        new_genotype = self.genotype.copy()
        mutation_mask = np.random.random(len(new_genotype)) < adaptive_rate
        
        # Different mutation types
        for i, should_mutate in enumerate(mutation_mask):
            if should_mutate:
                mutation_type = np.random.choice(['point', 'insertion', 'deletion'], p=[0.7, 0.15, 0.15])
                
                if mutation_type == 'point':
                    # Point mutation
                    new_genotype[i] += np.random.normal(0, 0.1)
                elif mutation_type == 'insertion':
                    # Gene duplication/insertion
                    new_genotype[i] *= np.random.uniform(1.1, 1.5)
                else:  # deletion
                    # Gene deletion/silencing
                    new_genotype[i] *= np.random.uniform(0.5, 0.9)
        
        # Create offspring
        offspring_id = f"{self.id}_m{self.generation + 1}"
        offspring = Organism(
            id=offspring_id,
            genotype=new_genotype,
            phenotype=self.phenotype.copy(),
            generation=self.generation + 1,
            lineage=self.lineage + [offspring_id]
        )
        
        return offspring
    
    def crossover(self, partner: 'Organism') -> Tuple['Organism', 'Organism']:
        """Perform genetic crossover with partner."""
        # Single-point crossover
        crossover_point = np.random.randint(1, len(self.genotype))
        
        # Create offspring genotypes
        offspring1_genotype = np.concatenate([
            self.genotype[:crossover_point],
            partner.genotype[crossover_point:]
        ])
        
        offspring2_genotype = np.concatenate([
            partner.genotype[:crossover_point],
            self.genotype[crossover_point:]
        ])
        
        # Create offspring
        offspring1 = Organism(
            id=f"{self.id}x{partner.id}_1",
            genotype=offspring1_genotype,
            phenotype={},
            generation=max(self.generation, partner.generation) + 1,
            lineage=self.lineage + partner.lineage
        )
        
        offspring2 = Organism(
            id=f"{self.id}x{partner.id}_2",
            genotype=offspring2_genotype,
            phenotype={},
            generation=max(self.generation, partner.generation) + 1,
            lineage=self.lineage + partner.lineage
        )
        
        return offspring1, offspring2


class FitnessFunction(ABC):
    """Abstract base class for fitness functions."""
    
    @abstractmethod
    def evaluate(
        self,
        organism: Organism,
        environment: Dict[str, Any],
        population: List[Organism]
    ) -> float:
        """Evaluate organism fitness."""
        pass


class EntropicFitnessFunction(FitnessFunction):
    """Entropy-based fitness function using thermodynamic principles."""
    
    def __init__(self, parameters: EvolutionaryParameters) -> None:
        self.parameters = parameters
    
    def evaluate(
        self,
        organism: Organism,
        environment: Dict[str, Any],
        population: List[Organism]
    ) -> float:
        """Evaluate fitness based on entropic principles."""
        # Compute organism entropy
        entropy = self._compute_organism_entropy(organism)
        
        # Compute complexity
        complexity = self._compute_complexity(organism)
        
        # Compute metabolic cost
        metabolic_cost = self._compute_metabolic_cost(organism)
        
        # Compute environmental adaptation
        adaptation = self._compute_environmental_adaptation(organism, environment)
        
        # Compute consciousness contribution
        consciousness = self._compute_consciousness_level(organism)
        
        # Fitness function: F = α*entropy + β*complexity - γ*cost + δ*adaptation + ε*consciousness
        fitness = (
            self.parameters.entropy_weight * entropy +
            self.parameters.complexity_reward * complexity -
            self.parameters.stability_penalty * metabolic_cost +
            0.3 * adaptation +
            0.2 * consciousness
        )
        
        # Apply temperature scaling (Boltzmann factor)
        scaled_fitness = fitness * np.exp(-metabolic_cost / (self.parameters.boltzmann_constant * self.parameters.temperature))
        
        # Store computed values
        organism.entropy = entropy
        organism.complexity = complexity
        organism.metabolic_cost = metabolic_cost
        organism.consciousness_level = consciousness
        organism.fitness = scaled_fitness
        
        return scaled_fitness
    
    def _compute_organism_entropy(self, organism: Organism) -> float:
        """Compute organism's internal entropy."""
        genotype = organism.genotype
        
        # Information-theoretic entropy
        # Discretize genotype for entropy calculation
        discretized = np.digitize(genotype, bins=np.linspace(genotype.min(), genotype.max(), 20))
        unique, counts = np.unique(discretized, return_counts=True)
        probabilities = counts / counts.sum()
        
        # Shannon entropy
        entropy = -np.sum(probabilities * np.log(probabilities + 1e-10))
        
        # Normalize by maximum possible entropy
        max_entropy = np.log(len(unique))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        return normalized_entropy
    
    def _compute_complexity(self, organism: Organism) -> float:
        """Compute organism complexity."""
        genotype = organism.genotype
        
        # Measures of complexity
        variance = np.var(genotype)
        correlation = np.corrcoef(genotype[:-1], genotype[1:])[0, 1] if len(genotype) > 1 else 0
        range_span = np.ptp(genotype)  # Peak-to-peak range
        
        # Combine measures
        complexity = (
            0.4 * variance +
            0.3 * abs(correlation) +
            0.3 * range_span
        )
        
        return complexity
    
    def _compute_metabolic_cost(self, organism: Organism) -> float:
        """Compute metabolic cost of maintaining organism."""
        genotype = organism.genotype
        
        # Cost proportional to genome size and activity
        size_cost = len(genotype) / 1000.0  # Normalize
        activity_cost = np.sum(np.abs(genotype)) / len(genotype)
        
        # Complexity penalty (maintaining complex structures is expensive)
        complexity_cost = organism.complexity * 0.1
        
        total_cost = size_cost + activity_cost + complexity_cost
        return total_cost
    
    def _compute_environmental_adaptation(
        self,
        organism: Organism,
        environment: Dict[str, Any]
    ) -> float:
        """Compute how well organism adapts to environment."""
        if not environment:
            return 0.5  # Neutral adaptation
        
        # Extract environmental conditions
        temperature = environment.get('temperature', 310.0)
        resource_availability = environment.get('resources', 1.0)
        competition = environment.get('competition', 0.5)
        
        # Adaptation based on genotype matching environmental conditions
        temp_adaptation = 1.0 - abs(temperature - 310.0) / 100.0  # Optimal at 310K
        resource_adaptation = min(resource_availability * 2.0, 1.0)
        competition_adaptation = 1.0 - competition
        
        # Weight different factors
        adaptation = (
            0.4 * temp_adaptation +
            0.4 * resource_adaptation +
            0.2 * competition_adaptation
        )
        
        return max(0, min(adaptation, 1.0))
    
    def _compute_consciousness_level(self, organism: Organism) -> float:
        """Compute consciousness level based on complexity and integration."""
        complexity = organism.complexity
        entropy = organism.entropy
        genotype = organism.genotype
        
        # Information integration measure (simplified IIT)
        integration = self._compute_information_integration(genotype)
        
        # Neural complexity proxy
        neural_complexity = self._compute_neural_complexity(genotype)
        
        # Consciousness level
        consciousness = (
            0.3 * complexity +
            0.3 * entropy +
            0.2 * integration +
            0.2 * neural_complexity
        )
        
        return consciousness
    
    def _compute_information_integration(self, genotype: np.ndarray) -> float:
        """Compute information integration measure."""
        # Simplified Φ (phi) measure
        n = len(genotype)
        if n < 2:
            return 0
        
        # Mutual information between halves
        mid = n // 2
        half1, half2 = genotype[:mid], genotype[mid:]
        
        # Correlation as proxy for mutual information
        correlation = np.corrcoef(half1, half2[:len(half1)])[0, 1] if len(half1) == len(half2[:len(half1)]) else 0
        
        # Convert to information integration
        integration = abs(correlation) if not np.isnan(correlation) else 0
        
        return integration
    
    def _compute_neural_complexity(self, genotype: np.ndarray) -> float:
        """Compute neural complexity proxy."""
        # Model genotype as neural network weights
        # Complexity based on weight distribution and structure
        
        weight_variance = np.var(genotype)
        weight_sparsity = np.sum(np.abs(genotype) < 0.01) / len(genotype)
        
        # Neural complexity favors diverse weights with some sparsity
        complexity = weight_variance * (1.0 - weight_sparsity * 0.5)
        
        return complexity


class Environment:
    """Evolutionary environment with changing conditions."""
    
    def __init__(
        self,
        base_conditions: Optional[Dict[str, Any]] = None,
        change_rate: float = 0.01
    ) -> None:
        self.base_conditions = base_conditions or {
            'temperature': 310.0,
            'resources': 1.0,
            'competition': 0.5,
            'entropy': 0.3
        }
        self.current_conditions = self.base_conditions.copy()
        self.change_rate = change_rate
        self.time_step = 0
    
    def update(self) -> Dict[str, Any]:
        """Update environmental conditions."""
        self.time_step += 1
        
        # Environmental drift
        for key, value in self.current_conditions.items():
            if isinstance(value, (int, float)):
                # Random walk with reversion to base
                base_value = self.base_conditions[key]
                noise = np.random.normal(0, self.change_rate)
                reversion = (base_value - value) * 0.01
                
                new_value = value + noise + reversion
                
                # Keep within reasonable bounds
                if key == 'temperature':
                    new_value = max(280, min(350, new_value))  # 280K to 350K
                elif key in ['resources', 'competition', 'entropy']:
                    new_value = max(0, min(1, new_value))
                
                self.current_conditions[key] = new_value
        
        return self.current_conditions.copy()
    
    def add_perturbation(self, perturbation: Dict[str, float]) -> None:
        """Add environmental perturbation."""
        for key, delta in perturbation.items():
            if key in self.current_conditions:
                self.current_conditions[key] += delta


class Population:
    """Population of evolutionary organisms."""
    
    def __init__(
        self,
        initial_size: int,
        genotype_length: int,
        parameters: EvolutionaryParameters
    ) -> None:
        self.parameters = parameters
        self.organisms: List[Organism] = []
        self.generation = 0
        self.fitness_history: List[Dict[str, float]] = []
        self.diversity_history: List[float] = []
        
        # Initialize population
        self._initialize_population(initial_size, genotype_length)
        
        logger.info(f"Initialized population: {len(self.organisms)} organisms")
    
    def _initialize_population(self, size: int, genotype_length: int) -> None:
        """Initialize random population."""
        for i in range(size):
            # Random genotype
            genotype = np.random.normal(0, 1, genotype_length)
            
            organism = Organism(
                id=f"org_{i}_gen0",
                genotype=genotype,
                phenotype={},
                generation=0
            )
            
            self.organisms.append(organism)
    
    def evaluate_fitness(
        self,
        fitness_function: FitnessFunction,
        environment: Dict[str, Any]
    ) -> None:
        """Evaluate fitness for all organisms."""
        for organism in self.organisms:
            fitness_function.evaluate(organism, environment, self.organisms)
    
    def select_parents(self) -> List[Organism]:
        """Select parents for reproduction."""
        # Sort by fitness
        self.organisms.sort(key=lambda x: x.fitness, reverse=True)
        
        # Elite selection + tournament selection
        num_elites = int(self.parameters.elite_fraction * len(self.organisms))
        elites = self.organisms[:num_elites]
        
        # Tournament selection for remaining spots
        num_tournaments = len(self.organisms) - num_elites
        tournament_winners = []
        
        for _ in range(num_tournaments):
            # Tournament of size 3
            candidates = random.sample(self.organisms, min(3, len(self.organisms)))
            winner = max(candidates, key=lambda x: x.fitness)
            tournament_winners.append(winner)
        
        return elites + tournament_winners
    
    def reproduce(self, parents: List[Organism], environment: Dict[str, Any]) -> List[Organism]:
        """Generate offspring from parents."""
        offspring = []
        environmental_entropy = environment.get('entropy', 0.3)
        
        while len(offspring) < len(self.organisms):
            # Select two parents
            parent1, parent2 = random.sample(parents, 2)
            
            # Crossover with probability
            if random.random() < self.parameters.crossover_rate:
                child1, child2 = parent1.crossover(parent2)
                offspring.extend([child1, child2])
            else:
                # Asexual reproduction (mutation only)
                child1 = parent1.mutate(self.parameters.mutation_rate, environmental_entropy)
                child2 = parent2.mutate(self.parameters.mutation_rate, environmental_entropy)
                offspring.extend([child1, child2])
        
        return offspring[:len(self.organisms)]  # Maintain population size
    
    def evolve_generation(
        self,
        fitness_function: FitnessFunction,
        environment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evolve population by one generation."""
        # Evaluate fitness
        self.evaluate_fitness(fitness_function, environment)
        
        # Compute generation statistics
        fitnesses = [org.fitness for org in self.organisms]
        consciousness_levels = [org.consciousness_level for org in self.organisms]
        complexities = [org.complexity for org in self.organisms]
        
        stats = {
            'generation': self.generation,
            'avg_fitness': np.mean(fitnesses),
            'max_fitness': np.max(fitnesses),
            'fitness_std': np.std(fitnesses),
            'avg_consciousness': np.mean(consciousness_levels),
            'max_consciousness': np.max(consciousness_levels),
            'avg_complexity': np.mean(complexities),
            'population_size': len(self.organisms)
        }
        
        # Compute diversity
        diversity = self._compute_population_diversity()
        stats['diversity'] = diversity
        
        # Store history
        self.fitness_history.append(stats)
        self.diversity_history.append(diversity)
        
        # Select parents and reproduce
        parents = self.select_parents()
        offspring = self.reproduce(parents, environment)
        
        # Replace population
        self.organisms = offspring
        self.generation += 1
        
        return stats
    
    def _compute_population_diversity(self) -> float:
        """Compute genetic diversity of population."""
        if len(self.organisms) < 2:
            return 0.0
        
        # Compute pairwise genetic distances
        genotypes = np.array([org.genotype for org in self.organisms])
        
        # Average pairwise Euclidean distance
        distances = []
        for i in range(len(genotypes)):
            for j in range(i + 1, len(genotypes)):
                distance = np.linalg.norm(genotypes[i] - genotypes[j])
                distances.append(distance)
        
        diversity = np.mean(distances) if distances else 0.0
        return diversity
    
    def get_best_organisms(self, n: int = 10) -> List[Organism]:
        """Get top n organisms by fitness."""
        sorted_orgs = sorted(self.organisms, key=lambda x: x.fitness, reverse=True)
        return sorted_orgs[:n]
    
    def get_consciousness_leaders(self, n: int = 10) -> List[Organism]:
        """Get top n organisms by consciousness level."""
        sorted_orgs = sorted(self.organisms, key=lambda x: x.consciousness_level, reverse=True)
        return sorted_orgs[:n]


class E3DE:
    """Entropic Evolutionary Dynamics Engine main class."""
    
    def __init__(
        self,
        parameters: Optional[EvolutionaryParameters] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize E³DE system."""
        self.config = config or get_config().e3de
        
        if parameters is None:
            parameters = EvolutionaryParameters(
                selection_pressure=self.config.get("selection_pressure", 1.0),
                mutation_rate=self.config.get("mutation_rate", 0.01),
                population_size=self.config.get("population_size", 100),
                entropy_weight=self.config.get("entropy_weight", 0.5)
            )
        
        self.parameters = parameters
        self.fitness_function = EntropicFitnessFunction(parameters)
        self.environment = Environment()
        self.populations: Dict[str, Population] = {}
        self.simulation_history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized E³DE with parameters: {parameters}")
    
    def create_population(
        self,
        name: str,
        size: int,
        genotype_length: int,
        embedding: Optional[LatentEmbedding] = None
    ) -> Population:
        """Create new evolutionary population."""
        with timer_context(f"Creating population {name}"):
            population = Population(size, genotype_length, self.parameters)
            
            # Initialize from embedding if provided
            if embedding is not None:
                self._initialize_from_embedding(population, embedding)
            
            self.populations[name] = population
            logger.info(f"Created population {name}: {size} organisms, {genotype_length} genes")
            
            return population
    
    def evolve_population(
        self,
        population_name: str,
        generations: int,
        environmental_changes: Optional[List[Dict[str, float]]] = None
    ) -> Dict[str, Any]:
        """Evolve population for specified generations."""
        if population_name not in self.populations:
            raise ValueError(f"Population {population_name} not found")
        
        population = self.populations[population_name]
        
        with timer_context(f"Evolving {population_name} for {generations} generations"):
            evolution_history = []
            
            for gen in range(generations):
                # Update environment
                current_env = self.environment.update()
                
                # Apply environmental changes if specified
                if environmental_changes and gen < len(environmental_changes):
                    self.environment.add_perturbation(environmental_changes[gen])
                
                # Evolve one generation
                gen_stats = population.evolve_generation(self.fitness_function, current_env)
                gen_stats['environment'] = current_env.copy()
                evolution_history.append(gen_stats)
                
                # Log progress
                if gen % (generations // 10) == 0 or gen == generations - 1:
                    logger.info(
                        f"Generation {gen}: fitness={gen_stats['avg_fitness']:.3f}, "
                        f"consciousness={gen_stats['avg_consciousness']:.3f}"
                    )
            
            # Store simulation results
            simulation_result = {
                'population_name': population_name,
                'generations': generations,
                'final_generation': evolution_history[-1],
                'history': evolution_history
            }
            
            self.simulation_history.append(simulation_result)
            
            logger.info(f"Evolution complete: {generations} generations")
            return simulation_result
    
    def analyze_consciousness_emergence(
        self,
        population_name: str
    ) -> Dict[str, Any]:
        """Analyze consciousness emergence in population."""
        if population_name not in self.populations:
            raise ValueError(f"Population {population_name} not found")
        
        population = self.populations[population_name]
        
        with timer_context("Analyzing consciousness emergence"):
            # Get consciousness leaders
            consciousness_leaders = population.get_consciousness_leaders(10)
            
            # Analyze consciousness distribution
            consciousness_levels = [org.consciousness_level for org in population.organisms]
            
            analysis = {
                'population_size': len(population.organisms),
                'generation': population.generation,
                'consciousness_distribution': {
                    'mean': np.mean(consciousness_levels),
                    'std': np.std(consciousness_levels),
                    'max': np.max(consciousness_levels),
                    'min': np.min(consciousness_levels),
                    'above_threshold': sum(1 for c in consciousness_levels if c > self.parameters.consciousness_threshold)
                },
                'emergence_indicators': {
                    'complexity_gradient': self._compute_complexity_gradient(population),
                    'integration_level': self._compute_population_integration(population),
                    'information_flow': self._compute_information_flow(population),
                    'emergence_potential': self._compute_emergence_potential(population)
                },
                'top_conscious_organisms': [
                    {
                        'id': org.id,
                        'consciousness_level': org.consciousness_level,
                        'complexity': org.complexity,
                        'fitness': org.fitness,
                        'generation': org.generation
                    }
                    for org in consciousness_leaders
                ]
            }
            
            logger.info(f"Consciousness analysis: {analysis['consciousness_distribution']}")
            return analysis
    
    def simulate_multi_scale_evolution(
        self,
        scales: List[EvolutionScale],
        generations_per_scale: int = 100
    ) -> Dict[str, Any]:
        """Simulate evolution across multiple scales."""
        with timer_context("Multi-scale evolution simulation"):
            results = {}
            
            for scale in scales:
                scale_name = scale.value
                
                # Scale-specific parameters
                if scale == EvolutionScale.MOLECULAR:
                    size, genotype_len = 50, 20
                elif scale == EvolutionScale.CELLULAR:
                    size, genotype_len = 100, 50
                elif scale == EvolutionScale.ORGANISM:
                    size, genotype_len = 200, 100
                else:
                    size, genotype_len = 100, 50
                
                # Create and evolve population
                population = self.create_population(scale_name, size, genotype_len)
                result = self.evolve_population(scale_name, generations_per_scale)
                
                results[scale_name] = result
                
                logger.info(f"Completed {scale_name} scale evolution")
            
            # Cross-scale analysis
            cross_scale_analysis = self._analyze_cross_scale_patterns(results)
            results['cross_scale_analysis'] = cross_scale_analysis
            
            return results
    
    def _initialize_from_embedding(
        self,
        population: Population,
        embedding: LatentEmbedding
    ) -> None:
        """Initialize population from latent embedding."""
        embeddings_list = list(embedding.embeddings.values())
        
        # Use embedding vectors to seed initial genotypes
        for i, organism in enumerate(population.organisms):
            if i < len(embeddings_list):
                # Use embedding as genotype initialization
                embedding_vec = np.array(embeddings_list[i])
                
                # Resize to match genotype length
                if len(embedding_vec) != len(organism.genotype):
                    # Interpolate or pad
                    if len(embedding_vec) > len(organism.genotype):
                        organism.genotype = embedding_vec[:len(organism.genotype)]
                    else:
                        organism.genotype[:len(embedding_vec)] = embedding_vec
    
    def _compute_complexity_gradient(self, population: Population) -> float:
        """Compute complexity gradient across population."""
        complexities = [org.complexity for org in population.organisms]
        return np.std(complexities) / np.mean(complexities) if np.mean(complexities) > 0 else 0
    
    def _compute_population_integration(self, population: Population) -> float:
        """Compute information integration across population."""
        # Simplified measure based on organism interactions
        return np.mean([org.consciousness_level for org in population.organisms])
    
    def _compute_information_flow(self, population: Population) -> float:
        """Compute information flow in population."""
        # Measure based on genetic diversity and fitness correlation
        fitnesses = [org.fitness for org in population.organisms]
        complexities = [org.complexity for org in population.organisms]
        
        correlation = np.corrcoef(fitnesses, complexities)[0, 1] if len(fitnesses) > 1 else 0
        return abs(correlation) if not np.isnan(correlation) else 0
    
    def _compute_emergence_potential(self, population: Population) -> float:
        """Compute potential for consciousness emergence."""
        consciousness_levels = [org.consciousness_level for org in population.organisms]
        
        # Factors contributing to emergence potential
        high_consciousness = sum(1 for c in consciousness_levels if c > self.parameters.consciousness_threshold)
        diversity = population._compute_population_diversity()
        avg_complexity = np.mean([org.complexity for org in population.organisms])
        
        emergence_potential = (
            0.4 * (high_consciousness / len(population.organisms)) +
            0.3 * min(diversity / 10.0, 1.0) +
            0.3 * avg_complexity
        )
        
        return emergence_potential
    
    def _analyze_cross_scale_patterns(
        self,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze patterns across evolutionary scales."""
        analysis = {
            'scale_progression': {},
            'consciousness_scaling': {},
            'complexity_trends': {},
            'fitness_relationships': {}
        }
        
        # Extract final generation data from each scale
        for scale_name, result in results.items():
            if isinstance(result, dict) and 'final_generation' in result:
                final_gen = result['final_generation']
                
                analysis['scale_progression'][scale_name] = {
                    'final_fitness': final_gen['avg_fitness'],
                    'final_consciousness': final_gen['avg_consciousness'],
                    'final_complexity': final_gen['avg_complexity'],
                    'diversity': final_gen['diversity']
                }
        
        return analysis
    
    def __repr__(self) -> str:
        """String representation of E³DE."""
        num_pops = len(self.populations)
        total_organisms = sum(len(pop.organisms) for pop in self.populations.values())
        return f"E3DE({num_pops} populations, {total_organisms} organisms)"
