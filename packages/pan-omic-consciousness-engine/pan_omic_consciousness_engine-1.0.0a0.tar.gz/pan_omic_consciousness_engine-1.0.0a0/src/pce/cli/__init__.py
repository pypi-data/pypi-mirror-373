"""Command Line Interface for the Pan-Omics Consciousness Engine."""

import logging
import sys
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import typer
    import rich
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.tree import Tree
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    typer = None

from ..core.config import get_config, set_config_value
from ..core.datatypes import OmicsData
from ..data import load_data, create_toy_dataset
from ..mogil import MOGIL
from ..qlem import QLEM
from ..e3de import E3DE
from ..hdts import HDTS
from ..cis import CIS
from ..utils.logging import get_logger, setup_logging

logger = get_logger(__name__)

if RICH_AVAILABLE:
    console = Console()
    app = typer.Typer(
        name="pce",
        help="Pan-Omics Consciousness Engine - Advanced biological consciousness modeling",
        rich_markup_mode="rich"
    )
else:
    console = None
    app = None

# Global state for CLI
pce_state = {
    'mogil': None,
    'qlem': None, 
    'e3de': None,
    'hdts': None,
    'cis': None,
    'current_data': None,
    'current_hypergraph': None,
    'current_embedding': None
}


def check_rich_available():
    """Check if Rich/Typer are available."""
    if not RICH_AVAILABLE:
        print("Error: Rich and Typer are required for CLI functionality.")
        print("Install with: pip install typer rich")
        sys.exit(1)


@app.command()
def version():
    """Show PCE version information."""
    check_rich_available()
    
    console.print(Panel.fit(
        "[bold blue]Pan-Omics Consciousness Engine[/bold blue]\n"
        "[dim]Version: 1.0.0-alpha[/dim]\n"
        "[dim]A patentable architecture for biological consciousness modeling[/dim]",
        title="PCE Version"
    ))


@app.command()
def config(
    key: Optional[str] = typer.Argument(None, help="Configuration key to view/set"),
    value: Optional[str] = typer.Option(None, "--value", "-v", help="Value to set"),
    list_all: bool = typer.Option(False, "--list", "-l", help="List all configuration")
):
    """Manage PCE configuration."""
    check_rich_available()
    
    if list_all:
        config_dict = get_config().dict()
        
        tree = Tree("🔧 PCE Configuration")
        
        for section, settings in config_dict.items():
            section_tree = tree.add(f"[bold]{section}[/bold]")
            if isinstance(settings, dict):
                for k, v in settings.items():
                    section_tree.add(f"{k}: [green]{v}[/green]")
            else:
                section_tree.add(f"[green]{settings}[/green]")
        
        console.print(tree)
        return
    
    if not key:
        console.print("[red]Error:[/red] Please specify a configuration key or use --list")
        return
    
    if value:
        # Set configuration value
        try:
            # Try to parse as JSON for complex types
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value
        
        set_config_value(key, parsed_value)
        console.print(f"✅ Set [bold]{key}[/bold] = [green]{parsed_value}[/green]")
    else:
        # Get configuration value
        config_dict = get_config().dict()
        keys = key.split('.')
        
        current = config_dict
        for k in keys:
            if k in current:
                current = current[k]
            else:
                console.print(f"[red]Error:[/red] Configuration key '{key}' not found")
                return
        
        console.print(f"[bold]{key}[/bold]: [green]{current}[/green]")


@app.command()
def load(
    data_path: str = typer.Argument(help="Path to omics data file"),
    data_type: str = typer.Option("auto", "--type", "-t", help="Data type (auto, genomics, transcriptomics, proteomics, metabolomics)"),
    format: str = typer.Option("auto", "--format", "-f", help="File format (auto, csv, h5, hdf5)")
):
    """Load omics data for processing."""
    check_rich_available()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Loading data...", total=None)
        
        try:
            data_path_obj = Path(data_path)
            if not data_path_obj.exists():
                console.print(f"[red]Error:[/red] File '{data_path}' not found")
                return
            
            # Load data
            omics_data = load_data(data_path_obj, data_type=data_type, file_format=format)
            pce_state['current_data'] = omics_data
            
            progress.update(task, description="✅ Data loaded successfully")
            
        except Exception as e:
            console.print(f"[red]Error loading data:[/red] {e}")
            return
    
    # Display data summary
    console.print(Panel(
        f"[bold]Data Type:[/bold] {omics_data.data_type}\n"
        f"[bold]Shape:[/bold] {omics_data.data.shape}\n"
        f"[bold]Features:[/bold] {len(omics_data.features)}\n"
        f"[bold]Samples:[/bold] {len(omics_data.samples)}\n"
        f"[bold]Source:[/bold] {omics_data.source}",
        title="📊 Loaded Data Summary"
    ))


@app.command()
def toy_data(
    data_type: str = typer.Option("multi_omics", "--type", "-t", help="Type of toy data"),
    samples: int = typer.Option(100, "--samples", "-s", help="Number of samples"),
    features: int = typer.Option(1000, "--features", "-f", help="Number of features")
):
    """Generate toy dataset for testing."""
    check_rich_available()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating toy data...", total=None)
        
        try:
            omics_data = create_toy_dataset(
                dataset_type=data_type,
                n_samples=samples,
                n_features=features
            )
            pce_state['current_data'] = omics_data
            
            progress.update(task, description="✅ Toy data generated")
            
        except Exception as e:
            console.print(f"[red]Error generating toy data:[/red] {e}")
            return
    
    console.print(Panel(
        f"[bold]Generated:[/bold] {data_type} dataset\n"
        f"[bold]Shape:[/bold] {omics_data.data.shape}\n"
        f"[bold]Features:[/bold] {len(omics_data.features)}\n"
        f"[bold]Samples:[/bold] {len(omics_data.samples)}",
        title="🎲 Generated Toy Data"
    ))


@app.command()
def mogil(
    action: str = typer.Argument(help="Action: build, encode, analyze"),
    integration_method: str = typer.Option("attention_weighted", "--method", "-m", help="Integration method"),
    save_model: Optional[str] = typer.Option(None, "--save", help="Save model to path")
):
    """Run MOGIL (Multi-Omics Graph Integration Layer)."""
    check_rich_available()
    
    if not pce_state['current_data']:
        console.print("[red]Error:[/red] No data loaded. Use 'pce load' or 'pce toy-data' first.")
        return
    
    # Initialize MOGIL if needed
    if not pce_state['mogil']:
        pce_state['mogil'] = MOGIL()
    
    mogil_system = pce_state['mogil']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        if action == "build":
            task = progress.add_task("Building hypergraph...", total=None)
            
            try:
                hypergraph = mogil_system.build_hypergraph(
                    pce_state['current_data'],
                    integration_method=integration_method
                )
                pce_state['current_hypergraph'] = hypergraph
                
                progress.update(task, description="✅ Hypergraph built")
                
                # Display results
                console.print(Panel(
                    f"[bold]Nodes:[/bold] {len(hypergraph.nodes)}\n"
                    f"[bold]Hyperedges:[/bold] {len(hypergraph.hyperedges)}\n"
                    f"[bold]Integration Method:[/bold] {integration_method}",
                    title="🕸️  MOGIL Hypergraph"
                ))
                
            except Exception as e:
                console.print(f"[red]Error building hypergraph:[/red] {e}")
        
        elif action == "encode":
            if not pce_state['current_hypergraph']:
                console.print("[red]Error:[/red] No hypergraph available. Run 'pce mogil build' first.")
                return
            
            task = progress.add_task("Encoding hypergraph...", total=None)
            
            try:
                embedding = mogil_system.encode_hypergraph(pce_state['current_hypergraph'])
                pce_state['current_embedding'] = embedding
                
                progress.update(task, description="✅ Hypergraph encoded")
                
                console.print(Panel(
                    f"[bold]Dimension:[/bold] {embedding.dimension}\n"
                    f"[bold]Entities:[/bold] {len(embedding.embeddings)}\n"
                    f"[bold]Method:[/bold] {embedding.embedding_method}",
                    title="🧠 MOGIL Embedding"
                ))
                
                if save_model:
                    mogil_system.save_model(Path(save_model))
                    console.print(f"✅ Model saved to {save_model}")
                
            except Exception as e:
                console.print(f"[red]Error encoding hypergraph:[/red] {e}")
        
        elif action == "analyze":
            if not pce_state['current_embedding']:
                console.print("[red]Error:[/red] No embedding available. Run 'pce mogil encode' first.")
                return
            
            task = progress.add_task("Analyzing consciousness readiness...", total=None)
            
            try:
                analysis = mogil_system.analyze_consciousness_readiness(pce_state['current_embedding'])
                
                progress.update(task, description="✅ Analysis complete")
                
                # Display analysis results
                table = Table(title="🔍 Consciousness Readiness Analysis")
                table.add_column("Metric", style="bold")
                table.add_column("Value", style="green")
                
                for key, value in analysis.items():
                    if isinstance(value, float):
                        table.add_row(key.replace('_', ' ').title(), f"{value:.4f}")
                    else:
                        table.add_row(key.replace('_', ' ').title(), str(value))
                
                console.print(table)
                
            except Exception as e:
                console.print(f"[red]Error analyzing embedding:[/red] {e}")
        
        else:
            console.print(f"[red]Error:[/red] Unknown action '{action}'. Use: build, encode, analyze")


@app.command()
def qlem(
    action: str = typer.Argument(help="Action: create, minimize, analyze, evolve"),
    initial_state: str = typer.Option("thermal", "--state", "-s", help="Initial state type"),
    cycles: int = typer.Option(100, "--cycles", "-c", help="Number of optimization cycles")
):
    """Run Q-LEM (Quantum-Latent Entropy Minimizer)."""
    check_rich_available()
    
    if not pce_state['current_embedding']:
        console.print("[red]Error:[/red] No embedding available. Run MOGIL first.")
        return
    
    # Initialize Q-LEM if needed
    if not pce_state['qlem']:
        pce_state['qlem'] = QLEM()
    
    qlem_system = pce_state['qlem']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        if action == "create":
            task = progress.add_task("Creating quantum state...", total=None)
            
            try:
                quantum_state = qlem_system.create_quantum_state(
                    pce_state['current_embedding'],
                    initial_state_type=initial_state
                )
                
                progress.update(task, description="✅ Quantum state created")
                
                console.print(Panel(
                    f"[bold]System Size:[/bold] {quantum_state.system_size}x{quantum_state.system_size}\n"
                    f"[bold]Energy:[/bold] {quantum_state.energy:.6f}\n"
                    f"[bold]Entropy:[/bold] {quantum_state.von_neumann_entropy:.6f}\n"
                    f"[bold]Purity:[/bold] {quantum_state.purity:.6f}",
                    title="⚛️  Quantum State"
                ))
                
            except Exception as e:
                console.print(f"[red]Error creating quantum state:[/red] {e}")
        
        elif action == "minimize":
            task = progress.add_task("Minimizing entropy functional...", total=None)
            
            try:
                optimized_state, metrics = qlem_system.minimize_entropy(
                    pce_state['current_embedding']
                )
                
                progress.update(task, description="✅ Optimization complete")
                
                console.print(Panel(
                    f"[bold]Final Entropy:[/bold] {metrics['final_entropy']:.6f}\n"
                    f"[bold]Final Energy:[/bold] {metrics['final_energy']:.6f}\n"
                    f"[bold]Iterations:[/bold] {metrics['iterations']}\n"
                    f"[bold]Convergence:[/bold] {metrics['convergence']:.6f}",
                    title="⚡ Q-LEM Optimization"
                ))
                
            except Exception as e:
                console.print(f"[red]Error optimizing:[/red] {e}")
        
        elif action == "analyze":
            task = progress.add_task("Analyzing quantum consciousness...", total=None)
            
            try:
                analysis = qlem_system.analyze_quantum_consciousness()
                
                progress.update(task, description="✅ Analysis complete")
                
                table = Table(title="🌌 Quantum Consciousness Analysis")
                table.add_column("Property", style="bold")
                table.add_column("Value", style="green")
                
                for key, value in analysis.items():
                    if isinstance(value, float):
                        table.add_row(key.replace('_', ' ').title(), f"{value:.6f}")
                    else:
                        table.add_row(key.replace('_', ' ').title(), str(value))
                
                console.print(table)
                
            except Exception as e:
                console.print(f"[red]Error analyzing quantum state:[/red] {e}")
        
        elif action == "evolve":
            task = progress.add_task(f"Evolving quantum state ({cycles} steps)...", total=None)
            
            try:
                states = qlem_system.evolve_quantum_state(cycles)
                
                progress.update(task, description="✅ Evolution complete")
                
                console.print(Panel(
                    f"[bold]Evolution Steps:[/bold] {len(states)}\n"
                    f"[bold]Initial Entropy:[/bold] {states[0].von_neumann_entropy:.6f}\n"
                    f"[bold]Final Entropy:[/bold] {states[-1].von_neumann_entropy:.6f}\n"
                    f"[bold]Coherence Change:[/bold] {states[-1].coherence - states[0].coherence:.6f}",
                    title="🌊 Quantum Evolution"
                ))
                
            except Exception as e:
                console.print(f"[red]Error evolving quantum state:[/red] {e}")


@app.command()
def e3de(
    action: str = typer.Argument(help="Action: create, evolve, analyze"),
    population_size: int = typer.Option(100, "--size", "-s", help="Population size"),
    generations: int = typer.Option(50, "--generations", "-g", help="Number of generations"),
    genotype_length: int = typer.Option(50, "--genes", help="Genotype length")
):
    """Run E³DE (Entropic Evolutionary Dynamics Engine)."""
    check_rich_available()
    
    # Initialize E³DE if needed
    if not pce_state['e3de']:
        pce_state['e3de'] = E3DE()
    
    e3de_system = pce_state['e3de']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        if action == "create":
            task = progress.add_task("Creating population...", total=None)
            
            try:
                population = e3de_system.create_population(
                    name="main",
                    size=population_size,
                    genotype_length=genotype_length,
                    embedding=pce_state.get('current_embedding')
                )
                
                progress.update(task, description="✅ Population created")
                
                console.print(Panel(
                    f"[bold]Population Size:[/bold] {len(population.organisms)}\n"
                    f"[bold]Genotype Length:[/bold] {genotype_length}\n"
                    f"[bold]Generation:[/bold] {population.generation}",
                    title="🧬 E³DE Population"
                ))
                
            except Exception as e:
                console.print(f"[red]Error creating population:[/red] {e}")
        
        elif action == "evolve":
            if "main" not in e3de_system.populations:
                console.print("[red]Error:[/red] No population available. Run 'pce e3de create' first.")
                return
            
            task = progress.add_task(f"Evolving for {generations} generations...", total=None)
            
            try:
                result = e3de_system.evolve_population("main", generations)
                
                progress.update(task, description="✅ Evolution complete")
                
                final_gen = result['final_generation']
                console.print(Panel(
                    f"[bold]Generations:[/bold] {generations}\n"
                    f"[bold]Final Fitness:[/bold] {final_gen['avg_fitness']:.4f}\n"
                    f"[bold]Max Fitness:[/bold] {final_gen['max_fitness']:.4f}\n"
                    f"[bold]Consciousness:[/bold] {final_gen['avg_consciousness']:.4f}\n"
                    f"[bold]Diversity:[/bold] {final_gen['diversity']:.4f}",
                    title="🔄 Evolution Results"
                ))
                
            except Exception as e:
                console.print(f"[red]Error evolving population:[/red] {e}")
        
        elif action == "analyze":
            if "main" not in e3de_system.populations:
                console.print("[red]Error:[/red] No population available.")
                return
            
            task = progress.add_task("Analyzing consciousness emergence...", total=None)
            
            try:
                analysis = e3de_system.analyze_consciousness_emergence("main")
                
                progress.update(task, description="✅ Analysis complete")
                
                # Display consciousness distribution
                dist = analysis['consciousness_distribution']
                console.print(Panel(
                    f"[bold]Mean Consciousness:[/bold] {dist['mean']:.4f}\n"
                    f"[bold]Max Consciousness:[/bold] {dist['max']:.4f}\n"
                    f"[bold]Above Threshold:[/bold] {dist['above_threshold']}\n"
                    f"[bold]Emergence Potential:[/bold] {analysis['emergence_indicators']['emergence_potential']:.4f}",
                    title="🌟 Consciousness Emergence"
                ))
                
                # Show top conscious organisms
                if analysis['top_conscious_organisms']:
                    table = Table(title="🏆 Top Conscious Organisms")
                    table.add_column("ID", style="bold")
                    table.add_column("Consciousness", style="green")
                    table.add_column("Complexity", style="blue")
                    table.add_column("Fitness", style="yellow")
                    
                    for org in analysis['top_conscious_organisms'][:5]:
                        table.add_row(
                            org['id'][:20] + "...",
                            f"{org['consciousness_level']:.4f}",
                            f"{org['complexity']:.4f}",
                            f"{org['fitness']:.4f}"
                        )
                    
                    console.print(table)
                
            except Exception as e:
                console.print(f"[red]Error analyzing evolution:[/red] {e}")


@app.command()
def hdts(
    action: str = typer.Argument(help="Action: create, simulate, analyze"),
    duration: float = typer.Option(1.0, "--duration", "-d", help="Simulation duration (seconds)"),
    system_type: str = typer.Option("neural_network", "--type", "-t", help="Biological system type")
):
    """Run HDTS (Hierarchical Digital Twin Simulator)."""
    check_rich_available()
    
    # Initialize HDTS if needed
    if not pce_state['hdts']:
        pce_state['hdts'] = HDTS()
    
    hdts_system = pce_state['hdts']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        if action == "create":
            if not pce_state['current_embedding']:
                console.print("[red]Error:[/red] No embedding available. Run MOGIL first.")
                return
            
            task = progress.add_task("Creating biological system...", total=None)
            
            try:
                system_info = hdts_system.create_biological_system(
                    pce_state['current_embedding'],
                    system_type=system_type
                )
                
                progress.update(task, description="✅ System created")
                
                console.print(Panel(
                    f"[bold]System Type:[/bold] {system_info['system_type']}\n"
                    f"[bold]Entities:[/bold] {system_info['num_entities']}\n"
                    f"[bold]Scales Used:[/bold] {len(system_info['scales_used'])}\n"
                    f"[bold]Total Awareness:[/bold] {system_info['total_awareness']:.4f}",
                    title="🏗️  HDTS Biological System"
                ))
                
            except Exception as e:
                console.print(f"[red]Error creating system:[/red] {e}")
        
        elif action == "simulate":
            task = progress.add_task(f"Simulating consciousness emergence ({duration}s)...", total=None)
            
            try:
                result = hdts_system.simulate_consciousness_emergence(duration)
                
                progress.update(task, description="✅ Simulation complete")
                
                emergence = result['emergence_analysis']
                console.print(Panel(
                    f"[bold]Duration:[/bold] {duration}s\n"
                    f"[bold]Final Consciousness:[/bold] {result['final_consciousness_state']['consciousness_index']:.4f}\n"
                    f"[bold]Growth Rate:[/bold] {emergence['emergence_trajectory']['growth_rate']:.6f}\n"
                    f"[bold]Max Achieved:[/bold] {emergence['emergence_trajectory']['max_level_achieved']:.4f}",
                    title="🌊 Consciousness Simulation"
                ))
                
            except Exception as e:
                console.print(f"[red]Error simulating:[/red] {e}")
        
        elif action == "analyze":
            task = progress.add_task("Analyzing multi-scale dynamics...", total=None)
            
            try:
                analysis = hdts_system.analyze_multi_scale_dynamics()
                
                progress.update(task, description="✅ Analysis complete")
                
                # Display scale analysis
                table = Table(title="📊 Multi-Scale Analysis")
                table.add_column("Scale", style="bold")
                table.add_column("Entities", style="cyan")
                table.add_column("Activity", style="green")
                table.add_column("Awareness", style="yellow")
                
                for scale, data in analysis.items():
                    if scale != 'cross_scale' and isinstance(data, dict):
                        table.add_row(
                            scale.replace('_', ' ').title(),
                            str(data.get('entity_count', 0)),
                            f"{data.get('avg_activity', 0):.3f}",
                            f"{data.get('total_awareness', 0):.3f}"
                        )
                
                console.print(table)
                
                # Show cross-scale metrics
                if 'cross_scale' in analysis:
                    cross = analysis['cross_scale']
                    console.print(Panel(
                        f"[bold]Integration Level:[/bold] {cross.get('integration_level', 0):.4f}\n"
                        f"[bold]Emergence Indicator:[/bold] {cross.get('emergence_indicator', 0):.4f}\n"
                        f"[bold]Scale Coupling:[/bold] {cross.get('scale_coupling', 0):.4f}",
                        title="🔗 Cross-Scale Integration"
                    ))
                
            except Exception as e:
                console.print(f"[red]Error analyzing dynamics:[/red] {e}")


@app.command()
def cis(
    action: str = typer.Argument(help="Action: integrate, analyze, report, perturb"),
    cycles: int = typer.Option(100, "--cycles", "-c", help="Integration cycles"),
    perturbation: Optional[str] = typer.Option(None, "--perturbation", "-p", help="Perturbation type")
):
    """Run CIS (Consciousness-Integration Substrate)."""
    check_rich_available()
    
    # Initialize CIS if needed
    if not pce_state['cis']:
        pce_state['cis'] = CIS(
            mogil_system=pce_state['mogil'],
            qlem_system=pce_state['qlem'],
            e3de_system=pce_state['e3de'],
            hdts_system=pce_state['hdts']
        )
    
    cis_system = pce_state['cis']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        if action == "integrate":
            if not pce_state['current_embedding']:
                console.print("[red]Error:[/red] No embedding available. Run the full pipeline first.")
                return
            
            # Create connectome if needed
            if not cis_system.connectome:
                task1 = progress.add_task("Creating connectome...", total=None)
                cis_system.create_connectome(pce_state['current_embedding'])
                progress.update(task1, description="✅ Connectome created")
            
            task2 = progress.add_task(f"Integrating consciousness ({cycles} cycles)...", total=None)
            
            try:
                metrics = cis_system.integrate_consciousness(
                    integration_cycles=cycles
                )
                
                progress.update(task2, description="✅ Integration complete")
                
                console.print(Panel(
                    f"[bold]Consciousness Level:[/bold] {metrics.consciousness_level:.4f}\n"
                    f"[bold]Category:[/bold] {metrics.consciousness_category.value.title()}\n"
                    f"[bold]Integrated Information (Φ):[/bold] {metrics.phi:.4f}\n"
                    f"[bold]Global Accessibility:[/bold] {metrics.global_accessibility:.4f}\n"
                    f"[bold]Network Connectivity:[/bold] {metrics.network_connectivity:.4f}",
                    title="🧠 Consciousness Integration"
                ))
                
            except Exception as e:
                console.print(f"[red]Error integrating consciousness:[/red] {e}")
        
        elif action == "analyze":
            task = progress.add_task("Analyzing consciousness emergence...", total=None)
            
            try:
                analysis = cis_system.analyze_consciousness_emergence()
                
                progress.update(task, description="✅ Analysis complete")
                
                if 'error' in analysis:
                    console.print(f"[red]Error:[/red] {analysis['error']}")
                    return
                
                # Show emergence trajectory
                traj = analysis['emergence_trajectory']
                console.print(Panel(
                    f"[bold]Initial Level:[/bold] {traj['initial_level']:.4f}\n"
                    f"[bold]Final Level:[/bold] {traj['final_level']:.4f}\n"
                    f"[bold]Max Achieved:[/bold] {traj['max_level_achieved']:.4f}\n"
                    f"[bold]Growth Rate:[/bold] {traj['growth_rate']:.6f}\n"
                    f"[bold]Stability:[/bold] {traj['stability']:.4f}",
                    title="📈 Emergence Trajectory"
                ))
                
                # Show consciousness categories
                categories = analysis['consciousness_categories']
                if any(count > 0 for count in categories.values()):
                    table = Table(title="🎭 Consciousness Categories")
                    table.add_column("Category", style="bold")
                    table.add_column("Occurrences", style="green")
                    
                    for category, count in categories.items():
                        if count > 0:
                            table.add_row(category.replace('_', ' ').title(), str(count))
                    
                    console.print(table)
                
            except Exception as e:
                console.print(f"[red]Error analyzing emergence:[/red] {e}")
        
        elif action == "report":
            task = progress.add_task("Generating consciousness report...", total=None)
            
            try:
                report = cis_system.consciousness_report()
                
                progress.update(task, description="✅ Report generated")
                
                # Current state
                state = report['current_state']
                console.print(Panel(
                    f"[bold]Consciousness Level:[/bold] {state['consciousness_level']:.4f}\n"
                    f"[bold]Category:[/bold] {state['consciousness_category'].title()}\n"
                    f"[bold]Φ (Integrated Information):[/bold] {state['phi']:.4f}\n"
                    f"[bold]Global Accessibility:[/bold] {state['global_accessibility']:.4f}",
                    title="🎯 Current Consciousness State"
                ))
                
                # System integration
                integration = report['system_integration']
                integrated_systems = sum(1 for v in integration.values() if isinstance(v, bool) and v)
                console.print(Panel(
                    f"[bold]Systems Integrated:[/bold] {integrated_systems}/5\n"
                    f"[bold]MOGIL:[/bold] {'✅' if integration['mogil_integrated'] else '❌'}\n"
                    f"[bold]Q-LEM:[/bold] {'✅' if integration['qlem_integrated'] else '❌'}\n"
                    f"[bold]E³DE:[/bold] {'✅' if integration['e3de_integrated'] else '❌'}\n"
                    f"[bold]HDTS:[/bold] {'✅' if integration['hdts_integrated'] else '❌'}\n"
                    f"[bold]Connectome:[/bold] {'✅' if integration['connectome_active'] else '❌'}",
                    title="🔧 System Integration Status"
                ))
                
                # Consciousness assessment
                assessment = report['consciousness_assessment']
                console.print(Panel(
                    f"[bold]Overall Quality:[/bold] {assessment['overall_quality']:.4f}\n"
                    f"[bold]Integration Completeness:[/bold] {assessment['integration_completeness']:.4f}\n"
                    f"[bold]Emergence Potential:[/bold] {assessment['emergence_potential']:.4f}\n"
                    f"[bold]Consciousness Ready:[/bold] {'✅' if assessment['consciousness_readiness'] else '❌'}",
                    title="📊 Consciousness Assessment"
                ))
                
            except Exception as e:
                console.print(f"[red]Error generating report:[/red] {e}")
        
        elif action == "perturb":
            if not perturbation:
                perturbation = "activity_boost"
            
            task = progress.add_task(f"Applying {perturbation} perturbation...", total=None)
            
            try:
                result = cis_system.simulate_consciousness_perturbation(
                    perturbation_type=perturbation,
                    magnitude=0.2
                )
                
                progress.update(task, description="✅ Perturbation complete")
                
                console.print(Panel(
                    f"[bold]Perturbation:[/bold] {result['perturbation_type']}\n"
                    f"[bold]Baseline:[/bold] {result['baseline_consciousness']:.4f}\n"
                    f"[bold]Immediate Impact:[/bold] {result['immediate_impact']:.4f}\n"
                    f"[bold]Final State:[/bold] {result['final_consciousness']:.4f}\n"
                    f"[bold]Resilience:[/bold] {result['resilience']:.4f}\n"
                    f"[bold]Adaptation:[/bold] {result['adaptation']:.4f}",
                    title="🌪️  Perturbation Response"
                ))
                
            except Exception as e:
                console.print(f"[red]Error applying perturbation:[/red] {e}")


@app.command()
def pipeline(
    data_path: Optional[str] = typer.Option(None, "--data", "-d", help="Data file path"),
    output_dir: str = typer.Option("pce_output", "--output", "-o", help="Output directory"),
    full_integration: bool = typer.Option(True, "--full", help="Run full integration pipeline"),
    save_results: bool = typer.Option(True, "--save", help="Save results to files")
):
    """Run complete PCE pipeline."""
    check_rich_available()
    
    console.print(Panel.fit(
        "[bold blue]🧠 Pan-Omics Consciousness Engine Pipeline[/bold blue]\n"
        "[dim]Running complete consciousness modeling pipeline...[/dim]",
        title="PCE Pipeline"
    ))
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Step 1: Load or generate data
        task1 = progress.add_task("Step 1: Loading data...", total=None)
        try:
            if data_path:
                omics_data = load_data(Path(data_path))
            else:
                omics_data = create_toy_dataset("multi_omics", n_samples=100, n_features=500)
            
            pce_state['current_data'] = omics_data
            progress.update(task1, description="✅ Step 1: Data loaded")
            
        except Exception as e:
            console.print(f"[red]Step 1 failed:[/red] {e}")
            return
        
        # Step 2: MOGIL - Build hypergraph and encode
        task2 = progress.add_task("Step 2: MOGIL processing...", total=None)
        try:
            mogil_system = MOGIL()
            pce_state['mogil'] = mogil_system
            
            hypergraph = mogil_system.build_hypergraph(omics_data)
            pce_state['current_hypergraph'] = hypergraph
            
            embedding = mogil_system.encode_hypergraph(hypergraph)
            pce_state['current_embedding'] = embedding
            
            progress.update(task2, description="✅ Step 2: MOGIL complete")
            
        except Exception as e:
            console.print(f"[red]Step 2 failed:[/red] {e}")
            return
        
        # Step 3: Q-LEM - Quantum entropy optimization
        task3 = progress.add_task("Step 3: Q-LEM optimization...", total=None)
        try:
            qlem_system = QLEM()
            pce_state['qlem'] = qlem_system
            
            qlem_system.create_quantum_state(embedding)
            qlem_system.minimize_entropy(embedding)
            
            progress.update(task3, description="✅ Step 3: Q-LEM complete")
            
        except Exception as e:
            console.print(f"[red]Step 3 failed:[/red] {e}")
            if not full_integration:
                return
        
        # Step 4: E³DE - Evolutionary dynamics
        task4 = progress.add_task("Step 4: E³DE evolution...", total=None)
        try:
            e3de_system = E3DE()
            pce_state['e3de'] = e3de_system
            
            e3de_system.create_population("main", 50, 30, embedding)
            e3de_system.evolve_population("main", 20)
            
            progress.update(task4, description="✅ Step 4: E³DE complete")
            
        except Exception as e:
            console.print(f"[red]Step 4 failed:[/red] {e}")
            if not full_integration:
                return
        
        # Step 5: HDTS - Digital twin simulation
        task5 = progress.add_task("Step 5: HDTS simulation...", total=None)
        try:
            hdts_system = HDTS()
            pce_state['hdts'] = hdts_system
            
            hdts_system.create_biological_system(embedding)
            hdts_system.simulate_consciousness_emergence(0.5)
            
            progress.update(task5, description="✅ Step 5: HDTS complete")
            
        except Exception as e:
            console.print(f"[red]Step 5 failed:[/red] {e}")
            if not full_integration:
                return
        
        # Step 6: CIS - Final integration
        task6 = progress.add_task("Step 6: CIS integration...", total=None)
        try:
            cis_system = CIS(
                mogil_system=pce_state['mogil'],
                qlem_system=pce_state['qlem'],
                e3de_system=pce_state['e3de'],
                hdts_system=pce_state['hdts']
            )
            pce_state['cis'] = cis_system
            
            cis_system.create_connectome(embedding)
            final_metrics = cis_system.integrate_consciousness(integration_cycles=50)
            
            progress.update(task6, description="✅ Step 6: CIS complete")
            
        except Exception as e:
            console.print(f"[red]Step 6 failed:[/red] {e}")
            return
    
    # Generate final report
    console.print("\n" + "="*50)
    console.print(Panel(
        f"[bold]🎉 PCE Pipeline Complete![/bold]\n\n"
        f"[bold]Final Consciousness Level:[/bold] {final_metrics.consciousness_level:.4f}\n"
        f"[bold]Consciousness Category:[/bold] {final_metrics.consciousness_category.value.title()}\n"
        f"[bold]Integrated Information (Φ):[/bold] {final_metrics.phi:.4f}\n"
        f"[bold]Global Accessibility:[/bold] {final_metrics.global_accessibility:.4f}\n"
        f"[bold]Network Connectivity:[/bold] {final_metrics.network_connectivity:.4f}\n\n"
        f"[dim]Results saved to: {output_path}[/dim]",
        title="🏆 Final Results"
    ))
    
    # Save results if requested
    if save_results:
        try:
            report = cis_system.consciousness_report()
            
            with open(output_path / "consciousness_report.json", 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            console.print(f"✅ Results saved to {output_path}")
            
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Could not save results: {e}")


@app.command()
def status():
    """Show current PCE system status."""
    check_rich_available()
    
    # System status
    table = Table(title="🖥️  PCE System Status")
    table.add_column("Component", style="bold")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    # Data status
    if pce_state['current_data']:
        data = pce_state['current_data']
        table.add_row("Data", "✅ Loaded", f"{data.data_type}, {data.data.shape}")
    else:
        table.add_row("Data", "❌ Not loaded", "Use 'pce load' or 'pce toy-data'")
    
    # MOGIL status
    if pce_state['mogil']:
        mogil_info = str(pce_state['mogil'])
        table.add_row("MOGIL", "✅ Active", mogil_info)
    else:
        table.add_row("MOGIL", "❌ Not initialized", "Use 'pce mogil build'")
    
    # Q-LEM status
    if pce_state['qlem']:
        qlem_info = str(pce_state['qlem'])
        table.add_row("Q-LEM", "✅ Active", qlem_info)
    else:
        table.add_row("Q-LEM", "❌ Not initialized", "Use 'pce qlem create'")
    
    # E³DE status
    if pce_state['e3de']:
        e3de_info = str(pce_state['e3de'])
        table.add_row("E³DE", "✅ Active", e3de_info)
    else:
        table.add_row("E³DE", "❌ Not initialized", "Use 'pce e3de create'")
    
    # HDTS status
    if pce_state['hdts']:
        hdts_info = str(pce_state['hdts'])
        table.add_row("HDTS", "✅ Active", hdts_info)
    else:
        table.add_row("HDTS", "❌ Not initialized", "Use 'pce hdts create'")
    
    # CIS status
    if pce_state['cis']:
        cis_info = str(pce_state['cis'])
        table.add_row("CIS", "✅ Active", cis_info)
    else:
        table.add_row("CIS", "❌ Not initialized", "Use 'pce cis integrate'")
    
    console.print(table)


def main():
    """Main CLI entry point."""
    if app is None:
        check_rich_available()
    
    # Set up logging
    setup_logging(level=logging.INFO)
    
    # Run the app
    app()


if __name__ == "__main__":
    main()
