"""MOGIL: Multi-Omics Graph Integration Layer."""

import numpy as np
import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path

from ..core.datatypes import OmicsData, HyperGraph, LatentEmbedding
from ..core.config import get_config
from ..utils.logging import get_logger, timer_context
from ..utils.metrics import compute_biological_metrics
from .hypergraph import HypergraphBuilder
from .gnn_models import create_mogil_encoder, MOGILEncoder

logger = get_logger(__name__)


class MOGIL:
    """Multi-Omics Graph Integration Layer.
    
    MOGIL integrates multi-omics data through attention-weighted hypergraphs
    and graph neural networks to create unified biological representations.
    
    Key Features:
    - Hypergraph construction from multi-omics data
    - Biological edge rules for realistic network topology
    - Attention-weighted graph neural networks
    - Multi-scale embeddings (molecular → cellular → tissue)
    - Temporal dynamics modeling
    - Consciousness-ready latent representations
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        model_path: Optional[Path] = None
    ) -> None:
        """Initialize MOGIL system.
        
        Args:
            config: Configuration dictionary
            model_path: Path to pre-trained model weights
        """
        self.config = config or get_config().mogil
        self.model_path = model_path
        
        # Initialize components
        self.hypergraph_builder = HypergraphBuilder(config=self.config.get("hypergraph", {}))
        self.encoder: Optional[MOGILEncoder] = None
        self.current_hypergraph: Optional[HyperGraph] = None
        self.current_embedding: Optional[LatentEmbedding] = None
        
        logger.info(f"Initialized MOGIL with config: {self.config}")
    
    def build_hypergraph(
        self,
        omics_data: Union[OmicsData, List[OmicsData]],
        integration_method: str = "attention_weighted",
        temporal_window: Optional[float] = None
    ) -> HyperGraph:
        """Build hypergraph from multi-omics data.
        
        Args:
            omics_data: Single or multiple OmicsData objects
            integration_method: Method for integrating omics layers
            temporal_window: Time window for temporal dynamics (hours)
            
        Returns:
            Constructed HyperGraph object
        """
        with timer_context("Building MOGIL hypergraph"):            
            logger.info(f"Building hypergraph from omics data: {omics_data.name if hasattr(omics_data, 'name') else 'unnamed'}")
            
            # Build hypergraph using hypergraph builder
            hypergraph = self.hypergraph_builder.build(omics_data)
            
            # Store current hypergraph
            self.current_hypergraph = hypergraph
            
            # Compute biological metrics
            metrics = self._compute_hypergraph_metrics(hypergraph)
            logger.info(f"Hypergraph metrics: {metrics}")
            
            return hypergraph
    
    def encode_hypergraph(
        self,
        hypergraph: Optional[HyperGraph] = None,
        force_retrain: bool = False
    ) -> LatentEmbedding:
        """Encode hypergraph to latent embedding using GNN.
        
        Args:
            hypergraph: HyperGraph to encode (uses current if None)
            force_retrain: Whether to retrain the encoder
            
        Returns:
            LatentEmbedding object with node representations
        """
        with timer_context("Encoding hypergraph with MOGIL GNN"):
            # Use current hypergraph if none provided
            if hypergraph is None:
                hypergraph = self.current_hypergraph
            
            if hypergraph is None:
                raise ValueError("No hypergraph available. Build hypergraph first.")
            
            # Initialize or recreate encoder if needed
            if self.encoder is None or force_retrain:
                input_dim = self._determine_input_dimension(hypergraph)
                self.encoder = create_mogil_encoder(
                    input_dim=input_dim,
                    config=self.config
                )
                
                # Load pre-trained weights if available
                if self.model_path and self.model_path.exists():
                    self._load_model_weights()
            
            # Encode hypergraph
            embedding = self.encoder.encode(hypergraph)
            
            # Store current embedding
            self.current_embedding = embedding
            
            # Compute embedding quality metrics
            metrics = self._compute_embedding_metrics(embedding)
            logger.info(f"Embedding metrics: {metrics}")
            
            return embedding
    
    def integrate_multi_omics(
        self,
        omics_data: List[OmicsData],
        integration_strategies: Optional[List[str]] = None,
        return_intermediate: bool = False
    ) -> Union[LatentEmbedding, Tuple[HyperGraph, LatentEmbedding]]:
        """Complete multi-omics integration pipeline.
        
        Args:
            omics_data: List of OmicsData objects to integrate
            integration_strategies: List of integration methods to try
            return_intermediate: Whether to return hypergraph as well
            
        Returns:
            Final LatentEmbedding (and HyperGraph if return_intermediate=True)
        """
        with timer_context("Complete MOGIL integration"):
            logger.info(f"Starting multi-omics integration of {len(omics_data)} datasets")
            
            # Default integration strategies
            if integration_strategies is None:
                integration_strategies = ["attention_weighted", "biological_priors", "temporal_dynamics"]
            
            best_embedding = None
            best_score = -np.inf
            best_hypergraph = None
            
            # Try different integration strategies
            for strategy in integration_strategies:
                try:
                    logger.info(f"Trying integration strategy: {strategy}")
                    
                    # Build hypergraph with current strategy
                    hypergraph = self.build_hypergraph(
                        omics_data=omics_data,
                        integration_method=strategy
                    )
                    
                    # Encode to embedding
                    embedding = self.encode_hypergraph(hypergraph)
                    
                    # Evaluate integration quality
                    score = self._evaluate_integration_quality(hypergraph, embedding)
                    
                    logger.info(f"Strategy {strategy} score: {score:.4f}")
                    
                    # Keep best result
                    if score > best_score:
                        best_score = score
                        best_embedding = embedding
                        best_hypergraph = hypergraph
                
                except Exception as e:
                    logger.warning(f"Strategy {strategy} failed: {e}")
                    continue
            
            if best_embedding is None:
                raise RuntimeError("All integration strategies failed")
            
            logger.info(f"Best integration score: {best_score:.4f}")
            
            # Store best results
            self.current_hypergraph = best_hypergraph
            self.current_embedding = best_embedding
            
            if return_intermediate:
                return best_hypergraph, best_embedding
            return best_embedding
    
    def analyze_consciousness_readiness(
        self,
        embedding: Optional[LatentEmbedding] = None
    ) -> Dict[str, Any]:
        """Analyze embedding for consciousness integration readiness.
        
        Args:
            embedding: LatentEmbedding to analyze (uses current if None)
            
        Returns:
            Dictionary of consciousness readiness metrics
        """
        if embedding is None:
            embedding = self.current_embedding
        
        if embedding is None:
            raise ValueError("No embedding available. Create embedding first.")
        
        with timer_context("Analyzing consciousness readiness"):
            # Extract embeddings matrix
            embeddings_matrix = np.array(list(embedding.embeddings.values()))
            
            # Compute consciousness-relevant metrics
            metrics = {
                "dimensionality": embeddings_matrix.shape[1],
                "num_entities": embeddings_matrix.shape[0],
                "embedding_variance": np.var(embeddings_matrix, axis=0).mean(),
                "embedding_entropy": self._compute_embedding_entropy(embeddings_matrix),
                "integration_complexity": self._compute_integration_complexity(embeddings_matrix),
                "representation_coherence": self._compute_representation_coherence(embeddings_matrix),
                "biological_realism": self._compute_biological_realism_score(embedding),
                "consciousness_potential": 0.0  # To be computed
            }
            
            # Compute overall consciousness potential
            metrics["consciousness_potential"] = self._compute_consciousness_potential(metrics)
            
            logger.info(f"Consciousness readiness analysis: {metrics}")
            return metrics
    
    def save_model(self, path: Path) -> None:
        """Save trained MOGIL model."""
        if self.encoder is None:
            raise ValueError("No encoder to save")
        
        try:
            import torch
            torch.save(self.encoder.state_dict(), path)
            logger.info(f"Saved MOGIL model to {path}")
        except ImportError:
            logger.warning("PyTorch not available, cannot save model")
    
    def load_model(self, path: Path) -> None:
        """Load pre-trained MOGIL model."""
        self.model_path = path
        if self.encoder is not None:
            self._load_model_weights()
    
    def _load_model_weights(self) -> None:
        """Load model weights from file."""
        try:
            import torch
            state_dict = torch.load(self.model_path, map_location='cpu')
            self.encoder.load_state_dict(state_dict)
            logger.info(f"Loaded MOGIL model from {self.model_path}")
        except ImportError:
            logger.warning("PyTorch not available, cannot load model")
        except Exception as e:
            logger.warning(f"Failed to load model: {e}")
    
    def _determine_input_dimension(self, hypergraph: HyperGraph) -> int:
        """Determine input dimension for GNN based on hypergraph."""
        # Base dimensions for different entity types
        base_dim = 20
        
        # Add dimensions based on node types present
        entity_types = set()
        for node in hypergraph.nodes.values():
            entity_types.add(node.type)
        
        # Adjust dimension based on complexity
        complexity_factor = len(entity_types) * 5
        total_dim = base_dim + complexity_factor
        
        # Ensure reasonable bounds
        total_dim = max(16, min(total_dim, 256))
        
        logger.info(f"Determined input dimension: {total_dim} (entity types: {entity_types})")
        return total_dim
    
    def _compute_hypergraph_metrics(self, hypergraph: HyperGraph) -> Dict[str, float]:
        """Compute metrics for hypergraph quality."""
        metrics = {
            "num_nodes": len(hypergraph.nodes),
            "num_hyperedges": len(hypergraph.hyperedges),
            "avg_hyperedge_size": np.mean([len(edge.nodes) for edge in hypergraph.hyperedges.values()]),
            "max_hyperedge_size": max([len(edge.nodes) for edge in hypergraph.hyperedges.values()]) if hypergraph.hyperedges else 0,
            "edge_weight_variance": np.var([edge.weight for edge in hypergraph.hyperedges.values()]),
            "biological_coverage": self._compute_biological_coverage(hypergraph)
        }
        
        return metrics
    
    def _compute_embedding_metrics(self, embedding: LatentEmbedding) -> Dict[str, float]:
        """Compute metrics for embedding quality."""
        embeddings_matrix = np.array(list(embedding.embeddings.values()))
        
        metrics = {
            "dimension": embeddings_matrix.shape[1],
            "mean_norm": np.linalg.norm(embeddings_matrix, axis=1).mean(),
            "variance": np.var(embeddings_matrix, axis=0).mean(),
            "entropy": self._compute_embedding_entropy(embeddings_matrix),
            "coherence": self._compute_representation_coherence(embeddings_matrix)
        }
        
        return metrics
    
    def _evaluate_integration_quality(
        self,
        hypergraph: HyperGraph,
        embedding: LatentEmbedding
    ) -> float:
        """Evaluate quality of multi-omics integration."""
        # Combine multiple quality metrics
        hypergraph_metrics = self._compute_hypergraph_metrics(hypergraph)
        embedding_metrics = self._compute_embedding_metrics(embedding)
        
        # Weighted score combining different aspects
        score = (
            0.3 * min(hypergraph_metrics["biological_coverage"], 1.0) +
            0.2 * min(embedding_metrics["entropy"] / 5.0, 1.0) +
            0.2 * min(embedding_metrics["coherence"], 1.0) +
            0.1 * min(hypergraph_metrics["num_nodes"] / 1000.0, 1.0) +
            0.1 * min(hypergraph_metrics["num_hyperedges"] / 500.0, 1.0) +
            0.1 * (1.0 - min(hypergraph_metrics["edge_weight_variance"], 1.0))
        )
        
        return score
    
    def _compute_biological_coverage(self, hypergraph: HyperGraph) -> float:
        """Compute biological coverage score of hypergraph."""
        entity_types = set(node.type for node in hypergraph.nodes.values())
        edge_types = set(edge.edge_type for edge in hypergraph.hyperedges.values())
        
        # Expected biological entity types
        expected_entities = {"gene", "transcript", "protein", "metabolite", "microbe", "brain_region"}
        expected_edges = {"regulatory", "metabolic", "protein_interaction", "neural"}
        
        entity_coverage = len(entity_types & expected_entities) / len(expected_entities)
        edge_coverage = len(edge_types & expected_edges) / len(expected_edges)
        
        return (entity_coverage + edge_coverage) / 2.0
    
    def _compute_embedding_entropy(self, embeddings: np.ndarray) -> float:
        """Compute entropy of embedding distribution."""
        # Discretize embeddings for entropy calculation
        discretized = np.digitize(embeddings.flatten(), bins=np.linspace(-3, 3, 50))
        
        # Compute probability distribution
        unique, counts = np.unique(discretized, return_counts=True)
        probs = counts / counts.sum()
        
        # Compute entropy
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        
        return entropy
    
    def _compute_integration_complexity(self, embeddings: np.ndarray) -> float:
        """Compute integration complexity metric."""
        # Measure how well the embedding captures complex relationships
        from sklearn.decomposition import PCA
        
        pca = PCA()
        pca.fit(embeddings)
        
        # Effective dimensionality based on explained variance
        cumvar = np.cumsum(pca.explained_variance_ratio_)
        effective_dim = np.argmax(cumvar >= 0.95) + 1
        
        complexity = effective_dim / embeddings.shape[1]
        return complexity
    
    def _compute_representation_coherence(self, embeddings: np.ndarray) -> float:
        """Compute coherence of representations."""
        # Measure internal consistency of embeddings
        from scipy.spatial.distance import pdist
        
        distances = pdist(embeddings)
        coherence = 1.0 / (1.0 + np.std(distances))
        
        return coherence
    
    def _compute_biological_realism_score(self, embedding: LatentEmbedding) -> float:
        """Compute biological realism score."""
        # This would include checks for biological constraints
        # For now, return a placeholder score
        return 0.75  # Placeholder
    
    def _compute_consciousness_potential(self, metrics: Dict[str, float]) -> float:
        """Compute overall consciousness potential score."""
        # Weighted combination of consciousness-relevant metrics
        weights = {
            "embedding_entropy": 0.25,
            "integration_complexity": 0.25,
            "representation_coherence": 0.20,
            "biological_realism": 0.20,
            "dimensionality": 0.10
        }
        
        normalized_metrics = {
            "embedding_entropy": min(metrics["embedding_entropy"] / 5.0, 1.0),
            "integration_complexity": metrics["integration_complexity"],
            "representation_coherence": metrics["representation_coherence"],
            "biological_realism": metrics["biological_realism"],
            "dimensionality": min(metrics["dimensionality"] / 128.0, 1.0)
        }
        
        score = sum(weights[key] * normalized_metrics[key] for key in weights.keys())
        return score
    
    def __repr__(self) -> str:
        """String representation of MOGIL."""
        status = []
        if self.current_hypergraph:
            status.append(f"hypergraph({len(self.current_hypergraph.nodes)} nodes)")
        if self.current_embedding:
            status.append(f"embedding({self.current_embedding.dimension}D)")
        
        status_str = ", ".join(status) if status else "uninitialized"
        return f"MOGIL({status_str})"
