"""Core data types for the Pan-Omics Consciousness Engine."""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Tuple, Protocol
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import uuid
from datetime import datetime

try:
    import torch
    from torch import Tensor
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    Tensor = Any

import networkx as nx
from pydantic import BaseModel, Field, validator


class OmicsType(Enum):
    """Types of omics data."""
    GENOMICS = "genomics"
    EPIGENOMICS = "epigenomics" 
    TRANSCRIPTOMICS = "transcriptomics"
    PROTEOMICS = "proteomics"
    METABOLOMICS = "metabolomics"
    MICROBIOMICS = "microbiomics"
    CONNECTOMICS = "connectomics"
    PHENOMICS = "phenomics"


class EdgeType(Enum):
    """Types of edges in biological networks."""
    REGULATORY = "regulatory"
    METABOLIC = "metabolic"
    PROTEIN_INTERACTION = "protein_interaction"
    NEURAL = "neural"
    CAUSAL = "causal"
    TEMPORAL = "temporal"


@dataclass
class BiologicalEntity:
    """Base class for biological entities."""
    id: str
    name: str
    type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class Gene(BiologicalEntity):
    """Gene entity."""
    chromosome: str = ""
    start_pos: int = 0
    end_pos: int = 0
    strand: str = "+"
    
    def __post_init__(self) -> None:
        self.type = "gene"


@dataclass
class Transcript(BiologicalEntity):
    """Transcript entity."""
    gene_id: str = ""
    expression_level: float = 0.0
    
    def __post_init__(self) -> None:
        self.type = "transcript"


@dataclass  
class Protein(BiologicalEntity):
    """Protein entity."""
    sequence: str = ""
    molecular_weight: float = 0.0
    abundance: float = 0.0
    
    def __post_init__(self) -> None:
        self.type = "protein"


@dataclass
class Metabolite(BiologicalEntity):
    """Metabolite entity."""
    formula: str = ""
    mass: float = 0.0
    concentration: float = 0.0
    
    def __post_init__(self) -> None:
        self.type = "metabolite"


@dataclass
class Microbe(BiologicalEntity):
    """Microbial entity."""
    taxonomy: str = ""
    abundance: float = 0.0
    
    def __post_init__(self) -> None:
        self.type = "microbe"


@dataclass
class BrainRegion(BiologicalEntity):
    """Brain region entity."""
    coordinates: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    activity: float = 0.0
    
    def __post_init__(self) -> None:
        self.type = "brain_region"


class OmicsData(BaseModel):
    """Container for multi-omics data."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed Dataset"
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Omics layers
    genomics: Optional[Dict[str, Gene]] = Field(default_factory=dict)
    epigenomics: Optional[pd.DataFrame] = None
    transcriptomics: Optional[Dict[str, Transcript]] = Field(default_factory=dict) 
    proteomics: Optional[Dict[str, Protein]] = Field(default_factory=dict)
    metabolomics: Optional[Dict[str, Metabolite]] = Field(default_factory=dict)
    microbiomics: Optional[Dict[str, Microbe]] = Field(default_factory=dict)
    connectomics: Optional[Dict[str, BrainRegion]] = Field(default_factory=dict)
    
    # Temporal information
    timepoints: Optional[List[float]] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
    
    @validator('genomics', 'transcriptomics', 'proteomics', 'metabolomics', 
              'microbiomics', 'connectomics', pre=True, always=True)
    def ensure_dict(cls, v: Any) -> Dict[str, Any]:
        """Ensure omics data is a dictionary."""
        if v is None:
            return {}
        return v if isinstance(v, dict) else {}
    
    def get_entities(self, omics_type: OmicsType) -> Dict[str, BiologicalEntity]:
        """Get entities for a specific omics type."""
        attr_name = omics_type.value
        return getattr(self, attr_name, {}) or {}
    
    def get_all_entities(self) -> Dict[str, BiologicalEntity]:
        """Get all biological entities across omics types."""
        entities = {}
        for omics_type in OmicsType:
            if omics_type != OmicsType.EPIGENOMICS:  # Skip DataFrame
                entities.update(self.get_entities(omics_type))
        return entities
    
    def summary(self) -> str:
        """Get summary of the dataset."""
        lines = [f"Dataset: {self.name} (ID: {self.id[:8]}...)"]
        
        for omics_type in OmicsType:
            if omics_type == OmicsType.EPIGENOMICS:
                data = self.epigenomics
                count = len(data) if data is not None else 0
            else:
                data = self.get_entities(omics_type)
                count = len(data)
            
            if count > 0:
                lines.append(f"  {omics_type.value}: {count} entities")
        
        if self.timepoints:
            lines.append(f"  Temporal: {len(self.timepoints)} timepoints")
        
        return "\n".join(lines)


class HyperEdge(BaseModel):
    """Hyperedge connecting multiple nodes."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nodes: List[str] = Field(default_factory=list)
    edge_type: EdgeType = EdgeType.REGULATORY
    weight: float = 1.0
    confidence: float = 1.0
    timestamp: Optional[float] = None
    
    # Attention weights for each node
    attention_weights: Optional[List[float]] = None
    
    # Additional attributes
    attributes: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('attention_weights', always=True)
    def validate_attention_weights(cls, v: Optional[List[float]], values: Dict[str, Any]) -> Optional[List[float]]:
        """Validate attention weights match number of nodes."""
        if v is not None and 'nodes' in values:
            nodes = values['nodes']
            if len(v) != len(nodes):
                raise ValueError("Attention weights must match number of nodes")
        return v
    
    def get_normalized_attention(self) -> Optional[List[float]]:
        """Get normalized attention weights."""
        if self.attention_weights is None:
            return None
        
        weights = np.array(self.attention_weights)
        total = weights.sum()
        return (weights / total).tolist() if total > 0 else [1.0 / len(weights)] * len(weights)


class HyperGraph(BaseModel):
    """Hypergraph representation of multi-omics data."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed Hypergraph"
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Graph structure
    nodes: Dict[str, BiologicalEntity] = Field(default_factory=dict)
    hyperedges: Dict[str, HyperEdge] = Field(default_factory=dict)
    
    # Temporal dynamics
    temporal: bool = False
    timepoints: Optional[List[float]] = None
    
    # Graph properties
    node_features: Optional[Dict[str, np.ndarray]] = None
    edge_features: Optional[Dict[str, np.ndarray]] = None
    
    # Attention mechanism
    use_attention: bool = False
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
    
    @property
    def num_nodes(self) -> int:
        """Number of nodes in the hypergraph."""
        return len(self.nodes)
    
    @property
    def num_edges(self) -> int:
        """Number of hyperedges in the hypergraph."""
        return len(self.hyperedges)
    
    def add_node(self, entity: BiologicalEntity) -> None:
        """Add a node to the hypergraph."""
        self.nodes[entity.id] = entity
    
    def add_edge(self, hyperedge: HyperEdge) -> None:
        """Add a hyperedge to the hypergraph."""
        self.hyperedges[hyperedge.id] = hyperedge
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get neighboring nodes."""
        neighbors = set()
        for edge in self.hyperedges.values():
            if node_id in edge.nodes:
                neighbors.update(edge.nodes)
        neighbors.discard(node_id)
        return list(neighbors)
    
    def get_node_edges(self, node_id: str) -> List[HyperEdge]:
        """Get all hyperedges containing a node."""
        return [edge for edge in self.hyperedges.values() if node_id in edge.nodes]
    
    def to_networkx(self) -> nx.Graph:
        """Convert to NetworkX graph (simplified representation)."""
        G = nx.Graph()
        
        # Add nodes
        for node_id, entity in self.nodes.items():
            G.add_node(node_id, **entity.metadata, type=entity.type, name=entity.name)
        
        # Add edges (hyperedges become multiple pairwise edges)
        for edge in self.hyperedges.values():
            nodes = edge.nodes
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    G.add_edge(nodes[i], nodes[j], 
                             weight=edge.weight,
                             edge_type=edge.edge_type.value,
                             confidence=edge.confidence)
        
        return G
    
    def summary(self) -> str:
        """Get summary of the hypergraph."""
        lines = [f"Hypergraph: {self.name} (ID: {self.id[:8]}...)"]
        lines.append(f"  Nodes: {self.num_nodes}")
        lines.append(f"  Hyperedges: {self.num_edges}")
        
        if self.temporal:
            lines.append(f"  Temporal: {len(self.timepoints) if self.timepoints else 0} timepoints")
        
        if self.use_attention:
            lines.append("  Attention: enabled")
        
        # Edge type distribution
        edge_types = {}
        for edge in self.hyperedges.values():
            edge_type = edge.edge_type.value
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        for edge_type, count in sorted(edge_types.items()):
            lines.append(f"    {edge_type}: {count}")
        
        return "\n".join(lines)


class LatentEmbedding(BaseModel):
    """Latent space embedding of biological data."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed Embedding"
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Embedding data
    embeddings: Dict[str, np.ndarray] = Field(default_factory=dict)
    dimension: int = 256
    
    # Source information
    source_graph_id: Optional[str] = None
    embedding_method: str = "unknown"
    
    # Quantum-inspired properties
    quantum_states: Optional[Dict[str, np.ndarray]] = None
    entanglement_matrix: Optional[np.ndarray] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
    
    @property
    def num_entities(self) -> int:
        """Number of embedded entities."""
        return len(self.embeddings)
    
    def get_embedding(self, entity_id: str) -> Optional[np.ndarray]:
        """Get embedding for an entity."""
        return self.embeddings.get(entity_id)
    
    def add_embedding(self, entity_id: str, embedding: np.ndarray) -> None:
        """Add embedding for an entity."""
        if len(embedding) != self.dimension:
            raise ValueError(f"Embedding dimension {len(embedding)} != expected {self.dimension}")
        self.embeddings[entity_id] = embedding
    
    def get_similarity(self, entity1: str, entity2: str, metric: str = "cosine") -> Optional[float]:
        """Compute similarity between two entities."""
        emb1 = self.get_embedding(entity1)
        emb2 = self.get_embedding(entity2)
        
        if emb1 is None or emb2 is None:
            return None
        
        if metric == "cosine":
            return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
        elif metric == "euclidean":
            return float(-np.linalg.norm(emb1 - emb2))
        else:
            raise ValueError(f"Unknown similarity metric: {metric}")
    
    def summary(self) -> str:
        """Get summary of the embedding."""
        lines = [f"LatentEmbedding: {self.name} (ID: {self.id[:8]}...)"]
        lines.append(f"  Entities: {self.num_entities}")
        lines.append(f"  Dimension: {self.dimension}")
        lines.append(f"  Method: {self.embedding_method}")
        
        if self.quantum_states is not None:
            lines.append(f"  Quantum states: {len(self.quantum_states)}")
        
        return "\n".join(lines)


class SimulationResult(BaseModel):
    """Results from digital twin simulation."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed Simulation"
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Simulation parameters
    steps: int = 0
    levels: List[str] = Field(default_factory=list)
    
    # Results data
    trajectories: Dict[str, np.ndarray] = Field(default_factory=dict)
    energy_history: List[float] = Field(default_factory=list)
    entropy_history: List[float] = Field(default_factory=list)
    
    # Level-specific results
    level_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Anomaly detection
    anomalies: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Performance metrics
    computation_time: float = 0.0
    memory_usage: float = 0.0
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_trajectory(self, entity_id: str, trajectory: np.ndarray) -> None:
        """Add trajectory for an entity."""
        self.trajectories[entity_id] = trajectory
    
    def get_final_state(self) -> Dict[str, float]:
        """Get final state values."""
        final_state = {}
        for entity_id, trajectory in self.trajectories.items():
            if len(trajectory) > 0:
                final_state[entity_id] = float(trajectory[-1])
        return final_state
    
    def summary(self) -> str:
        """Get summary of simulation results."""
        lines = [f"SimulationResult: {self.name} (ID: {self.id[:8]}...)"]
        lines.append(f"  Steps: {self.steps}")
        lines.append(f"  Levels: {', '.join(self.levels)}")
        lines.append(f"  Trajectories: {len(self.trajectories)}")
        
        if self.energy_history:
            lines.append(f"  Final energy: {self.energy_history[-1]:.6f}")
        
        if self.entropy_history:
            lines.append(f"  Final entropy: {self.entropy_history[-1]:.6f}")
        
        if self.anomalies:
            lines.append(f"  Anomalies detected: {len(self.anomalies)}")
        
        lines.append(f"  Computation time: {self.computation_time:.2f}s")
        
        return "\n".join(lines)


# Protocol for custom omics data adapters
class OmicsAdapter(Protocol):
    """Protocol for omics data adapters."""
    
    def load(self, path: str, **kwargs: Any) -> OmicsData:
        """Load omics data from file."""
        ...
    
    def save(self, data: OmicsData, path: str, **kwargs: Any) -> None:
        """Save omics data to file."""
        ...
    
    def validate(self, data: OmicsData) -> bool:
        """Validate omics data format."""
        ...
