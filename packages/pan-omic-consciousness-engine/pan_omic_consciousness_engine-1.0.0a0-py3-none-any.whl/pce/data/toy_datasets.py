"""Toy datasets for testing and demonstration."""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

from ..core.datatypes import (
    OmicsData, Gene, Transcript, Protein, Metabolite, 
    Microbe, BrainRegion, OmicsType
)
from ..data.ingestion import DatasetInfo

logger = logging.getLogger(__name__)


def create_toy_mixed_omics(
    n_genes: int = 100,
    n_proteins: int = 80,
    n_metabolites: int = 50,
    n_microbes: int = 30,
    n_brain_regions: int = 20,
    n_timepoints: int = 10,
    random_state: int = 42
) -> OmicsData:
    """Create a toy mixed omics dataset for testing.
    
    Args:
        n_genes: Number of genes
        n_proteins: Number of proteins
        n_metabolites: Number of metabolites
        n_microbes: Number of microbes
        n_brain_regions: Number of brain regions
        n_timepoints: Number of timepoints
        random_state: Random seed
        
    Returns:
        Synthetic omics data
    """
    np.random.seed(random_state)
    
    # Create genomics data
    genes = {}
    chromosomes = [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"]
    
    for i in range(n_genes):
        gene_id = f"GENE_{i:04d}"
        chromosome = np.random.choice(chromosomes)
        start_pos = np.random.randint(1000000, 100000000)
        end_pos = start_pos + np.random.randint(1000, 50000)
        strand = np.random.choice(["+", "-"])
        
        genes[gene_id] = Gene(
            id=gene_id,
            name=f"Gene {i+1}",
            type="gene",
            chromosome=chromosome,
            start_pos=start_pos,
            end_pos=end_pos,
            strand=strand
        )
    
    # Create transcriptomics data
    transcripts = {}
    gene_ids = list(genes.keys())
    
    for i, gene_id in enumerate(gene_ids):
        transcript_id = f"TRANS_{i:04d}"
        expression_level = np.random.lognormal(mean=0, sigma=1)
        
        transcripts[transcript_id] = Transcript(
            id=transcript_id,
            name=f"Transcript {i+1}",
            type="transcript",
            gene_id=gene_id,
            expression_level=expression_level
        )
    
    # Create proteomics data
    proteins = {}
    amino_acids = "ACDEFGHIKLMNPQRSTVWY"
    
    for i in range(n_proteins):
        protein_id = f"PROT_{i:04d}"
        sequence_length = np.random.randint(50, 1000)
        sequence = "".join(np.random.choice(list(amino_acids), sequence_length))
        molecular_weight = sequence_length * 110  # Approximate
        abundance = np.random.exponential(scale=2.0)
        
        proteins[protein_id] = Protein(
            id=protein_id,
            name=f"Protein {i+1}",
            type="protein",
            sequence=sequence,
            molecular_weight=molecular_weight,
            abundance=abundance
        )
    
    # Create metabolomics data
    metabolites = {}
    
    for i in range(n_metabolites):
        metabolite_id = f"METAB_{i:04d}"
        
        # Generate simple molecular formula
        c_atoms = np.random.randint(1, 20)
        h_atoms = np.random.randint(1, 40)
        o_atoms = np.random.randint(0, 10)
        n_atoms = np.random.randint(0, 5)
        
        formula = f"C{c_atoms}H{h_atoms}"
        if o_atoms > 0:
            formula += f"O{o_atoms}"
        if n_atoms > 0:
            formula += f"N{n_atoms}"
        
        mass = c_atoms * 12.01 + h_atoms * 1.008 + o_atoms * 15.999 + n_atoms * 14.007
        concentration = np.random.exponential(scale=5.0)
        
        metabolites[metabolite_id] = Metabolite(
            id=metabolite_id,
            name=f"Metabolite {i+1}",
            formula=formula,
            mass=mass,
            concentration=concentration
        )
    
    # Create microbiomics data
    microbes = {}
    phyla = ["Firmicutes", "Bacteroidetes", "Proteobacteria", "Actinobacteria"]
    
    for i in range(n_microbes):
        microbe_id = f"MICROBE_{i:04d}"
        phylum = np.random.choice(phyla)
        family = f"{phylum}aceae"
        genus = f"Genus{i+1}"
        species = f"species{i+1}"
        
        taxonomy = f"{phylum};{family};{genus};{species}"
        abundance = np.random.exponential(scale=1.0)
        
        microbes[microbe_id] = Microbe(
            id=microbe_id,
            name=f"Microbe {i+1}",
            taxonomy=taxonomy,
            abundance=abundance
        )
    
    # Create connectomics data
    brain_regions = {}
    regions = [
        "Frontal Cortex", "Parietal Cortex", "Temporal Cortex", "Occipital Cortex",
        "Hippocampus", "Amygdala", "Thalamus", "Hypothalamus", "Brainstem", "Cerebellum"
    ]
    
    for i in range(n_brain_regions):
        region_id = f"REGION_{i:04d}"
        region_name = regions[i % len(regions)] if i < len(regions) else f"Region {i+1}"
        
        # Random 3D coordinates
        x = np.random.uniform(-100, 100)
        y = np.random.uniform(-100, 100)
        z = np.random.uniform(-50, 50)
        
        activity = np.random.normal(loc=0.5, scale=0.2)
        activity = np.clip(activity, 0, 1)  # Clip to [0, 1]
        
        brain_regions[region_id] = BrainRegion(
            id=region_id,
            name=region_name,
            coordinates=(x, y, z),
            activity=activity
        )
    
    # Create timepoints
    timepoints = list(np.linspace(0, 24, n_timepoints))  # 24 hours
    
    # Create the omics data object
    omics_data = OmicsData(
        name="Toy Mixed Omics Dataset",
        genomics=genes,
        transcriptomics=transcripts,
        proteomics=proteins,
        metabolomics=metabolites,
        microbiomics=microbes,
        connectomics=brain_regions,
        timepoints=timepoints,
        metadata={
            "description": "Synthetic multi-omics dataset for testing",
            "n_genes": n_genes,
            "n_proteins": n_proteins,
            "n_metabolites": n_metabolites,
            "n_microbes": n_microbes,
            "n_brain_regions": n_brain_regions,
            "n_timepoints": n_timepoints,
            "random_state": random_state,
            "synthetic": True
        }
    )
    
    return omics_data


def create_toy_genomics_only(
    n_genes: int = 1000,
    random_state: int = 42
) -> OmicsData:
    """Create a toy genomics-only dataset."""
    np.random.seed(random_state)
    
    genes = {}
    chromosomes = [f"chr{i}" for i in range(1, 23)] + ["chrX", "chrY"]
    
    for i in range(n_genes):
        gene_id = f"GENE_{i:05d}"
        chromosome = np.random.choice(chromosomes)
        start_pos = np.random.randint(1000000, 200000000)
        end_pos = start_pos + np.random.randint(500, 100000)
        strand = np.random.choice(["+", "-"])
        
        genes[gene_id] = Gene(
            id=gene_id,
            name=f"Gene {i+1}",
            type="gene",
            chromosome=chromosome,
            start_pos=start_pos,
            end_pos=end_pos,
            strand=strand
        )
    
    return OmicsData(
        name="Toy Genomics Dataset",
        genomics=genes,
        metadata={
            "description": "Synthetic genomics dataset",
            "n_genes": n_genes,
            "random_state": random_state,
            "synthetic": True
        }
    )


def create_toy_expression_timeseries(
    n_genes: int = 50,
    n_timepoints: int = 20,
    random_state: int = 42
) -> OmicsData:
    """Create a toy expression time series dataset."""
    np.random.seed(random_state)
    
    # Create genes
    genes = {}
    transcripts = {}
    
    for i in range(n_genes):
        gene_id = f"GENE_{i:04d}"
        transcript_id = f"TRANS_{i:04d}"
        
        genes[gene_id] = Gene(
            id=gene_id,
            name=f"Gene {i+1}",
            type="gene",
            chromosome=f"chr{(i % 22) + 1}",
            start_pos=i * 10000 + 1000000,
            end_pos=i * 10000 + 1005000,
            strand="+"
        )
        
        # Create time-varying expression
        base_expression = np.random.lognormal(mean=0, sigma=1)
        
        # Add some periodic components
        t = np.linspace(0, 2 * np.pi, n_timepoints)
        periodic1 = 0.3 * np.sin(t + np.random.uniform(0, 2 * np.pi))
        periodic2 = 0.1 * np.sin(3 * t + np.random.uniform(0, 2 * np.pi))
        noise = 0.1 * np.random.normal(0, 1, n_timepoints)
        
        expression_series = base_expression * (1 + periodic1 + periodic2 + noise)
        expression_series = np.maximum(expression_series, 0)  # Ensure non-negative
        
        # Use mean expression for the transcript object
        transcripts[transcript_id] = Transcript(
            id=transcript_id,
            name=f"Transcript {i+1}",
            gene_id=gene_id,
            expression_level=float(np.mean(expression_series))
        )
        
        # Store full time series in metadata
        transcripts[transcript_id].metadata["expression_timeseries"] = expression_series.tolist()
    
    timepoints = list(np.linspace(0, 48, n_timepoints))  # 48 hours
    
    return OmicsData(
        name="Toy Expression Timeseries Dataset",
        genomics=genes,
        transcriptomics=transcripts,
        timepoints=timepoints,
        metadata={
            "description": "Synthetic expression time series dataset",
            "n_genes": n_genes,
            "n_timepoints": n_timepoints,
            "random_state": random_state,
            "synthetic": True
        }
    )


def create_toy_microbiome_diversity(
    n_samples: int = 100,
    n_species: int = 200,
    random_state: int = 42
) -> OmicsData:
    """Create a toy microbiome diversity dataset."""
    np.random.seed(random_state)
    
    # Create species with realistic taxonomic structure
    phyla = ["Firmicutes", "Bacteroidetes", "Proteobacteria", "Actinobacteria", "Verrucomicrobia"]
    microbes = {}
    
    for i in range(n_species):
        microbe_id = f"SPECIES_{i:04d}"
        
        phylum = np.random.choice(phyla)
        class_name = f"{phylum}_class{i//50 + 1}"
        order_name = f"{class_name}_order{i//20 + 1}"
        family_name = f"{order_name}_family{i//10 + 1}"
        genus_name = f"Genus{i//5 + 1}"
        species_name = f"species{i + 1}"
        
        taxonomy = f"{phylum};{class_name};{order_name};{family_name};{genus_name};{species_name}"
        
        # Create abundance with realistic distribution
        # Some species are very abundant, most are rare
        if i < 10:  # Top 10 species are abundant
            abundance = np.random.exponential(scale=10.0)
        elif i < 50:  # Next 40 are moderate
            abundance = np.random.exponential(scale=2.0)
        else:  # Rest are rare
            abundance = np.random.exponential(scale=0.5)
        
        microbes[microbe_id] = Microbe(
            id=microbe_id,
            name=species_name,
            taxonomy=taxonomy,
            abundance=abundance
        )
    
    return OmicsData(
        name="Toy Microbiome Diversity Dataset",
        microbiomics=microbes,
        metadata={
            "description": "Synthetic microbiome diversity dataset",
            "n_samples": n_samples,
            "n_species": n_species,
            "random_state": random_state,
            "synthetic": True
        }
    )


# Registry of toy datasets
TOY_DATASETS = {
    "toy_mixed_omics": create_toy_mixed_omics,
    "toy_genomics_only": create_toy_genomics_only,
    "toy_expression_timeseries": create_toy_expression_timeseries,
    "toy_microbiome_diversity": create_toy_microbiome_diversity,
}


def get_toy_dataset(name: str, **kwargs) -> OmicsData:
    """Get a toy dataset by name.
    
    Args:
        name: Dataset name
        **kwargs: Additional parameters for dataset creation
        
    Returns:
        Toy omics dataset
    """
    if name not in TOY_DATASETS:
        available = ", ".join(TOY_DATASETS.keys())
        raise ValueError(f"Unknown toy dataset: {name}. Available: {available}")
    
    logger.info(f"Creating toy dataset: {name}")
    return TOY_DATASETS[name](**kwargs)


def get_toy_dataset_info(name: str) -> DatasetInfo:
    """Get information about a toy dataset.
    
    Args:
        name: Dataset name
        
    Returns:
        Dataset information
    """
    if name not in TOY_DATASETS:
        available = ", ".join(TOY_DATASETS.keys())
        raise ValueError(f"Unknown toy dataset: {name}. Available: {available}")
    
    # Create a sample to get info
    sample_data = TOY_DATASETS[name]()
    
    omics_types = []
    for omics_type in OmicsType:
        if omics_type == OmicsType.EPIGENOMICS:
            continue  # Skip DataFrame type
        
        entities = sample_data.get_entities(omics_type)
        if entities:
            omics_types.append(omics_type.value)
    
    return DatasetInfo(
        name=name,
        description=sample_data.metadata.get("description", "Synthetic dataset"),
        format="synthetic",
        size_mb=0.001,  # Very small synthetic data
        num_samples=sample_data.metadata.get("n_samples", 1),
        omics_types=omics_types,
        metadata=sample_data.metadata
    )


def list_toy_datasets() -> List[str]:
    """List all available toy datasets.
    
    Returns:
        List of toy dataset names
    """
    return list(TOY_DATASETS.keys())


def create_custom_toy_dataset(
    omics_config: Dict[str, Dict[str, Any]],
    name: str = "Custom Toy Dataset",
    random_state: int = 42
) -> OmicsData:
    """Create a custom toy dataset with specified configuration.
    
    Args:
        omics_config: Configuration for each omics type
        name: Dataset name
        random_state: Random seed
        
    Returns:
        Custom toy omics dataset
        
    Example:
        >>> config = {
        ...     "genomics": {"n_genes": 500},
        ...     "transcriptomics": {"n_genes": 500},
        ...     "proteomics": {"n_proteins": 300}
        ... }
        >>> dataset = create_custom_toy_dataset(config)
    """
    np.random.seed(random_state)
    
    omics_data = OmicsData(name=name, metadata={"custom": True, "random_state": random_state})
    
    # Genomics
    if "genomics" in omics_config:
        config = omics_config["genomics"]
        n_genes = config.get("n_genes", 100)
        
        genes = {}
        for i in range(n_genes):
            gene_id = f"GENE_{i:05d}"
            genes[gene_id] = Gene(
                id=gene_id,
                name=f"Gene {i+1}",
                type="gene",
                chromosome=f"chr{(i % 22) + 1}",
                start_pos=i * 10000 + 1000000,
                end_pos=i * 10000 + 1005000,
                strand=np.random.choice(["+", "-"])
            )
        
        omics_data.genomics = genes
    
    # Transcriptomics
    if "transcriptomics" in omics_config:
        config = omics_config["transcriptomics"]
        n_transcripts = config.get("n_genes", len(omics_data.genomics) if omics_data.genomics else 100)
        
        transcripts = {}
        gene_ids = list(omics_data.genomics.keys()) if omics_data.genomics else [f"GENE_{i:05d}" for i in range(n_transcripts)]
        
        for i, gene_id in enumerate(gene_ids[:n_transcripts]):
            transcript_id = f"TRANS_{i:05d}"
            transcripts[transcript_id] = Transcript(
                id=transcript_id,
                name=f"Transcript {i+1}",
                gene_id=gene_id,
                expression_level=np.random.lognormal(mean=0, sigma=1)
            )
        
        omics_data.transcriptomics = transcripts
    
    # Add other omics types as needed...
    
    return omics_data


def create_toy_dataset(
    dataset_type: str,
    n_samples: int = 100,
    n_features: int = 200,
    random_state: int = 42,
    **kwargs
) -> OmicsData:
    """Create a toy dataset of the specified type.
    
    This is a convenience function that dispatches to specific toy dataset creators.
    
    Args:
        dataset_type: Type of dataset to create
        n_samples: Number of samples
        n_features: Number of features per omics layer
        random_state: Random seed for reproducibility
        **kwargs: Additional parameters for specific dataset types
        
    Returns:
        OmicsData object
        
    Available dataset types:
        - "toy_basic": Basic genomics-only dataset
        - "toy_mixed_omics": Multi-omics dataset with 5 layers
        - "toy_neural_omics": Neural-specific multi-omics data
        - "toy_genomics": Genomics-only dataset
        - "toy_timeseries": Expression timeseries data
        - "toy_microbiome": Microbiome diversity dataset
    """
    if dataset_type in ["toy_basic", "toy_genomics"]:
        return create_toy_genomics_only(
            n_genes=n_features,
            random_state=random_state
        )
    elif dataset_type in ["toy_mixed_omics", "toy_neural_omics"]:
        return create_toy_mixed_omics(
            n_genes=min(n_features, 150),
            n_proteins=min(n_features//2, 100),
            n_metabolites=min(n_features//4, 50),
            random_state=random_state
        )
    elif dataset_type == "toy_timeseries":
        return create_toy_expression_timeseries(
            n_genes=n_features,
            random_state=random_state
        )
    elif dataset_type == "toy_microbiome":
        return create_toy_microbiome_diversity(
            random_state=random_state
        )
    else:
        # Default to mixed omics
        logger.warning(f"Unknown dataset type '{dataset_type}', using mixed omics")
        return create_toy_mixed_omics(
            n_genes=min(n_features, 150),
            n_proteins=min(n_features//2, 100),
            n_metabolites=min(n_features//4, 50),
            random_state=random_state
        )
