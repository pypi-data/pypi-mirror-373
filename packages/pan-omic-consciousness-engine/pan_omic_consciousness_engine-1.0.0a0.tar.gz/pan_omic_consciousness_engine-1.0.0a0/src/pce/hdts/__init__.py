"""HDTS: Hierarchical Digital Twin Simulator.

Adaptive zoom digital twin system with biological scales L0-L5:
- L0: Molecular (proteins, metabolites)
- L1: Subcellular (organelles, pathways)
- L2: Cellular (individual cells)
- L3: Tissue (cell populations, organs)
- L4: Organism (whole body systems)
- L5: Population (groups, ecosystems)

Features:
- Scale-adaptive resolution
- Cross-scale information propagation
- Real-time simulation with consciousness modeling
- Physics-based biological constraints
"""

import numpy as np
import logging
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import time
from collections import defaultdict, deque

from ..core.datatypes import LatentEmbedding, HyperGraph, OmicsData
from ..core.config import get_config
from ..utils.logging import get_logger, timer_context
from ..utils.metrics import compute_biological_metrics

logger = get_logger(__name__)


class BiologicalScale(Enum):
    """Hierarchical biological scales."""
    L0_MOLECULAR = "L0_molecular"        # 10^-9 m, proteins, metabolites
    L1_SUBCELLULAR = "L1_subcellular"   # 10^-6 m, organelles, pathways
    L2_CELLULAR = "L2_cellular"         # 10^-5 m, individual cells
    L3_TISSUE = "L3_tissue"             # 10^-3 m, tissues, organs
    L4_ORGANISM = "L4_organism"         # 10^0 m, whole organism
    L5_POPULATION = "L5_population"     # 10^3 m, populations, ecosystems
    
    @property
    def length_scale(self) -> float:
        """Characteristic length scale in meters."""
        scales = {
            self.L0_MOLECULAR: 1e-9,
            self.L1_SUBCELLULAR: 1e-6,
            self.L2_CELLULAR: 1e-5,
            self.L3_TISSUE: 1e-3,
            self.L4_ORGANISM: 1.0,
            self.L5_POPULATION: 1e3
        }
        return scales[self]
    
    @property
    def time_scale(self) -> float:
        """Characteristic time scale in seconds."""
        scales = {
            self.L0_MOLECULAR: 1e-12,    # Picoseconds
            self.L1_SUBCELLULAR: 1e-6,   # Microseconds
            self.L2_CELLULAR: 1e-3,      # Milliseconds
            self.L3_TISSUE: 1.0,         # Seconds
            self.L4_ORGANISM: 3600,      # Hours
            self.L5_POPULATION: 86400    # Days
        }
        return scales[self]


@dataclass
class SimulationParameters:
    """Parameters for hierarchical simulation."""
    # Resolution parameters
    min_resolution: float = 1e-9      # Minimum spatial resolution (m)
    max_resolution: float = 1e3       # Maximum spatial resolution (m)
    adaptive_threshold: float = 0.1   # Threshold for resolution adaptation
    
    # Time stepping
    base_dt: float = 1e-6             # Base time step (s)
    max_dt: float = 3600              # Maximum time step (s)
    adaptive_time_stepping: bool = True
    
    # Physics parameters
    diffusion_coefficient: float = 1e-9  # m²/s
    reaction_rate_constant: float = 1e6   # M⁻¹s⁻¹
    temperature: float = 310.0            # K
    viscosity: float = 1e-3               # Pa·s (water at body temp)
    
    # Biological parameters
    metabolic_rate: float = 2000          # kcal/day for average human
    cell_division_time: float = 86400     # s (24 hours)
    protein_synthesis_rate: float = 10    # proteins/s per ribosome
    
    # Consciousness parameters
    consciousness_integration_time: float = 0.1  # s
    awareness_propagation_speed: float = 100     # m/s (neural conduction)


@dataclass
class DigitalTwinEntity:
    """Entity within digital twin simulation."""
    id: str
    entity_type: str                    # protein, cell, tissue, etc.
    scale: BiologicalScale
    position: np.ndarray                # Spatial position
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    state_vector: np.ndarray = field(default_factory=lambda: np.zeros(10))
    
    # Physical properties
    mass: float = 1e-15                 # kg (typical protein mass)
    size: float = 1e-9                  # m (typical protein size)
    charge: float = 0.0                 # Elementary charges
    
    # Biological properties
    activity: float = 1.0               # Activity level [0,1]
    health: float = 1.0                 # Health status [0,1]
    age: float = 0.0                    # Age in simulation time
    
    # Consciousness properties
    awareness_level: float = 0.0        # Consciousness contribution
    information_content: float = 0.0    # Information carried
    
    # Relationships
    connections: List[str] = field(default_factory=list)
    parent_entities: List[str] = field(default_factory=list)
    child_entities: List[str] = field(default_factory=list)
    
    def update_physics(self, dt: float, forces: np.ndarray) -> None:
        """Update entity physics."""
        # Simple Newtonian dynamics
        acceleration = forces / self.mass
        self.velocity += acceleration * dt
        self.position += self.velocity * dt
        
        # Apply damping (viscous drag in biological medium)
        damping = 0.99
        self.velocity *= damping
    
    def update_biology(self, dt: float, environment: Dict[str, float]) -> None:
        """Update biological state."""
        # Metabolic activity
        metabolic_rate = environment.get('nutrients', 1.0) * self.activity
        
        # Aging
        self.age += dt
        
        # Health decay with age (simple model)
        age_factor = np.exp(-self.age / (365 * 24 * 3600))  # Years in seconds
        self.health = min(self.health, age_factor)
        
        # Activity based on health and environment
        self.activity = self.health * metabolic_rate
    
    def update_consciousness(self, dt: float, network_state: Dict[str, Any]) -> None:
        """Update consciousness-related properties."""
        # Information integration from connections
        if self.connections:
            connection_info = sum(network_state.get(conn_id, 0) for conn_id in self.connections)
            self.information_content = connection_info / len(self.connections)
        
        # Awareness level based on information and scale
        scale_factor = 1.0 / (1.0 + self.scale.length_scale * 1e6)  # Smaller scales less aware
        self.awareness_level = self.information_content * scale_factor * self.activity


class ScaleManager:
    """Manages adaptive resolution across biological scales."""
    
    def __init__(self, parameters: SimulationParameters) -> None:
        self.parameters = parameters
        self.current_scales: Dict[str, BiologicalScale] = {}
        self.resolution_map: Dict[BiologicalScale, float] = {}
        self.active_regions: Dict[BiologicalScale, List[Tuple[np.ndarray, float]]] = defaultdict(list)
        
        # Initialize resolution map
        for scale in BiologicalScale:
            self.resolution_map[scale] = scale.length_scale
    
    def determine_optimal_scale(
        self,
        position: np.ndarray,
        entity_size: float,
        required_detail: float
    ) -> BiologicalScale:
        """Determine optimal simulation scale for given requirements."""
        # Find scale that matches required detail level
        target_resolution = entity_size / required_detail
        
        best_scale = BiologicalScale.L0_MOLECULAR
        min_diff = float('inf')
        
        for scale in BiologicalScale:
            diff = abs(np.log10(scale.length_scale) - np.log10(target_resolution))
            if diff < min_diff:
                min_diff = diff
                best_scale = scale
        
        return best_scale
    
    def add_active_region(
        self,
        scale: BiologicalScale,
        center: np.ndarray,
        radius: float
    ) -> None:
        """Add region requiring high-resolution simulation."""
        self.active_regions[scale].append((center, radius))
    
    def get_local_resolution(
        self,
        position: np.ndarray,
        scale: BiologicalScale
    ) -> float:
        """Get local resolution at position and scale."""
        base_resolution = self.resolution_map[scale]
        
        # Check if position is in high-resolution region
        for region_center, region_radius in self.active_regions[scale]:
            distance = np.linalg.norm(position - region_center)
            if distance <= region_radius:
                # Increase resolution in active regions
                enhancement = max(0.1, 1.0 - distance / region_radius)
                return base_resolution * enhancement
        
        return base_resolution
    
    def adapt_resolution(
        self,
        entities: List[DigitalTwinEntity],
        activity_threshold: float = 0.5
    ) -> Dict[BiologicalScale, float]:
        """Adapt resolution based on entity activity."""
        scale_activities = defaultdict(list)
        
        # Collect activity levels by scale
        for entity in entities:
            scale_activities[entity.scale].append(entity.activity)
        
        # Update resolutions based on activity
        new_resolutions = {}
        for scale, activities in scale_activities.items():
            avg_activity = np.mean(activities)
            
            if avg_activity > activity_threshold:
                # Increase resolution for active regions
                enhancement_factor = 1.0 + avg_activity
                new_resolution = self.resolution_map[scale] / enhancement_factor
            else:
                # Decrease resolution for inactive regions
                new_resolution = self.resolution_map[scale] * 1.1
            
            # Clamp to reasonable bounds
            min_res = self.parameters.min_resolution
            max_res = self.parameters.max_resolution
            new_resolution = max(min_res, min(max_res, new_resolution))
            
            new_resolutions[scale] = new_resolution
            self.resolution_map[scale] = new_resolution
        
        return new_resolutions


class CrossScaleCommunicator:
    """Handles information flow between scales."""
    
    def __init__(self) -> None:
        self.message_queues: Dict[Tuple[BiologicalScale, BiologicalScale], deque] = defaultdict(deque)
        self.aggregation_rules: Dict[str, Callable] = {
            'upscale_average': self._upscale_average,
            'upscale_sum': self._upscale_sum,
            'downscale_broadcast': self._downscale_broadcast,
            'downscale_distribute': self._downscale_distribute
        }
    
    def send_upward(
        self,
        from_scale: BiologicalScale,
        to_scale: BiologicalScale,
        data: Dict[str, Any]
    ) -> None:
        """Send information from lower to higher scale."""
        message = {
            'type': 'upward',
            'from_scale': from_scale,
            'to_scale': to_scale,
            'data': data,
            'timestamp': time.time()
        }
        self.message_queues[(from_scale, to_scale)].append(message)
    
    def send_downward(
        self,
        from_scale: BiologicalScale,
        to_scale: BiologicalScale,
        data: Dict[str, Any]
    ) -> None:
        """Send information from higher to lower scale."""
        message = {
            'type': 'downward',
            'from_scale': from_scale,
            'to_scale': to_scale,
            'data': data,
            'timestamp': time.time()
        }
        self.message_queues[(from_scale, to_scale)].append(message)
    
    def process_messages(
        self,
        target_scale: BiologicalScale
    ) -> List[Dict[str, Any]]:
        """Process all messages for target scale."""
        processed_messages = []
        
        # Process messages from all scales to target scale
        for (from_scale, to_scale), queue in self.message_queues.items():
            if to_scale == target_scale and queue:
                message = queue.popleft()
                
                # Apply aggregation rules
                if message['type'] == 'upward':
                    processed_data = self._aggregate_upward_message(message)
                else:  # downward
                    processed_data = self._aggregate_downward_message(message)
                
                processed_messages.append({
                    'from_scale': from_scale,
                    'processed_data': processed_data,
                    'original_message': message
                })
        
        return processed_messages
    
    def _aggregate_upward_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate message going upward in scale."""
        data = message['data']
        
        # Example: average molecular concentrations to cellular level
        if 'concentrations' in data:
            data['concentrations'] = {
                k: np.mean(v) if isinstance(v, (list, np.ndarray)) else v
                for k, v in data['concentrations'].items()
            }
        
        return data
    
    def _aggregate_downward_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate message going downward in scale."""
        data = message['data']
        
        # Example: distribute tissue-level signals to individual cells
        if 'signal_strength' in data:
            # Add noise for realistic distribution
            noise = np.random.normal(0, 0.1)
            data['signal_strength'] = max(0, data['signal_strength'] + noise)
        
        return data
    
    def _upscale_average(self, values: List[float]) -> float:
        """Average values when upscaling."""
        return np.mean(values) if values else 0.0
    
    def _upscale_sum(self, values: List[float]) -> float:
        """Sum values when upscaling."""
        return np.sum(values)
    
    def _downscale_broadcast(self, value: float, n_targets: int) -> List[float]:
        """Broadcast single value to multiple targets."""
        return [value] * n_targets
    
    def _downscale_distribute(self, value: float, n_targets: int) -> List[float]:
        """Distribute value among targets with noise."""
        base_value = value / n_targets
        return [base_value + np.random.normal(0, base_value * 0.1) for _ in range(n_targets)]


class SimulationEngine:
    """Main simulation engine for hierarchical digital twin."""
    
    def __init__(self, parameters: SimulationParameters) -> None:
        self.parameters = parameters
        self.scale_manager = ScaleManager(parameters)
        self.communicator = CrossScaleCommunicator()
        
        # Entity management
        self.entities: Dict[str, DigitalTwinEntity] = {}
        self.entities_by_scale: Dict[BiologicalScale, List[str]] = defaultdict(list)
        
        # Simulation state
        self.current_time: float = 0.0
        self.simulation_history: List[Dict[str, Any]] = []
        self.consciousness_state: Dict[str, float] = {}
        
        # Performance tracking
        self.compute_times: Dict[BiologicalScale, List[float]] = defaultdict(list)
        self.entity_counts: Dict[BiologicalScale, int] = defaultdict(int)
    
    def add_entity(self, entity: DigitalTwinEntity) -> None:
        """Add entity to simulation."""
        self.entities[entity.id] = entity
        self.entities_by_scale[entity.scale].append(entity.id)
        self.entity_counts[entity.scale] += 1
        
        logger.debug(f"Added entity {entity.id} at scale {entity.scale.value}")
    
    def remove_entity(self, entity_id: str) -> None:
        """Remove entity from simulation."""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            self.entities_by_scale[entity.scale].remove(entity_id)
            self.entity_counts[entity.scale] -= 1
            del self.entities[entity_id]
            
            logger.debug(f"Removed entity {entity_id}")
    
    def step(self, dt: Optional[float] = None) -> Dict[str, Any]:
        """Execute one simulation step."""
        if dt is None:
            dt = self._compute_adaptive_timestep()
        
        step_start_time = time.time()
        step_stats = {}
        
        # Update entities at each scale
        for scale in BiologicalScale:
            scale_start_time = time.time()
            
            entity_ids = self.entities_by_scale[scale]
            if not entity_ids:
                continue
            
            # Get adaptive timestep for this scale
            scale_dt = min(dt, scale.time_scale)
            
            # Update entities at this scale
            scale_updates = self._update_scale_entities(scale, entity_ids, scale_dt)
            
            # Record computation time
            scale_compute_time = time.time() - scale_start_time
            self.compute_times[scale].append(scale_compute_time)
            
            step_stats[scale.value] = scale_updates
        
        # Handle cross-scale communication
        self._process_cross_scale_communication()
        
        # Update global consciousness state
        self._update_consciousness_state()
        
        # Update simulation time
        self.current_time += dt
        
        # Record step statistics
        total_step_time = time.time() - step_start_time
        step_info = {
            'simulation_time': self.current_time,
            'dt': dt,
            'compute_time': total_step_time,
            'entity_counts': dict(self.entity_counts),
            'scale_stats': step_stats,
            'consciousness_state': self.consciousness_state.copy()
        }
        
        self.simulation_history.append(step_info)
        
        return step_info
    
    def run_simulation(
        self,
        duration: float,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """Run simulation for specified duration."""
        with timer_context(f"HDTS simulation for {duration}s"):
            start_time = self.current_time
            step_count = 0
            
            while self.current_time - start_time < duration:
                step_info = self.step()
                step_count += 1
                
                # Call progress callback
                if progress_callback and step_count % 100 == 0:
                    progress = (self.current_time - start_time) / duration
                    progress_callback(progress, step_info)
                
                # Adaptive resolution updates
                if step_count % 1000 == 0:
                    self.scale_manager.adapt_resolution(list(self.entities.values()))
            
            logger.info(
                f"Simulation completed: {step_count} steps, "
                f"{len(self.entities)} entities across {len(BiologicalScale)} scales"
            )
            
            return self.simulation_history
    
    def _compute_adaptive_timestep(self) -> float:
        """Compute adaptive timestep based on system dynamics."""
        if not self.parameters.adaptive_time_stepping:
            return self.parameters.base_dt
        
        # Find smallest relevant timescale from active entities
        min_timescale = self.parameters.max_dt
        
        for scale, entity_ids in self.entities_by_scale.items():
            if entity_ids:  # Scale has active entities
                min_timescale = min(min_timescale, scale.time_scale)
        
        # Use fraction of smallest timescale
        dt = min_timescale * 0.1
        
        # Clamp to allowed range
        dt = max(self.parameters.base_dt, min(dt, self.parameters.max_dt))
        
        return dt
    
    def _update_scale_entities(
        self,
        scale: BiologicalScale,
        entity_ids: List[str],
        dt: float
    ) -> Dict[str, Any]:
        """Update all entities at given scale."""
        updates = {
            'entities_updated': len(entity_ids),
            'avg_activity': 0.0,
            'avg_health': 0.0,
            'total_awareness': 0.0
        }
        
        if not entity_ids:
            return updates
        
        # Environment for this scale
        environment = self._get_scale_environment(scale)
        
        # Update each entity
        activities = []
        healths = []
        awareness_levels = []
        
        for entity_id in entity_ids:
            entity = self.entities[entity_id]
            
            # Physics update
            forces = self._compute_entity_forces(entity, scale)
            entity.update_physics(dt, forces)
            
            # Biology update
            entity.update_biology(dt, environment)
            
            # Consciousness update
            entity.update_consciousness(dt, self.consciousness_state)
            
            # Collect statistics
            activities.append(entity.activity)
            healths.append(entity.health)
            awareness_levels.append(entity.awareness_level)
        
        # Compute scale statistics
        updates['avg_activity'] = np.mean(activities)
        updates['avg_health'] = np.mean(healths)
        updates['total_awareness'] = np.sum(awareness_levels)
        
        return updates
    
    def _get_scale_environment(self, scale: BiologicalScale) -> Dict[str, float]:
        """Get environmental conditions for scale."""
        # Base environment
        environment = {
            'temperature': self.parameters.temperature,
            'nutrients': 1.0,
            'oxygen': 0.21,  # Atmospheric fraction
            'ph': 7.4,       # Physiological pH
            'pressure': 101325.0  # Pa, atmospheric pressure
        }
        
        # Scale-specific modifications
        if scale == BiologicalScale.L0_MOLECULAR:
            # Molecular environment - high local variation
            environment['nutrients'] *= np.random.uniform(0.5, 1.5)
            environment['ph'] += np.random.normal(0, 0.1)
            
        elif scale == BiologicalScale.L1_SUBCELLULAR:
            # Subcellular - organelle-specific conditions
            environment['nutrients'] *= 0.8  # Limited by transport
            
        elif scale == BiologicalScale.L2_CELLULAR:
            # Cellular - cell-type specific
            environment['oxygen'] *= np.random.uniform(0.8, 1.2)
            
        # Add temporal variations
        time_factor = np.sin(self.current_time / 3600) * 0.1  # Hourly cycle
        environment['nutrients'] *= (1.0 + time_factor)
        
        return environment
    
    def _compute_entity_forces(
        self,
        entity: DigitalTwinEntity,
        scale: BiologicalScale
    ) -> np.ndarray:
        """Compute forces acting on entity."""
        forces = np.zeros(3)
        
        # Brownian motion (thermal fluctuations)
        kT = 1.38e-23 * self.parameters.temperature  # Thermal energy
        brownian_force = np.random.normal(0, np.sqrt(2 * kT / entity.mass), 3)
        forces += brownian_force
        
        # Interaction forces with other entities
        for other_id in self.entities_by_scale[scale]:
            if other_id != entity.id:
                other = self.entities[other_id]
                
                # Simple repulsive force at short range
                r_vec = entity.position - other.position
                r = np.linalg.norm(r_vec)
                
                if r > 0 and r < entity.size + other.size:
                    # Repulsive force
                    force_magnitude = 1e-12 / (r ** 2)  # Simple inverse square
                    force_direction = r_vec / r
                    forces += force_magnitude * force_direction
        
        # Viscous drag
        drag_coefficient = 6 * np.pi * self.parameters.viscosity * entity.size
        drag_force = -drag_coefficient * entity.velocity
        forces += drag_force
        
        return forces
    
    def _process_cross_scale_communication(self) -> None:
        """Process communication between scales."""
        # Send information upward (aggregation)
        for scale in BiologicalScale:
            entity_ids = self.entities_by_scale[scale]
            if not entity_ids:
                continue
            
            # Collect scale statistics
            entities = [self.entities[eid] for eid in entity_ids]
            scale_data = {
                'avg_activity': np.mean([e.activity for e in entities]),
                'avg_health': np.mean([e.health for e in entities]),
                'total_awareness': np.sum([e.awareness_level for e in entities]),
                'entity_count': len(entities)
            }
            
            # Send to higher scales
            scale_index = list(BiologicalScale).index(scale)
            for i in range(scale_index + 1, len(BiologicalScale)):
                higher_scale = list(BiologicalScale)[i]
                self.communicator.send_upward(scale, higher_scale, scale_data)
        
        # Process downward communication (distribution)
        for scale in reversed(list(BiologicalScale)):
            messages = self.communicator.process_messages(scale)
            
            for message in messages:
                # Apply message effects to entities at this scale
                entity_ids = self.entities_by_scale[scale]
                for entity_id in entity_ids:
                    entity = self.entities[entity_id]
                    
                    # Example: higher-scale signals affect activity
                    if 'avg_activity' in message['processed_data']:
                        signal_strength = message['processed_data']['avg_activity']
                        entity.activity = 0.9 * entity.activity + 0.1 * signal_strength
    
    def _update_consciousness_state(self) -> None:
        """Update global consciousness state."""
        # Collect consciousness contributions from all entities
        total_awareness = 0.0
        total_information = 0.0
        entity_count = 0
        
        for entity in self.entities.values():
            total_awareness += entity.awareness_level
            total_information += entity.information_content
            entity_count += 1
        
        if entity_count > 0:
            self.consciousness_state = {
                'total_awareness': total_awareness,
                'avg_awareness': total_awareness / entity_count,
                'total_information': total_information,
                'avg_information': total_information / entity_count,
                'consciousness_index': self._compute_consciousness_index(),
                'integration_level': self._compute_integration_level(),
                'emergence_indicator': self._compute_emergence_indicator()
            }
        else:
            self.consciousness_state = {key: 0.0 for key in ['total_awareness', 'avg_awareness', 
                                                            'total_information', 'avg_information',
                                                            'consciousness_index', 'integration_level',
                                                            'emergence_indicator']}
    
    def _compute_consciousness_index(self) -> float:
        """Compute global consciousness index."""
        if not self.entities:
            return 0.0
        
        # Weighted consciousness based on scale hierarchy
        weighted_consciousness = 0.0
        total_weight = 0.0
        
        for scale in BiologicalScale:
            entity_ids = self.entities_by_scale[scale]
            if not entity_ids:
                continue
            
            # Higher scales contribute more to consciousness
            scale_weight = list(BiologicalScale).index(scale) + 1
            
            scale_consciousness = sum(
                self.entities[eid].awareness_level for eid in entity_ids
            )
            
            weighted_consciousness += scale_weight * scale_consciousness
            total_weight += scale_weight * len(entity_ids)
        
        return weighted_consciousness / total_weight if total_weight > 0 else 0.0
    
    def _compute_integration_level(self) -> float:
        """Compute information integration level."""
        # Measure connectivity across scales
        cross_scale_connections = 0
        total_possible_connections = 0
        
        for scale in BiologicalScale:
            entity_ids = self.entities_by_scale[scale]
            
            for entity_id in entity_ids:
                entity = self.entities[entity_id]
                
                # Count connections to other scales
                for connection_id in entity.connections:
                    if connection_id in self.entities:
                        connected_entity = self.entities[connection_id]
                        if connected_entity.scale != scale:
                            cross_scale_connections += 1
                
                # Possible connections to other scales
                other_scales_entities = sum(
                    len(self.entities_by_scale[s]) for s in BiologicalScale if s != scale
                )
                total_possible_connections += other_scales_entities
        
        return cross_scale_connections / total_possible_connections if total_possible_connections > 0 else 0.0
    
    def _compute_emergence_indicator(self) -> float:
        """Compute emergence indicator."""
        # Look for non-linear relationships between scales
        if len(self.simulation_history) < 10:
            return 0.0
        
        # Get recent consciousness states
        recent_states = self.simulation_history[-10:]
        consciousness_values = [state['consciousness_state']['consciousness_index'] for state in recent_states]
        
        # Compute rate of change and acceleration
        if len(consciousness_values) >= 3:
            velocities = np.diff(consciousness_values)
            accelerations = np.diff(velocities)
            
            # Emergence indicated by positive acceleration in consciousness
            emergence = np.mean(accelerations) if len(accelerations) > 0 else 0.0
            return max(0.0, emergence)
        
        return 0.0


class HDTS:
    """Hierarchical Digital Twin Simulator main class."""
    
    def __init__(
        self,
        parameters: Optional[SimulationParameters] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize HDTS system."""
        self.config = config or get_config().hdts
        
        if parameters is None:
            parameters = SimulationParameters(
                adaptive_threshold=self.config.get("adaptive_threshold", 0.1),
                base_dt=self.config.get("base_dt", 1e-6),
                temperature=self.config.get("temperature", 310.0)
            )
        
        self.parameters = parameters
        self.engine = SimulationEngine(parameters)
        
        logger.info(f"Initialized HDTS with parameters: {parameters}")
    
    def create_biological_system(
        self,
        embedding: LatentEmbedding,
        system_type: str = "neural_network"
    ) -> Dict[str, Any]:
        """Create biological system from embedding."""
        with timer_context(f"Creating {system_type} system"):
            # Extract entities from embedding
            entities = self._embedding_to_entities(embedding, system_type)
            
            # Add entities to simulation
            for entity in entities:
                self.engine.add_entity(entity)
            
            # Create connections based on embedding relationships
            self._create_entity_connections(entities, embedding)
            
            system_info = {
                'system_type': system_type,
                'num_entities': len(entities),
                'scales_used': list(set(entity.scale for entity in entities)),
                'total_awareness': sum(entity.awareness_level for entity in entities),
                'creation_time': time.time()
            }
            
            logger.info(f"Created biological system: {system_info}")
            return system_info
    
    def simulate_consciousness_emergence(
        self,
        duration: float,
        perturbations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Simulate consciousness emergence over time."""
        with timer_context(f"Simulating consciousness emergence for {duration}s"):
            # Apply perturbations if specified
            if perturbations:
                self._apply_perturbations(perturbations)
            
            # Run simulation
            history = self.engine.run_simulation(duration)
            
            # Analyze consciousness emergence
            analysis = self._analyze_consciousness_emergence(history)
            
            result = {
                'simulation_duration': duration,
                'final_consciousness_state': self.engine.consciousness_state,
                'emergence_analysis': analysis,
                'simulation_history': history[-100:]  # Keep last 100 steps
            }
            
            logger.info(f"Consciousness simulation complete: {analysis}")
            return result
    
    def analyze_multi_scale_dynamics(self) -> Dict[str, Any]:
        """Analyze dynamics across all scales."""
        with timer_context("Analyzing multi-scale dynamics"):
            analysis = {}
            
            for scale in BiologicalScale:
                entity_ids = self.engine.entities_by_scale[scale]
                if not entity_ids:
                    continue
                
                entities = [self.engine.entities[eid] for eid in entity_ids]
                
                scale_analysis = {
                    'entity_count': len(entities),
                    'avg_activity': np.mean([e.activity for e in entities]),
                    'avg_health': np.mean([e.health for e in entities]),
                    'total_awareness': np.sum([e.awareness_level for e in entities]),
                    'avg_age': np.mean([e.age for e in entities]),
                    'spatial_distribution': self._analyze_spatial_distribution(entities),
                    'temporal_dynamics': self._analyze_temporal_dynamics(entities, scale)
                }
                
                analysis[scale.value] = scale_analysis
            
            # Cross-scale analysis
            analysis['cross_scale'] = {
                'integration_level': self.engine.consciousness_state.get('integration_level', 0.0),
                'emergence_indicator': self.engine.consciousness_state.get('emergence_indicator', 0.0),
                'scale_coupling': self._compute_scale_coupling(),
                'information_flow': self._compute_information_flow_metrics()
            }
            
            return analysis
    
    def _embedding_to_entities(
        self,
        embedding: LatentEmbedding,
        system_type: str
    ) -> List[DigitalTwinEntity]:
        """Convert embedding to digital twin entities."""
        entities = []
        
        # Determine scales for entities based on embedding
        embedding_ids = list(embedding.embeddings.keys())
        n_entities = len(embedding_ids)
        
        # Distribute entities across scales
        if system_type == "neural_network":
            # Neural network: mostly L0-L2 scales
            scale_distribution = [0.4, 0.3, 0.2, 0.1, 0.0, 0.0]
        elif system_type == "metabolic_network":
            # Metabolic: L0-L3 scales
            scale_distribution = [0.5, 0.3, 0.15, 0.05, 0.0, 0.0]
        else:
            # Uniform distribution
            scale_distribution = [1/6] * 6
        
        scales = list(BiologicalScale)
        
        for i, entity_id in enumerate(embedding_ids):
            # Assign scale based on distribution
            scale_idx = np.random.choice(len(scales), p=scale_distribution)
            scale = scales[scale_idx]
            
            # Get embedding vector
            embedding_vec = np.array(embedding.embeddings[entity_id])
            
            # Create entity
            entity = DigitalTwinEntity(
                id=entity_id,
                entity_type=self._infer_entity_type(entity_id, scale),
                scale=scale,
                position=np.random.uniform(-1e-3, 1e-3, 3),  # Random initial position
                state_vector=embedding_vec[:10] if len(embedding_vec) >= 10 else np.pad(embedding_vec, (0, 10-len(embedding_vec))),
                mass=self._estimate_entity_mass(scale),
                size=scale.length_scale,
                activity=np.random.uniform(0.5, 1.0),
                awareness_level=np.random.uniform(0.0, 0.1)
            )
            
            entities.append(entity)
        
        return entities
    
    def _infer_entity_type(self, entity_id: str, scale: BiologicalScale) -> str:
        """Infer entity type from ID and scale."""
        type_mappings = {
            BiologicalScale.L0_MOLECULAR: "protein",
            BiologicalScale.L1_SUBCELLULAR: "organelle",
            BiologicalScale.L2_CELLULAR: "cell",
            BiologicalScale.L3_TISSUE: "tissue",
            BiologicalScale.L4_ORGANISM: "organ",
            BiologicalScale.L5_POPULATION: "organism"
        }
        
        return type_mappings.get(scale, "unknown")
    
    def _estimate_entity_mass(self, scale: BiologicalScale) -> float:
        """Estimate entity mass based on scale."""
        mass_mappings = {
            BiologicalScale.L0_MOLECULAR: 1e-15,      # kg, typical protein
            BiologicalScale.L1_SUBCELLULAR: 1e-12,   # kg, organelle
            BiologicalScale.L2_CELLULAR: 1e-9,       # kg, cell
            BiologicalScale.L3_TISSUE: 1e-6,         # kg, tissue sample
            BiologicalScale.L4_ORGANISM: 70.0,       # kg, human
            BiologicalScale.L5_POPULATION: 70.0 * 1000  # kg, population
        }
        
        return mass_mappings.get(scale, 1e-15)
    
    def _create_entity_connections(
        self,
        entities: List[DigitalTwinEntity],
        embedding: LatentEmbedding
    ) -> None:
        """Create connections between entities based on embedding similarities."""
        entity_dict = {entity.id: entity for entity in entities}
        
        # Compute similarities and create connections
        embedding_ids = list(embedding.embeddings.keys())
        embeddings_matrix = np.array([embedding.embeddings[eid] for eid in embedding_ids])
        
        # Compute pairwise similarities
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(embeddings_matrix)
        
        # Create connections for high similarity pairs
        threshold = 0.7
        for i, entity_id in enumerate(embedding_ids):
            if entity_id not in entity_dict:
                continue
            
            entity = entity_dict[entity_id]
            
            for j, other_id in enumerate(embedding_ids):
                if i != j and other_id in entity_dict and similarities[i, j] > threshold:
                    entity.connections.append(other_id)
    
    def _apply_perturbations(self, perturbations: List[Dict[str, Any]]) -> None:
        """Apply perturbations to the system."""
        for perturbation in perturbations:
            if perturbation['type'] == 'activity_boost':
                # Boost activity of random entities
                target_entities = np.random.choice(
                    list(self.engine.entities.keys()),
                    size=perturbation.get('num_targets', 10),
                    replace=False
                )
                
                for entity_id in target_entities:
                    entity = self.engine.entities[entity_id]
                    entity.activity = min(1.0, entity.activity * perturbation.get('factor', 1.5))
            
            elif perturbation['type'] == 'consciousness_stimulus':
                # Increase awareness levels
                for entity in self.engine.entities.values():
                    entity.awareness_level = min(1.0, entity.awareness_level + perturbation.get('boost', 0.1))
    
    def _analyze_consciousness_emergence(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze consciousness emergence from simulation history."""
        if not history:
            return {}
        
        # Extract consciousness metrics over time
        consciousness_indices = [step['consciousness_state']['consciousness_index'] for step in history]
        integration_levels = [step['consciousness_state']['integration_level'] for step in history]
        emergence_indicators = [step['consciousness_state']['emergence_indicator'] for step in history]
        
        analysis = {
            'final_consciousness_index': consciousness_indices[-1],
            'consciousness_growth_rate': np.mean(np.diff(consciousness_indices)) if len(consciousness_indices) > 1 else 0.0,
            'max_consciousness_achieved': np.max(consciousness_indices),
            'integration_progression': {
                'initial': integration_levels[0],
                'final': integration_levels[-1],
                'max': np.max(integration_levels)
            },
            'emergence_events': sum(1 for e in emergence_indicators if e > 0.01),
            'emergence_threshold_reached': any(c > 0.5 for c in consciousness_indices)
        }
        
        return analysis
    
    def _analyze_spatial_distribution(self, entities: List[DigitalTwinEntity]) -> Dict[str, float]:
        """Analyze spatial distribution of entities."""
        if not entities:
            return {}
        
        positions = np.array([entity.position for entity in entities])
        
        return {
            'centroid': np.mean(positions, axis=0).tolist(),
            'spread': np.std(positions, axis=0).mean(),
            'max_distance': np.max([np.linalg.norm(pos - positions[0]) for pos in positions]),
            'density': len(entities) / (np.prod(np.ptp(positions, axis=0)) + 1e-10)
        }
    
    def _analyze_temporal_dynamics(
        self,
        entities: List[DigitalTwinEntity],
        scale: BiologicalScale
    ) -> Dict[str, float]:
        """Analyze temporal dynamics at scale."""
        if not entities:
            return {}
        
        activities = [entity.activity for entity in entities]
        ages = [entity.age for entity in entities]
        
        return {
            'activity_variance': np.var(activities),
            'avg_age': np.mean(ages),
            'age_spread': np.std(ages),
            'characteristic_timescale': scale.time_scale
        }
    
    def _compute_scale_coupling(self) -> float:
        """Compute coupling strength between scales."""
        # Measure how much information flows between scales
        total_coupling = 0.0
        coupling_count = 0
        
        scales = list(BiologicalScale)
        for i, scale1 in enumerate(scales):
            for j, scale2 in enumerate(scales):
                if i != j:
                    # Measure connections between scales
                    entities1 = self.engine.entities_by_scale[scale1]
                    entities2 = self.engine.entities_by_scale[scale2]
                    
                    if entities1 and entities2:
                        cross_connections = 0
                        for entity_id in entities1:
                            entity = self.engine.entities[entity_id]
                            cross_connections += sum(1 for conn in entity.connections if conn in entities2)
                        
                        coupling = cross_connections / (len(entities1) * len(entities2))
                        total_coupling += coupling
                        coupling_count += 1
        
        return total_coupling / coupling_count if coupling_count > 0 else 0.0
    
    def _compute_information_flow_metrics(self) -> Dict[str, float]:
        """Compute information flow metrics."""
        # Simplified information flow analysis
        total_info = sum(entity.information_content for entity in self.engine.entities.values())
        total_awareness = sum(entity.awareness_level for entity in self.engine.entities.values())
        
        return {
            'total_information': total_info,
            'total_awareness': total_awareness,
            'information_density': total_info / len(self.engine.entities) if self.engine.entities else 0.0,
            'awareness_density': total_awareness / len(self.engine.entities) if self.engine.entities else 0.0
        }
    
    def __repr__(self) -> str:
        """String representation of HDTS."""
        total_entities = len(self.engine.entities)
        active_scales = len([s for s in BiologicalScale if self.engine.entities_by_scale[s]])
        return f"HDTS({total_entities} entities, {active_scales} active scales, t={self.engine.current_time:.3f}s)"
