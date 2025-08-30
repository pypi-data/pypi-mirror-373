"""Random seed utilities for reproducible experiments."""

import random
import numpy as np
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)

# Global random state storage
_random_states: Dict[str, Any] = {}


def set_random_seed(
    seed: int,
    libraries: Optional[list] = None,
    save_state: bool = True
) -> None:
    """Set random seed for reproducible experiments.
    
    Args:
        seed: Random seed value
        libraries: List of libraries to set seed for. If None, sets for all available.
        save_state: Whether to save the random state for later restoration
    """
    if libraries is None:
        libraries = ["python", "numpy", "torch", "tensorflow"]
    
    logger.info(f"Setting random seed: {seed}")
    
    # Python built-in random
    if "python" in libraries:
        random.seed(seed)
        if save_state:
            _random_states["python"] = random.getstate()
    
    # NumPy
    if "numpy" in libraries:
        np.random.seed(seed)
        if save_state:
            _random_states["numpy"] = np.random.get_state()
    
    # PyTorch
    if "torch" in libraries:
        try:
            import torch
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            
            # Make CUDA operations deterministic
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            
            if save_state:
                _random_states["torch"] = torch.get_rng_state()
                if torch.cuda.is_available():
                    _random_states["torch_cuda"] = torch.cuda.get_rng_state_all()
                    
        except ImportError:
            logger.debug("PyTorch not available for random seed setting")
    
    # TensorFlow
    if "tensorflow" in libraries:
        try:
            import tensorflow as tf
            tf.random.set_seed(seed)
        except ImportError:
            logger.debug("TensorFlow not available for random seed setting")
    
    # Scikit-learn
    if "sklearn" in libraries:
        # scikit-learn uses numpy's random state, so setting numpy is sufficient
        pass
    
    # Additional libraries can be added here
    logger.debug(f"Random seed {seed} set for libraries: {', '.join(libraries)}")


def get_random_state(library: str = "numpy") -> Any:
    """Get current random state for a library.
    
    Args:
        library: Library name ("python", "numpy", "torch", etc.)
        
    Returns:
        Current random state for the specified library
    """
    if library == "python":
        return random.getstate()
    elif library == "numpy":
        return np.random.get_state()
    elif library == "torch":
        try:
            import torch
            return torch.get_rng_state()
        except ImportError:
            logger.warning("PyTorch not available")
            return None
    else:
        logger.warning(f"Unknown library for random state: {library}")
        return None


def save_random_states() -> Dict[str, Any]:
    """Save current random states for all libraries.
    
    Returns:
        Dictionary of saved random states
    """
    states = {}
    
    # Python
    states["python"] = random.getstate()
    
    # NumPy
    states["numpy"] = np.random.get_state()
    
    # PyTorch
    try:
        import torch
        states["torch"] = torch.get_rng_state()
        if torch.cuda.is_available():
            states["torch_cuda"] = torch.cuda.get_rng_state_all()
    except ImportError:
        pass
    
    logger.debug("Saved random states for all available libraries")
    return states


def restore_random_states(states: Dict[str, Any]) -> None:
    """Restore random states from saved states.
    
    Args:
        states: Dictionary of saved random states
    """
    # Python
    if "python" in states:
        random.setstate(states["python"])
    
    # NumPy
    if "numpy" in states:
        np.random.set_state(states["numpy"])
    
    # PyTorch
    if "torch" in states:
        try:
            import torch
            torch.set_rng_state(states["torch"])
            if "torch_cuda" in states and torch.cuda.is_available():
                torch.cuda.set_rng_state_all(states["torch_cuda"])
        except ImportError:
            pass
    
    logger.debug("Restored random states from saved states")


class RandomSeedContext:
    """Context manager for temporary random seed setting."""
    
    def __init__(
        self,
        seed: int,
        libraries: Optional[list] = None,
        restore_after: bool = True
    ) -> None:
        """Initialize random seed context.
        
        Args:
            seed: Random seed to set
            libraries: Libraries to set seed for
            restore_after: Whether to restore original states after context
        """
        self.seed = seed
        self.libraries = libraries
        self.restore_after = restore_after
        self.original_states: Dict[str, Any] = {}
    
    def __enter__(self) -> 'RandomSeedContext':
        """Enter context and set random seed."""
        if self.restore_after:
            self.original_states = save_random_states()
        
        set_random_seed(self.seed, self.libraries, save_state=False)
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and optionally restore original states."""
        if self.restore_after and self.original_states:
            restore_random_states(self.original_states)


def create_deterministic_config() -> Dict[str, Any]:
    """Create configuration for fully deterministic execution.
    
    Returns:
        Configuration dictionary for deterministic execution
    """
    config = {
        "seed": 42,
        "deterministic": True,
    }
    
    # PyTorch specific settings
    try:
        import torch
        config["torch"] = {
            "deterministic": True,
            "benchmark": False,
            "use_deterministic_algorithms": True,
        }
    except ImportError:
        pass
    
    # TensorFlow specific settings
    try:
        import tensorflow as tf
        config["tensorflow"] = {
            "deterministic_ops": True,
        }
    except ImportError:
        pass
    
    return config


def apply_deterministic_config(config: Optional[Dict[str, Any]] = None) -> None:
    """Apply deterministic configuration.
    
    Args:
        config: Configuration dictionary. If None, uses default deterministic config.
    """
    if config is None:
        config = create_deterministic_config()
    
    # Set random seed
    seed = config.get("seed", 42)
    set_random_seed(seed)
    
    # PyTorch settings
    torch_config = config.get("torch", {})
    if torch_config:
        try:
            import torch
            
            if torch_config.get("deterministic", False):
                torch.backends.cudnn.deterministic = True
            
            if not torch_config.get("benchmark", True):
                torch.backends.cudnn.benchmark = False
            
            if torch_config.get("use_deterministic_algorithms", False):
                torch.use_deterministic_algorithms(True)
                
        except ImportError:
            logger.debug("PyTorch not available for deterministic configuration")
    
    # TensorFlow settings  
    tf_config = config.get("tensorflow", {})
    if tf_config:
        try:
            import tensorflow as tf
            
            if tf_config.get("deterministic_ops", False):
                tf.config.experimental.enable_op_determinism()
                
        except ImportError:
            logger.debug("TensorFlow not available for deterministic configuration")
    
    logger.info(f"Applied deterministic configuration with seed {seed}")


# Utility function for generating reproducible random samples
def generate_reproducible_samples(
    distribution: str,
    size: int,
    seed: int,
    **params: Any
) -> np.ndarray:
    """Generate reproducible random samples from a distribution.
    
    Args:
        distribution: Distribution name ('normal', 'uniform', 'exponential', etc.)
        size: Number of samples to generate
        seed: Random seed
        **params: Distribution parameters
        
    Returns:
        Array of random samples
    """
    # Set seed for this function only
    original_state = np.random.get_state()
    np.random.seed(seed)
    
    try:
        if distribution == "normal":
            mean = params.get("mean", 0.0)
            std = params.get("std", 1.0)
            samples = np.random.normal(mean, std, size)
        elif distribution == "uniform":
            low = params.get("low", 0.0)
            high = params.get("high", 1.0)
            samples = np.random.uniform(low, high, size)
        elif distribution == "exponential":
            scale = params.get("scale", 1.0)
            samples = np.random.exponential(scale, size)
        elif distribution == "gamma":
            shape = params.get("shape", 1.0)
            scale = params.get("scale", 1.0)
            samples = np.random.gamma(shape, scale, size)
        elif distribution == "beta":
            a = params.get("a", 1.0)
            b = params.get("b", 1.0)
            samples = np.random.beta(a, b, size)
        else:
            raise ValueError(f"Unsupported distribution: {distribution}")
        
        return samples
        
    finally:
        # Restore original random state
        np.random.set_state(original_state)
