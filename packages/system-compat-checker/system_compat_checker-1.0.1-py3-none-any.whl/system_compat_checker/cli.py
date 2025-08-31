"""Command-line interface for the system compatibility checker.

This module provides the CLI commands for the system compatibility checker.
"""

import json
import sys
from typing import Optional, Dict, Any

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rich_print

from . import __version__
from .system_info import get_system_info
from .storage import store_api_key, get_api_key, delete_api_key
from .groq_analyzer import GroqCompatibilityAnalyzer

# Initialize Rich console
console = Console()


@click.group()
def cli():
    """System Compatibility Checker - Check if your system is compatible with various applications."""
    pass


@cli.command()
def install_check():
    """Check if the installation is working correctly and provide setup help."""
    from .install_check import print_usage_instructions
    print_usage_instructions()


@cli.command()
def version():
    """Show the version of the system compatibility checker."""
    console.print(f"System Compatibility Checker v{__version__}")


@cli.command()
@click.argument("api_key", required=False)
@click.option("--force", is_flag=True, help="Force setup even if an API key is already stored.")
def setup(api_key: Optional[str], force: bool):
    """Set up the system compatibility checker by storing the Groq API key.
    
    You can provide the API key as an argument:
        python -m src.cli setup YOUR_API_KEY
    
    Or run without arguments to be prompted:
        python -m src.cli setup
    """
    # Check if an API key is already stored
    existing_key = get_api_key()
    if existing_key and not force:
        console.print("[yellow]An API key is already stored. Use --force to overwrite it.[/yellow]")
        return
    
    # Get API key from argument or prompt
    if not api_key:
        console.print("[cyan]Please enter your Groq API key below.[/cyan]")
        console.print("[dim]Note: Your input will be hidden for security.[/dim]")
        try:
            api_key = click.prompt("Enter your Groq API key", hide_input=True, show_default=False)
        except (KeyboardInterrupt, click.Abort):
            console.print("\n[yellow]Setup cancelled.[/yellow]")
            return
    
    # Validate API key format
    if not api_key or not api_key.strip():
        console.print("[red]Error: API key cannot be empty.[/red]")
        return
    
    api_key = api_key.strip()
    
    # Basic validation for Groq API key format
    if not api_key.startswith("gsk_"):
        console.print("[yellow]Warning: API key doesn't start with 'gsk_'. Please verify it's correct.[/yellow]")
    
    # Store the API key
    console.print("[cyan]Storing API key...[/cyan]")
    if store_api_key(api_key):
        console.print("[green]✓ API key stored successfully.[/green]")
        console.print("[dim]You can now use 'python -m src.cli check' to analyze compatibility.[/dim]")
    else:
        console.print("[red]✗ Failed to store API key.[/red]")


@cli.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON.")
def system_info(output_json: bool):
    """Show system information."""
    # Get system information
    info = get_system_info()
    
    if output_json:
        # Output as JSON
        click.echo(json.dumps(info, indent=2))
    else:
        # Output as rich tables
        _display_system_info(info)


def _display_system_info(info: Dict[str, Any]):
    """Display system information using Rich tables.
    
    Args:
        info: The system information to display.
    """
    # Display OS information
    os_table = Table(title="Operating System Information")
    os_table.add_column("Property")
    os_table.add_column("Value")
    
    for key, value in info.get("os", {}).items():
        os_table.add_row(key, str(value))
    
    console.print(os_table)
    console.print("\n")
    
    # Display CPU information
    cpu_table = Table(title="CPU Information")
    cpu_table.add_column("Property")
    cpu_table.add_column("Value")
    
    cpu_info = info.get("cpu", {})
    for key, value in cpu_info.items():
        if key == "cores":
            cpu_table.add_row("Physical Cores", str(value.get("physical", "N/A")))
            cpu_table.add_row("Logical Cores", str(value.get("logical", "N/A")))
        elif key == "frequency":
            cpu_table.add_row("Current Frequency (MHz)", str(value.get("current", "N/A")))
            cpu_table.add_row("Min Frequency (MHz)", str(value.get("min", "N/A")))
            cpu_table.add_row("Max Frequency (MHz)", str(value.get("max", "N/A")))
        else:
            cpu_table.add_row(key, str(value))
    
    console.print(cpu_table)
    console.print("\n")
    
    # Display memory information
    memory_table = Table(title="Memory Information")
    memory_table.add_column("Property")
    memory_table.add_column("Value")
    
    memory_info = info.get("memory", {})
    for key, value in memory_info.items():
        if key == "swap":
            memory_table.add_row("Swap Total", f"{value.get('total', 0) / (1024 ** 3):.2f} GB")
            memory_table.add_row("Swap Used", f"{value.get('used', 0) / (1024 ** 3):.2f} GB")
            memory_table.add_row("Swap Free", f"{value.get('free', 0) / (1024 ** 3):.2f} GB")
            memory_table.add_row("Swap Percent Used", f"{value.get('percent_used', 0):.1f}%")
        elif key in ["total", "available", "used"]:
            memory_table.add_row(key, f"{value / (1024 ** 3):.2f} GB")
        else:
            memory_table.add_row(key, str(value))
    
    console.print(memory_table)
    console.print("\n")
    
    # Display GPU information
    gpu_info = info.get("gpu", {})
    if gpu_info and gpu_info.get("devices"):
        gpu_table = Table(title="GPU Information")
        gpu_table.add_column("Property")
        gpu_table.add_column("Value")
        
        for i, device in enumerate(gpu_info.get("devices", [])):
            gpu_table.add_row(f"GPU {i+1} Name", device.get("name", "N/A"))
            gpu_table.add_row(f"GPU {i+1} Vendor", device.get("vendor", "N/A"))
            if "memory" in device:
                gpu_table.add_row(f"GPU {i+1} Memory", device.get("memory", "N/A"))
            if "driver" in device:
                gpu_table.add_row(f"GPU {i+1} Driver", device.get("driver", "N/A"))
        
        console.print(gpu_table)
        console.print("\n")
    
    # Display storage information
    storage_info = info.get("storage", {})
    if storage_info and storage_info.get("partitions"):
        storage_table = Table(title="Storage Information")
        storage_table.add_column("Device")
        storage_table.add_column("Mountpoint")
        storage_table.add_column("Total")
        storage_table.add_column("Used")
        storage_table.add_column("Free")
        storage_table.add_column("Used %")
        
        for partition in storage_info.get("partitions", []):
            storage_table.add_row(
                partition.get("device", "N/A"),
                partition.get("mountpoint", "N/A"),
                f"{partition.get('total', 0) / (1024 ** 3):.2f} GB",
                f"{partition.get('used', 0) / (1024 ** 3):.2f} GB",
                f"{partition.get('free', 0) / (1024 ** 3):.2f} GB",
                f"{partition.get('percent_used', 0):.1f}%"
            )
        
        console.print(storage_table)
        console.print("\n")
    
    # Display performance information
    performance_info = info.get("performance", {})
    if performance_info:
        performance_table = Table(title="Performance Information")
        performance_table.add_column("Property")
        performance_table.add_column("Value")
        
        for key, value in performance_info.items():
            if key == "per_cpu_percent":
                for i, percent in enumerate(value):
                    performance_table.add_row(f"CPU {i+1} Usage", f"{percent:.1f}%")
            elif key == "load_avg":
                performance_table.add_row("Load Average (1 min)", f"{value[0]:.2f}")
                performance_table.add_row("Load Average (5 min)", f"{value[1]:.2f}")
                performance_table.add_row("Load Average (15 min)", f"{value[2]:.2f}")
            else:
                performance_table.add_row(key, str(value))
        
        console.print(performance_table)


@cli.command()
@click.argument("app_name")
@click.option("--requirements", "-r", type=click.Path(exists=True), help="Path to a JSON file with application requirements.")
@click.option("--output", "-o", type=click.Path(), help="Path to save the analysis result as JSON.")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON.")
def check(app_name: str, requirements: Optional[str], output: Optional[str], output_json: bool):
    """Check system compatibility with a specific application."""
    # Get the API key
    api_key = get_api_key()
    if not api_key:
        console.print("[red]No API key found. Please run 'syscheck setup' first.[/red]")
        sys.exit(1)
    
    # Get system information
    system_info = get_system_info()
    
    # Load requirements if provided
    req_data = None
    if requirements:
        try:
            with open(requirements, "r") as f:
                req_data = json.load(f)
        except Exception as e:
            console.print(f"[red]Failed to load requirements file: {e}[/red]")
            sys.exit(1)
    
    # Create analyzer and analyze compatibility
    analyzer = GroqCompatibilityAnalyzer(api_key)
    result = analyzer.analyze_compatibility(system_info, app_name, req_data)
    
    # Save output if requested
    if output:
        try:
            with open(output, "w") as f:
                json.dump(result, f, indent=2)
            console.print(f"[green]Analysis result saved to {output}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to save analysis result: {e}[/red]")
    
    # Display result
    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        _display_compatibility_result(result, app_name)


def _display_compatibility_result(result: Dict[str, Any], app_name: str):
    """Display compatibility analysis result using Rich.
    
    Args:
        result: The compatibility analysis result.
        app_name: The name of the application.
    """
    # Check if there was an error
    if "error" in result:
        console.print(f"[red]Error: {result['error']}[/red]")
        return
    
    # Determine compatibility status and color
    compatible = result.get("compatible", False)
    confidence = result.get("confidence", 0)
    color = "green" if compatible else "red"
    status = "Compatible" if compatible else "Not Compatible"
    
    # Create header panel
    header = Panel(
        f"[bold]{status}[/bold] with [bold]{app_name}[/bold] (Confidence: {confidence}%)",
        style=color
    )
    console.print(header)
    
    # Display issues if any
    issues = result.get("issues", [])
    if issues:
        console.print("\n[bold]Issues:[/bold]")
        for issue in issues:
            console.print(f"[yellow]• {issue}[/yellow]")
    
    # Display recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        console.print("\n[bold]Recommendations:[/bold]")
        for recommendation in recommendations:
            console.print(f"[blue]• {recommendation}[/blue]")
    
    # Display detailed analysis if available
    detailed_analysis = result.get("detailed_analysis")
    if detailed_analysis:
        console.print("\n[bold]Detailed Analysis:[/bold]")
        console.print(detailed_analysis)


@cli.command()
def reset():
    """Reset the system compatibility checker by removing the stored API key."""
    # Confirm deletion
    if click.confirm("Are you sure you want to remove the stored API key?"):
        if delete_api_key():
            console.print("[green]API key removed successfully.[/green]")
        else:
            console.print("[red]Failed to remove API key.[/red]")
    else:
        console.print("Operation cancelled.")


if __name__ == "__main__":
    cli()