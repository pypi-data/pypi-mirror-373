"""Core configuration for the Pan-Omics Consciousness Engine."""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field

import numpy as np
from omegaconf import OmegaConf, DictConfig


@dataclass
class PCEConfig:
    """Main configuration class for PCE."""
    
    # Paths
    data_dir: Path = field(default_factory=lambda: Path.home() / ".pce" / "data")
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".pce" / "cache")
    models_dir: Path = field(default_factory=lambda: Path.home() / ".pce" / "models")
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    
    # Compute
    device: str = "auto"  # "cpu", "cuda", "mps", "auto"
    num_workers: int = -1  # -1 for auto
    mixed_precision: bool = True
    
    # Memory
    max_memory_gb: Optional[float] = None
    cache_size_gb: float = 2.0
    
    # Random seed
    seed: int = 42
    
    # Model defaults
    default_latent_dim: int = 256
    default_batch_size: int = 32
    
    # MOGIL settings
    mogil: Dict[str, Any] = field(default_factory=lambda: {
        "attention_heads": 8,
        "hidden_dim": 512,
        "num_layers": 3,
        "dropout": 0.1,
        "edge_types": ["regulatory", "metabolic", "protein_interaction", "neural"],
        "temporal_window": 10,
    })
    
    # Q-LEM settings
    qlem: Dict[str, Any] = field(default_factory=lambda: {
        "alpha": 0.3,  # Energy weight
        "beta": 0.7,   # Complexity weight
        "entropy_type": "shannon",
        "energy_type": "flux",
        "complexity_type": "mdl",
        "optimization_steps": 1000,
        "learning_rate": 1e-3,
    })
    
    # E³DE settings
    e3de: Dict[str, Any] = field(default_factory=lambda: {
        "population_size": 100,
        "mutation_rate": 0.01,
        "recombination_rate": 0.1,
        "selection_pressure": 1.0,
        "operators": ["mutate", "recombine", "rewire", "duplicate"],
        "max_generations": 500,
    })
    
    # HDTS settings
    hdts: Dict[str, Any] = field(default_factory=lambda: {
        "levels": ["L0", "L1", "L2", "L3", "L4", "L5"],
        "adaptive_zoom": True,
        "zoom_threshold": 0.1,
        "compute_allocation": "dynamic",
        "timestep": 0.01,
    })
    
    # CIS settings
    cis: Dict[str, Any] = field(default_factory=lambda: {
        "manifold_dim": 128,
        "causal_layers": 4,
        "attention_mechanism": "self",
        "consciousness_threshold": 0.5,
        "narrative_export": True,
    })
    
    # Security
    biosecurity_level: int = 2  # 0=none, 1=basic, 2=standard, 3=high
    data_privacy: bool = True
    audit_logging: bool = True
    
    def __post_init__(self) -> None:
        """Post-initialization setup."""
        # Ensure directories exist
        for dir_path in [self.data_dir, self.cache_dir, self.models_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Auto-detect device
        if self.device == "auto":
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        
        # Auto-detect workers
        if self.num_workers == -1:
            self.num_workers = min(os.cpu_count() or 1, 8)
        
        # Set random seed
        np.random.seed(self.seed)
        try:
            import torch
            torch.manual_seed(self.seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(self.seed)
        except ImportError:
            pass
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> "PCEConfig":
        """Load configuration from file."""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        omega_conf = OmegaConf.load(config_path)
        return cls(**omega_conf)
    
    def to_file(self, config_path: Union[str, Path]) -> None:
        """Save configuration to file."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to OmegaConf for saving
        omega_conf = OmegaConf.structured(self)
        OmegaConf.save(omega_conf, config_path)
    
    def update(self, **kwargs: Any) -> "PCEConfig":
        """Update configuration with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logging.warning(f"Unknown config key: {key}")
        return self
    
    def get_device(self) -> str:
        """Get the compute device."""
        return self.device
    
    def get_data_dir(self) -> Path:
        """Get the data directory."""
        return self.data_dir
    
    def get_cache_dir(self) -> Path:
        """Get the cache directory."""
        return self.cache_dir


# Global configuration instance
_config: Optional[PCEConfig] = None


def get_config() -> PCEConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = PCEConfig()
    return _config


def set_config(config: PCEConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def load_config(config_path: Union[str, Path]) -> PCEConfig:
    """Load configuration from file and set as global."""
    config = PCEConfig.from_file(config_path)
    set_config(config)
    return config


def reset_config() -> PCEConfig:
    """Reset configuration to defaults."""
    global _config
    _config = PCEConfig()
    return _config
