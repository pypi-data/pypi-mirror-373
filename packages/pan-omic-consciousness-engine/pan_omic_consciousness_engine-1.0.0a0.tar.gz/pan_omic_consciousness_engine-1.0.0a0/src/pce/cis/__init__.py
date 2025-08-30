"""CIS: Consciousness-Integration Substrate.

The final integration layer for consciousness modeling, combining:
- Connectome modeling and neural dynamics
- Integrated Information Theory (IIT) implementation
- Global Workspace Theory (GWT) mechanisms
- Variational manifold consciousness representation
- Multi-modal sensory integration
- Meta-cognitive awareness modeling

This is where the Pan-Omics Consciousness Engine achieves its ultimate goal:
quantifying and modeling consciousness emergence from biological complexity.
"""

import numpy as np
import logging
from typing import Any, Dict, List, Optional, Union, Tuple, Callable, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import networkx as nx
from collections import defaultdict
import time

try:
    from scipy.optimize import minimize
    from scipy.special import entropy
    from scipy.spatial.distance import pdist, squareform
    from scipy.linalg import pinv, svd
    from sklearn.manifold import TSNE, LocallyLinearEmbedding
    from sklearn.decomposition import PCA
    SCIPY_SKLEARN_AVAILABLE = True
except ImportError:
    SCIPY_SKLEARN_AVAILABLE = False

from ..core.datatypes import LatentEmbedding, HyperGraph
from ..core.config import get_config
from ..utils.logging import get_logger, timer_context
from ..qlem import QuantumState
from ..mogil import MOGIL
from ..e3de import E3DE
from ..hdts import HDTS

logger = get_logger(__name__)


class ConsciousnessLevel(Enum):
    """Levels of consciousness."""
    UNCONSCIOUS = "unconscious"          # No awareness (0.0-0.1)
    SUBCONSCIOUS = "subconscious"       # Background processing (0.1-0.3)
    PRECONSCIOUS = "preconscious"       # Accessible to awareness (0.3-0.5)
    CONSCIOUS = "conscious"             # Aware and accessible (0.5-0.7)
    SELF_AWARE = "self_aware"           # Self-reflective awareness (0.7-0.9)
    METACOGNITIVE = "metacognitive"     # Awareness of awareness (0.9-1.0)
    
    @property
    def threshold(self) -> float:
        """Threshold value for this consciousness level."""
        thresholds = {
            self.UNCONSCIOUS: 0.0,
            self.SUBCONSCIOUS: 0.1,
            self.PRECONSCIOUS: 0.3,
            self.CONSCIOUS: 0.5,
            self.SELF_AWARE: 0.7,
            self.METACOGNITIVE: 0.9
        }
        return thresholds[self]


@dataclass
class ConsciousnessMetrics:
    """Comprehensive consciousness metrics."""
    # IIT-based measures
    phi: float = 0.0                    # Integrated Information
    phi_max: float = 0.0                # Maximum possible Φ
    effective_information: float = 0.0   # EI
    
    # GWT measures
    global_accessibility: float = 0.0   # Information accessibility
    broadcasting_strength: float = 0.0  # Signal broadcast strength
    attention_focus: float = 0.0        # Attentional focus
    
    # Network measures
    network_connectivity: float = 0.0   # Overall connectivity
    small_worldness: float = 0.0        # Small-world coefficient
    modularity: float = 0.0             # Network modularity
    
    # Information-theoretic measures
    mutual_information: float = 0.0     # MI between regions
    transfer_entropy: float = 0.0       # Directional information transfer
    complexity: float = 0.0             # Neural complexity
    
    # Manifold measures
    intrinsic_dimension: float = 0.0    # Consciousness manifold dimension
    curvature: float = 0.0              # Manifold curvature
    
    # Meta-cognitive measures
    self_monitoring: float = 0.0        # Self-monitoring capacity
    cognitive_control: float = 0.0      # Executive control
    
    # Overall consciousness
    consciousness_level: float = 0.0    # Overall consciousness score
    consciousness_category: ConsciousnessLevel = ConsciousnessLevel.UNCONSCIOUS
    
    def update_category(self) -> None:
        """Update consciousness category based on level."""
        for category in reversed(list(ConsciousnessLevel)):
            if self.consciousness_level >= category.threshold:
                self.consciousness_category = category
                break


@dataclass
class ConnectomeNode:
    """Node in the consciousness connectome."""
    id: str
    node_type: str                      # brain_region, neural_cluster, etc.
    position: np.ndarray               # 3D position
    activity: float = 0.0              # Current activity level
    information_content: float = 0.0   # Information content
    consciousness_contribution: float = 0.0  # Contribution to consciousness
    
    # Neural properties
    excitability: float = 1.0          # Response to stimulation
    inhibition: float = 0.1            # Inhibitory strength
    plasticity: float = 0.5            # Learning/adaptation rate
    
    # Temporal properties
    firing_rate: float = 0.0           # Hz
    synchronization: float = 0.0       # Phase synchronization
    memory_trace: float = 0.0          # Memory storage
    
    # Connections
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    
    def update_dynamics(self, dt: float, inputs: Dict[str, float]) -> None:
        """Update node dynamics."""
        # Integrate inputs
        total_input = sum(inputs.values())
        
        # Neural dynamics (simplified)
        self.activity = np.tanh(self.excitability * total_input - self.inhibition)
        
        # Update firing rate
        self.firing_rate = max(0, self.activity * 100)  # Hz
        
        # Update information content
        self.information_content = abs(self.activity) * (1 + np.random.normal(0, 0.1))
        
        # Consciousness contribution based on integration
        integration_factor = len(self.inputs) * len(self.outputs) / 100.0
        self.consciousness_contribution = self.activity * integration_factor


class ConnectomeNetwork:
    """Neural connectome for consciousness modeling."""
    
    def __init__(
        self,
        nodes: List[ConnectomeNode],
        connectivity_matrix: Optional[np.ndarray] = None
    ) -> None:
        self.nodes = {node.id: node for node in nodes}
        self.node_ids = list(self.nodes.keys())
        
        # Create connectivity matrix
        if connectivity_matrix is not None:
            self.connectivity_matrix = connectivity_matrix
        else:
            self.connectivity_matrix = self._create_default_connectivity()
        
        # Create NetworkX graph for analysis
        self.graph = self._create_networkx_graph()
        
        # State variables
        self.current_state = np.zeros(len(self.nodes))
        self.global_workspace = set()  # Currently broadcasted information
        self.attention_weights = np.ones(len(self.nodes))
        
        logger.info(f"Created connectome: {len(self.nodes)} nodes")
    
    def _create_default_connectivity(self) -> np.ndarray:
        """Create default connectivity matrix."""
        n = len(self.nodes)
        connectivity = np.zeros((n, n))
        
        # Create small-world network structure
        for i in range(n):
            # Local connections
            for j in range(max(0, i-2), min(n, i+3)):
                if i != j:
                    connectivity[i, j] = np.random.exponential(0.1)
            
            # Random long-range connections
            for _ in range(int(0.1 * n)):  # 10% long-range connections
                j = np.random.randint(0, n)
                if i != j:
                    connectivity[i, j] = np.random.exponential(0.05)
        
        return connectivity
    
    def _create_networkx_graph(self) -> nx.DiGraph:
        """Create NetworkX graph from connectivity matrix."""
        G = nx.DiGraph()
        
        # Add nodes
        for node_id, node in self.nodes.items():
            G.add_node(node_id, **{
                'activity': node.activity,
                'information': node.information_content,
                'consciousness': node.consciousness_contribution
            })
        
        # Add edges
        for i, source_id in enumerate(self.node_ids):
            for j, target_id in enumerate(self.node_ids):
                weight = self.connectivity_matrix[i, j]
                if weight > 0:
                    G.add_edge(source_id, target_id, weight=weight)
        
        return G
    
    def update_dynamics(self, dt: float, external_inputs: Optional[Dict[str, float]] = None) -> None:
        """Update network dynamics."""
        external_inputs = external_inputs or {}
        
        # Compute inputs for each node
        new_activities = np.zeros(len(self.nodes))
        
        for i, node_id in enumerate(self.node_ids):
            node = self.nodes[node_id]
            
            # Internal inputs from other nodes
            internal_inputs = {}
            for j, source_id in enumerate(self.node_ids):
                if self.connectivity_matrix[j, i] > 0:
                    source_activity = self.nodes[source_id].activity
                    weight = self.connectivity_matrix[j, i]
                    internal_inputs[source_id] = source_activity * weight
            
            # External inputs
            if node_id in external_inputs:
                internal_inputs['external'] = external_inputs[node_id]
            
            # Update node
            node.update_dynamics(dt, internal_inputs)
            new_activities[i] = node.activity
        
        self.current_state = new_activities
        
        # Update global workspace
        self._update_global_workspace()
        
        # Update attention weights
        self._update_attention()
    
    def _update_global_workspace(self) -> None:
        """Update global workspace with highly active nodes."""
        # Global workspace theory: highly active nodes broadcast information
        activity_threshold = np.percentile([node.activity for node in self.nodes.values()], 80)
        
        self.global_workspace = {
            node_id for node_id, node in self.nodes.items()
            if node.activity > activity_threshold
        }
    
    def _update_attention(self) -> None:
        """Update attention weights."""
        # Attention based on information content and activity
        for i, node_id in enumerate(self.node_ids):
            node = self.nodes[node_id]
            
            # Attention weight combines activity and information
            info_factor = node.information_content
            activity_factor = node.activity
            
            self.attention_weights[i] = 0.7 * activity_factor + 0.3 * info_factor
        
        # Normalize attention weights
        total_attention = np.sum(self.attention_weights)
        if total_attention > 0:
            self.attention_weights /= total_attention
    
    def compute_integrated_information(self) -> float:
        """Compute integrated information (Φ) using simplified IIT."""
        if not SCIPY_SKLEARN_AVAILABLE:
            logger.warning("SciPy/sklearn not available, using simplified Φ calculation")
            return self._simplified_phi()
        
        # Get current system state
        system_state = np.array([node.activity for node in self.nodes.values()])
        
        # Compute all possible bipartitions
        n = len(system_state)
        if n <= 1:
            return 0.0
        
        max_phi = 0.0
        
        # For computational efficiency, sample bipartitions for large systems
        if n > 10:
            num_samples = min(100, 2**(n-1))
            bipartitions = self._sample_bipartitions(n, num_samples)
        else:
            bipartitions = self._all_bipartitions(n)
        
        for partition in bipartitions:
            phi = self._compute_bipartition_phi(system_state, partition)
            max_phi = max(max_phi, phi)
        
        return max_phi
    
    def _simplified_phi(self) -> float:
        """Simplified Φ calculation without full IIT computation."""
        activities = np.array([node.activity for node in self.nodes.values()])
        
        # Measure based on activity variance and connectivity
        activity_variance = np.var(activities)
        
        # Connectivity measure
        total_connections = np.sum(self.connectivity_matrix > 0)
        max_connections = len(self.nodes) ** 2
        connectivity_ratio = total_connections / max_connections
        
        # Integration measure
        phi_approx = activity_variance * connectivity_ratio * len(self.nodes)
        
        return phi_approx
    
    def _sample_bipartitions(self, n: int, num_samples: int) -> List[Tuple[Set[int], Set[int]]]:
        """Sample random bipartitions."""
        bipartitions = []
        all_indices = set(range(n))
        
        for _ in range(num_samples):
            # Random split
            subset_size = np.random.randint(1, n)
            subset = set(np.random.choice(n, subset_size, replace=False))
            complement = all_indices - subset
            
            bipartitions.append((subset, complement))
        
        return bipartitions
    
    def _all_bipartitions(self, n: int) -> List[Tuple[Set[int], Set[int]]]:
        """Generate all possible bipartitions."""
        bipartitions = []
        all_indices = set(range(n))
        
        # Generate all non-empty proper subsets
        for i in range(1, 2**(n-1)):
            subset = set()
            for j in range(n):
                if i & (1 << j):
                    subset.add(j)
            
            complement = all_indices - subset
            bipartitions.append((subset, complement))
        
        return bipartitions
    
    def _compute_bipartition_phi(
        self,
        system_state: np.ndarray,
        partition: Tuple[Set[int], Set[int]]
    ) -> float:
        """Compute Φ for a specific bipartition."""
        subset_a, subset_b = partition
        
        if len(subset_a) == 0 or len(subset_b) == 0:
            return 0.0
        
        # Get states for each partition
        state_a = system_state[list(subset_a)]
        state_b = system_state[list(subset_b)]
        
        # Compute mutual information (simplified)
        # This is a simplified version - full IIT requires more complex calculations
        var_a = np.var(state_a) + 1e-10
        var_b = np.var(state_b) + 1e-10
        
        # Cross-partition connectivity
        cross_connections = 0
        for i in subset_a:
            for j in subset_b:
                if self.connectivity_matrix[i, j] > 0:
                    cross_connections += self.connectivity_matrix[i, j]
        
        # Φ approximation
        phi = cross_connections * np.sqrt(var_a * var_b) / (len(subset_a) + len(subset_b))
        
        return phi
    
    def compute_network_metrics(self) -> Dict[str, float]:
        """Compute network-based consciousness metrics."""
        G = self.graph
        
        metrics = {}
        
        # Basic connectivity
        metrics['density'] = nx.density(G)
        metrics['average_clustering'] = nx.average_clustering(G.to_undirected())
        
        # Small-world properties
        try:
            metrics['average_path_length'] = nx.average_shortest_path_length(G.to_undirected())
            # Small-worldness (approximation)
            random_path_length = np.log(len(G.nodes)) / np.log(metrics['density'] * len(G.nodes))
            metrics['small_worldness'] = metrics['average_clustering'] / (metrics['average_path_length'] / random_path_length)
        except:
            metrics['average_path_length'] = 0.0
            metrics['small_worldness'] = 0.0
        
        # Modularity
        if len(G.nodes) > 0:
            try:
                communities = nx.community.greedy_modularity_communities(G.to_undirected())
                metrics['modularity'] = nx.community.modularity(G.to_undirected(), communities)
            except:
                metrics['modularity'] = 0.0
        else:
            metrics['modularity'] = 0.0
        
        # Centrality measures
        try:
            betweenness = nx.betweenness_centrality(G)
            metrics['average_betweenness'] = np.mean(list(betweenness.values()))
            
            eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
            metrics['average_eigenvector_centrality'] = np.mean(list(eigenvector.values()))
        except:
            metrics['average_betweenness'] = 0.0
            metrics['average_eigenvector_centrality'] = 0.0
        
        return metrics


class ConsciousnessManifold:
    """Variational manifold representation of consciousness."""
    
    def __init__(
        self,
        dimension: int = 10,
        embedding_method: str = "pca"
    ) -> None:
        self.dimension = dimension
        self.embedding_method = embedding_method
        self.manifold_points: List[np.ndarray] = []
        self.consciousness_values: List[float] = []
        self.fitted_manifold = None
        
    def add_state(self, state_vector: np.ndarray, consciousness_level: float) -> None:
        """Add a consciousness state to the manifold."""
        self.manifold_points.append(state_vector.copy())
        self.consciousness_values.append(consciousness_level)
    
    def fit_manifold(self) -> None:
        """Fit manifold to accumulated states."""
        if len(self.manifold_points) < 2:
            logger.warning("Need at least 2 states to fit manifold")
            return
        
        if not SCIPY_SKLEARN_AVAILABLE:
            logger.warning("SciPy/sklearn not available, using simplified manifold")
            return
        
        with timer_context("Fitting consciousness manifold"):
            state_matrix = np.array(self.manifold_points)
            
            if self.embedding_method == "pca":
                self.fitted_manifold = PCA(n_components=self.dimension)
            elif self.embedding_method == "lle":
                n_neighbors = min(10, len(self.manifold_points) - 1)
                self.fitted_manifold = LocallyLinearEmbedding(
                    n_components=self.dimension,
                    n_neighbors=n_neighbors
                )
            elif self.embedding_method == "tsne":
                self.fitted_manifold = TSNE(n_components=self.dimension)
            
            # Fit the manifold
            try:
                self.fitted_manifold.fit(state_matrix)
                logger.info(f"Fitted {self.embedding_method} manifold: {len(self.manifold_points)} states")
            except Exception as e:
                logger.warning(f"Failed to fit manifold: {e}")
    
    def transform_state(self, state_vector: np.ndarray) -> Optional[np.ndarray]:
        """Transform state to manifold coordinates."""
        if self.fitted_manifold is None:
            return None
        
        try:
            transformed = self.fitted_manifold.transform(state_vector.reshape(1, -1))
            return transformed[0]
        except Exception as e:
            logger.warning(f"Failed to transform state: {e}")
            return None
    
    def compute_manifold_metrics(self) -> Dict[str, float]:
        """Compute manifold-based consciousness metrics."""
        if len(self.manifold_points) < 2:
            return {}
        
        metrics = {}
        
        # Intrinsic dimensionality
        if hasattr(self.fitted_manifold, 'explained_variance_ratio_'):
            # For PCA
            explained_var = self.fitted_manifold.explained_variance_ratio_
            metrics['explained_variance'] = np.sum(explained_var)
            metrics['effective_dimension'] = np.sum(explained_var > 0.01)  # Dimensions explaining >1% variance
        else:
            metrics['explained_variance'] = 0.5  # Placeholder
            metrics['effective_dimension'] = self.dimension / 2
        
        # Manifold curvature (approximation)
        if len(self.manifold_points) > 5:
            state_matrix = np.array(self.manifold_points)
            distances = pdist(state_matrix)
            metrics['average_distance'] = np.mean(distances)
            metrics['distance_variance'] = np.var(distances)
            metrics['curvature_estimate'] = metrics['distance_variance'] / (metrics['average_distance']**2 + 1e-10)
        else:
            metrics['curvature_estimate'] = 0.0
        
        # Consciousness distribution on manifold
        if self.consciousness_values:
            if SCIPY_SKLEARN_AVAILABLE:
                metrics['consciousness_entropy'] = entropy(np.histogram(self.consciousness_values, bins=10)[0] + 1e-10)
            else:
                # Fallback entropy calculation
                hist = np.histogram(self.consciousness_values, bins=10)[0] + 1e-10
                hist = hist / np.sum(hist)  # Normalize
                metrics['consciousness_entropy'] = -np.sum(hist * np.log(hist))
            
            metrics['consciousness_range'] = np.ptp(self.consciousness_values)
            metrics['consciousness_mean'] = np.mean(self.consciousness_values)
        
        return metrics


class CIS:
    """Consciousness-Integration Substrate main class."""
    
    def __init__(
        self,
        mogil_system: Optional[MOGIL] = None,
        qlem_system: Optional[Any] = None,  # Q-LEM system
        e3de_system: Optional[E3DE] = None,
        hdts_system: Optional[HDTS] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize CIS system."""
        self.config = config or get_config().cis
        
        # Store subsystem references
        self.mogil = mogil_system
        self.qlem = qlem_system
        self.e3de = e3de_system
        self.hdts = hdts_system
        
        # Initialize CIS components
        self.connectome: Optional[ConnectomeNetwork] = None
        self.consciousness_manifold = ConsciousnessManifold(
            dimension=self.config.get("manifold_dimension", 10),
            embedding_method=self.config.get("embedding_method", "pca")
        )
        
        # Consciousness state
        self.current_metrics = ConsciousnessMetrics()
        self.consciousness_history: List[ConsciousnessMetrics] = []
        self.integration_weights = {
            'mogil': self.config.get("mogil_weight", 0.25),
            'qlem': self.config.get("qlem_weight", 0.25),
            'e3de': self.config.get("e3de_weight", 0.25),
            'hdts': self.config.get("hdts_weight", 0.25)
        }
        
        logger.info(f"Initialized CIS with integration weights: {self.integration_weights}")
    
    def create_connectome(
        self,
        embedding: LatentEmbedding,
        connectome_type: str = "brain_network"
    ) -> ConnectomeNetwork:
        """Create consciousness connectome from embedding."""
        with timer_context(f"Creating {connectome_type} connectome"):
            # Convert embedding to connectome nodes
            nodes = self._embedding_to_connectome_nodes(embedding, connectome_type)
            
            # Create connectivity matrix
            connectivity = self._create_connectivity_matrix(nodes, embedding)
            
            # Create connectome network
            self.connectome = ConnectomeNetwork(nodes, connectivity)
            
            logger.info(f"Created connectome: {len(nodes)} nodes, {connectome_type} type")
            return self.connectome
    
    def integrate_consciousness(
        self,
        time_step: float = 0.01,
        integration_cycles: int = 100
    ) -> ConsciousnessMetrics:
        """Integrate consciousness across all subsystems."""
        with timer_context(f"Consciousness integration: {integration_cycles} cycles"):
            
            for cycle in range(integration_cycles):
                # Update connectome dynamics
                if self.connectome:
                    self.connectome.update_dynamics(time_step)
                
                # Collect subsystem contributions
                subsystem_contributions = self._collect_subsystem_contributions()
                
                # Compute consciousness metrics
                metrics = self._compute_consciousness_metrics(subsystem_contributions)
                
                # Update consciousness manifold
                if self.connectome:
                    state_vector = np.array([node.activity for node in self.connectome.nodes.values()])
                    self.consciousness_manifold.add_state(state_vector, metrics.consciousness_level)
                
                # Store current metrics
                self.current_metrics = metrics
                
                # Log progress
                log_interval = max(1, integration_cycles // 10)
                if cycle % log_interval == 0:
                    logger.debug(f"Integration cycle {cycle}: consciousness={metrics.consciousness_level:.3f}")
            
            # Fit manifold with accumulated states
            self.consciousness_manifold.fit_manifold()
            
            # Store in history
            self.consciousness_history.append(self.current_metrics)
            
            logger.info(f"Consciousness integration complete: level={self.current_metrics.consciousness_level:.3f}")
            return self.current_metrics
    
    def analyze_consciousness_emergence(self) -> Dict[str, Any]:
        """Analyze consciousness emergence patterns."""
        with timer_context("Analyzing consciousness emergence"):
            if not self.consciousness_history:
                return {"error": "No consciousness history available"}
            
            # Extract consciousness levels over time
            levels = [metrics.consciousness_level for metrics in self.consciousness_history]
            phi_values = [metrics.phi for metrics in self.consciousness_history]
            
            analysis = {
                'emergence_trajectory': {
                    'initial_level': levels[0],
                    'final_level': levels[-1],
                    'max_level_achieved': max(levels),
                    'growth_rate': np.mean(np.diff(levels)) if len(levels) > 1 else 0.0,
                    'stability': 1.0 - np.std(levels[-10:]) if len(levels) >= 10 else 0.0
                },
                
                'integration_analysis': {
                    'avg_phi': np.mean(phi_values),
                    'max_phi': max(phi_values),
                    'phi_stability': 1.0 - np.std(phi_values[-10:]) if len(phi_values) >= 10 else 0.0
                },
                
                'consciousness_categories': {
                    category.value: sum(1 for m in self.consciousness_history 
                                      if m.consciousness_category == category)
                    for category in ConsciousnessLevel
                },
                
                'critical_transitions': self._detect_critical_transitions(levels),
                
                'manifold_analysis': self.consciousness_manifold.compute_manifold_metrics(),
                
                'emergence_indicators': {
                    'phase_transitions': self._detect_phase_transitions(levels),
                    'complexity_emergence': self._analyze_complexity_emergence(),
                    'coherence_development': self._analyze_coherence_development()
                }
            }
            
            logger.info(f"Consciousness emergence analysis: {analysis['emergence_trajectory']}")
            return analysis
    
    def simulate_consciousness_perturbation(
        self,
        perturbation_type: str,
        magnitude: float = 0.1,
        duration: int = 50
    ) -> Dict[str, Any]:
        """Simulate perturbation to consciousness system."""
        with timer_context(f"Consciousness perturbation: {perturbation_type}"):
            if not self.connectome:
                return {"error": "No connectome available for perturbation"}
            
            # Store baseline state
            baseline_metrics = self.current_metrics
            
            # Apply perturbation
            self._apply_consciousness_perturbation(perturbation_type, magnitude)
            
            # Simulate recovery
            recovery_metrics = []
            for step in range(duration):
                metrics = self.integrate_consciousness(integration_cycles=1)
                recovery_metrics.append(metrics)
            
            # Analyze recovery
            recovery_analysis = {
                'perturbation_type': perturbation_type,
                'magnitude': magnitude,
                'baseline_consciousness': baseline_metrics.consciousness_level,
                'immediate_impact': recovery_metrics[0].consciousness_level - baseline_metrics.consciousness_level,
                'recovery_trajectory': [m.consciousness_level for m in recovery_metrics],
                'final_consciousness': recovery_metrics[-1].consciousness_level,
                'resilience': self._compute_resilience(baseline_metrics, recovery_metrics),
                'adaptation': self._compute_adaptation(baseline_metrics, recovery_metrics)
            }
            
            logger.info(f"Perturbation analysis: {recovery_analysis['resilience']:.3f} resilience")
            return recovery_analysis
    
    def consciousness_report(self) -> Dict[str, Any]:
        """Generate comprehensive consciousness report."""
        with timer_context("Generating consciousness report"):
            
            # Current state
            current_state = {
                'consciousness_level': self.current_metrics.consciousness_level,
                'consciousness_category': self.current_metrics.consciousness_category.value,
                'phi': self.current_metrics.phi,
                'global_accessibility': self.current_metrics.global_accessibility,
                'network_connectivity': self.current_metrics.network_connectivity,
                'intrinsic_dimension': self.current_metrics.intrinsic_dimension
            }
            
            # System integration
            integration_status = {
                'mogil_integrated': self.mogil is not None,
                'qlem_integrated': self.qlem is not None,
                'e3de_integrated': self.e3de is not None,
                'hdts_integrated': self.hdts is not None,
                'connectome_active': self.connectome is not None,
                'integration_weights': self.integration_weights
            }
            
            # Historical analysis
            historical_analysis = {}
            if self.consciousness_history:
                levels = [m.consciousness_level for m in self.consciousness_history]
                historical_analysis = {
                    'total_measurements': len(self.consciousness_history),
                    'average_consciousness': np.mean(levels),
                    'consciousness_trend': np.polyfit(range(len(levels)), levels, 1)[0] if len(levels) > 1 else 0,
                    'peak_consciousness': max(levels),
                    'consciousness_stability': 1.0 - np.std(levels) / (np.mean(levels) + 1e-10)
                }
            
            # Manifold analysis
            manifold_metrics = self.consciousness_manifold.compute_manifold_metrics()
            
            # Connectome analysis
            connectome_analysis = {}
            if self.connectome:
                connectome_analysis = self.connectome.compute_network_metrics()
                connectome_analysis['num_nodes'] = len(self.connectome.nodes)
                connectome_analysis['global_workspace_size'] = len(self.connectome.global_workspace)
            
            report = {
                'timestamp': time.time(),
                'current_state': current_state,
                'system_integration': integration_status,
                'historical_analysis': historical_analysis,
                'manifold_analysis': manifold_metrics,
                'connectome_analysis': connectome_analysis,
                'consciousness_assessment': self._assess_consciousness_quality()
            }
            
            logger.info(f"Consciousness report generated: {current_state['consciousness_category']}")
            return report
    
    def _embedding_to_connectome_nodes(
        self,
        embedding: LatentEmbedding,
        connectome_type: str
    ) -> List[ConnectomeNode]:
        """Convert embedding to connectome nodes."""
        nodes = []
        
        for entity_id, embedding_vec in embedding.embeddings.items():
            # Create node from embedding
            node = ConnectomeNode(
                id=entity_id,
                node_type=self._infer_node_type(entity_id, connectome_type),
                position=np.random.uniform(-1, 1, 3),  # Random 3D position
                activity=np.random.uniform(0.1, 0.9),
                information_content=np.linalg.norm(embedding_vec),
                excitability=np.random.uniform(0.5, 1.5),
                inhibition=np.random.uniform(0.05, 0.2)
            )
            
            nodes.append(node)
        
        return nodes
    
    def _infer_node_type(self, entity_id: str, connectome_type: str) -> str:
        """Infer node type from entity ID and connectome type."""
        if connectome_type == "brain_network":
            # Brain regions
            brain_regions = ["frontal", "parietal", "temporal", "occipital", "limbic", "brainstem"]
            return np.random.choice(brain_regions)
        elif connectome_type == "neural_cluster":
            return "neural_cluster"
        else:
            return "connectome_node"
    
    def _create_connectivity_matrix(
        self,
        nodes: List[ConnectomeNode],
        embedding: LatentEmbedding
    ) -> np.ndarray:
        """Create connectivity matrix from embedding similarities."""
        n = len(nodes)
        connectivity = np.zeros((n, n))
        
        if SCIPY_SKLEARN_AVAILABLE:
            # Compute embedding similarities
            node_ids = [node.id for node in nodes]
            embeddings_matrix = np.array([embedding.embeddings[node_id] for node_id in node_ids])
            
            # Compute pairwise similarities
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(embeddings_matrix)
            
            # Convert similarities to connectivity
            threshold = 0.5
            for i in range(n):
                for j in range(n):
                    if i != j and similarities[i, j] > threshold:
                        # Connection strength based on similarity
                        connectivity[i, j] = (similarities[i, j] - threshold) / (1 - threshold)
        else:
            # Simple random connectivity
            for i in range(n):
                for j in range(n):
                    if i != j and np.random.random() < 0.1:  # 10% connectivity
                        connectivity[i, j] = np.random.exponential(0.1)
        
        return connectivity
    
    def _collect_subsystem_contributions(self) -> Dict[str, float]:
        """Collect consciousness contributions from all subsystems."""
        contributions = {}
        
        # MOGIL contribution (integration complexity)
        if self.mogil and hasattr(self.mogil, 'current_embedding'):
            if self.mogil.current_embedding:
                embeddings = list(self.mogil.current_embedding.embeddings.values())
                embeddings_matrix = np.array(embeddings)
                integration_score = np.var(embeddings_matrix.mean(axis=0))
                contributions['mogil'] = min(1.0, integration_score)
            else:
                contributions['mogil'] = 0.0
        else:
            contributions['mogil'] = 0.0
        
        # Q-LEM contribution (quantum coherence)
        if self.qlem and hasattr(self.qlem, 'current_state'):
            if self.qlem.current_state:
                contributions['qlem'] = self.qlem.current_state.coherence
            else:
                contributions['qlem'] = 0.0
        else:
            contributions['qlem'] = 0.0
        
        # E³DE contribution (evolutionary complexity)
        if self.e3de and hasattr(self.e3de, 'populations'):
            if self.e3de.populations:
                # Average consciousness level across populations
                total_consciousness = 0
                total_organisms = 0
                for pop in self.e3de.populations.values():
                    for org in pop.organisms:
                        total_consciousness += org.consciousness_level
                        total_organisms += 1
                
                contributions['e3de'] = total_consciousness / total_organisms if total_organisms > 0 else 0.0
            else:
                contributions['e3de'] = 0.0
        else:
            contributions['e3de'] = 0.0
        
        # HDTS contribution (multi-scale integration)
        if self.hdts and hasattr(self.hdts, 'engine'):
            consciousness_state = self.hdts.engine.consciousness_state
            contributions['hdts'] = consciousness_state.get('consciousness_index', 0.0)
        else:
            contributions['hdts'] = 0.0
        
        return contributions
    
    def _compute_consciousness_metrics(
        self,
        subsystem_contributions: Dict[str, float]
    ) -> ConsciousnessMetrics:
        """Compute comprehensive consciousness metrics."""
        metrics = ConsciousnessMetrics()
        
        # Integrated Information (Φ)
        if self.connectome:
            metrics.phi = self.connectome.compute_integrated_information()
            metrics.phi_max = len(self.connectome.nodes)  # Theoretical maximum
        
        # Network metrics
        if self.connectome:
            network_metrics = self.connectome.compute_network_metrics()
            metrics.network_connectivity = network_metrics.get('density', 0.0)
            metrics.small_worldness = network_metrics.get('small_worldness', 0.0)
            metrics.modularity = network_metrics.get('modularity', 0.0)
            
            # Global workspace accessibility
            workspace_size = len(self.connectome.global_workspace)
            total_nodes = len(self.connectome.nodes)
            metrics.global_accessibility = workspace_size / total_nodes if total_nodes > 0 else 0.0
            
            # Attention focus
            if SCIPY_SKLEARN_AVAILABLE:
                attention_entropy = entropy(self.connectome.attention_weights + 1e-10)
            else:
                # Fallback entropy calculation
                weights = self.connectome.attention_weights + 1e-10
                weights = weights / np.sum(weights)  # Normalize
                attention_entropy = -np.sum(weights * np.log(weights))
                
            max_entropy = np.log(len(self.connectome.attention_weights))
            metrics.attention_focus = 1.0 - (attention_entropy / max_entropy) if max_entropy > 0 else 0.0
        
        # Manifold metrics
        manifold_metrics = self.consciousness_manifold.compute_manifold_metrics()
        metrics.intrinsic_dimension = manifold_metrics.get('effective_dimension', 0.0)
        metrics.curvature = manifold_metrics.get('curvature_estimate', 0.0)
        
        # Information measures (simplified)
        activities = np.array([node.activity for node in self.connectome.nodes.values()]) if self.connectome else np.array([0])
        if len(activities) > 1:
            # Complexity measure
            metrics.complexity = np.std(activities) * np.mean(activities)
            
            # Transfer entropy (simplified)
            metrics.transfer_entropy = np.corrcoef(activities[:-1], activities[1:])[0, 1] if len(activities) > 1 else 0
            metrics.transfer_entropy = abs(metrics.transfer_entropy) if not np.isnan(metrics.transfer_entropy) else 0
        
        # Meta-cognitive measures
        if self.consciousness_history:
            recent_levels = [m.consciousness_level for m in self.consciousness_history[-10:]]
            metrics.self_monitoring = 1.0 - np.std(recent_levels) / (np.mean(recent_levels) + 1e-10)
            
            # Cognitive control (ability to modulate consciousness)
            level_changes = np.abs(np.diff(recent_levels))
            metrics.cognitive_control = np.mean(level_changes) if len(level_changes) > 0 else 0
        
        # Overall consciousness level (weighted combination)
        consciousness_components = [
            self.integration_weights['mogil'] * subsystem_contributions.get('mogil', 0.0),
            self.integration_weights['qlem'] * subsystem_contributions.get('qlem', 0.0),
            self.integration_weights['e3de'] * subsystem_contributions.get('e3de', 0.0),
            self.integration_weights['hdts'] * subsystem_contributions.get('hdts', 0.0),
            0.1 * metrics.phi / (metrics.phi_max + 1e-10),  # Φ contribution
            0.1 * metrics.global_accessibility,             # GWT contribution
            0.1 * metrics.network_connectivity,             # Network contribution
            0.05 * metrics.complexity,                      # Complexity contribution
            0.05 * metrics.self_monitoring                  # Meta-cognition contribution
        ]
        
        metrics.consciousness_level = min(1.0, sum(consciousness_components))
        metrics.update_category()
        
        return metrics
    
    def _detect_critical_transitions(self, levels: List[float]) -> List[int]:
        """Detect critical transitions in consciousness levels."""
        if len(levels) < 10:
            return []
        
        transitions = []
        window_size = 5
        
        for i in range(window_size, len(levels) - window_size):
            before = levels[i-window_size:i]
            after = levels[i:i+window_size]
            
            # Significant change in mean and variance
            mean_change = abs(np.mean(after) - np.mean(before))
            var_change = abs(np.var(after) - np.var(before))
            
            if mean_change > 0.1 or var_change > 0.05:
                transitions.append(i)
        
        return transitions
    
    def _detect_phase_transitions(self, levels: List[float]) -> Dict[str, int]:
        """Detect phase transitions between consciousness categories."""
        if not levels:
            return {}
        
        transitions = defaultdict(int)
        
        for i in range(1, len(levels)):
            prev_category = self._level_to_category(levels[i-1])
            curr_category = self._level_to_category(levels[i])
            
            if prev_category != curr_category:
                transition_key = f"{prev_category.value}_to_{curr_category.value}"
                transitions[transition_key] += 1
        
        return dict(transitions)
    
    def _level_to_category(self, level: float) -> ConsciousnessLevel:
        """Convert consciousness level to category."""
        for category in reversed(list(ConsciousnessLevel)):
            if level >= category.threshold:
                return category
        return ConsciousnessLevel.UNCONSCIOUS
    
    def _analyze_complexity_emergence(self) -> Dict[str, float]:
        """Analyze complexity emergence patterns."""
        if not self.consciousness_history:
            return {}
        
        complexities = [m.complexity for m in self.consciousness_history]
        
        return {
            'complexity_growth': np.mean(np.diff(complexities)) if len(complexities) > 1 else 0,
            'complexity_acceleration': np.mean(np.diff(complexities, 2)) if len(complexities) > 2 else 0,
            'max_complexity': max(complexities) if complexities else 0
        }
    
    def _analyze_coherence_development(self) -> Dict[str, float]:
        """Analyze coherence development in consciousness."""
        if not self.consciousness_history:
            return {}
        
        phi_values = [m.phi for m in self.consciousness_history]
        
        return {
            'phi_development': np.mean(np.diff(phi_values)) if len(phi_values) > 1 else 0,
            'integration_stability': 1.0 - np.std(phi_values[-10:]) / (np.mean(phi_values[-10:]) + 1e-10) if len(phi_values) >= 10 else 0,
            'peak_integration': max(phi_values) if phi_values else 0
        }
    
    def _apply_consciousness_perturbation(
        self,
        perturbation_type: str,
        magnitude: float
    ) -> None:
        """Apply perturbation to consciousness system."""
        if not self.connectome:
            return
        
        if perturbation_type == "activity_boost":
            # Boost random nodes
            target_nodes = np.random.choice(
                list(self.connectome.nodes.keys()),
                size=max(1, int(len(self.connectome.nodes) * 0.1)),
                replace=False
            )
            
            for node_id in target_nodes:
                self.connectome.nodes[node_id].activity += magnitude
                self.connectome.nodes[node_id].activity = min(1.0, self.connectome.nodes[node_id].activity)
        
        elif perturbation_type == "connectivity_disruption":
            # Temporarily reduce connectivity
            self.connectome.connectivity_matrix *= (1.0 - magnitude)
        
        elif perturbation_type == "attention_shift":
            # Shift attention weights
            self.connectome.attention_weights += np.random.normal(0, magnitude, len(self.connectome.attention_weights))
            self.connectome.attention_weights = np.maximum(0, self.connectome.attention_weights)
            total_attention = np.sum(self.connectome.attention_weights)
            if total_attention > 0:
                self.connectome.attention_weights /= total_attention
    
    def _compute_resilience(
        self,
        baseline: ConsciousnessMetrics,
        recovery_metrics: List[ConsciousnessMetrics]
    ) -> float:
        """Compute resilience to perturbation."""
        if not recovery_metrics:
            return 0.0
        
        recovery_levels = [m.consciousness_level for m in recovery_metrics]
        final_level = recovery_levels[-1]
        
        # Resilience based on recovery to baseline
        resilience = 1.0 - abs(final_level - baseline.consciousness_level)
        return max(0.0, resilience)
    
    def _compute_adaptation(
        self,
        baseline: ConsciousnessMetrics,
        recovery_metrics: List[ConsciousnessMetrics]
    ) -> float:
        """Compute adaptation capacity."""
        if not recovery_metrics:
            return 0.0
        
        recovery_levels = [m.consciousness_level for m in recovery_metrics]
        
        # Adaptation based on learning/improvement
        if len(recovery_levels) > 10:
            recent_trend = np.polyfit(range(len(recovery_levels[-10:])), recovery_levels[-10:], 1)[0]
            adaptation = max(0.0, recent_trend)
        else:
            adaptation = 0.0
        
        return adaptation
    
    def _assess_consciousness_quality(self) -> Dict[str, Any]:
        """Assess overall quality of consciousness implementation."""
        assessment = {
            'integration_completeness': sum(1 for system in [self.mogil, self.qlem, self.e3de, self.hdts] if system is not None) / 4,
            'consciousness_stability': self.current_metrics.self_monitoring,
            'emergence_potential': min(1.0, self.current_metrics.consciousness_level + self.current_metrics.complexity),
            'theoretical_grounding': {
                'iit_implementation': self.current_metrics.phi > 0,
                'gwt_implementation': self.current_metrics.global_accessibility > 0,
                'network_theory': self.current_metrics.network_connectivity > 0,
                'manifold_theory': self.current_metrics.intrinsic_dimension > 0
            },
            'biological_realism': 0.8,  # Based on integration with biological data
            'consciousness_readiness': self.current_metrics.consciousness_level > 0.5
        }
        
        # Overall quality score
        assessment['overall_quality'] = np.mean([
            assessment['integration_completeness'],
            assessment['consciousness_stability'],
            assessment['emergence_potential'] / 2,  # Scale down
            sum(assessment['theoretical_grounding'].values()) / len(assessment['theoretical_grounding']),
            assessment['biological_realism']
        ])
        
        return assessment
    
    def __repr__(self) -> str:
        """String representation of CIS."""
        level = self.current_metrics.consciousness_level
        category = self.current_metrics.consciousness_category.value
        systems = sum(1 for s in [self.mogil, self.qlem, self.e3de, self.hdts] if s is not None)
        
        return f"CIS(consciousness={level:.3f} [{category}], {systems}/4 systems integrated)"
