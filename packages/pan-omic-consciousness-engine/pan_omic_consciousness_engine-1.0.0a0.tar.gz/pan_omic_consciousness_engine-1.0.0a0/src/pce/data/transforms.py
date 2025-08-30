"""Data processing and transformation utilities."""

import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import scipy.stats as stats

from ..core.datatypes import OmicsData, HyperGraph, LatentEmbedding
from ..utils.logging import get_logger, timer_context

logger = get_logger(__name__)


@dataclass
class TransformConfig:
    """Configuration for data transformations."""
    normalize: bool = True
    normalization_method: str = "standard"  # "standard", "minmax", "robust"
    log_transform: bool = True
    remove_outliers: bool = True
    outlier_threshold: float = 3.0  # z-score threshold
    impute_missing: bool = True
    imputation_method: str = "median"  # "mean", "median", "mode", "knn"
    batch_correction: bool = False
    filter_low_variance: bool = True
    variance_threshold: float = 0.01


class BaseTransform(ABC):
    """Base class for data transformations."""
    
    @abstractmethod
    def fit(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> 'BaseTransform':
        """Fit the transformation to data."""
        pass
    
    @abstractmethod
    def transform(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> np.ndarray:
        """Apply the transformation to data."""
        pass
    
    def fit_transform(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> np.ndarray:
        """Fit and transform data in one step."""
        return self.fit(data, **kwargs).transform(data, **kwargs)


class NormalizationTransform(BaseTransform):
    """Normalization transformation for omics data."""
    
    def __init__(self, method: str = "standard") -> None:
        self.method = method
        self.scaler: Optional[Any] = None
    
    def fit(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> 'NormalizationTransform':
        """Fit normalization parameters."""
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        if self.method == "standard":
            self.scaler = StandardScaler()
        elif self.method == "minmax":
            self.scaler = MinMaxScaler()
        elif self.method == "robust":
            self.scaler = RobustScaler()
        else:
            raise ValueError(f"Unknown normalization method: {self.method}")
        
        self.scaler.fit(data)
        return self
    
    def transform(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> np.ndarray:
        """Apply normalization."""
        if self.scaler is None:
            raise ValueError("Transform must be fitted before use")
        
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        return self.scaler.transform(data)


class LogTransform(BaseTransform):
    """Log transformation with handling for zero and negative values."""
    
    def __init__(self, base: str = "natural", pseudocount: float = 1.0) -> None:
        self.base = base
        self.pseudocount = pseudocount
    
    def fit(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> 'LogTransform':
        """Log transform doesn't require fitting."""
        return self
    
    def transform(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> np.ndarray:
        """Apply log transformation."""
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        # Add pseudocount to handle zeros
        data_shifted = data + self.pseudocount
        
        if self.base == "natural":
            return np.log(data_shifted)
        elif self.base == "log2":
            return np.log2(data_shifted)
        elif self.base == "log10":
            return np.log10(data_shifted)
        else:
            raise ValueError(f"Unknown log base: {self.base}")


class OutlierRemovalTransform(BaseTransform):
    """Outlier removal using z-score or IQR methods."""
    
    def __init__(self, method: str = "zscore", threshold: float = 3.0) -> None:
        self.method = method
        self.threshold = threshold
        self.outlier_mask: Optional[np.ndarray] = None
    
    def fit(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> 'OutlierRemovalTransform':
        """Identify outliers."""
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        if self.method == "zscore":
            z_scores = np.abs(stats.zscore(data, axis=0, nan_policy='omit'))
            self.outlier_mask = np.any(z_scores > self.threshold, axis=1)
        elif self.method == "iqr":
            Q1 = np.percentile(data, 25, axis=0)
            Q3 = np.percentile(data, 75, axis=0)
            IQR = Q3 - Q1
            lower_bound = Q1 - self.threshold * IQR
            upper_bound = Q3 + self.threshold * IQR
            self.outlier_mask = np.any(
                (data < lower_bound) | (data > upper_bound), axis=1
            )
        else:
            raise ValueError(f"Unknown outlier detection method: {self.method}")
        
        logger.info(f"Identified {np.sum(self.outlier_mask)} outliers out of {len(data)} samples")
        return self
    
    def transform(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> np.ndarray:
        """Remove outliers."""
        if self.outlier_mask is None:
            raise ValueError("Transform must be fitted before use")
        
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        # Return data without outliers
        return data[~self.outlier_mask]


class ImputationTransform(BaseTransform):
    """Missing value imputation."""
    
    def __init__(self, method: str = "median") -> None:
        self.method = method
        self.fill_values: Optional[np.ndarray] = None
        self.knn_imputer: Optional[Any] = None
    
    def fit(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> 'ImputationTransform':
        """Fit imputation parameters."""
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        if self.method == "mean":
            self.fill_values = np.nanmean(data, axis=0)
        elif self.method == "median":
            self.fill_values = np.nanmedian(data, axis=0)
        elif self.method == "mode":
            self.fill_values = stats.mode(data, axis=0, nan_policy='omit')[0].flatten()
        elif self.method == "knn":
            from sklearn.impute import KNNImputer
            self.knn_imputer = KNNImputer(n_neighbors=5)
            self.knn_imputer.fit(data)
        else:
            raise ValueError(f"Unknown imputation method: {self.method}")
        
        return self
    
    def transform(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> np.ndarray:
        """Apply imputation."""
        if isinstance(data, pd.DataFrame):
            data = data.values.copy()
        else:
            data = data.copy()
        
        if self.method == "knn":
            if self.knn_imputer is None:
                raise ValueError("KNN imputer not fitted")
            return self.knn_imputer.transform(data)
        else:
            if self.fill_values is None:
                raise ValueError("Fill values not computed")
            
            # Replace NaN values with fill values
            for i in range(data.shape[1]):
                mask = np.isnan(data[:, i])
                data[mask, i] = self.fill_values[i]
            
            return data


class VarianceFilterTransform(BaseTransform):
    """Filter features with low variance."""
    
    def __init__(self, threshold: float = 0.01) -> None:
        self.threshold = threshold
        self.selected_features: Optional[np.ndarray] = None
    
    def fit(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> 'VarianceFilterTransform':
        """Identify high-variance features."""
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        variances = np.var(data, axis=0)
        self.selected_features = variances > self.threshold
        
        logger.info(
            f"Selected {np.sum(self.selected_features)} features out of "
            f"{len(self.selected_features)} based on variance > {self.threshold}"
        )
        return self
    
    def transform(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> np.ndarray:
        """Filter features by variance."""
        if self.selected_features is None:
            raise ValueError("Transform must be fitted before use")
        
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        return data[:, self.selected_features]


class DimensionalityReductionTransform(BaseTransform):
    """Dimensionality reduction using PCA or t-SNE."""
    
    def __init__(self, method: str = "pca", n_components: int = 50, **kwargs: Any) -> None:
        self.method = method
        self.n_components = n_components
        self.kwargs = kwargs
        self.reducer: Optional[Any] = None
    
    def fit(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> 'DimensionalityReductionTransform':
        """Fit dimensionality reduction."""
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        if self.method == "pca":
            self.reducer = PCA(n_components=self.n_components, **self.kwargs)
        elif self.method == "tsne":
            self.reducer = TSNE(n_components=self.n_components, **self.kwargs)
        else:
            raise ValueError(f"Unknown dimensionality reduction method: {self.method}")
        
        self.reducer.fit(data)
        return self
    
    def transform(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> np.ndarray:
        """Apply dimensionality reduction."""
        if self.reducer is None:
            raise ValueError("Transform must be fitted before use")
        
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        return self.reducer.transform(data)


class BatchCorrectionTransform(BaseTransform):
    """Batch effect correction using ComBat or similar methods."""
    
    def __init__(self, batch_labels: Optional[np.ndarray] = None) -> None:
        self.batch_labels = batch_labels
        self.correction_params: Optional[Dict[str, Any]] = None
    
    def fit(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> 'BatchCorrectionTransform':
        """Fit batch correction parameters."""
        if self.batch_labels is None:
            logger.warning("No batch labels provided, skipping batch correction")
            return self
        
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        # Simple mean centering per batch (placeholder for more sophisticated methods)
        self.correction_params = {}
        unique_batches = np.unique(self.batch_labels)
        
        for batch in unique_batches:
            batch_mask = self.batch_labels == batch
            batch_data = data[batch_mask]
            batch_mean = np.mean(batch_data, axis=0)
            self.correction_params[batch] = batch_mean
        
        # Global mean
        self.correction_params['global_mean'] = np.mean(data, axis=0)
        
        return self
    
    def transform(self, data: Union[np.ndarray, pd.DataFrame], **kwargs: Any) -> np.ndarray:
        """Apply batch correction."""
        if self.batch_labels is None or self.correction_params is None:
            logger.warning("Batch correction not fitted, returning original data")
            if isinstance(data, pd.DataFrame):
                return data.values
            return data
        
        if isinstance(data, pd.DataFrame):
            data = data.values.copy()
        else:
            data = data.copy()
        
        # Apply correction
        global_mean = self.correction_params['global_mean']
        
        for batch in np.unique(self.batch_labels):
            batch_mask = self.batch_labels == batch
            batch_mean = self.correction_params[batch]
            
            # Center batch data and shift to global mean
            data[batch_mask] = data[batch_mask] - batch_mean + global_mean
        
        return data


class OmicsDataTransformer:
    """Main transformer for omics data with configurable pipeline."""
    
    def __init__(self, config: Optional[TransformConfig] = None) -> None:
        self.config = config or TransformConfig()
        self.transforms: List[BaseTransform] = []
        self.fitted = False
    
    def build_pipeline(self, batch_labels: Optional[np.ndarray] = None) -> None:
        """Build transformation pipeline based on configuration."""
        self.transforms = []
        
        # Imputation (should be first)
        if self.config.impute_missing:
            self.transforms.append(
                ImputationTransform(method=self.config.imputation_method)
            )
        
        # Log transformation
        if self.config.log_transform:
            self.transforms.append(LogTransform())
        
        # Outlier removal
        if self.config.remove_outliers:
            self.transforms.append(
                OutlierRemovalTransform(threshold=self.config.outlier_threshold)
            )
        
        # Variance filtering
        if self.config.filter_low_variance:
            self.transforms.append(
                VarianceFilterTransform(threshold=self.config.variance_threshold)
            )
        
        # Batch correction
        if self.config.batch_correction and batch_labels is not None:
            self.transforms.append(
                BatchCorrectionTransform(batch_labels=batch_labels)
            )
        
        # Normalization (should be last)
        if self.config.normalize:
            self.transforms.append(
                NormalizationTransform(method=self.config.normalization_method)
            )
    
    def fit(
        self,
        data: Union[np.ndarray, pd.DataFrame],
        batch_labels: Optional[np.ndarray] = None
    ) -> 'OmicsDataTransformer':
        """Fit all transformations in the pipeline."""
        if not self.transforms:
            self.build_pipeline(batch_labels)
        
        current_data = data
        
        with timer_context("Fitting omics data transformations"):
            for i, transform in enumerate(self.transforms):
                logger.debug(f"Fitting transform {i+1}/{len(self.transforms)}: {type(transform).__name__}")
                transform.fit(current_data)
                
                # Apply transform to prepare data for next step
                # (except for outlier removal which changes sample size)
                if not isinstance(transform, OutlierRemovalTransform):
                    current_data = transform.transform(current_data)
        
        self.fitted = True
        return self
    
    def transform(self, data: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Apply all transformations in sequence."""
        if not self.fitted:
            raise ValueError("Transformer must be fitted before use")
        
        current_data = data
        
        with timer_context("Applying omics data transformations"):
            for i, transform in enumerate(self.transforms):
                logger.debug(f"Applying transform {i+1}/{len(self.transforms)}: {type(transform).__name__}")
                current_data = transform.transform(current_data)
        
        return current_data
    
    def fit_transform(
        self,
        data: Union[np.ndarray, pd.DataFrame],
        batch_labels: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Fit and transform data in one step."""
        return self.fit(data, batch_labels).transform(data)
    
    def transform_omics_data(self, omics_data: OmicsData) -> Dict[str, np.ndarray]:
        """Transform all omics layers in OmicsData object."""
        results = {}
        
        for omics_type in ["genomics", "transcriptomics", "proteomics", 
                          "metabolomics", "microbiomics", "connectomics"]:
            
            entities = getattr(omics_data, omics_type, {})
            if not entities:
                continue
            
            # Convert entities to matrix (simplified)
            entity_ids = list(entities.keys())
            
            if omics_type == "transcriptomics":
                values = [entities[eid].expression_level for eid in entity_ids]
            elif omics_type == "proteomics":
                values = [entities[eid].abundance for eid in entity_ids]
            elif omics_type == "metabolomics":
                values = [entities[eid].concentration for eid in entity_ids]
            elif omics_type == "microbiomics":
                values = [entities[eid].abundance for eid in entity_ids]
            elif omics_type == "connectomics":
                values = [entities[eid].activity for eid in entity_ids]
            else:
                values = [1.0] * len(entity_ids)  # Default for genomics
            
            if values:
                data_matrix = np.array(values).reshape(-1, 1)
                transformed_data = self.transform(data_matrix)
                results[omics_type] = transformed_data.flatten()
        
        return results
