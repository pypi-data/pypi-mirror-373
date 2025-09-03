"""
Enhanced CLI Commands for Semantic Kernel Integration
====================================================

Modern CLI commands that leverage the enhanced architecture from Tasks 1-6:
- Unified settings system (Task 1-2)
- Enhanced kernel management (Task 2)
- Modern plugin architecture (Task 3)
- Validated service integration (Task 4)
- Optimized MSA plugins (Task 5)
- API interface integration (Task 6)
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import create_settings
from ..sk_core.kernel_manager import create_kernel

console = Console()
logger = logging.getLogger(__name__)


def setup_enhanced_logging() -> None:
    """Setup enhanced logging for CLI commands."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# Enhanced CLI command decorators
def async_command(f):
    """Decorator for async click commands."""

    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


def with_kernel(f):
    """Decorator to provide kernel instance to commands."""

    async def wrapper(*args, **kwargs):
        # Get settings from context
        ctx = click.get_current_context()
        settings = ctx.obj.get("settings")

        if not settings:
            settings = create_settings()

        # Create kernel instance
        try:
            kernel = create_kernel(settings)
            return await f(kernel, *args, **kwargs)
        except Exception as e:
            console.print(f"[red]❌ Kernel initialization failed: {e}[/red]")
            raise click.Abort()

    return wrapper


@click.command()
@click.option("--query", "-q", required=True, help="Query to analyze with MSA")
@click.option(
    "--plugin", "-p", default="enhanced", type=click.Choice(["simple", "enhanced"]), help="MSA plugin type to use"
)
@click.option("--domain", "-d", help="Domain context for analysis")
@click.option("--use-ai", is_flag=True, default=True, help="Use AI-powered analysis")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.pass_context
@async_command
@with_kernel
async def msa_analyze(kernel, ctx, query: str, plugin: str, domain: str | None, use_ai: bool, output: str):
    """Enhanced MSA analysis using optimized plugins from Task 5."""
    console.print(f"[bold blue]🔬 MSA Analysis: {plugin} plugin[/bold blue]")
    console.print(f"[dim]Query: {query}[/dim]")

    if domain:
        console.print(f"[dim]Domain: {domain}[/dim]")

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Analyzing with MSA pipeline...", total=None)

        try:
            # Get the appropriate MSA plugin
            plugin_name = f"msa_reasoning_{plugin}"

            # Import plugin dynamically based on selection
            if plugin == "enhanced":
                from ..plugins.msa_reasoning_enhanced import create_msa_reasoning_enhanced

                msa_plugin = create_msa_reasoning_enhanced()
            else:
                from ..plugins.msa_reasoning_simple import create_msa_reasoning_simple

                msa_plugin = create_msa_reasoning_simple()

            # Add plugin to kernel
            kernel.add_plugin(msa_plugin, plugin_name)

            # Prepare arguments
            kwargs = {"query": query}
            if domain:
                kwargs["domain"] = domain
            if plugin == "enhanced":
                kwargs["use_ai"] = use_ai

            # Get and invoke the analysis function
            analyze_function = kernel.get_function(plugin_name, "analyze")
            result = await kernel.invoke(analyze_function, **kwargs)

            progress.update(task, description="Analysis complete!")

            # Format output
            if output == "json":
                if hasattr(result, "value"):
                    console.print(json.dumps(result.value, indent=2))
                else:
                    console.print(json.dumps(str(result), indent=2))
            else:
                console.print(
                    Panel(
                        str(result.value if hasattr(result, "value") else result),
                        title="MSA Analysis Result",
                        border_style="green",
                    )
                )

        except Exception as e:
            progress.update(task, description="Analysis failed!")
            console.print(f"[red]❌ MSA Analysis failed: {e}[/red]")
            logger.exception("MSA analysis error")


@click.command()
@click.option("--include-functions", is_flag=True, help="Include function details")
@click.pass_context
@async_command
@with_kernel
async def list_plugins(kernel, ctx, include_functions: bool):
    """List available plugins with enhanced details."""
    console.print("[bold blue]🔌 Available Semantic Kernel Plugins[/bold blue]")

    try:
        # Create table for plugin information
        table = Table("Plugin Name", "Type", "Functions", "Status", title="Semantic Kernel Plugins")

        plugins = kernel.plugins

        if not plugins:
            console.print("[yellow]⚠️ No plugins loaded[/yellow]")
            return

        for plugin_name, plugin in plugins.items():
            functions = list(plugin.functions.keys())
            function_count = len(functions)

            # Determine plugin type
            plugin_type = "Standard"
            if "msa" in plugin_name.lower():
                plugin_type = "MSA"
            elif "reasoning" in plugin_name.lower():
                plugin_type = "Reasoning"

            table.add_row(plugin_name, plugin_type, str(function_count), "[green]Active[/green]")

            if include_functions and functions:
                for func_name in functions:
                    table.add_row(f"  └─ {func_name}", "Function", "", "[dim]Available[/dim]")

        console.print(table)

    except Exception as e:
        console.print(f"[red]❌ Plugin listing failed: {e}[/red]")
        logger.exception("Plugin listing error")


@click.command()
@click.option("--plugin", "-p", required=True, help="Plugin name")
@click.option("--function", "-f", required=True, help="Function name")
@click.option("--args", "-a", help="Function arguments as JSON")
@click.option("--timeout", "-t", type=int, default=30, help="Function timeout in seconds")
@click.pass_context
@async_command
@with_kernel
async def invoke_function(kernel, ctx, plugin: str, function: str, args: str | None, timeout: int):
    """Enhanced function invocation with better error handling."""
    console.print(f"[bold blue]⚙️ Invoking: {plugin}.{function}[/bold blue]")

    # Parse arguments
    kwargs = {}
    if args:
        try:
            kwargs = json.loads(args)
            console.print(f"[dim]Arguments: {json.dumps(kwargs, indent=2)}[/dim]")
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Invalid JSON arguments: {e}[/red]")
            return

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task(f"Invoking {plugin}.{function}...", total=None)

        try:
            # Get function from kernel
            kernel_function = kernel.get_function(plugin, function)
            if not kernel_function:
                console.print(f"[red]❌ Function {plugin}.{function} not found[/red]")
                return

            # Invoke with timeout
            try:
                result = await asyncio.wait_for(kernel.invoke(kernel_function, **kwargs), timeout=timeout)

                progress.update(task, description="Function completed!")

                # Display result
                if hasattr(result, "value"):
                    result_value = result.value
                else:
                    result_value = str(result)

                console.print(Panel(str(result_value), title=f"Result: {plugin}.{function}", border_style="green"))

            except asyncio.TimeoutError:
                progress.update(task, description="Function timed out!")
                console.print(f"[red]❌ Function timed out after {timeout} seconds[/red]")

        except Exception as e:
            progress.update(task, description="Function failed!")
            console.print(f"[red]❌ Function invocation failed: {e}[/red]")
            logger.exception("Function invocation error")


@click.command()
@click.pass_context
@async_command
@with_kernel
async def system_health(kernel, ctx):
    """Enhanced system health check for all components."""
    console.print("[bold blue]🏥 System Health Check[/bold blue]")

    health_checks = []

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:

        # Check kernel
        task1 = progress.add_task("Checking kernel...", total=None)
        try:
            # Basic kernel check
            plugins = kernel.plugins
            health_checks.append(
                {"component": "Semantic Kernel", "status": "✅ Healthy", "details": f"{len(plugins)} plugins loaded"}
            )
        except Exception as e:
            health_checks.append({"component": "Semantic Kernel", "status": "❌ Unhealthy", "details": str(e)})
        progress.update(task1, description="Kernel checked!")

        # Check MSA plugins
        task2 = progress.add_task("Checking MSA plugins...", total=None)
        try:
            from ..plugins.msa_reasoning_simple import create_msa_reasoning_simple
            from ..plugins.msa_reasoning_enhanced import create_msa_reasoning_enhanced

            # Test simple plugin
            simple_plugin = create_msa_reasoning_simple()
            enhanced_plugin = create_msa_reasoning_enhanced()

            health_checks.append(
                {"component": "MSA Plugins", "status": "✅ Healthy", "details": "Simple and Enhanced plugins available"}
            )
        except Exception as e:
            health_checks.append({"component": "MSA Plugins", "status": "❌ Unhealthy", "details": str(e)})
        progress.update(task2, description="MSA plugins checked!")

        # Check settings
        task3 = progress.add_task("Checking configuration...", total=None)
        try:
            settings = ctx.obj.get("settings") or create_settings()
            missing = []

            # Check critical settings
            if hasattr(settings, "azure_openai_endpoint") and not settings.azure_openai_endpoint:
                missing.append("Azure OpenAI endpoint")
            if hasattr(settings, "azure_openai_api_key") and not settings.azure_openai_api_key:
                missing.append("Azure OpenAI API key")

            if missing:
                health_checks.append(
                    {"component": "Configuration", "status": "⚠️ Warning", "details": f"Missing: {', '.join(missing)}"}
                )
            else:
                health_checks.append(
                    {"component": "Configuration", "status": "✅ Healthy", "details": "All required settings present"}
                )
        except Exception as e:
            health_checks.append({"component": "Configuration", "status": "❌ Unhealthy", "details": str(e)})
        progress.update(task3, description="Configuration checked!")

    # Display results
    table = Table("Component", "Status", "Details", title="System Health Report")

    for check in health_checks:
        table.add_row(check["component"], check["status"], check["details"])

    console.print(table)


# Export commands for integration
enhanced_commands = [msa_analyze, list_plugins, invoke_function, system_health]
