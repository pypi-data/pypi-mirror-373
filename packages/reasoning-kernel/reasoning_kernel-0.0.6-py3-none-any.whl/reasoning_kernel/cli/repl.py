"""
Interactive REPL for Reasoning Kernel

This module provides a comprehensive Read-Eval-Print Loop interface for
exploring and debugging the MSA pipeline with rich terminal UI and
seamless Redis Cloud integration.
"""

import asyncio
import difflib
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import ValidationError, Validator
from rich.console import Console

from ..core.logging_config import get_logger
from ..integrations.langcache_client import LangCacheClient
from ..reasoning.llm_reasoner import LLMReasoner
from ..services.msa_redis_integration import MSARedisIntegration
from ..services.unified_redis_service import create_unified_redis_service
from .commands import CommandRegistry
from .ui import REPLInterface

logger = get_logger(__name__)


class ReasoningREPL:
    """
    Interactive REPL for the Reasoning Kernel MSA Pipeline

    Features:
    - Rich terminal UI with syntax highlighting
    - Command auto-completion and history
    - Real-time MSA pipeline execution
    - Redis Cloud integration
    - Vector similarity search
    - Comprehensive debugging tools
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        environment: str = "development",
        config_file: Optional[str] = None,
    ):
        """Initialize the REPL with configuration"""
        self.console = Console()
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.environment = environment
        self.config_file = config_file

        # Initialize services
        self.redis_service = None
        self.msa_integration = None
        self.langcache = None
        self.llm_reasoner: Optional[LLMReasoner] = None

        # REPL state
        self.session_id = f"repl_{uuid.uuid4().hex[:8]}"
        self.current_request_id = None
        self.verbose_mode = True
        self.debug_level = "info"
        self.running = False

        # Data & history
        self.last_result: Optional[Dict[str, Any]] = None
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        self.explanation_cache: Dict[str, Any] = {}
        self.replay_steps: List[Dict[str, str]] = []

        # UI components
        self.ui = REPLInterface(self.console)
        self.command_registry = CommandRegistry(self)

        # Setup prompt session
        self._setup_prompt_session()

        # Performance tracking
        self.command_history = []
        self.performance_metrics = {}

    def _setup_prompt_session(self):
        """Setup the prompt session with history, completion, and key bindings"""
        # Create history file
        history_dir = Path.home() / ".reasoning_kernel"
        history_dir.mkdir(exist_ok=True)
        history_file = history_dir / "repl_history.txt"

        # Setup completion
        commands = [
            "/reason",
            "/parse",
            "/knowledge",
            "/graph",
            "/synthesis",
            "/inference",
            "/redis",
            "/confidence",
            "/explain",
            "/debug",
            "/benchmark",
            "/help",
            "/history",
            "/export",
            "/config",
            "/status",
            "/clear",
            "/exit",
        ]
        completer = WordCompleter(commands, ignore_case=True)

        # Setup key bindings
        bindings = KeyBindings()

        @bindings.add("c-c")
        def _(event):
            """Handle Ctrl+C gracefully"""
            event.app.exit(exception=KeyboardInterrupt)

        @bindings.add("c-d")
        def _(event):
            """Handle Ctrl+D as exit"""
            event.app.exit()

        @bindings.add("c-l")
        def _(event):
            """Clear screen (Ctrl+L)"""
            self.console.clear()

        @bindings.add("c-s")
        def _(event):
            """Quick save session (Ctrl+S)"""
            # Inject /save into buffer and submit
            event.current_buffer.text = "/save"
            event.current_buffer.validate_and_handle()

        @bindings.add("c-z")
        def _(event):
            """Undo last (Ctrl+Z)"""
            event.current_buffer.text = "/undo"
            event.current_buffer.validate_and_handle()

        @bindings.add("c-y")
        def _(event):
            """Redo (Ctrl+Y)"""
            event.current_buffer.text = "/redo"
            event.current_buffer.validate_and_handle()

        # Setup style
        style = Style.from_dict(
            {
                "prompt": "#00aa00 bold",
                "path": "#884444",
                "command": "#0000aa bold",
                "argument": "#aa0000",
            }
        )

        # Real-time validator for immediate command feedback
        class CommandValidator(Validator):
            def validate(self, document):
                text = document.text.strip()
                if not text:
                    return
                if text.startswith("/"):
                    cmd = text.split()[0]
                    known = set(commands)
                    if cmd not in known and "|" not in text:
                        suggestions = difflib.get_close_matches(
                            cmd, list(known), n=1, cutoff=0.6
                        )
                        message = (
                            f"Unknown {cmd}. Try {suggestions[0]}"
                            if suggestions
                            else "Unknown command"
                        )
                        raise ValidationError(message=message, cursor_position=len(cmd))

        self.validator = CommandValidator()

        # Create prompt session
        self.prompt_session = PromptSession(
            history=FileHistory(str(history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=completer,
            key_bindings=bindings,
            style=style,
            complete_style="column",
            mouse_support=True,
            validator=self.validator,
        )

    async def initialize(self):
        """Initialize async services"""
        try:
            self.ui.show_startup_banner()

            with self.console.status("[bold green]Initializing services..."):
                # Initialize Redis service
                self.redis_service = await create_unified_redis_service(
                    redis_url=self.redis_url, environment=self.environment
                )

                # Initialize MSA integration
                self.msa_integration = await MSARedisIntegration.create(
                    redis_url=self.redis_url, environment=self.environment
                )

                # Initialize LangCache (uses unified redis client as backing cache)
                self.langcache = LangCacheClient()

                # Initialize LLM Reasoner with Redis-backed caching
                self.llm_reasoner = LLMReasoner(
                    redis_cache=self.redis_service.redis_client
                )

                # Test Redis connection
                await self.redis_service.redis_client.ping()

            self.ui.show_initialization_success(self.redis_url, self.session_id)

        except Exception as e:
            self.ui.show_error(f"Failed to initialize services: {e}")
            raise

    async def run(self):
        """Main REPL loop"""
        self.running = True

        try:
            await self.initialize()
            self.ui.show_help_hint()

            while self.running:
                try:
                    # Create dynamic prompt
                    prompt_text = self._create_prompt()

                    # Get user input
                    user_input = await self.prompt_session.prompt_async(
                        HTML(prompt_text), multiline=False
                    )

                    # Skip empty input
                    if not user_input.strip():
                        continue

                    # Process command
                    await self._process_command(user_input.strip())

                except KeyboardInterrupt:
                    self.console.print(
                        "\n[yellow]Use /exit to quit gracefully[/yellow]"
                    )
                    continue
                except EOFError:
                    break
                except Exception as e:
                    self.ui.show_error(f"Unexpected error: {e}")
                    logger.exception("REPL error")

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interrupted by user[/yellow]")
        finally:
            await self._cleanup()

    def _create_prompt(self) -> str:
        """Create dynamic prompt with context information"""
        prompt_parts = []

        # Base prompt
        prompt_parts.append("<prompt>reasoning-kernel</prompt>")

        # Add session info
        if self.current_request_id:
            prompt_parts.append(f"<path>[{self.current_request_id[:8]}]</path>")

        # Add environment indicator
        if self.environment != "production":
            prompt_parts.append(f"<argument>({self.environment})</argument>")

        prompt_parts.append("<prompt>></prompt> ")

        return "".join(prompt_parts)

    async def _process_command(self, command: str):
        """Process a user command"""
        start_time = time.time()

        try:
            # Parse command
            parts = command.split()
            if not parts:
                return

            cmd_name = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            # Handle built-in commands
            if cmd_name == "/exit":
                await self._handle_exit()
                return
            elif cmd_name == "/clear":
                self.console.clear()
                return
            elif cmd_name == "/help":
                await self._handle_help(args)
                return
            elif cmd_name == "/save":
                await self._save_session()
                return
            elif cmd_name == "/undo":
                await self._undo()
                return
            elif cmd_name == "/redo":
                await self._redo()
                return

            # Execute command through registry with chaining support
            # Allow pipelines like: /reason "x" | /export json
            if "|" in command:
                # naive chain parse: execute each segment sequentially
                for seg in command.split("|"):
                    seg = seg.strip()
                    if not seg:
                        continue
                    seg_parts = seg.split()
                    seg_cmd = seg_parts[0]
                    seg_args = seg_parts[1:]
                    await self.command_registry.execute(seg_cmd, seg_args)
            else:
                await self.command_registry.execute(cmd_name, args)

        except Exception as e:
            self.ui.show_error(f"Command execution failed: {e}")
            logger.exception(f"Command failed: {command}")
        finally:
            # Track performance
            execution_time = time.time() - start_time
            self.command_history.append(
                {
                    "command": command,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "execution_time": execution_time,
                    "session_id": self.session_id,
                }
            )

    async def _undo(self):
        if not self.undo_stack:
            self.console.print("[yellow]Nothing to undo[/yellow]")
            return
        state = self.undo_stack.pop()
        self.redo_stack.append(self.last_result or {})
        self.last_result = state
        self.console.print("[green]Undid last action[/green]")

    async def _redo(self):
        if not self.redo_stack:
            self.console.print("[yellow]Nothing to redo[/yellow]")
            return
        state = self.redo_stack.pop()
        self.undo_stack.append(self.last_result or {})
        self.last_result = state
        self.console.print("[green]Redid action[/green]")

    async def _handle_exit(self):
        """Handle graceful exit"""
        if confirm("Save current session before exiting?"):
            await self._save_session()

        self.ui.show_goodbye()
        self.running = False

    async def _handle_help(self, args: List[str]):
        """Handle help command"""
        if args:
            # Show help for specific command
            command = args[0]
            self.command_registry.show_command_help(command)
        else:
            # Show general help
            self.ui.show_help()

    async def _save_session(self):
        """Save current session to Redis"""
        try:
            session_data = {
                "session_id": self.session_id,
                "command_history": self.command_history,
                "performance_metrics": self.performance_metrics,
                "current_request_id": self.current_request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "environment": self.environment,
            }

            session_key = f"session:{self.session_id}"
            await self.redis_service.redis_client.json().set(
                session_key, "$", session_data
            )
            await self.redis_service.redis_client.expire(
                session_key, 86400 * 7
            )  # 1 week

            self.console.print(f"[green]Session saved as {session_key}[/green]")

        except Exception as e:
            self.ui.show_error(f"Failed to save session: {e}")

    async def _cleanup(self):
        """Cleanup resources"""
        try:
            if self.redis_service:
                # Close Redis connections gracefully
                await self.redis_service.redis_client.close()

            self.console.print("[dim]Resources cleaned up[/dim]")

        except Exception:
            logger.exception("Cleanup error")


# CLI entry point
@click.command()
@click.option("--redis-url", default=None, help="Redis connection URL")
@click.option(
    "--environment", default="development", help="Environment (development/production)"
)
@click.option("--config", default=None, help="Configuration file path")
@click.option("--verbose", is_flag=True, help="Enable verbose output")
def main(redis_url, environment, config, verbose):
    """
    Start the Reasoning Kernel Interactive REPL

    A comprehensive interface for exploring MSA pipeline capabilities,
    debugging reasoning processes, and managing Redis Cloud data.
    """
    try:
        repl = ReasoningREPL(
            redis_url=redis_url, environment=environment, config_file=config
        )

        if verbose:
            repl.verbose_mode = True

        # Run the REPL
        asyncio.run(repl.run())

    except KeyboardInterrupt:
        click.echo("\nGoodbye!")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
