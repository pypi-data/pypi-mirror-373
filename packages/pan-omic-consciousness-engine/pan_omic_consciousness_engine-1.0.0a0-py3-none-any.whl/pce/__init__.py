"""PCE - Pan-Omics Consciousness Engine.

A patentable, scientifically grounded framework for modeling consciousness
emergence from multi-omics biological data.

The PCE system consists of five integrated subsystems:

1. MOGIL (Multi-Omics Graph Integration Layer):
   - Hypergraph construction from multi-omics data
   - Attention-weighted graph neural networks
   - Biological knowledge integration

2. Q-LEM (Quantum-Latent Entropy Minimizer):
   - Bio-quantum entropy functional optimization
   - Von Neumann entropy minimization
   - Quantum coherence modeling

3. E³DE (Entropic Evolutionary Dynamics Engine):
   - Physics-based evolutionary simulation
   - Entropy-driven selection pressure
   - Consciousness emergence through complexity

4. HDTS (Hierarchical Digital Twin Simulator):
   - Multi-scale biological simulation (L0-L5)
   - Adaptive resolution management
   - Cross-scale information propagation

5. CIS (Consciousness-Integration Substrate):
   - Integrated Information Theory (IIT) implementation
   - Global Workspace Theory (GWT) mechanisms
   - Variational manifold consciousness representation

The system provides a unified framework for:
- Multi-omics data integration
- Biological network modeling
- Quantum-biological processes
- Evolutionary dynamics
- Multi-scale simulation
- Consciousness emergence quantification

Example:
    Quick consciousness analysis::

        import pce
        
        # Load toy multi-omics data
        data = pce.load_data("toy_neural_omics")
        
        # Run full consciousness analysis
        metrics = pce.quick_consciousness_analysis(
            data, integration_cycles=100
        )
        
        # View consciousness quantification
        print(f"Consciousness Level: {metrics.phi}")
        print(f"Global Access: {metrics.global_accessibility}")
        print(f"Quantum Coherence: {metrics.quantum_coherence}")
        
    Complete PCE system::
    
        # Create integrated PCE system
        pce_system = pce.create_pce_system()
        
        # Process through all subsystems
        hypergraph = pce_system.mogil.build_hypergraph(data)
        embedding = pce_system.mogil.encode_hypergraph(hypergraph)
        
        pce_system.qlem.create_quantum_state(embedding)
        pce_system.qlem.minimize_entropy(embedding)
        
        pce_system.e3de.create_population("neural", 100, 50, embedding)
        pce_system.e3de.evolve_population("neural", 25)
        
        pce_system.hdts.create_biological_system(embedding)
        pce_system.hdts.simulate_consciousness_emergence(1.0)
        
        pce_system.create_connectome(embedding)
        final_metrics = pce_system.integrate_consciousness()
        
        # Generate comprehensive report
        report = pce_system.consciousness_report()
"""

import logging
from typing import Any, Dict, List, Optional, Union
import json
from pathlib import Path

# Core imports
from .core import config
from .core.datatypes import OmicsData, HyperGraph, LatentEmbedding, BiologicalEntity, HyperEdge
from .core.config import PCEConfig, get_config, set_config
from .data.ingestion import load_data
from .data.toy_datasets import create_toy_dataset
from .utils.logging import setup_logging, get_logger
from .utils.metrics import timer_context, compute_biological_metrics

# Main subsystem imports
from .mogil import MOGIL, HypergraphBuilder, create_mogil_encoder
from .qlem import QLEM, QuantumState, BioQuantumParameters, EntropyFunctional
from .e3de import E3DE, EvolutionaryParameters, Population, Organism, EvolutionScale
from .hdts import HDTS, BiologicalScale, SimulationParameters, DigitalTwinEntity
from .cis import CIS, ConsciousnessLevel, ConsciousnessMetrics, ConnectomeNetwork

# Version information
__version__ = "1.0.0-alpha"
__author__ = "PCE Development Team"
__license__ = "Proprietary"
__email__ = "dev@pce.ai"

# Set up logging
setup_logging()
logger = get_logger(__name__)

# CLI import (optional, requires typer/rich)
try:
    from .cli import main as cli_main
    CLI_AVAILABLE = True
except ImportError:
    cli_main = None
    CLI_AVAILABLE = False
    logger.debug("CLI not available (missing typer/rich dependencies)")

# Public API exports
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    
    # Core components
    "PCEConfig",
    "OmicsData", 
    "BiologicalEntity",
    "HyperGraph",
    "HyperEdge", 
    "LatentEmbedding",
    
    # Main subsystems
    "MOGIL",
    "QLEM", 
    "E3DE",
    "HDTS",
    "CIS",
    
    # Subsystem components
    "HypergraphBuilder",
    "create_mogil_encoder",
    "QuantumState",
    "BioQuantumParameters",
    "EntropyFunctional",
    "EvolutionaryParameters",
    "Population",
    "Organism", 
    "EvolutionScale",
    "BiologicalScale",
    "SimulationParameters",
    "DigitalTwinEntity",
    "ConsciousnessLevel",
    "ConsciousnessMetrics",
    "ConnectomeNetwork",
    
    # Data and utilities
    "load_data",
    "create_toy_dataset",
    "get_config",
    "set_config",
    "get_logger",
    "setup_logging",
    "timer_context",
    "compute_biological_metrics",
    
    # High-level functions
    "create_pce_system",
    "quick_consciousness_analysis",
    
    # CLI (if available)
    "cli_main",
    "CLI_AVAILABLE",
]


def create_pce_system(
    mogil_config: Optional[Dict] = None,
    qlem_config: Optional[Dict] = None,
    e3de_config: Optional[Dict] = None,
    hdts_config: Optional[Dict] = None,
    cis_config: Optional[Dict] = None
) -> CIS:
    """Create a fully integrated PCE system.
    
    Args:
        mogil_config: Configuration for MOGIL subsystem
        qlem_config: Configuration for Q-LEM subsystem
        e3de_config: Configuration for E³DE subsystem
        hdts_config: Configuration for HDTS subsystem
        cis_config: Configuration for CIS subsystem
        
    Returns:
        Fully integrated CIS system ready for consciousness modeling
        
    Example:
        >>> pce_system = create_pce_system()
        >>> # Process data through all subsystems
        >>> data = load_data("toy_neural_omics")
        >>> hypergraph = pce_system.mogil.build_hypergraph(data)
        >>> embedding = pce_system.mogil.encode_hypergraph(hypergraph)
        >>> # Continue with quantum, evolutionary, and simulation processing...
    """
    logger.info("Creating integrated PCE system...")
    
    # Initialize subsystems with provided configurations
    mogil = MOGIL(config=mogil_config)
    qlem = QLEM(config=qlem_config)
    e3de = E3DE(config=e3de_config)
    hdts = HDTS(config=hdts_config)
    
    # Create integrated consciousness substrate
    cis = CIS(
        mogil_system=mogil,
        qlem_system=qlem,
        e3de_system=e3de,
        hdts_system=hdts,
        config=cis_config
    )
    
    logger.info("PCE system created successfully with all subsystems integrated")
    return cis


def quick_consciousness_analysis(
    omics_data: OmicsData,
    integration_cycles: int = 100,
    save_results: bool = True,
    output_path: str = "pce_results"
) -> ConsciousnessMetrics:
    """Quick consciousness analysis pipeline.
    
    Runs a complete consciousness analysis using all PCE subsystems with
    optimized parameters for quick results while maintaining scientific rigor.
    
    Args:
        omics_data: Multi-omics data to analyze
        integration_cycles: Number of consciousness integration cycles
        save_results: Whether to save results to disk
        output_path: Path to save results
        
    Returns:
        Final consciousness metrics including φ (phi), global accessibility,
        quantum coherence, and hierarchical complexity measures
        
    Example:
        >>> data = load_data("toy_neural_omics")
        >>> metrics = quick_consciousness_analysis(data)
        >>> print(f"Consciousness φ: {metrics.phi:.4f}")
        >>> print(f"Global Access: {metrics.global_accessibility:.4f}")
    """
    logger.info("Starting quick consciousness analysis pipeline")
    
    with timer_context("Full PCE Analysis"):
        # Create optimized PCE system for quick analysis
        pce = create_pce_system(
            mogil_config={"embedding_dim": 128, "attention_heads": 4},
            qlem_config={"state_dim": 64, "optimization_steps": 50},
            e3de_config={"population_size": 20, "max_generations": 15},
            hdts_config={"num_scales": 4, "simulation_steps": 50},
            cis_config={"integration_cycles": integration_cycles}
        )
        
        # Step 1: Build hypergraph and encode (MOGIL)
        logger.info("Building hypergraph representation...")
        hypergraph = pce.mogil.build_hypergraph(omics_data)
        embedding = pce.mogil.encode_hypergraph(hypergraph)
        
        # Step 2: Quantum optimization (Q-LEM)
        logger.info("Performing quantum state optimization...")
        pce.qlem.create_quantum_state(embedding)
        pce.qlem.minimize_entropy(embedding)
        
        # Step 3: Evolutionary simulation (E³DE) - quick version
        logger.info("Running evolutionary dynamics simulation...")
        pce.e3de.create_population("quick_analysis", 20, 20, embedding)
        pce.e3de.evolve_population("quick_analysis", 15)
        
        # Step 4: Digital twin simulation (HDTS) - short duration
        logger.info("Simulating hierarchical digital twin...")
        pce.hdts.create_biological_system(embedding)
        pce.hdts.simulate_consciousness_emergence(0.1)  # Short simulation
        
        # Step 5: Final consciousness integration (CIS)
        logger.info("Integrating consciousness across all scales...")
        pce.create_connectome(embedding)
        metrics = pce.integrate_consciousness(integration_cycles=integration_cycles)
    
    # Save results if requested
    if save_results:
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Saving results to {output_dir}")
        report = pce.consciousness_report()
        
        # Save comprehensive report
        with open(output_dir / "consciousness_analysis.json", 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save metrics summary
        metrics_dict = {
            "phi": float(metrics.phi),
            "global_accessibility": float(metrics.global_accessibility),
            "quantum_coherence": float(metrics.quantum_coherence),
            "hierarchical_complexity": float(metrics.hierarchical_complexity),
            "consciousness_level": str(metrics.consciousness_level),
            "integration_cycles": integration_cycles,
            "analysis_timestamp": str(metrics.timestamp)
        }
        
        with open(output_dir / "consciousness_metrics.json", 'w') as f:
            json.dump(metrics_dict, f, indent=2)
    
    logger.info(f"Consciousness analysis complete. φ = {metrics.phi:.4f}")
    return metrics


# Legacy function for backward compatibility
def build_hypergraph(
    data: OmicsData,
    temporal: bool = True,
    use_attention: bool = True,
    edge_types: Optional[List[str]] = None,
    **kwargs: Any
) -> HyperGraph:
    """Build hypergraph representation from multi-omics data.
    
    This is a convenience function that creates a MOGIL system and
    builds a hypergraph. For more control, use MOGIL directly.
    
    Args:
        data: Multi-omics data
        temporal: Whether to include temporal dynamics
        use_attention: Whether to use attention-weighted edges
        edge_types: Types of edges to include
        **kwargs: Additional hypergraph parameters
        
    Returns:
        Constructed hypergraph
        
    Example:
        >>> data = load_data("toy_mixed_omics")
        >>> graph = build_hypergraph(data, temporal=True, use_attention=True)
        >>> print(f"Graph: {graph.num_nodes} nodes, {graph.num_edges} hyperedges")
    """
    mogil = MOGIL(config={
        "temporal": temporal,
        "use_attention": use_attention,
        "edge_types": edge_types,
        **kwargs
    })
    return mogil.build_hypergraph(data)


logger.info(f"PCE v{__version__} initialized successfully")
logger.info(f"CLI available: {CLI_AVAILABLE}")
logger.info("Ready for consciousness emergence modeling")
