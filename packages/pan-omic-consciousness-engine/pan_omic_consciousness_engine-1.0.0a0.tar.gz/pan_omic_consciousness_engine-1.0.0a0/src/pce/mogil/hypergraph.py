"""Multi-Omics Graph Integration Layer (MOGIL) - Dynamic Hypergraph Construction."""

import numpy as np
import networkx as nx
from typing import Any, Dict, List, Optional, Union, Tuple, Set
import logging
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import uuid
from datetime import datetime

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch_geometric.data import Data, HeteroData
    from torch_geometric.transforms import ToUndirected
    TORCH_GEOMETRIC_AVAILABLE = True
except ImportError:
    TORCH_GEOMETRIC_AVAILABLE = False
    nn = None
    F = None

from ..core.datatypes import (
    OmicsData, HyperGraph, HyperEdge, EdgeType, OmicsType,
    BiologicalEntity, Gene, Transcript, Protein, Metabolite, Microbe, BrainRegion
)
from ..core.config import get_config
from ..utils.logging import get_logger, timer_context

logger = get_logger(__name__)


@dataclass
class EdgeRule:
    """Rule for creating edges between biological entities."""
    source_type: str
    target_type: str
    edge_type: EdgeType
    weight_function: Optional[str] = None
    confidence_threshold: float = 0.1
    max_distance: Optional[float] = None
    temporal_decay: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class HypergraphBuilder:
    """Builder for constructing biological hypergraphs from omics data."""
    
    def __init__(
        self,
        temporal: bool = True,
        use_attention: bool = True,
        edge_types: Optional[List[str]] = None,
        distance_threshold: float = 1.0,
        confidence_threshold: float = 0.1,
        **kwargs: Any
    ) -> None:
        """Initialize hypergraph builder.
        
        Args:
            temporal: Whether to include temporal dynamics
            use_attention: Whether to use attention-weighted edges
            edge_types: Types of edges to include
            distance_threshold: Maximum distance for edge creation
            confidence_threshold: Minimum confidence for edge inclusion
            **kwargs: Additional configuration
        """
        self.temporal = temporal
        self.use_attention = use_attention
        self.distance_threshold = distance_threshold
        self.confidence_threshold = confidence_threshold
        
        # Default edge types
        if edge_types is None:
            edge_types = ["regulatory", "metabolic", "protein_interaction", "neural"]
        self.edge_types = [EdgeType(et) for et in edge_types]
        
        # Edge construction rules
        self.edge_rules = self._create_default_edge_rules()
        
        # Configuration
        config = get_config()
        self.config = config.mogil
    
    def build(self, omics_data: OmicsData) -> HyperGraph:
        """Build hypergraph from omics data.
        
        Args:
            omics_data: Multi-omics data
            
        Returns:
            Constructed hypergraph
        """
        with timer_context("Building biological hypergraph"):
            # Create hypergraph object
            hypergraph = HyperGraph(
                name=f"Hypergraph of {omics_data.name}",
                temporal=self.temporal,
                timepoints=omics_data.timepoints,
                use_attention=self.use_attention
            )
            
            # Add nodes from all omics layers
            self._add_nodes_from_omics(hypergraph, omics_data)
            
            # Create edges based on rules
            self._create_edges(hypergraph, omics_data)
            
            # Add temporal dynamics if enabled
            if self.temporal and omics_data.timepoints:
                self._add_temporal_dynamics(hypergraph, omics_data)
            
            # Compute attention weights if enabled
            if self.use_attention:
                self._compute_attention_weights(hypergraph)
            
            logger.info(f"Built hypergraph: {hypergraph.summary()}")
            return hypergraph
    
    def _add_nodes_from_omics(self, hypergraph: HyperGraph, omics_data: OmicsData) -> None:
        """Add nodes from all omics layers."""
        # Add entities from each omics type
        for omics_type in OmicsType:
            if omics_type == OmicsType.EPIGENOMICS:
                continue  # Skip DataFrame type for now
            
            entities = omics_data.get_entities(omics_type)
            for entity in entities.values():
                hypergraph.add_node(entity)
        
        logger.debug(f"Added {hypergraph.num_nodes} nodes to hypergraph")
    
    def _create_edges(self, hypergraph: HyperGraph, omics_data: OmicsData) -> None:
        """Create edges based on predefined rules."""
        nodes = hypergraph.nodes
        
        for rule in self.edge_rules:
            # Find source and target nodes
            source_nodes = [
                node for node in nodes.values() 
                if node.type == rule.source_type
            ]
            target_nodes = [
                node for node in nodes.values()
                if node.type == rule.target_type
            ]
            
            # Create edges between compatible nodes
            for source in source_nodes:
                for target in target_nodes:
                    if source.id != target.id:
                        edge = self._create_edge_between_nodes(
                            source, target, rule, omics_data
                        )
                        if edge:
                            hypergraph.add_edge(edge)
        
        logger.debug(f"Created {hypergraph.num_edges} hyperedges")
    
    def _create_edge_between_nodes(
        self,
        source: BiologicalEntity,
        target: BiologicalEntity,
        rule: EdgeRule,
        omics_data: OmicsData
    ) -> Optional[HyperEdge]:
        """Create edge between two nodes based on rule."""
        # Compute edge weight and confidence
        weight, confidence = self._compute_edge_properties(source, target, rule, omics_data)
        
        # Check confidence threshold
        if confidence < rule.confidence_threshold:
            return None
        
        # Create hyperedge
        edge = HyperEdge(
            nodes=[source.id, target.id],
            edge_type=rule.edge_type,
            weight=weight,
            confidence=confidence,
            attributes={
                "rule": rule.metadata,
                "source_type": source.type,
                "target_type": target.type
            }
        )
        
        return edge
    
    def _compute_edge_properties(
        self,
        source: BiologicalEntity,
        target: BiologicalEntity,
        rule: EdgeRule,
        omics_data: OmicsData
    ) -> Tuple[float, float]:
        """Compute weight and confidence for an edge."""
        weight = 1.0
        confidence = 1.0
        
        # Apply weight function if specified
        if rule.weight_function:
            weight = self._apply_weight_function(source, target, rule.weight_function)
        
        # Compute distance-based confidence
        distance = self._compute_biological_distance(source, target)
        if rule.max_distance and distance > rule.max_distance:
            confidence = 0.0
        else:
            confidence = np.exp(-distance / self.distance_threshold)
        
        # Apply specific rules based on biological knowledge
        if rule.edge_type == EdgeType.REGULATORY:
            weight, confidence = self._compute_regulatory_edge(source, target)
        elif rule.edge_type == EdgeType.METABOLIC:
            weight, confidence = self._compute_metabolic_edge(source, target)
        elif rule.edge_type == EdgeType.PROTEIN_INTERACTION:
            weight, confidence = self._compute_protein_interaction_edge(source, target)
        elif rule.edge_type == EdgeType.NEURAL:
            weight, confidence = self._compute_neural_edge(source, target)
        
        return weight, confidence
    
    def _compute_biological_distance(
        self,
        entity1: BiologicalEntity,
        entity2: BiologicalEntity
    ) -> float:
        """Compute biological distance between entities."""
        # Simple distance based on entity types
        type_distances = {
            ("gene", "transcript"): 0.1,
            ("transcript", "protein"): 0.2,
            ("protein", "metabolite"): 0.5,
            ("metabolite", "microbe"): 0.8,
            ("brain_region", "brain_region"): 0.3,
            ("gene", "gene"): 1.0,
            ("protein", "protein"): 0.4,
        }
        
        key1 = (entity1.type, entity2.type)
        key2 = (entity2.type, entity1.type)
        
        distance = type_distances.get(key1, type_distances.get(key2, 1.0))
        
        # Add positional distance for genomic entities
        if hasattr(entity1, 'chromosome') and hasattr(entity2, 'chromosome'):
            if entity1.chromosome == entity2.chromosome:
                pos_dist = abs(entity1.start_pos - entity2.start_pos) / 1e6  # Mb
                distance += 0.1 * np.tanh(pos_dist / 10)  # Normalize
        
        return distance
    
    def _compute_regulatory_edge(
        self,
        source: BiologicalEntity,
        target: BiologicalEntity
    ) -> Tuple[float, float]:
        """Compute regulatory edge properties."""
        # Gene-transcript regulatory relationships
        if source.type == "gene" and target.type == "transcript":
            if isinstance(target, Transcript) and target.gene_id == source.id:
                return 1.0, 0.95  # High confidence for direct gene-transcript
            else:
                return 0.5, 0.1  # Low confidence for trans regulation
        
        # Transcript-protein regulatory relationships  
        if source.type == "transcript" and target.type == "protein":
            # Assume some correspondence between transcript and protein names
            name_similarity = self._compute_name_similarity(source.name, target.name)
            return name_similarity, name_similarity * 0.8
        
        return 0.5, 0.2
    
    def _compute_metabolic_edge(
        self,
        source: BiologicalEntity,
        target: BiologicalEntity
    ) -> Tuple[float, float]:
        """Compute metabolic edge properties."""
        # Protein-metabolite interactions
        if source.type == "protein" and target.type == "metabolite":
            # Simple heuristic based on abundance/concentration
            if isinstance(source, Protein) and isinstance(target, Metabolite):
                # Higher abundance proteins more likely to interact
                weight = np.tanh(source.abundance / 5.0) * np.tanh(target.concentration / 10.0)
                confidence = 0.3 + 0.4 * weight
                return weight, confidence
        
        # Metabolite-microbe interactions
        if source.type == "metabolite" and target.type == "microbe":
            if isinstance(source, Metabolite) and isinstance(target, Microbe):
                # Microbes with higher abundance may process more metabolites
                weight = np.tanh(target.abundance / 2.0) * np.tanh(source.concentration / 5.0)
                confidence = 0.2 + 0.3 * weight
                return weight, confidence
        
        return 0.3, 0.15
    
    def _compute_protein_interaction_edge(
        self,
        source: BiologicalEntity,
        target: BiologicalEntity
    ) -> Tuple[float, float]:
        """Compute protein interaction edge properties."""
        if source.type == "protein" and target.type == "protein":
            if isinstance(source, Protein) and isinstance(target, Protein):
                # Simple heuristic based on molecular weight similarity
                mw_diff = abs(source.molecular_weight - target.molecular_weight)
                weight = np.exp(-mw_diff / 50000)  # Similar MW = higher interaction probability
                
                # Abundance-based confidence
                abundance_product = np.sqrt(source.abundance * target.abundance)
                confidence = 0.1 + 0.4 * np.tanh(abundance_product / 10.0)
                
                return weight, confidence
        
        return 0.2, 0.1
    
    def _compute_neural_edge(
        self,
        source: BiologicalEntity,
        target: BiologicalEntity
    ) -> Tuple[float, float]:
        """Compute neural connectivity edge properties."""
        if source.type == "brain_region" and target.type == "brain_region":
            if isinstance(source, BrainRegion) and isinstance(target, BrainRegion):
                # Distance-based connectivity
                x1, y1, z1 = source.coordinates
                x2, y2, z2 = target.coordinates
                
                euclidean_dist = np.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)
                
                # Closer regions more likely to be connected
                weight = np.exp(-euclidean_dist / 50.0)
                
                # Activity correlation-based confidence
                activity_product = source.activity * target.activity
                confidence = 0.2 + 0.6 * activity_product
                
                return weight, confidence
        
        return 0.1, 0.05
    
    def _compute_name_similarity(self, name1: str, name2: str) -> float:
        """Compute simple name similarity."""
        # Simple Jaccard similarity on words
        words1 = set(name1.lower().split())
        words2 = set(name2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _apply_weight_function(
        self,
        source: BiologicalEntity,
        target: BiologicalEntity,
        function_name: str
    ) -> float:
        """Apply named weight function."""
        if function_name == "expression_correlation":
            # Placeholder for expression correlation
            return np.random.uniform(0.1, 0.9)
        elif function_name == "co_abundance":
            # Placeholder for co-abundance
            return np.random.uniform(0.2, 0.8)
        else:
            return 1.0
    
    def _add_temporal_dynamics(self, hypergraph: HyperGraph, omics_data: OmicsData) -> None:
        """Add temporal dynamics to hypergraph edges."""
        if not omics_data.timepoints:
            return
        
        # Add timestamp to edges for temporal modeling
        for edge in hypergraph.hyperedges.values():
            # For now, assign random timestamps
            # In real implementation, this would be based on data
            edge.timestamp = np.random.choice(omics_data.timepoints)
            
            # Add temporal decay to weights
            if hasattr(edge, 'attributes') and 'temporal_decay' in edge.attributes:
                decay_rate = edge.attributes['temporal_decay']
                time_factor = np.exp(-decay_rate * edge.timestamp)
                edge.weight *= time_factor
    
    def _compute_attention_weights(self, hypergraph: HyperGraph) -> None:
        """Compute attention weights for hyperedges."""
        for edge in hypergraph.hyperedges.values():
            num_nodes = len(edge.nodes)
            
            # Simple attention based on node centrality
            attention_weights = []
            
            for node_id in edge.nodes:
                # Count how many edges this node participates in
                node_degree = sum(
                    1 for e in hypergraph.hyperedges.values()
                    if node_id in e.nodes
                )
                
                # Higher degree = higher attention
                attention = np.log(node_degree + 1)
                attention_weights.append(attention)
            
            # Normalize attention weights
            total_attention = sum(attention_weights)
            if total_attention > 0:
                edge.attention_weights = [w / total_attention for w in attention_weights]
            else:
                edge.attention_weights = [1.0 / num_nodes] * num_nodes
    
    def _create_default_edge_rules(self) -> List[EdgeRule]:
        """Create default edge construction rules."""
        rules = []
        
        # Regulatory rules
        rules.extend([
            EdgeRule("gene", "transcript", EdgeType.REGULATORY, confidence_threshold=0.1),
            EdgeRule("transcript", "protein", EdgeType.REGULATORY, confidence_threshold=0.1),
        ])
        
        # Metabolic rules
        rules.extend([
            EdgeRule("protein", "metabolite", EdgeType.METABOLIC, confidence_threshold=0.1),
            EdgeRule("metabolite", "microbe", EdgeType.METABOLIC, confidence_threshold=0.1),
        ])
        
        # Protein interaction rules
        rules.append(
            EdgeRule("protein", "protein", EdgeType.PROTEIN_INTERACTION, confidence_threshold=0.2)
        )
        
        # Neural connectivity rules
        rules.append(
            EdgeRule("brain_region", "brain_region", EdgeType.NEURAL, confidence_threshold=0.1)
        )
        
        return rules
    
    def add_custom_rule(self, rule: EdgeRule) -> None:
        """Add custom edge construction rule."""
        self.edge_rules.append(rule)
        logger.info(f"Added custom edge rule: {rule.source_type} -> {rule.target_type}")
    
    def remove_rule(self, source_type: str, target_type: str, edge_type: EdgeType) -> bool:
        """Remove edge construction rule."""
        for i, rule in enumerate(self.edge_rules):
            if (rule.source_type == source_type and 
                rule.target_type == target_type and 
                rule.edge_type == edge_type):
                del self.edge_rules[i]
                logger.info(f"Removed edge rule: {source_type} -> {target_type}")
                return True
        return False


class HypergraphAnalyzer:
    """Analyzer for biological hypergraphs."""
    
    def __init__(self, hypergraph: HyperGraph) -> None:
        self.hypergraph = hypergraph
    
    def compute_statistics(self) -> Dict[str, Any]:
        """Compute basic hypergraph statistics."""
        stats = {
            "num_nodes": self.hypergraph.num_nodes,
            "num_edges": self.hypergraph.num_edges,
            "density": self._compute_density(),
            "avg_node_degree": self._compute_avg_node_degree(),
            "edge_type_distribution": self._compute_edge_type_distribution(),
            "node_type_distribution": self._compute_node_type_distribution(),
        }
        
        if self.hypergraph.temporal:
            stats["temporal_statistics"] = self._compute_temporal_statistics()
        
        if self.hypergraph.use_attention:
            stats["attention_statistics"] = self._compute_attention_statistics()
        
        return stats
    
    def _compute_density(self) -> float:
        """Compute hypergraph density."""
        n_nodes = self.hypergraph.num_nodes
        n_edges = self.hypergraph.num_edges
        
        if n_nodes <= 1:
            return 0.0
        
        # Maximum possible hyperedges (all possible subsets of nodes)
        max_edges = 2**n_nodes - n_nodes - 1  # Exclude empty set and singletons
        
        return n_edges / max_edges if max_edges > 0 else 0.0
    
    def _compute_avg_node_degree(self) -> float:
        """Compute average node degree."""
        if not self.hypergraph.nodes:
            return 0.0
        
        degrees = []
        for node_id in self.hypergraph.nodes:
            degree = len(self.hypergraph.get_node_edges(node_id))
            degrees.append(degree)
        
        return np.mean(degrees)
    
    def _compute_edge_type_distribution(self) -> Dict[str, int]:
        """Compute distribution of edge types."""
        distribution = {}
        
        for edge in self.hypergraph.hyperedges.values():
            edge_type = edge.edge_type.value
            distribution[edge_type] = distribution.get(edge_type, 0) + 1
        
        return distribution
    
    def _compute_node_type_distribution(self) -> Dict[str, int]:
        """Compute distribution of node types."""
        distribution = {}
        
        for node in self.hypergraph.nodes.values():
            node_type = node.type
            distribution[node_type] = distribution.get(node_type, 0) + 1
        
        return distribution
    
    def _compute_temporal_statistics(self) -> Dict[str, Any]:
        """Compute temporal statistics."""
        timestamps = [
            edge.timestamp for edge in self.hypergraph.hyperedges.values()
            if edge.timestamp is not None
        ]
        
        if not timestamps:
            return {"num_temporal_edges": 0}
        
        return {
            "num_temporal_edges": len(timestamps),
            "min_timestamp": min(timestamps),
            "max_timestamp": max(timestamps),
            "avg_timestamp": np.mean(timestamps),
            "timestamp_std": np.std(timestamps),
        }
    
    def _compute_attention_statistics(self) -> Dict[str, Any]:
        """Compute attention weight statistics."""
        all_weights = []
        
        for edge in self.hypergraph.hyperedges.values():
            if edge.attention_weights:
                all_weights.extend(edge.attention_weights)
        
        if not all_weights:
            return {"num_attention_edges": 0}
        
        return {
            "num_attention_edges": len([e for e in self.hypergraph.hyperedges.values() if e.attention_weights]),
            "avg_attention_weight": np.mean(all_weights),
            "attention_weight_std": np.std(all_weights),
            "min_attention_weight": min(all_weights),
            "max_attention_weight": max(all_weights),
        }
    
    def find_hubs(self, top_k: int = 10) -> List[Tuple[str, int]]:
        """Find hub nodes with highest degrees."""
        node_degrees = []
        
        for node_id in self.hypergraph.nodes:
            degree = len(self.hypergraph.get_node_edges(node_id))
            node_degrees.append((node_id, degree))
        
        # Sort by degree and return top k
        node_degrees.sort(key=lambda x: x[1], reverse=True)
        return node_degrees[:top_k]
    
    def find_communities(self) -> List[Set[str]]:
        """Find communities in the hypergraph (simplified)."""
        # Convert to simple graph for community detection
        G = self.hypergraph.to_networkx()
        
        try:
            import community  # python-louvain
            partition = community.best_partition(G)
            
            # Group nodes by community
            communities = {}
            for node, comm_id in partition.items():
                if comm_id not in communities:
                    communities[comm_id] = set()
                communities[comm_id].add(node)
            
            return list(communities.values())
            
        except ImportError:
            logger.warning("python-louvain not available, using simple community detection")
            # Fallback to connected components
            return [set(component) for component in nx.connected_components(G)]
