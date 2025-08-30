"""Metrics and evaluation utilities for PCE."""

import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
from collections import defaultdict
import scipy.stats as stats
from sklearn.metrics import mutual_info_score
import networkx as nx

logger = logging.getLogger(__name__)


@dataclass
class MetricResult:
    """Container for metric computation results."""
    name: str
    value: float
    confidence_interval: Optional[Tuple[float, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        if self.confidence_interval:
            ci_str = f" (95% CI: [{self.confidence_interval[0]:.4f}, {self.confidence_interval[1]:.4f}])"
        else:
            ci_str = ""
        return f"{self.name}: {self.value:.6f}{ci_str}"


class BaseMetrics(ABC):
    """Base class for metric computation."""
    
    @abstractmethod
    def compute(self, data: Any, **kwargs: Any) -> Dict[str, MetricResult]:
        """Compute metrics for the given data."""
        pass


class EntropyMetrics(BaseMetrics):
    """Entropy-based metrics for biological systems."""
    
    def compute(self, data: Union[np.ndarray, List[float]], **kwargs: Any) -> Dict[str, MetricResult]:
        """Compute entropy metrics."""
        if isinstance(data, list):
            data = np.array(data)
        
        results = {}
        
        # Shannon entropy
        shannon = self._shannon_entropy(data)
        results["shannon_entropy"] = MetricResult("Shannon Entropy", shannon)
        
        # Renyi entropy (with alpha=2)
        renyi = self._renyi_entropy(data, alpha=2.0)
        results["renyi_entropy"] = MetricResult("Renyi Entropy (α=2)", renyi)
        
        # Approximate entropy
        approx_ent = self._approximate_entropy(data, m=2, r=0.2)
        results["approximate_entropy"] = MetricResult("Approximate Entropy", approx_ent)
        
        # Sample entropy
        sample_ent = self._sample_entropy(data, m=2, r=0.2)
        results["sample_entropy"] = MetricResult("Sample Entropy", sample_ent)
        
        return results
    
    def _shannon_entropy(self, data: np.ndarray) -> float:
        """Compute Shannon entropy."""
        # Handle continuous data by binning
        if data.dtype != int and len(np.unique(data)) > 50:
            hist, _ = np.histogram(data, bins=50, density=True)
            hist = hist[hist > 0]  # Remove zero bins
            return -np.sum(hist * np.log2(hist))
        else:
            # Discrete data
            _, counts = np.unique(data, return_counts=True)
            probs = counts / len(data)
            return -np.sum(probs * np.log2(probs))
    
    def _renyi_entropy(self, data: np.ndarray, alpha: float) -> float:
        """Compute Renyi entropy."""
        if alpha == 1.0:
            return self._shannon_entropy(data)
        
        if data.dtype != int and len(np.unique(data)) > 50:
            hist, _ = np.histogram(data, bins=50, density=True)
            hist = hist[hist > 0]
        else:
            _, counts = np.unique(data, return_counts=True)
            hist = counts / len(data)
        
        if alpha == np.inf:
            return -np.log2(np.max(hist))  # Min-entropy
        
        sum_probs_alpha = np.sum(hist ** alpha)
        if sum_probs_alpha == 0:
            return float('inf')
        
        return (1 / (1 - alpha)) * np.log2(sum_probs_alpha)
    
    def _approximate_entropy(self, data: np.ndarray, m: int, r: float) -> float:
        """Compute approximate entropy (ApEn)."""
        N = len(data)
        
        def _maxdist(xi: np.ndarray, xj: np.ndarray) -> float:
            return max([abs(ua - va) for ua, va in zip(xi, xj)])
        
        def _phi(m: int) -> float:
            patterns = np.array([data[i:i + m] for i in range(N - m + 1)])
            C = np.zeros(N - m + 1)
            
            for i in range(N - m + 1):
                template = patterns[i]
                matches = sum([1 for j in range(N - m + 1) 
                             if _maxdist(template, patterns[j]) <= r])
                C[i] = matches / (N - m + 1)
            
            phi = np.mean(np.log(C))
            return phi
        
        return _phi(m) - _phi(m + 1)
    
    def _sample_entropy(self, data: np.ndarray, m: int, r: float) -> float:
        """Compute sample entropy (SampEn)."""
        N = len(data)
        
        def _maxdist(xi: np.ndarray, xj: np.ndarray) -> float:
            return max([abs(ua - va) for ua, va in zip(xi, xj)])
        
        def _phi(m: int) -> float:
            patterns = np.array([data[i:i + m] for i in range(N - m + 1)])
            matches = 0
            total = 0
            
            for i in range(N - m + 1):
                for j in range(i + 1, N - m + 1):
                    total += 1
                    if _maxdist(patterns[i], patterns[j]) <= r:
                        matches += 1
            
            return matches / total if total > 0 else 0
        
        phi_m = _phi(m)
        phi_m1 = _phi(m + 1)
        
        if phi_m1 == 0:
            return float('inf')
        
        return -np.log(phi_m1 / phi_m)


class PerformanceMetrics(BaseMetrics):
    """Performance and computational metrics."""
    
    def __init__(self) -> None:
        self.timings: Dict[str, List[float]] = defaultdict(list)
        self.memory_usage: List[float] = []
        self.gpu_usage: List[float] = []
    
    def add_timing(self, operation: str, duration: float) -> None:
        """Add timing measurement."""
        self.timings[operation].append(duration)
    
    def add_memory_usage(self, memory_mb: float) -> None:
        """Add memory usage measurement."""
        self.memory_usage.append(memory_mb)
    
    def add_gpu_usage(self, gpu_percent: float) -> None:
        """Add GPU usage measurement."""
        self.gpu_usage.append(gpu_percent)
    
    def compute(self, data: Optional[Any] = None, **kwargs: Any) -> Dict[str, MetricResult]:
        """Compute performance metrics."""
        results = {}
        
        # Timing statistics
        for operation, times in self.timings.items():
            if times:
                mean_time = np.mean(times)
                std_time = np.std(times)
                
                # 95% confidence interval for mean
                n = len(times)
                se = std_time / np.sqrt(n)
                ci = stats.t.interval(0.95, n-1, loc=mean_time, scale=se)
                
                results[f"{operation}_mean_time"] = MetricResult(
                    f"{operation} Mean Time",
                    mean_time,
                    confidence_interval=ci
                )
                
                results[f"{operation}_std_time"] = MetricResult(
                    f"{operation} Time Std Dev",
                    std_time
                )
        
        # Memory statistics
        if self.memory_usage:
            results["mean_memory"] = MetricResult(
                "Mean Memory Usage (MB)",
                np.mean(self.memory_usage)
            )
            results["max_memory"] = MetricResult(
                "Max Memory Usage (MB)",
                np.max(self.memory_usage)
            )
        
        # GPU statistics
        if self.gpu_usage:
            results["mean_gpu"] = MetricResult(
                "Mean GPU Usage (%)",
                np.mean(self.gpu_usage)
            )
            results["max_gpu"] = MetricResult(
                "Max GPU Usage (%)",
                np.max(self.gpu_usage)
            )
        
        return results


class BiologicalMetrics(BaseMetrics):
    """Biological and omics-specific metrics."""
    
    def compute(
        self, 
        data: Union[np.ndarray, Dict[str, np.ndarray]], 
        **kwargs: Any
    ) -> Dict[str, MetricResult]:
        """Compute biological metrics."""
        results = {}
        
        if isinstance(data, dict):
            # Multi-omics data
            for omics_type, omics_data in data.items():
                omics_results = self._compute_single_omics_metrics(omics_data, omics_type)
                results.update(omics_results)
            
            # Cross-omics metrics
            cross_results = self._compute_cross_omics_metrics(data)
            results.update(cross_results)
        else:
            # Single omics data
            results = self._compute_single_omics_metrics(data, "omics")
        
        return results
    
    def _compute_single_omics_metrics(
        self, 
        data: np.ndarray, 
        omics_type: str
    ) -> Dict[str, MetricResult]:
        """Compute metrics for single omics layer."""
        results = {}
        
        # Basic statistics
        results[f"{omics_type}_mean"] = MetricResult(
            f"{omics_type} Mean",
            np.mean(data)
        )
        results[f"{omics_type}_std"] = MetricResult(
            f"{omics_type} Std Dev",
            np.std(data)
        )
        
        # Sparsity (fraction of zeros)
        sparsity = np.sum(data == 0) / data.size
        results[f"{omics_type}_sparsity"] = MetricResult(
            f"{omics_type} Sparsity",
            sparsity
        )
        
        # Dynamic range
        if np.max(data) != np.min(data):
            dynamic_range = np.log10(np.max(data) / np.max(np.min(data), 1e-10))
        else:
            dynamic_range = 0.0
        
        results[f"{omics_type}_dynamic_range"] = MetricResult(
            f"{omics_type} Dynamic Range (log10)",
            dynamic_range
        )
        
        # Coefficient of variation
        cv = np.std(data) / np.max(np.mean(data), 1e-10)
        results[f"{omics_type}_cv"] = MetricResult(
            f"{omics_type} Coefficient of Variation",
            cv
        )
        
        return results
    
    def _compute_cross_omics_metrics(
        self, 
        data: Dict[str, np.ndarray]
    ) -> Dict[str, MetricResult]:
        """Compute cross-omics integration metrics."""
        results = {}
        
        omics_types = list(data.keys())
        
        # Pairwise correlations
        for i, omics1 in enumerate(omics_types):
            for j, omics2 in enumerate(omics_types[i+1:], i+1):
                # Flatten arrays for correlation
                data1 = data[omics1].flatten()
                data2 = data[omics2].flatten()
                
                # Ensure same length
                min_len = min(len(data1), len(data2))
                data1 = data1[:min_len]
                data2 = data2[:min_len]
                
                # Pearson correlation
                corr, p_value = stats.pearsonr(data1, data2)
                results[f"correlation_{omics1}_{omics2}"] = MetricResult(
                    f"Correlation {omics1}-{omics2}",
                    corr,
                    metadata={"p_value": p_value}
                )
                
                # Mutual information
                # Discretize for MI computation
                data1_discrete = pd.cut(data1, bins=20, labels=False)
                data2_discrete = pd.cut(data2, bins=20, labels=False)
                
                # Handle NaN values
                valid_mask = ~(pd.isna(data1_discrete) | pd.isna(data2_discrete))
                if np.sum(valid_mask) > 0:
                    mi = mutual_info_score(
                        data1_discrete[valid_mask], 
                        data2_discrete[valid_mask]
                    )
                    results[f"mutual_info_{omics1}_{omics2}"] = MetricResult(
                        f"Mutual Information {omics1}-{omics2}",
                        mi
                    )
        
        return results


class ConsciousnessMetrics(BaseMetrics):
    """Metrics for consciousness and neural complexity."""
    
    def compute(
        self, 
        data: Union[np.ndarray, nx.Graph], 
        **kwargs: Any
    ) -> Dict[str, MetricResult]:
        """Compute consciousness-related metrics."""
        results = {}
        
        if isinstance(data, nx.Graph):
            # Network-based metrics
            results.update(self._compute_network_metrics(data))
        elif isinstance(data, np.ndarray):
            # Time series or connectivity matrix metrics
            if data.ndim == 2 and data.shape[0] == data.shape[1]:
                # Treat as connectivity matrix
                G = nx.from_numpy_array(data)
                results.update(self._compute_network_metrics(G))
            else:
                # Treat as time series
                results.update(self._compute_timeseries_metrics(data))
        
        return results
    
    def _compute_network_metrics(self, graph: nx.Graph) -> Dict[str, MetricResult]:
        """Compute network-based consciousness metrics."""
        results = {}
        
        # Global efficiency (related to integration)
        try:
            global_eff = nx.global_efficiency(graph)
            results["global_efficiency"] = MetricResult(
                "Global Efficiency",
                global_eff
            )
        except:
            pass
        
        # Local efficiency (related to segregation)
        try:
            local_eff = nx.local_efficiency(graph)
            results["local_efficiency"] = MetricResult(
                "Local Efficiency",
                local_eff
            )
        except:
            pass
        
        # Small-worldness
        try:
            # Random graph for comparison
            n = graph.number_of_nodes()
            m = graph.number_of_edges()
            p = 2 * m / (n * (n - 1)) if n > 1 else 0
            
            random_graph = nx.erdos_renyi_graph(n, p)
            
            # Clustering coefficient
            cc_actual = nx.average_clustering(graph)
            cc_random = nx.average_clustering(random_graph)
            
            # Average shortest path length
            if nx.is_connected(graph):
                l_actual = nx.average_shortest_path_length(graph)
                l_random = nx.average_shortest_path_length(random_graph)
                
                # Small-worldness coefficient
                if cc_random > 0 and l_random > 0:
                    small_world = (cc_actual / cc_random) / (l_actual / l_random)
                    results["small_worldness"] = MetricResult(
                        "Small-worldness",
                        small_world
                    )
        except:
            pass
        
        # Modularity
        try:
            import community  # python-louvain
            partition = community.best_partition(graph)
            modularity = community.modularity(partition, graph)
            results["modularity"] = MetricResult(
                "Modularity",
                modularity
            )
        except ImportError:
            # Fallback: approximate modularity using networkx
            try:
                communities = nx.community.greedy_modularity_communities(graph)
                modularity = nx.community.modularity(graph, communities)
                results["modularity"] = MetricResult(
                    "Modularity",
                    modularity
                )
            except:
                pass
        
        # Rich club coefficient
        try:
            degrees = [d for n, d in graph.degree()]
            if degrees:
                k = int(np.percentile(degrees, 75))  # Top 25% of nodes
                rich_club = nx.rich_club_coefficient(graph, k)
                if k in rich_club:
                    results["rich_club"] = MetricResult(
                        f"Rich Club (k={k})",
                        rich_club[k]
                    )
        except:
            pass
        
        return results
    
    def _compute_timeseries_metrics(self, data: np.ndarray) -> Dict[str, MetricResult]:
        """Compute time series consciousness metrics."""
        results = {}
        
        # Lempel-Ziv complexity
        lz_complexity = self._lempel_ziv_complexity(data)
        results["lz_complexity"] = MetricResult(
            "Lempel-Ziv Complexity",
            lz_complexity
        )
        
        # Fractal dimension (Higuchi method)
        fractal_dim = self._fractal_dimension(data)
        results["fractal_dimension"] = MetricResult(
            "Fractal Dimension",
            fractal_dim
        )
        
        return results
    
    def _lempel_ziv_complexity(self, data: np.ndarray) -> float:
        """Compute Lempel-Ziv complexity."""
        # Binarize data
        binary_data = (data > np.median(data)).astype(int)
        
        # Convert to string
        s = ''.join(map(str, binary_data))
        
        # Compute LZ complexity
        n = len(s)
        complexity = 0
        i = 0
        
        while i < n:
            j = i + 1
            while j <= n:
                if s[i:j] not in s[:i]:
                    complexity += 1
                    i = j - 1
                    break
                j += 1
            else:
                complexity += 1
                break
            i += 1
        
        # Normalize by theoretical maximum
        max_complexity = n / np.log2(n) if n > 1 else 1
        return complexity / max_complexity
    
    def _fractal_dimension(self, data: np.ndarray, kmax: int = 10) -> float:
        """Compute fractal dimension using Higuchi method."""
        N = len(data)
        lk = np.zeros(kmax)
        
        for k in range(1, kmax + 1):
            lm = np.zeros(k)
            for m in range(k):
                ll = 0
                n_max = int((N - m - 1) / k)
                for i in range(1, n_max + 1):
                    ll += abs(data[m + i * k] - data[m + (i - 1) * k])
                ll = ll * (N - 1) / (n_max * k * k)
                lm[m] = ll
            lk[k - 1] = np.mean(lm)
        
        # Linear regression in log-log scale
        x = np.log(range(1, kmax + 1))
        y = np.log(lk)
        
        # Remove any infinite values
        valid_mask = np.isfinite(x) & np.isfinite(y)
        if np.sum(valid_mask) > 1:
            slope, _, _, _, _ = stats.linregress(x[valid_mask], y[valid_mask])
            return -slope
        else:
            return 1.0  # Default fallback


# Convenience functions

def timer_context(name: str = "Operation"):
    """Context manager for timing operations.
    
    Args:
        name: Name of the operation being timed
        
    Example:
        >>> with timer_context("Data loading"):
        ...     data = load_large_dataset()
    """
    import time
    import contextlib
    from ..utils.logging import get_logger
    
    logger = get_logger(__name__)
    
    @contextlib.contextmanager
    def timer():
        start_time = time.time()
        logger.info(f"Starting {name}...")
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            logger.info(f"{name} completed in {elapsed:.2f} seconds")
    
    return timer()


def compute_biological_metrics(
    data: 'OmicsData',
    include_entropy: bool = True,
    include_network: bool = True,
    include_consciousness: bool = False
) -> Dict[str, MetricResult]:
    """Compute biological metrics for omics data.
    
    Args:
        data: Multi-omics data
        include_entropy: Whether to compute entropy-based metrics
        include_network: Whether to compute network-based metrics
        include_consciousness: Whether to compute consciousness metrics
        
    Returns:
        Dictionary of computed metrics
    """
    metrics = {}
    
    if include_entropy:
        entropy_calc = EntropyMetrics()
        # Compute entropy for each omics layer
        for omics_type, layer_data in data.omics_layers.items():
            if hasattr(layer_data, 'values'):
                # Convert to array if needed
                if hasattr(layer_data, 'values'):
                    values = layer_data.values()
                else:
                    values = layer_data
                
                # Compute shannon entropy
                try:
                    entropy = entropy_calc.shannon_entropy(np.array(list(values)))
                    metrics[f"{omics_type}_shannon_entropy"] = entropy
                except:
                    pass
    
    if include_network:
        bio_calc = BiologicalMetrics()
        # Compute biological network metrics
        try:
            # This would require a proper graph construction from the data
            # For now, create a simple placeholder
            import networkx as nx
            n_nodes = min(len(data.samples), 50)  # Limit for performance
            G = nx.random_graph(n_nodes, 0.1)  # Placeholder graph
            
            network_metrics = bio_calc.compute_network_metrics(G)
            metrics.update(network_metrics)
        except:
            pass
    
    if include_consciousness:
        consciousness_calc = ConsciousnessMetrics()
        # Placeholder consciousness metrics
        try:
            # This would require actual consciousness computation
            dummy_phi = consciousness_calc.compute_phi(np.random.randn(10, 10))
            metrics["consciousness_phi"] = dummy_phi
        except:
            pass
    
    return metrics
