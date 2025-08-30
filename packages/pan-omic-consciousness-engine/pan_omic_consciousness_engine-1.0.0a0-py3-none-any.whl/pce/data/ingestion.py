"""Data ingestion and loading utilities for multi-omics data."""

import logging
import numpy as np
import pandas as pd
import h5py
import zarr
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from abc import ABC, abstractmethod
import json
import pickle
from dataclasses import dataclass

from ..core.datatypes import (
    OmicsData, OmicsType, BiologicalEntity, Gene, Transcript, 
    Protein, Metabolite, Microbe, BrainRegion
)
from ..core.registry import get_registry, omics_adapter
from ..utils.logging import get_logger, timer_context

logger = get_logger(__name__)


@dataclass
class DatasetInfo:
    """Information about a dataset."""
    name: str
    description: str
    format: str
    size_mb: float
    num_samples: int
    omics_types: List[str]
    metadata: Dict[str, Any]


class BaseAdapter(ABC):
    """Base class for omics data adapters."""
    
    @abstractmethod
    def load(self, path: str, **kwargs: Any) -> OmicsData:
        """Load omics data from file."""
        pass
    
    @abstractmethod
    def save(self, data: OmicsData, path: str, **kwargs: Any) -> None:
        """Save omics data to file."""
        pass
    
    @abstractmethod
    def validate(self, data: OmicsData) -> bool:
        """Validate omics data format."""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """List of supported file formats."""
        pass


@omics_adapter("h5")
class HDF5Adapter(BaseAdapter):
    """HDF5 format adapter for multi-omics data."""
    
    @property
    def supported_formats(self) -> List[str]:
        return [".h5", ".hdf5"]
    
    def load(self, path: str, **kwargs: Any) -> OmicsData:
        """Load omics data from HDF5 file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        with timer_context(f"Loading HDF5 data from {path.name}"):
            with h5py.File(path, 'r') as f:
                # Load metadata
                metadata = {}
                if 'metadata' in f:
                    metadata = json.loads(f['metadata'][()].decode('utf-8'))
                
                # Load each omics type
                omics_data = OmicsData(
                    name=metadata.get('name', path.stem),
                    metadata=metadata
                )
                
                # Load genomics
                if 'genomics' in f:
                    genes = {}
                    genomics_group = f['genomics']
                    
                    if 'genes' in genomics_group:
                        gene_data = genomics_group['genes']
                        for gene_id in gene_data.keys():
                            gene_info = gene_data[gene_id]
                            gene = Gene(
                                id=gene_id,
                                name=gene_info.attrs.get('name', gene_id),
                                chromosome=gene_info.attrs.get('chromosome', ''),
                                start_pos=int(gene_info.attrs.get('start_pos', 0)),
                                end_pos=int(gene_info.attrs.get('end_pos', 0)),
                                strand=gene_info.attrs.get('strand', '+')
                            )
                            genes[gene_id] = gene
                    
                    omics_data.genomics = genes
                
                # Load transcriptomics
                if 'transcriptomics' in f:
                    transcripts = {}
                    trans_group = f['transcriptomics']
                    
                    if 'expression_matrix' in trans_group:
                        expr_matrix = trans_group['expression_matrix'][:]
                        gene_ids = [x.decode('utf-8') for x in trans_group['gene_ids'][:]]
                        
                        for i, gene_id in enumerate(gene_ids):
                            transcript = Transcript(
                                id=f"transcript_{gene_id}",
                                name=f"Transcript of {gene_id}",
                                gene_id=gene_id,
                                expression_level=float(np.mean(expr_matrix[i, :]))
                            )
                            transcripts[transcript.id] = transcript
                    
                    omics_data.transcriptomics = transcripts
                
                # Load proteomics
                if 'proteomics' in f:
                    proteins = {}
                    prot_group = f['proteomics']
                    
                    if 'proteins' in prot_group:
                        protein_data = prot_group['proteins']
                        for protein_id in protein_data.keys():
                            prot_info = protein_data[protein_id]
                            protein = Protein(
                                id=protein_id,
                                name=prot_info.attrs.get('name', protein_id),
                                sequence=prot_info.attrs.get('sequence', ''),
                                molecular_weight=float(prot_info.attrs.get('molecular_weight', 0)),
                                abundance=float(prot_info.attrs.get('abundance', 0))
                            )
                            proteins[protein_id] = protein
                    
                    omics_data.proteomics = proteins
                
                # Load metabolomics
                if 'metabolomics' in f:
                    metabolites = {}
                    metab_group = f['metabolomics']
                    
                    if 'metabolites' in metab_group:
                        metab_data = metab_group['metabolites']
                        for metab_id in metab_data.keys():
                            metab_info = metab_data[metab_id]
                            metabolite = Metabolite(
                                id=metab_id,
                                name=metab_info.attrs.get('name', metab_id),
                                formula=metab_info.attrs.get('formula', ''),
                                mass=float(metab_info.attrs.get('mass', 0)),
                                concentration=float(metab_info.attrs.get('concentration', 0))
                            )
                            metabolites[metab_id] = metabolite
                    
                    omics_data.metabolomics = metabolites
                
                # Load microbiomics
                if 'microbiomics' in f:
                    microbes = {}
                    micro_group = f['microbiomics']
                    
                    if 'microbes' in micro_group:
                        micro_data = micro_group['microbes']
                        for microbe_id in micro_data.keys():
                            micro_info = micro_data[microbe_id]
                            microbe = Microbe(
                                id=microbe_id,
                                name=micro_info.attrs.get('name', microbe_id),
                                taxonomy=micro_info.attrs.get('taxonomy', ''),
                                abundance=float(micro_info.attrs.get('abundance', 0))
                            )
                            microbes[microbe_id] = microbe
                    
                    omics_data.microbiomics = microbes
                
                # Load connectomics
                if 'connectomics' in f:
                    brain_regions = {}
                    conn_group = f['connectomics']
                    
                    if 'regions' in conn_group:
                        region_data = conn_group['regions']
                        for region_id in region_data.keys():
                            region_info = region_data[region_id]
                            coords = region_info.attrs.get('coordinates', [0.0, 0.0, 0.0])
                            brain_region = BrainRegion(
                                id=region_id,
                                name=region_info.attrs.get('name', region_id),
                                coordinates=(float(coords[0]), float(coords[1]), float(coords[2])),
                                activity=float(region_info.attrs.get('activity', 0))
                            )
                            brain_regions[region_id] = brain_region
                    
                    omics_data.connectomics = brain_regions
                
                # Load temporal information
                if 'timepoints' in f:
                    omics_data.timepoints = f['timepoints'][:].tolist()
        
        logger.info(f"Loaded HDF5 data: {omics_data.summary()}")
        return omics_data
    
    def save(self, data: OmicsData, path: str, **kwargs: Any) -> None:
        """Save omics data to HDF5 file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with timer_context(f"Saving HDF5 data to {path.name}"):
            with h5py.File(path, 'w') as f:
                # Save metadata
                f.create_dataset(
                    'metadata',
                    data=json.dumps(data.metadata).encode('utf-8')
                )
                
                # Save genomics
                if data.genomics:
                    genomics_group = f.create_group('genomics')
                    genes_group = genomics_group.create_group('genes')
                    
                    for gene_id, gene in data.genomics.items():
                        gene_dataset = genes_group.create_dataset(gene_id, data=np.array([0]))
                        gene_dataset.attrs['name'] = gene.name
                        gene_dataset.attrs['chromosome'] = gene.chromosome
                        gene_dataset.attrs['start_pos'] = gene.start_pos
                        gene_dataset.attrs['end_pos'] = gene.end_pos
                        gene_dataset.attrs['strand'] = gene.strand
                
                # Save transcriptomics (simplified - would need proper expression matrix)
                if data.transcriptomics:
                    trans_group = f.create_group('transcriptomics')
                    trans_data = [(t.gene_id, t.expression_level) for t in data.transcriptomics.values()]
                    
                    if trans_data:
                        gene_ids = [x[0] for x in trans_data]
                        expr_levels = [x[1] for x in trans_data]
                        
                        trans_group.create_dataset('gene_ids', data=[x.encode('utf-8') for x in gene_ids])
                        trans_group.create_dataset('expression_matrix', data=np.array([expr_levels]))
                
                # Save other omics types similarly...
                # (Implementation continues for proteomics, metabolomics, etc.)
                
                # Save timepoints
                if data.timepoints:
                    f.create_dataset('timepoints', data=np.array(data.timepoints))
        
        logger.info(f"Saved HDF5 data to {path}")
    
    def validate(self, data: OmicsData) -> bool:
        """Validate omics data for HDF5 format."""
        # Basic validation
        if not data.name:
            return False
        
        # Check that at least one omics type has data
        has_data = any([
            data.genomics,
            data.transcriptomics,
            data.proteomics,
            data.metabolomics,
            data.microbiomics,
            data.connectomics
        ])
        
        return has_data


@omics_adapter("csv")
class CSVAdapter(BaseAdapter):
    """CSV format adapter for simple omics data."""
    
    @property
    def supported_formats(self) -> List[str]:
        return [".csv"]
    
    def load(self, path: str, **kwargs: Any) -> OmicsData:
        """Load omics data from CSV file."""
        path = Path(path)
        
        with timer_context(f"Loading CSV data from {path.name}"):
            df = pd.read_csv(path, **kwargs)
            
            omics_data = OmicsData(name=path.stem)
            
            # Assume CSV has columns: entity_type, entity_id, entity_name, value
            if 'entity_type' in df.columns:
                for entity_type in df['entity_type'].unique():
                    type_data = df[df['entity_type'] == entity_type]
                    entities = {}
                    
                    for _, row in type_data.iterrows():
                        entity_id = str(row['entity_id'])
                        entity_name = str(row.get('entity_name', entity_id))
                        value = float(row.get('value', 0))
                        
                        if entity_type == 'gene':
                            entities[entity_id] = Gene(id=entity_id, name=entity_name)
                        elif entity_type == 'transcript':
                            entities[entity_id] = Transcript(
                                id=entity_id, 
                                name=entity_name,
                                expression_level=value
                            )
                        # Add other entity types as needed
                    
                    if entity_type == 'gene':
                        omics_data.genomics = entities
                    elif entity_type == 'transcript':
                        omics_data.transcriptomics = entities
        
        logger.info(f"Loaded CSV data: {omics_data.summary()}")
        return omics_data
    
    def save(self, data: OmicsData, path: str, **kwargs: Any) -> None:
        """Save omics data to CSV file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        rows = []
        
        # Convert all entities to rows
        for omics_type in OmicsType:
            if omics_type == OmicsType.EPIGENOMICS:
                continue  # Skip DataFrame type
                
            entities = data.get_entities(omics_type)
            for entity_id, entity in entities.items():
                row = {
                    'entity_type': entity.type,
                    'entity_id': entity.id,
                    'entity_name': entity.name,
                    'value': 0  # Default value
                }
                
                # Add specific values based on entity type
                if isinstance(entity, Transcript):
                    row['value'] = entity.expression_level
                elif isinstance(entity, Protein):
                    row['value'] = entity.abundance
                elif isinstance(entity, Metabolite):
                    row['value'] = entity.concentration
                elif isinstance(entity, Microbe):
                    row['value'] = entity.abundance
                elif isinstance(entity, BrainRegion):
                    row['value'] = entity.activity
                
                rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(path, index=False, **kwargs)
        
        logger.info(f"Saved CSV data to {path}")
    
    def validate(self, data: OmicsData) -> bool:
        """Validate omics data for CSV format."""
        return data.name is not None


class DataLoader:
    """Main data loader with support for multiple formats."""
    
    def __init__(self) -> None:
        self.registry = get_registry()
        self.cache: Dict[str, OmicsData] = {}
        
    def load(
        self,
        dataset: str,
        format: str = "auto",
        cache: bool = True,
        **kwargs: Any
    ) -> OmicsData:
        """Load omics data from various sources.
        
        Args:
            dataset: Dataset name or path
            format: Data format ('h5', 'csv', 'zarr', 'auto')
            cache: Whether to cache loaded data
            **kwargs: Additional parameters for the adapter
            
        Returns:
            Loaded omics data
        """
        # Check cache first
        cache_key = f"{dataset}_{format}"
        if cache and cache_key in self.cache:
            logger.debug(f"Loading {dataset} from cache")
            return self.cache[cache_key]
        
        # Handle built-in toy datasets
        if dataset.startswith("toy_"):
            data = self._load_toy_dataset(dataset)
        else:
            # Load from file
            data = self._load_from_file(dataset, format, **kwargs)
        
        # Cache the result
        if cache:
            self.cache[cache_key] = data
        
        return data
    
    def _load_from_file(
        self,
        path: str,
        format: str = "auto",
        **kwargs: Any
    ) -> OmicsData:
        """Load data from file using appropriate adapter."""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {path}")
        
        # Auto-detect format from file extension
        if format == "auto":
            format = self._detect_format(path)
        
        # Get appropriate adapter
        adapter_name = format.lower()
        adapter_info = self.registry.get_plugin("omics_adapters", adapter_name)
        
        if adapter_info is None:
            raise ValueError(f"No adapter found for format: {format}")
        
        # Create adapter instance
        adapter = self.registry.create_instance(
            "omics_adapters",
            adapter_name
        )
        
        # Load data
        return adapter.load(str(path), **kwargs)
    
    def _detect_format(self, path: Path) -> str:
        """Auto-detect format from file extension."""
        suffix = path.suffix.lower()
        
        format_map = {
            '.h5': 'h5',
            '.hdf5': 'h5',
            '.csv': 'csv',
            '.zarr': 'zarr',
            '.json': 'json',
            '.pkl': 'pickle',
            '.pickle': 'pickle',
        }
        
        return format_map.get(suffix, 'h5')  # Default to h5
    
    def _load_toy_dataset(self, dataset: str) -> OmicsData:
        """Load built-in toy dataset."""
        from .toy_datasets import get_toy_dataset
        return get_toy_dataset(dataset)
    
    def save(
        self,
        data: OmicsData,
        path: str,
        format: str = "auto",
        **kwargs: Any
    ) -> None:
        """Save omics data to file.
        
        Args:
            data: Omics data to save
            path: Output path
            format: Output format
            **kwargs: Additional parameters for the adapter
        """
        path = Path(path)
        
        # Auto-detect format from file extension
        if format == "auto":
            format = self._detect_format(path)
        
        # Get appropriate adapter
        adapter_name = format.lower()
        adapter_info = self.registry.get_plugin("omics_adapters", adapter_name)
        
        if adapter_info is None:
            raise ValueError(f"No adapter found for format: {format}")
        
        # Create adapter instance
        adapter = self.registry.create_instance(
            "omics_adapters", 
            adapter_name
        )
        
        # Save data
        adapter.save(data, str(path), **kwargs)
    
    def get_dataset_info(self, dataset: str) -> DatasetInfo:
        """Get information about a dataset."""
        if dataset.startswith("toy_"):
            return self._get_toy_dataset_info(dataset)
        else:
            return self._get_file_dataset_info(dataset)
    
    def _get_file_dataset_info(self, path: str) -> DatasetInfo:
        """Get information about a file dataset."""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {path}")
        
        # Get file size
        size_mb = path.stat().st_size / (1024 * 1024)
        
        # Try to load metadata without loading full dataset
        format = self._detect_format(path)
        
        return DatasetInfo(
            name=path.stem,
            description=f"Dataset loaded from {path.name}",
            format=format,
            size_mb=size_mb,
            num_samples=0,  # Would need format-specific implementation
            omics_types=[],  # Would need format-specific implementation
            metadata={}
        )
    
    def _get_toy_dataset_info(self, dataset: str) -> DatasetInfo:
        """Get information about a toy dataset."""
        from .toy_datasets import get_toy_dataset_info
        return get_toy_dataset_info(dataset)
    
    def list_available_datasets(self) -> List[str]:
        """List all available datasets."""
        datasets = []
        
        # Add toy datasets
        from .toy_datasets import list_toy_datasets
        datasets.extend(list_toy_datasets())
        
        # Could add other dataset sources here
        
        return datasets
    
    def clear_cache(self) -> None:
        """Clear the data cache."""
        self.cache.clear()
        logger.info("Data cache cleared")


# Global data loader instance
_data_loader = None


def get_data_loader() -> DataLoader:
    """Get the global data loader instance."""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader


def load_data(
    dataset: str,
    format: str = "auto",
    cache: bool = True,
    **kwargs: Any
) -> OmicsData:
    """Load multi-omics dataset.
    
    This is a convenience function that uses the global DataLoader.
    
    Args:
        dataset: Dataset name or path
        format: Data format ('h5', 'csv', 'zarr', 'auto')
        cache: Whether to cache loaded data
        **kwargs: Additional loader parameters
        
    Returns:
        Loaded multi-omics data
        
    Example:
        >>> data = load_data("toy_mixed_omics")
        >>> print(data.summary())
        Loaded 5 omics layers: genomics, transcriptomics, proteomics, metabolomics, microbiomics
    """
    loader = get_data_loader()
    return loader.load(dataset, format=format, cache=cache, **kwargs)
