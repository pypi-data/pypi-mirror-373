"""
Main CLI Entry Point for Reasoning Kernel
=========================================

Command-line interface for the Semantic Kernel Reasoning System.
Provides commands for running the kernel, API server, and utilities.

Enhanced with Tasks 1-6 improvements:
- Unified settings system and kernel management
- Enhanced plugin architecture and MSA optimization
- Modern API integration capabilities
"""

import asyncio
import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

from settings import create_settings

console = Console()
logger = logging.getLogger(__name__)


def setup_logging(settings) -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(name)s - %(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--minimal", is_flag=True, help="Use minimal settings mode")
@click.pass_context
def main(ctx: click.Context, debug: bool, minimal: bool) -> None:
    """Reasoning Kernel - Advanced Semantic Kernel System."""
    ctx.ensure_object(dict)

    # Create settings based on mode
    settings = create_settings(minimal=minimal)
    if debug:
        settings.debug = True
        settings.log_level = "DEBUG"

    ctx.obj["settings"] = settings
    setup_logging(settings)

    if debug or settings.debug:
        console.print("[bold blue]🔧 Debug mode enabled[/bold blue]")

    console.print(
        f"[bold green]⚙️ Using {'minimal' if minimal or settings.use_minimal_mode else 'full'} settings[/bold green]"
    )


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.pass_context
def serve(ctx: click.Context, host: str, port: int, reload: bool) -> None:
    """Start the API server."""
    settings = ctx.obj["settings"]

    console.print(f"[bold green]🚀 Starting API server on {host}:{port}[/bold green]")

    if settings.is_development() and reload:
        console.print("[yellow]📝 Auto-reload enabled for development[/yellow]")

    console.print("[yellow]⚠️ API server functionality is under development[/yellow]")
    console.print("[dim]Use `reasoning-kernel kernel -i` for interactive mode[/dim]")


@main.command()
@click.option("--query", "-q", help="Query to process")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
@click.pass_context
def kernel(ctx: click.Context, query: str | None, interactive: bool) -> None:
    """Run the Semantic Kernel directly."""
    settings = ctx.obj["settings"]

    if interactive:
        console.print("[bold blue]🤖 Starting interactive kernel mode[/bold blue]")
        console.print("[dim]Type 'quit' or 'exit' to stop[/dim]")

        async def interactive_loop():
            console.print("[green]✓ Kernel initialized (basic mode)[/green]")

            while True:
                try:
                    user_input = console.input("\n[bold cyan]Query:[/bold cyan] ")
                    if user_input.lower() in ("quit", "exit", "q"):
                        console.print("[yellow]👋 Goodbye![/yellow]")
                        break

                    if user_input.strip():
                        console.print("[dim]Processing...[/dim]")
                        console.print(f"[green]✓ Processed: {user_input}[/green]")
                        console.print("[dim]Note: Full SK processing coming soon[/dim]")

                except KeyboardInterrupt:
                    console.print("\n[yellow]👋 Goodbye![/yellow]")
                    break
                except Exception as e:
                    console.print(f"[red]❌ Error: {e}[/red]")

        asyncio.run(interactive_loop())

    elif query:
        console.print(f"[bold blue]🔍 Processing query: {query}[/bold blue]")

        async def process_query():
            console.print("[dim]Processing...[/dim]")
            console.print(f"[green]✓ Processed: {query}[/green]")
            console.print("[dim]Note: Full SK processing coming soon[/dim]")

        asyncio.run(process_query())

    else:
        console.print("[yellow]❓ Please provide a query with -q or use -i for interactive mode[/yellow]")


@main.command()
@click.option("--input", "-i", help="Input data file or string")
@click.pass_context
def msa(ctx: click.Context, input: str | None) -> None:
    """Run Multi-Step Analysis (MSA) pipeline."""
    settings = ctx.obj["settings"]

    console.print("[bold blue]🔬 Running MSA Pipeline[/bold blue]")

    async def run_msa():
        try:
            if input:
                console.print(f"[dim]Processing input: {input}[/dim]")
                console.print(f"[green]✓ MSA Result: Processed '{input}' successfully[/green]")
                console.print("[dim]Note: Full MSA pipeline coming soon[/dim]")
            else:
                console.print("[yellow]❓ Please provide input data with -i[/yellow]")

        except Exception as e:
            console.print(f"[red]❌ MSA Error: {e}[/red]")
            sys.exit(1)

    asyncio.run(run_msa())


@main.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate configuration and dependencies."""
    settings = ctx.obj["settings"]

    console.print("[bold blue]🔍 Validating configuration...[/bold blue]")

    # Check required settings
    missing = settings.validate_required_settings()
    if missing:
        console.print(f"[red]❌ Missing required settings: {', '.join(missing)}[/red]")
        console.print("[yellow]💡 Set these environment variables or create a .env file[/yellow]")
        sys.exit(1)
    else:
        console.print("[green]✓ All required settings configured[/green]")

    # Basic validation complete
    console.print("[bold green]🎉 Basic validation complete![/bold green]")
    console.print("[dim]Note: Full kernel validation coming soon[/dim]")


@main.command()
@click.pass_context
def plugins(ctx: click.Context) -> None:
    """List available plugins and their functions."""
    settings = ctx.obj["settings"]

    console.print("[bold blue]🔌 Available Plugins[/bold blue]")

    async def show_plugins():
        try:
            # Use absolute import
            from reasoning_kernel.kernel import ReasoningKernel

            kernel_instance = ReasoningKernel(settings)
            plugin_info = kernel_instance.get_plugin_info()

            if not plugin_info:
                console.print("[yellow]⚠️ No plugins loaded[/yellow]")
                return

            for plugin_name, info in plugin_info.items():
                console.print(f"\n[bold green]📦 {plugin_name}[/bold green]")
                console.print(f"  Functions: {info['function_count']}")

                for func_name in info["functions"][:5]:  # Show first 5 functions
                    console.print(f"    • {func_name}")

                if info["function_count"] > 5:
                    remaining = info["function_count"] - 5
                    console.print(f"    ... and {remaining} more")

        except Exception as e:
            console.print(f"[red]❌ Plugin loading failed: {e}[/red]")
            console.print("[dim]This is expected if Redis or other services are not available[/dim]")

    asyncio.run(show_plugins())


@main.command()
@click.option("--plugin", "-p", required=True, help="Plugin name")
@click.option("--function", "-f", required=True, help="Function name")
@click.option("--args", "-a", help="Function arguments as JSON")
@click.pass_context
def test_function(ctx: click.Context, plugin: str, function: str, args: str | None) -> None:
    """Test a specific kernel function."""
    settings = ctx.obj["settings"]

    console.print(f"[bold blue]🧪 Testing Function: {plugin}.{function}[/bold blue]")

    async def run_test():
        try:
            import json
            from reasoning_kernel.kernel import ReasoningKernel

            kernel_instance = ReasoningKernel(settings)

            # Parse arguments if provided
            kwargs = {}
            if args:
                try:
                    kwargs = json.loads(args)
                    console.print(f"[dim]Arguments: {kwargs}[/dim]")
                except json.JSONDecodeError as e:
                    console.print(f"[red]❌ Invalid JSON arguments: {e}[/red]")
                    return

            # Get the function from the kernel
            try:
                kernel_function = kernel_instance.kernel.get_function(plugin, function)
                if not kernel_function:
                    console.print(f"[red]❌ Function {plugin}.{function} not found[/red]")
                    return
            except Exception as e:
                console.print(f"[red]❌ Error getting function {plugin}.{function}: {e}[/red]")
                return

            # Test the function by invoking it
            result = await kernel_instance.kernel.invoke(kernel_function, **kwargs)

            if result and hasattr(result, "value"):
                console.print(f"[green]✅ Result: {result.value}[/green]")
            else:
                console.print(f"[green]✅ Result: {result}[/green]")

        except Exception as e:
            console.print(f"[red]❌ Function test failed: {e}[/red]")
            import traceback

            console.print(f"[dim]{traceback.format_exc()}[/dim]")

    asyncio.run(run_test())


@main.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show system information."""
    settings = ctx.obj["settings"]

    console.print("[bold blue]ℹ️ Reasoning Kernel Information[/bold blue]")
    console.print(f"Environment: {settings.environment}")
    console.print(f"Debug Mode: {settings.debug}")
    console.print(f"Log Level: {settings.log_level}")
    console.print(f"Minimal Mode: {settings.use_minimal_mode}")

    if hasattr(settings, "enable_caching"):
        console.print(f"Caching: {settings.enable_caching}")

    if hasattr(settings, "azure_openai_endpoint") and settings.azure_openai_endpoint:
        console.print(f"Azure OpenAI Endpoint: {settings.azure_openai_endpoint}")
        console.print(f"Azure OpenAI Model: {settings.azure_openai_model}")

    console.print(f"Redis Host: {settings.redis_host}:{settings.redis_port}")


# Import and add enhanced commands from Task 7
try:
    from sk_core.cli_commands import enhanced_commands

    for command in enhanced_commands:
        main.add_command(command)

    logger.debug("Enhanced CLI commands loaded")
except ImportError as e:
    logger.warning(f"Enhanced CLI commands unavailable: {e}")


if __name__ == "__main__":
    main()
