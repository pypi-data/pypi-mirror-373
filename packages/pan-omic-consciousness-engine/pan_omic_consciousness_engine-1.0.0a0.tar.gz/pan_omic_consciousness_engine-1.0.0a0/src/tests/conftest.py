"""Test configuration and fixtures for PCE test suite."""

import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path

# Test configuration
@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary directory for test data."""
    tmpdir = tempfile.mkdtemp(prefix="pce_test_")
    yield Path(tmpdir)
    shutil.rmtree(tmpdir)

@pytest.fixture
def small_omics_data():
    """Generate small omics dataset for testing."""
    from pce.data.toy_datasets import create_toy_dataset
    return create_toy_dataset("toy_basic", n_samples=10, n_features=20)

@pytest.fixture  
def medium_omics_data():
    """Generate medium omics dataset for testing."""
    from pce.data.toy_datasets import create_toy_dataset
    return create_toy_dataset("toy_neural_omics", n_samples=50, n_features=100)

@pytest.fixture
def mock_embedding():
    """Generate mock latent embedding for testing."""
    from pce.core.datatypes import LatentEmbedding
    return LatentEmbedding(
        embeddings=np.random.randn(20, 16),
        dimension=16,
        entity_ids=[f"test_entity_{i}" for i in range(20)]
    )

# Test markers
pytestmark = pytest.mark.unit
