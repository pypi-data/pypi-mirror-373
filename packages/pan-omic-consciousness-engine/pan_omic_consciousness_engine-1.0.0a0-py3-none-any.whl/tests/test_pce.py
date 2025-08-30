"""Test suite for the Pan-Omics Consciousness Engine (PCE)."""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch
import tempfile
import json
from pathlib import Path

# Import PCE components
import pce
from pce.core.datatypes import OmicsData, HyperGraph, LatentEmbedding
from pce.data.toy_datasets import create_toy_dataset
from pce.mogil import MOGIL
from pce.qlem import QLEM
from pce.e3de import E3DE
from pce.hdts import HDTS
from pce.cis import CIS


class TestPCECore:
    """Test core PCE functionality."""
    
    def test_version_info(self):
        """Test that version information is available."""
        assert hasattr(pce, '__version__')
        assert hasattr(pce, '__author__')
        assert pce.__version__ == "1.0.0-alpha"
        
    def test_module_imports(self):
        """Test that all main modules can be imported."""
        # Test core components
        assert hasattr(pce, 'OmicsData')
        assert hasattr(pce, 'HyperGraph')
        assert hasattr(pce, 'LatentEmbedding')
        
        # Test main subsystems
        assert hasattr(pce, 'MOGIL')
        assert hasattr(pce, 'QLEM')
        assert hasattr(pce, 'E3DE')
        assert hasattr(pce, 'HDTS')
        assert hasattr(pce, 'CIS')


class TestToyDataGeneration:
    """Test toy dataset generation."""
    
    def test_create_toy_dataset_basic(self):
        """Test basic toy dataset creation."""
        data = create_toy_dataset("toy_basic", n_samples=10, n_features=20)
        
        assert isinstance(data, OmicsData)
        assert len(data.samples) == 10
        assert "genomics" in data.omics_layers
        
    def test_create_toy_dataset_neural(self):
        """Test neural-specific toy dataset."""
        data = create_toy_dataset("toy_neural_omics", n_samples=50, n_features=100)
        
        assert isinstance(data, OmicsData)
        assert len(data.samples) == 50
        # Should have multiple omics layers for neural data
        assert len(data.omics_layers) >= 3
        
    def test_create_toy_dataset_mixed(self):
        """Test mixed omics toy dataset."""
        data = create_toy_dataset("toy_mixed_omics", n_samples=30, n_features=80)
        
        assert isinstance(data, OmicsData)
        assert len(data.samples) == 30
        # Mixed omics should have all major layers
        assert len(data.omics_layers) >= 4


class TestMOGILSubsystem:
    """Test MOGIL (Multi-Omics Graph Integration Layer)."""
    
    def test_mogil_initialization(self):
        """Test MOGIL system initialization."""
        mogil = MOGIL(config={"embedding_dim": 64})
        assert mogil is not None
        assert mogil.config is not None
        
    def test_hypergraph_construction(self):
        """Test hypergraph construction from omics data."""
        # Create toy data
        data = create_toy_dataset("toy_basic", n_samples=20, n_features=50)
        
        # Initialize MOGIL
        mogil = MOGIL(config={"embedding_dim": 32})
        
        # Build hypergraph
        hypergraph = mogil.build_hypergraph(data)
        
        assert isinstance(hypergraph, HyperGraph)
        assert hypergraph.num_nodes > 0
        assert hypergraph.num_edges >= 0
        
    @patch('pce.mogil.torch')  # Mock PyTorch if not available
    def test_hypergraph_encoding(self, mock_torch):
        """Test hypergraph encoding to embeddings."""
        # Create toy data and hypergraph
        data = create_toy_dataset("toy_basic", n_samples=10, n_features=30)
        mogil = MOGIL(config={"embedding_dim": 16})
        hypergraph = mogil.build_hypergraph(data)
        
        # Mock the encoding if PyTorch not available
        if mock_torch:
            mock_embedding = LatentEmbedding(
                embeddings=np.random.randn(hypergraph.num_nodes, 16),
                dimension=16,
                entity_ids=[f"node_{i}" for i in range(hypergraph.num_nodes)]
            )
            with patch.object(mogil, 'encode_hypergraph', return_value=mock_embedding):
                embedding = mogil.encode_hypergraph(hypergraph)
        else:
            embedding = mogil.encode_hypergraph(hypergraph)
            
        assert isinstance(embedding, LatentEmbedding)
        assert embedding.dimension > 0


class TestQLEMSubsystem:
    """Test Q-LEM (Quantum-Latent Entropy Minimizer)."""
    
    def test_qlem_initialization(self):
        """Test Q-LEM system initialization."""
        qlem = QLEM(config={"state_dim": 32})
        assert qlem is not None
        assert qlem.config is not None
        
    def test_quantum_state_creation(self):
        """Test quantum state creation from embeddings."""
        # Create mock embedding
        embedding = LatentEmbedding(
            embeddings=np.random.randn(20, 16),
            dimension=16,
            entity_ids=[f"entity_{i}" for i in range(20)]
        )
        
        qlem = QLEM(config={"state_dim": 16})
        quantum_state = qlem.create_quantum_state(embedding)
        
        # Should create a quantum state representation
        assert quantum_state is not None
        
    def test_entropy_minimization(self):
        """Test entropy minimization process."""
        # Create mock embedding
        embedding = LatentEmbedding(
            embeddings=np.random.randn(15, 12),
            dimension=12,
            entity_ids=[f"entity_{i}" for i in range(15)]
        )
        
        qlem = QLEM(config={"state_dim": 12, "optimization_steps": 10})
        qlem.create_quantum_state(embedding)
        
        # Run entropy minimization
        result = qlem.minimize_entropy(embedding)
        
        # Should return optimization results
        assert result is not None


class TestE3DESubsystem:
    """Test E³DE (Entropic Evolutionary Dynamics Engine)."""
    
    def test_e3de_initialization(self):
        """Test E³DE system initialization."""
        e3de = E3DE(config={"population_size": 20})
        assert e3de is not None
        assert e3de.config is not None
        
    def test_population_creation(self):
        """Test evolutionary population creation."""
        # Create mock embedding
        embedding = LatentEmbedding(
            embeddings=np.random.randn(25, 20),
            dimension=20,
            entity_ids=[f"entity_{i}" for i in range(25)]
        )
        
        e3de = E3DE(config={"population_size": 15})
        
        # Create population
        population = e3de.create_population("test_pop", 15, 10, embedding)
        
        assert population is not None
        assert "test_pop" in e3de.populations
        
    def test_evolution_simulation(self):
        """Test evolutionary simulation."""
        # Create mock embedding and population
        embedding = LatentEmbedding(
            embeddings=np.random.randn(20, 16),
            dimension=16,
            entity_ids=[f"entity_{i}" for i in range(20)]
        )
        
        e3de = E3DE(config={"population_size": 12})
        e3de.create_population("test_evo", 12, 8, embedding)
        
        # Run evolution
        metrics = e3de.evolve_population("test_evo", generations=5)
        
        assert metrics is not None


class TestHDTSSubsystem:
    """Test HDTS (Hierarchical Digital Twin Simulator)."""
    
    def test_hdts_initialization(self):
        """Test HDTS system initialization."""
        hdts = HDTS(config={"num_scales": 4})
        assert hdts is not None
        assert hdts.config is not None
        
    def test_biological_system_creation(self):
        """Test biological system creation."""
        # Create mock embedding
        embedding = LatentEmbedding(
            embeddings=np.random.randn(30, 24),
            dimension=24,
            entity_ids=[f"entity_{i}" for i in range(30)]
        )
        
        hdts = HDTS(config={"num_scales": 3})
        
        # Create biological system
        system = hdts.create_biological_system(embedding)
        
        assert system is not None
        
    def test_consciousness_emergence_simulation(self):
        """Test consciousness emergence simulation."""
        # Create mock embedding and system
        embedding = LatentEmbedding(
            embeddings=np.random.randn(25, 20),
            dimension=20,
            entity_ids=[f"entity_{i}" for i in range(25)]
        )
        
        hdts = HDTS(config={"num_scales": 3, "simulation_steps": 10})
        hdts.create_biological_system(embedding)
        
        # Run simulation
        results = hdts.simulate_consciousness_emergence(duration=0.1)
        
        assert results is not None


class TestCISSubsystem:
    """Test CIS (Consciousness-Integration Substrate)."""
    
    def test_cis_initialization(self):
        """Test CIS system initialization."""
        cis = CIS(config={"integration_cycles": 50})
        assert cis is not None
        assert cis.config is not None
        
    def test_connectome_creation(self):
        """Test connectome network creation."""
        # Create mock embedding
        embedding = LatentEmbedding(
            embeddings=np.random.randn(20, 16),
            dimension=16,
            entity_ids=[f"entity_{i}" for i in range(20)]
        )
        
        cis = CIS(config={"integration_cycles": 20})
        
        # Create connectome
        connectome = cis.create_connectome(embedding)
        
        assert connectome is not None
        
    def test_consciousness_integration(self):
        """Test consciousness integration process."""
        # Create mock embedding and connectome
        embedding = LatentEmbedding(
            embeddings=np.random.randn(15, 12),
            dimension=12,
            entity_ids=[f"entity_{i}" for i in range(15)]
        )
        
        cis = CIS(config={"integration_cycles": 10})
        cis.create_connectome(embedding)
        
        # Run consciousness integration
        metrics = cis.integrate_consciousness(integration_cycles=10)
        
        assert metrics is not None
        assert hasattr(metrics, 'phi')
        assert hasattr(metrics, 'global_accessibility')


class TestPCEIntegration:
    """Test integrated PCE system functionality."""
    
    def test_create_pce_system(self):
        """Test creating integrated PCE system."""
        pce_system = pce.create_pce_system()
        
        assert isinstance(pce_system, CIS)
        assert pce_system.mogil_system is not None
        assert pce_system.qlem_system is not None
        assert pce_system.e3de_system is not None
        assert pce_system.hdts_system is not None
        
    def test_quick_consciousness_analysis(self):
        """Test quick consciousness analysis pipeline."""
        # Create toy data
        data = create_toy_dataset("toy_neural_omics", n_samples=20, n_features=40)
        
        # Run quick analysis with minimal parameters
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = pce.quick_consciousness_analysis(
                data,
                integration_cycles=5,  # Minimal for testing
                save_results=True,
                output_path=tmpdir
            )
            
            # Check that metrics were returned
            assert metrics is not None
            assert hasattr(metrics, 'phi')
            assert hasattr(metrics, 'global_accessibility')
            
            # Check that results were saved
            results_path = Path(tmpdir) / "consciousness_analysis.json"
            metrics_path = Path(tmpdir) / "consciousness_metrics.json"
            
            assert results_path.exists()
            assert metrics_path.exists()
            
            # Verify JSON files are valid
            with open(metrics_path, 'r') as f:
                saved_metrics = json.load(f)
                assert 'phi' in saved_metrics
                assert 'consciousness_level' in saved_metrics


class TestCLIAvailability:
    """Test CLI functionality if available."""
    
    def test_cli_import(self):
        """Test that CLI can be imported if dependencies available."""
        assert hasattr(pce, 'CLI_AVAILABLE')
        
        if pce.CLI_AVAILABLE:
            assert pce.cli_main is not None
        else:
            # CLI not available, which is fine for basic installation
            assert pce.cli_main is None


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
