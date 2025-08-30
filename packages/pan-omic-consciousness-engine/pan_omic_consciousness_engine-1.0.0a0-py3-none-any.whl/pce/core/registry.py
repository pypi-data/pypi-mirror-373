"""Plugin registry for extensible PCE architecture."""

import logging
from typing import Any, Dict, List, Type, Callable, Optional, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
import importlib
import inspect

from .datatypes import OmicsAdapter

logger = logging.getLogger(__name__)


class PluginInterface(ABC):
    """Base interface for PCE plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the plugin with configuration."""
        pass


@dataclass
class PluginInfo:
    """Information about a registered plugin."""
    name: str
    plugin_type: str
    plugin_class: Type[Any]
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    dependencies: List[str] = None
    
    def __post_init__(self) -> None:
        if self.dependencies is None:
            self.dependencies = []


class PluginRegistry:
    """Registry for managing PCE plugins and adapters."""
    
    def __init__(self) -> None:
        self._plugins: Dict[str, Dict[str, PluginInfo]] = {
            "omics_adapters": {},
            "entropy_functions": {},
            "evolution_operators": {},
            "consciousness_models": {},
            "visualization": {},
        }
        self._initialized_plugins: Dict[str, Any] = {}
        
        # Register built-in adapters
        self._register_builtins()
    
    def register_plugin(
        self,
        plugin_type: str,
        name: str,
        plugin_class: Type[Any],
        version: str = "1.0.0",
        description: str = "",
        author: str = "",
        dependencies: Optional[List[str]] = None
    ) -> None:
        """Register a plugin."""
        if plugin_type not in self._plugins:
            self._plugins[plugin_type] = {}
        
        if name in self._plugins[plugin_type]:
            logger.warning(f"Overriding existing plugin: {plugin_type}/{name}")
        
        info = PluginInfo(
            name=name,
            plugin_type=plugin_type,
            plugin_class=plugin_class,
            version=version,
            description=description,
            author=author,
            dependencies=dependencies or []
        )
        
        self._plugins[plugin_type][name] = info
        logger.info(f"Registered plugin: {plugin_type}/{name} v{version}")
    
    def get_plugin(self, plugin_type: str, name: str) -> Optional[PluginInfo]:
        """Get plugin information."""
        return self._plugins.get(plugin_type, {}).get(name)
    
    def list_plugins(self, plugin_type: Optional[str] = None) -> Dict[str, Dict[str, PluginInfo]]:
        """List all plugins or plugins of a specific type."""
        if plugin_type is not None:
            return {plugin_type: self._plugins.get(plugin_type, {})}
        return self._plugins.copy()
    
    def create_instance(
        self,
        plugin_type: str,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Any:
        """Create an instance of a plugin."""
        plugin_info = self.get_plugin(plugin_type, name)
        if plugin_info is None:
            raise ValueError(f"Plugin not found: {plugin_type}/{name}")
        
        # Check dependencies
        self._check_dependencies(plugin_info)
        
        # Create instance
        try:
            instance = plugin_info.plugin_class(**kwargs)
            
            # Initialize if it's a PluginInterface
            if isinstance(instance, PluginInterface):
                instance.initialize(config or {})
            
            # Cache initialized plugin
            cache_key = f"{plugin_type}/{name}"
            self._initialized_plugins[cache_key] = instance
            
            return instance
            
        except Exception as e:
            logger.error(f"Failed to create plugin instance {plugin_type}/{name}: {e}")
            raise
    
    def get_instance(self, plugin_type: str, name: str) -> Optional[Any]:
        """Get cached plugin instance."""
        cache_key = f"{plugin_type}/{name}"
        return self._initialized_plugins.get(cache_key)
    
    def _check_dependencies(self, plugin_info: PluginInfo) -> None:
        """Check plugin dependencies."""
        for dep in plugin_info.dependencies:
            try:
                importlib.import_module(dep)
            except ImportError as e:
                raise ImportError(f"Plugin {plugin_info.name} requires {dep}: {e}")
    
    def _register_builtins(self) -> None:
        """Register built-in plugins."""
        # This will be populated as we create built-in adapters
        pass
    
    def register_omics_adapter(
        self,
        name: str,
        adapter_class: Type[OmicsAdapter],
        **kwargs: Any
    ) -> None:
        """Convenience method to register omics adapter."""
        self.register_plugin("omics_adapters", name, adapter_class, **kwargs)
    
    def register_entropy_function(
        self,
        name: str,
        function: Callable[..., float],
        **kwargs: Any
    ) -> None:
        """Register entropy function."""
        # Wrap function in a class
        class EntropyWrapper:
            def __init__(self) -> None:
                self.function = function
            
            def compute(self, *args: Any, **kwargs: Any) -> float:
                return self.function(*args, **kwargs)
        
        self.register_plugin("entropy_functions", name, EntropyWrapper, **kwargs)
    
    def register_evolution_operator(
        self,
        name: str,
        operator_class: Type[Any],
        **kwargs: Any
    ) -> None:
        """Register evolution operator."""
        self.register_plugin("evolution_operators", name, operator_class, **kwargs)
    
    def register_consciousness_model(
        self,
        name: str,
        model_class: Type[Any],
        **kwargs: Any
    ) -> None:
        """Register consciousness model."""
        self.register_plugin("consciousness_models", name, model_class, **kwargs)
    
    def load_plugins_from_module(self, module_name: str) -> None:
        """Load plugins from a Python module."""
        try:
            module = importlib.import_module(module_name)
            
            # Look for plugin registration functions
            for name in dir(module):
                obj = getattr(module, name)
                
                # Check for plugin classes
                if (inspect.isclass(obj) and 
                    hasattr(obj, '__plugin_type__') and 
                    hasattr(obj, '__plugin_name__')):
                    
                    plugin_type = getattr(obj, '__plugin_type__')
                    plugin_name = getattr(obj, '__plugin_name__')
                    
                    self.register_plugin(
                        plugin_type=plugin_type,
                        name=plugin_name,
                        plugin_class=obj,
                        version=getattr(obj, '__plugin_version__', '1.0.0'),
                        description=getattr(obj, '__doc__', ''),
                        author=getattr(obj, '__plugin_author__', 'Unknown')
                    )
                
                # Check for registration functions
                elif (callable(obj) and 
                      name.startswith('register_') and 
                      name.endswith('_plugins')):
                    obj(self)
            
            logger.info(f"Loaded plugins from module: {module_name}")
            
        except ImportError as e:
            logger.error(f"Failed to load plugins from {module_name}: {e}")
    
    def summary(self) -> str:
        """Get summary of registered plugins."""
        lines = ["Plugin Registry Summary:"]
        
        for plugin_type, plugins in self._plugins.items():
            if plugins:
                lines.append(f"  {plugin_type}: {len(plugins)} plugins")
                for name, info in plugins.items():
                    lines.append(f"    - {name} v{info.version}")
        
        return "\n".join(lines)


# Global registry instance
_registry: Optional[PluginRegistry] = None


def get_registry() -> PluginRegistry:
    """Get the global plugin registry."""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry


def register_plugin(
    plugin_type: str,
    name: str,
    plugin_class: Type[Any],
    **kwargs: Any
) -> None:
    """Register a plugin with the global registry."""
    registry = get_registry()
    registry.register_plugin(plugin_type, name, plugin_class, **kwargs)


# Decorators for easy plugin registration
def omics_adapter(name: str, **kwargs: Any) -> Callable[[Type[Any]], Type[Any]]:
    """Decorator to register an omics adapter."""
    def decorator(cls: Type[Any]) -> Type[Any]:
        cls.__plugin_type__ = "omics_adapters"
        cls.__plugin_name__ = name
        register_plugin("omics_adapters", name, cls, **kwargs)
        return cls
    return decorator


def entropy_function(name: str, **kwargs: Any) -> Callable[[Callable[..., float]], Callable[..., float]]:
    """Decorator to register an entropy function."""
    def decorator(func: Callable[..., float]) -> Callable[..., float]:
        get_registry().register_entropy_function(name, func, **kwargs)
        return func
    return decorator


def evolution_operator(name: str, **kwargs: Any) -> Callable[[Type[Any]], Type[Any]]:
    """Decorator to register an evolution operator."""
    def decorator(cls: Type[Any]) -> Type[Any]:
        cls.__plugin_type__ = "evolution_operators"
        cls.__plugin_name__ = name
        register_plugin("evolution_operators", name, cls, **kwargs)
        return cls
    return decorator
