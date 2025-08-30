#!/usr/bin/env python3
"""Setup script for the Pan-Omics Consciousness Engine (PCE)."""

from setuptools import setup, find_packages
from pathlib import Path
import os

# Read version from __init__.py
def get_version():
    """Extract version from __init__.py"""
    init_file = Path(__file__).parent / "src" / "pce" / "__init__.py"
    with open(init_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return "1.0.0-alpha"

# Read README for long description
def get_long_description():
    """Get long description from README.md"""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Pan-Omics Consciousness Engine - A computational framework for modeling consciousness emergence."

# Define package requirements
REQUIREMENTS = [
    # Core scientific computing
    "numpy>=1.21.0",
    "scipy>=1.7.0",
    "scikit-learn>=1.0.0",
    
    # Data handling
    "pandas>=1.3.0",
    "h5py>=3.1.0",
    "zarr>=2.8.0",
    
    # Graph and network analysis
    "networkx>=2.6.0",
    
    # Visualization
    "matplotlib>=3.4.0",
    "seaborn>=0.11.0",
    
    # Utilities
    "tqdm>=4.62.0",
    "pydantic>=1.8.0",
    "python-dateutil>=2.8.0",
]

# Optional dependencies for enhanced functionality
EXTRAS_REQUIRE = {
    "pytorch": [
        "torch>=1.9.0",
        "torch-geometric>=2.0.0",
    ],
    "cli": [
        "typer[all]>=0.6.0",
        "rich>=12.0.0",
        "click>=8.0.0",
    ],
    "dev": [
        # Testing
        "pytest>=6.2.0",
        "pytest-cov>=2.12.0",
        "pytest-xdist>=2.3.0",
        
        # Code quality
        "black>=21.6b0",
        "flake8>=3.9.0",
        "mypy>=0.910",
        "isort>=5.9.0",
        
        # Documentation  
        "sphinx>=4.1.0",
        "sphinx-rtd-theme>=0.5.0",
        "myst-parser>=0.15.0",
    ],
    "jupyter": [
        "jupyter>=1.0.0",
        "jupyterlab>=3.1.0",
        "ipywidgets>=7.6.0",
        "plotly>=5.0.0",
    ],
    "optimization": [
        "optuna>=2.9.0",
        "hyperopt>=0.2.5",
        "ray[tune]>=1.4.0",
    ],
    "distributed": [
        "dask[complete]>=2021.7.0",
        "ray>=1.4.0",
    ],
}

# Full installation includes all extras
EXTRAS_REQUIRE["full"] = list(set(
    req for extra in EXTRAS_REQUIRE.values() 
    for req in extra
))

# Console scripts for CLI
CONSOLE_SCRIPTS = [
    "pan-omic-ce=pce.cli:main",
]

# Entry points for plugins
ENTRY_POINTS = {
    "console_scripts": CONSOLE_SCRIPTS,
    "pce.consciousness_theories": [
        "iit=pce.cis:IntegratedInformationTheory",
        "gwt=pce.cis:GlobalWorkspaceTheory",
        "quantum=pce.qlem:QuantumConsciousnessTheory",
    ],
    "pce.omics_loaders": [
        "csv=pce.data.ingestion:CSVLoader",
        "h5=pce.data.ingestion:HDF5Loader",
        "zarr=pce.data.ingestion:ZarrLoader",
    ],
}

setup(
    name="pan-omic-consciousness-engine",
    version=get_version(),
    description="Pan-Omics Consciousness Engine - A computational framework for modeling consciousness emergence",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Krishna Bajpai and Veddanshi Gupta",
    author_email="krishna@krishna.me",
    url="https://github.com/krish567366/pan-omic",
    project_urls={
        "Documentation": "https://krish567366.github.io/pan-omic/",
        "Source": "https://github.com/krish567366/pan-omic",
        "Tracker": "https://github.com/krish567366/pan-omic/issues",
    },
    
    # Package structure
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={
        "pce": [
            "data/toy_datasets/*.csv",
            "data/toy_datasets/*.h5",
            "config/*.yaml",
            "config/*.json",
        ]
    },
    include_package_data=True,
    
    # Requirements
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
    
    # Entry points
    entry_points=ENTRY_POINTS,
    
    # Classification
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research", 
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    # Keywords for discovery
    keywords=[
        "consciousness", "multi-omics", "bioinformatics", "quantum-biology",
        "graph-neural-networks", "evolutionary-dynamics", "digital-twin",
        "neuroscience", "complex-systems", "emergence", "hypergraphs",
        "integrated-information-theory", "global-workspace-theory"
    ],
    
    # Zip safety
    zip_safe=False,
    
    # Additional metadata
    platforms=["any"],
    license="Proprietary",
)
