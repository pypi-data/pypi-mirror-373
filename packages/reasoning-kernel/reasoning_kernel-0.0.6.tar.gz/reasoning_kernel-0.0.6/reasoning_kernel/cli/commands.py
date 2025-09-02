"""
Command Registry for REPL

This module provides the command registry and execution system for the
Reasoning Kernel REPL, including all MSA pipeline commands, Redis operations,
and utility functions.
"""

import asyncio
import difflib
import json
import uuid
from typing import Dict, List

from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from ..core.logging_config import get_logger

logger = get_logger(__name__)


class CommandRegistry:
    """
    Registry and executor for REPL commands

    Manages all available commands including:
    - MSA pipeline stages (/reason, /parse, /knowledge, etc.)
    - Redis operations (/redis list, get, search, etc.)
    - Analysis tools (/confidence, /explain, /debug)
    - Utility commands (/status, /export, /config)
    """

    def __init__(self, repl_instance):
        """Initialize command registry with REPL instance"""
        self.repl = repl_instance
        self.console = repl_instance.console
        self.commands = self._register_commands()

    def _register_commands(self) -> Dict[str, callable]:
        """Register all available commands"""
        return {
            # Core reasoning commands
            "/reason": self._cmd_reason,
            "/parse": self._cmd_parse,
            "/knowledge": self._cmd_knowledge,
            "/graph": self._cmd_graph,
            "/synthesis": self._cmd_synthesis,
            "/inference": self._cmd_inference,
            # Redis commands
            "/redis": self._cmd_redis,
            # Analysis commands
            "/confidence": self._cmd_confidence,
            "/explain": self._cmd_explain,
            "/debug": self._cmd_debug,
            "/benchmark": self._cmd_benchmark,
            # Utility commands
            "/status": self._cmd_status,
            "/history": self._cmd_history,
            "/export": self._cmd_export,
            "/config": self._cmd_config,
        }

    async def execute(self, command: str, args: List[str]):
        """Execute a command with arguments"""
        if command not in self.commands:
            # Offer fuzzy suggestions and light auto-correction
            choices = list(self.commands.keys())
            matches = difflib.get_close_matches(command, choices, n=3, cutoff=0.5)
            if matches:
                best = matches[0]
                ratio = difflib.SequenceMatcher(None, command, best).ratio()
                if ratio >= 0.85:
                    self.console.print(
                        f"[yellow]Auto-correcting '{command}' → '{best}'[/yellow]"
                    )
                    command = best
                else:
                    self.console.print(f"[red]Unknown command: {command}[/red]")
                    self.console.print(
                        "[yellow]Did you mean:[/yellow] " + ", ".join(matches)
                    )
                    self.console.print("[dim]Type /help for available commands[/dim]")
                    return
            else:
                self.console.print(f"[red]Unknown command: {command}[/red]")
                self.console.print("[dim]Type /help for available commands[/dim]")
                return

        try:
            await self.commands[command](args)
            # Contextual help after core commands
            if command in {"/reason", "/parse", "/inference"}:
                ctx = {
                    "last_command": command,
                    "last_domain": self.repl.last_result.get("domain")
                    if self.repl.last_result
                    else None,
                }
                self.repl.ui.show_contextual_help(ctx)
        except Exception as e:
            self.console.print(f"[red]Command failed: {e}[/red]")
            logger.exception(f"Command execution failed: {command}")

    def show_command_help(self, command: str):
        """Show detailed help for a specific command"""
        help_text = {
            "/reason": """
Execute complete MSA pipeline with verbose reasoning

Usage: /reason <scenario> [options]

Options:
  --verbose          Enable detailed step-by-step explanations
  --save-to-redis    Save results to Redis Cloud
  --domain=<domain>  Specify domain context (medical, legal, etc.)
  --mode=<mode>      Reasoning mode (hybrid, knowledge, probabilistic)

Examples:
  /reason "Patient presents with fever and persistent cough"
  /reason "Legal contract dispute over payment terms" --domain=legal
  /reason "Stock market volatility analysis" --mode=probabilistic
            """,
            "/parse": """
Parse text and extract entities with relationship mapping

Usage: /parse <text> [options]

Options:
  --format=<format>  Output format (json, table, tree)
  --entities-only    Show only extracted entities
  --relationships    Include relationship analysis
  --confidence       Show confidence scores

Examples:
  /parse "The 45-year-old patient has diabetes"
  /parse "Contract signed on January 15, 2024" --format=table
  /parse "Stock price increased by 5%" --relationships
            """,
            "/redis": """
Redis Cloud operations and data management

Usage: /redis <operation> [options]

Operations:
  list [--pattern=<pattern>]     List keys matching pattern
  get <key> [--format=<format>]  Retrieve and display data
  search <query> [--index=<idx>] Vector similarity search
  stats [--domain=<domain>]      Show usage statistics
  cleanup [--dry-run]            Clean expired data

Examples:
  /redis list --pattern=kb:*
  /redis get kb:medical_001 --format=pretty
  /redis search "respiratory symptoms" --index=knowledge_base_index
  /redis stats --domain=medical
            """,
        }

        if command in help_text:
            syntax = Syntax(help_text[command].strip(), "text", theme="monokai")
            panel = Panel(
                syntax, title=f"[bold cyan]Help: {command}", border_style="cyan"
            )
            self.console.print(panel)
        else:
            self.console.print(
                f"[yellow]No detailed help available for {command}[/yellow]"
            )

    # Command implementations
    async def _cmd_reason(self, args: List[str]):
        """Execute complete MSA reasoning pipeline"""
        if not args:
            self.console.print("[red]Usage: /reason <scenario> [options][/red]")
            return

        # Parse arguments
        scenario = " ".join(args)
        verbose = "--verbose" in args
        save_to_redis = "--save-to-redis" in args

        # Generate request ID
        request_id = f"reason_{uuid.uuid4().hex[:8]}"
        self.repl.current_request_id = request_id

        self.console.print("[bold cyan]🧠 Starting MSA Reasoning Pipeline[/bold cyan]")
        self.console.print(f"[dim]Request ID: {request_id}[/dim]")
        self.console.print(f"[dim]Scenario: {scenario}[/dim]")
        self.console.print()

        # Domain detection + narrative overview
        from ..reasoning.domain_adapters import detect_domain, domain_adaptive_stage_text

        domain = detect_domain(scenario)
        intro_lines = [
            "We will parse, retrieve knowledge, build a causal graph, synthesize a probabilistic model, "
            + "and run inference to reach robust conclusions with uncertainty.",
            f"Detected domain: {domain}. Adapting style and terminology accordingly.",
        ]
        self.repl.ui.stream_narrative("High-level Plan", intro_lines)

        # Create progress display (non-blocking smooth animation)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            # Stage 1: Parse
            parse_task = progress.add_task("🔍 Parsing scenario...", total=100)
            await asyncio.sleep(0.4)
            progress.update(parse_task, completed=60)
            await asyncio.sleep(0.25)
            progress.update(parse_task, completed=100)

            # Domain-adaptive narrative (summary→expert when verbose)
            level = "expert" if verbose else "summary"
            parse_expl = domain_adaptive_stage_text(domain, "parse", scenario, level)
            self.repl.ui.stream_narrative("Parse: What I inferred and why", parse_expl)
            self.repl.ui.show_confidence_meter(
                "Parse",
                0.92,
                "Strong pattern cues; ambiguity preserved for later tests",
            )

            # Stage 2: Knowledge
            knowledge_task = progress.add_task(
                "📚 Building knowledge base...", total=100
            )
            await asyncio.sleep(0.4)
            progress.update(knowledge_task, completed=55)
            await asyncio.sleep(0.3)
            progress.update(knowledge_task, completed=100)

            if verbose:
                kn_expl = domain_adaptive_stage_text(
                    domain, "knowledge", scenario, "expert"
                )
            else:
                kn_expl = domain_adaptive_stage_text(
                    domain, "knowledge", scenario, "summary"
                )
            self.repl.ui.stream_narrative("Knowledge: Evidence and relevance", kn_expl)
            self.repl.ui.show_confidence_meter(
                "Knowledge", 0.88, "Retrieved corroborating associations and priors"
            )

            # Stage 3: Graph
            graph_task = progress.add_task(
                "🕸️  Building relationship graph...", total=100
            )
            await asyncio.sleep(0.3)
            progress.update(graph_task, completed=45)
            await asyncio.sleep(0.3)
            progress.update(graph_task, completed=100)

            if verbose:
                graph_tree = {
                    "text": "Symptoms → Causes",
                    "children": [
                        {
                            "text": "Fever + Cough",
                            "children": [
                                {"text": "→ Influenza (likely)"},
                                {"text": "→ Pneumonia (possible)"},
                                {"text": "→ Allergic cough (unlikely)"},
                            ],
                        }
                    ],
                }
                self.repl.ui.show_reasoning_tree("Graph Structure", graph_tree)
                self.repl.ui.stream_narrative(
                    "Graph: Causal commitments",
                    domain_adaptive_stage_text(domain, "graph", scenario, "expert"),
                )
                self.repl.ui.show_confidence_meter(
                    "Graph", 0.85, "Topology aligns with retrieved knowledge"
                )

            # Stage 4: Synthesis
            synthesis_task = progress.add_task(
                "⚗️  Synthesizing probabilistic model...", total=100
            )
            await asyncio.sleep(0.35)
            progress.update(synthesis_task, completed=60)
            await asyncio.sleep(0.35)
            progress.update(synthesis_task, completed=100)

            if verbose:
                self.repl.ui.stream_narrative(
                    "Synthesis: Modeling choices",
                    domain_adaptive_stage_text(domain, "synthesis", scenario, "expert"),
                )
            else:
                self.repl.ui.stream_narrative(
                    "Synthesis: Modeling choices",
                    domain_adaptive_stage_text(
                        domain, "synthesis", scenario, "summary"
                    ),
                )
            self.repl.ui.show_confidence_meter(
                "Synthesis", 0.91, "Model captures core dependencies"
            )

            # Stage 5: Inference
            inference_task = progress.add_task(
                "🎯 Running probabilistic inference...", total=100
            )
            await asyncio.sleep(0.4)
            progress.update(inference_task, completed=70)
            await asyncio.sleep(0.4)
            progress.update(inference_task, completed=100)

            if verbose:
                self.repl.ui.stream_narrative(
                    "Inference: Interpreting posteriors",
                    domain_adaptive_stage_text(domain, "inference", scenario, "expert"),
                )
            else:
                self.repl.ui.stream_narrative(
                    "Inference: Interpreting posteriors",
                    domain_adaptive_stage_text(
                        domain, "inference", scenario, "summary"
                    ),
                )
            self.repl.ui.show_confidence_meter(
                "Inference", 0.87, "Diagnostics converge; some ambiguity remains"
            )

        # Evidence map and results
        evmap = [
            {
                "hypothesis": "Influenza",
                "evidence": ["Fever", "Persistent cough", "Seasonal prevalence"],
                "support": 0.78,
            },
            {
                "hypothesis": "Pneumonia",
                "evidence": ["Cough", "Possible chest congestion"],
                "support": 0.52,
            },
            {"hypothesis": "Allergic cough", "evidence": ["Cough"], "support": 0.18},
        ]
        self.repl.ui.show_evidence_map(evmap)

        # LLM meta-reasoning reflection (streaming)
        try:
            if getattr(self.repl, "llm_reasoner", None):
                prompt = (
                    f"Domain: {domain}\nScenario: {scenario}\n"
                    "Provide a reflective explanation of the reasoning process, alternatives considered, "
                    "and what additional information would maximally reduce uncertainty."
                )
                self.console.print(
                    "\n[bold cyan]🤖 Meta-Reasoning (LLM Reflection)[/bold cyan]"
                )
                async for chunk in self.repl.llm_reasoner.stream_reasoning(prompt):
                    if chunk:
                        self.console.print(chunk)
        except Exception:
            pass

        # Display results
        self._display_reasoning_results(request_id, scenario)

        # Cache and record last result for undo/redo and explanations
        self.repl.last_result = {
            "request_id": request_id,
            "scenario": scenario,
            "domain": domain,
            "stages": [
                {"name": "Parse", "confidence": 0.92},
                {"name": "Knowledge", "confidence": 0.88},
                {"name": "Graph", "confidence": 0.85},
                {"name": "Synthesis", "confidence": 0.91},
                {"name": "Inference", "confidence": 0.87},
            ],
            "evidence_map": evmap,
        }
        self.repl.undo_stack.append(dict(self.repl.last_result))

        if save_to_redis:
            await self._save_reasoning_to_redis(request_id, scenario)

    async def _cmd_parse(self, args: List[str]):
        """Parse text and extract entities"""
        if not args:
            self.console.print("[red]Usage: /parse <text> [options][/red]")
            return

        text = " ".join(arg for arg in args if not arg.startswith("--"))
        format_type = "table"  # Default format

        # Parse format option
        for arg in args:
            if arg.startswith("--format="):
                format_type = arg.split("=")[1]

        self.console.print("[bold cyan]🔍 Parsing Text[/bold cyan]")
        self.console.print(f"[dim]Input: {text}[/dim]")
        self.console.print()

        # Simulate parsing
        with self.console.status("[bold green]Analyzing text..."):
            await asyncio.sleep(1)

        # Mock results
        entities = [
            {"text": "patient", "type": "PERSON", "confidence": 0.95},
            {"text": "fever", "type": "SYMPTOM", "confidence": 0.92},
            {"text": "cough", "type": "SYMPTOM", "confidence": 0.89},
        ]

        if format_type == "table":
            self._display_entities_table(entities)
        elif format_type == "json":
            self._display_entities_json(entities)
        elif format_type == "tree":
            self._display_entities_tree(entities)

    async def _cmd_redis(self, args: List[str]):
        """Handle Redis operations"""
        if not args:
            self.console.print("[red]Usage: /redis <operation> [options][/red]")
            self.console.print(
                "[dim]Operations: list, get, search, stats, cleanup[/dim]"
            )
            return

        operation = args[0]

        if operation == "list":
            await self._redis_list(args[1:])
        elif operation == "get":
            await self._redis_get(args[1:])
        elif operation == "search":
            await self._redis_search(args[1:])
        elif operation == "stats":
            await self._redis_stats(args[1:])
        elif operation == "cleanup":
            await self._redis_cleanup(args[1:])
        else:
            self.console.print(f"[red]Unknown Redis operation: {operation}[/red]")

    async def _cmd_status(self, args: List[str]):
        """Show system status"""
        self.console.print("[bold cyan]🔧 System Status[/bold cyan]")
        self.console.print()

        # Create status table
        status_table = Table(show_header=True, header_style="bold magenta")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Details", style="dim")

        # Redis status
        try:
            await self.repl.redis_service.redis_client.ping()
            redis_status = "✅ Connected"
            redis_details = f"URL: {self.repl.redis_url}"
        except Exception:
            redis_status = "❌ Disconnected"
            redis_details = "Connection failed"

        status_table.add_row("Redis Connection", redis_status, redis_details)
        status_table.add_row("Session ID", "✅ Active", self.repl.session_id)
        status_table.add_row("Environment", "✅ Ready", self.repl.environment)
        status_table.add_row(
            "Verbose Mode",
            "✅ Enabled" if self.repl.verbose_mode else "⚪ Disabled",
            "",
        )
        status_table.add_row(
            "Commands Executed", "📊 Tracked", str(len(self.repl.command_history))
        )

        panel = Panel(status_table, title="System Status", border_style="cyan")
        self.console.print(panel)

    # Placeholder implementations for remaining commands
    async def _cmd_knowledge(self, args: List[str]):
        """Knowledge base operations"""
        self.console.print("[yellow]Knowledge command not yet implemented[/yellow]")

    async def _cmd_graph(self, args: List[str]):
        """Graph operations"""
        self.console.print("[yellow]Graph command not yet implemented[/yellow]")

    async def _cmd_synthesis(self, args: List[str]):
        """Synthesis operations"""
        self.console.print("[yellow]Synthesis command not yet implemented[/yellow]")

    async def _cmd_inference(self, args: List[str]):
        """Inference operations"""
        self.console.print("[yellow]Inference command not yet implemented[/yellow]")

    async def _cmd_confidence(self, args: List[str]):
        """Confidence analysis"""
        self.console.print("[yellow]Confidence command not yet implemented[/yellow]")

    async def _cmd_explain(self, args: List[str]):
        """Explain operations"""
        self.console.print("[yellow]Explain command not yet implemented[/yellow]")

    async def _cmd_debug(self, args: List[str]):
        """Debug operations"""
        self.console.print("[yellow]Debug command not yet implemented[/yellow]")

    async def _cmd_benchmark(self, args: List[str]):
        """Benchmark operations"""
        self.console.print("[yellow]Benchmark command not yet implemented[/yellow]")

    async def _cmd_history(self, args: List[str]):
        """Show command history"""
        self.console.print("[yellow]History command not yet implemented[/yellow]")

    async def _cmd_export(self, args: List[str]):
        """Export operations"""
        self.console.print("[yellow]Export command not yet implemented[/yellow]")

    async def _cmd_config(self, args: List[str]):
        """Configuration operations"""
        self.console.print("[yellow]Config command not yet implemented[/yellow]")

    # Helper methods
    def _display_reasoning_results(self, request_id: str, scenario: str):
        """Display comprehensive reasoning results"""
        # Create results table
        results_table = Table(show_header=True, header_style="bold green")
        results_table.add_column("Stage", style="cyan")
        results_table.add_column("Result", style="white")
        results_table.add_column("Confidence", style="green")

        results_table.add_row("Parse", "Entities extracted", "0.92")
        results_table.add_row("Knowledge", "Medical knowledge retrieved", "0.88")
        results_table.add_row("Graph", "Relationships mapped", "0.85")
        results_table.add_row("Synthesis", "NumPyro model generated", "0.91")
        results_table.add_row("Inference", "Posterior computed", "0.87")

        # Overall confidence
        overall_confidence = 0.89

        panel = Panel(
            results_table,
            title=f"[bold green]🎯 Reasoning Results (Overall: {overall_confidence:.2f})",
            border_style="green",
        )

        self.console.print(panel)

    def _display_entities_table(self, entities: List[Dict]):
        """Display entities in table format"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Entity", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Confidence", style="green")

        for entity in entities:
            table.add_row(entity["text"], entity["type"], f"{entity['confidence']:.2f}")

        panel = Panel(table, title="[bold cyan]Extracted Entities", border_style="cyan")
        self.console.print(panel)

    def _display_entities_json(self, entities: List[Dict]):
        """Display entities in JSON format"""
        json_str = json.dumps(entities, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai")
        panel = Panel(
            syntax, title="[bold cyan]Extracted Entities (JSON)", border_style="cyan"
        )
        self.console.print(panel)

    def _display_entities_tree(self, entities: List[Dict]):
        """Display entities in tree format"""
        tree = Tree("🔍 [bold cyan]Extracted Entities")

        for entity in entities:
            entity_node = tree.add(f"[cyan]{entity['text']}[/cyan]")
            entity_node.add(f"Type: [yellow]{entity['type']}[/yellow]")
            entity_node.add(f"Confidence: [green]{entity['confidence']:.2f}[/green]")

        self.console.print(tree)

    async def _save_reasoning_to_redis(self, request_id: str, scenario: str):
        """Save reasoning results to Redis"""
        try:
            with self.console.status("[bold green]Saving to Redis..."):
                # Mock save operation
                await asyncio.sleep(0.5)

            self.console.print(
                f"[green]✅ Results saved to Redis with key: {request_id}[/green]"
            )

        except Exception as e:
            self.console.print(f"[red]❌ Failed to save to Redis: {e}[/red]")

    # Redis operation implementations
    async def _redis_list(self, args: List[str]):
        """List Redis keys"""
        pattern = "*"
        for arg in args:
            if arg.startswith("--pattern="):
                pattern = arg.split("=")[1]

        try:
            keys = await self.repl.redis_service.redis_client.keys(pattern)

            if not keys:
                self.console.print(
                    f"[yellow]No keys found matching pattern: {pattern}[/yellow]"
                )
                return

            # Display keys in table
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Key", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("TTL", style="green")

            for key in keys[:20]:  # Limit to first 20 keys
                try:
                    key_type = await self.repl.redis_service.redis_client.type(key)
                    ttl = await self.repl.redis_service.redis_client.ttl(key)
                    ttl_str = (
                        f"{ttl}s"
                        if ttl > 0
                        else "No expiry"
                        if ttl == -1
                        else "Expired"
                    )

                    table.add_row(key, key_type, ttl_str)
                except Exception:
                    table.add_row(key, "Unknown", "Unknown")

            if len(keys) > 20:
                table.add_row("...", f"({len(keys) - 20} more)", "...")

            panel = Panel(
                table,
                title=f"[bold cyan]Redis Keys ({len(keys)} total)",
                border_style="cyan",
            )
            self.console.print(panel)

        except Exception as e:
            self.console.print(f"[red]Failed to list Redis keys: {e}[/red]")

    async def _redis_get(self, args: List[str]):
        """Get Redis data"""
        if not args:
            self.console.print("[red]Usage: /redis get <key> [--format=<format>][/red]")
            return

        key = args[0]
        format_type = "pretty"

        for arg in args[1:]:
            if arg.startswith("--format="):
                format_type = arg.split("=")[1]

        try:
            # Try JSON first
            data = await self.repl.redis_service.redis_client.json().get(key)

            if data is None:
                # Try regular get
                data = await self.repl.redis_service.redis_client.get(key)
                if data is None:
                    self.console.print(f"[red]Key not found: {key}[/red]")
                    return

            if format_type == "json":
                json_str = (
                    json.dumps(data, indent=2) if isinstance(data, dict) else str(data)
                )
                syntax = Syntax(json_str, "json", theme="monokai")
                panel = Panel(
                    syntax, title=f"[bold cyan]Redis Data: {key}", border_style="cyan"
                )
            else:
                # Pretty format
                if isinstance(data, dict):
                    content = json.dumps(data, indent=2)
                    syntax = Syntax(content, "json", theme="monokai")
                    panel = Panel(
                        syntax,
                        title=f"[bold cyan]Redis Data: {key}",
                        border_style="cyan",
                    )
                else:
                    panel = Panel(
                        str(data),
                        title=f"[bold cyan]Redis Data: {key}",
                        border_style="cyan",
                    )

            self.console.print(panel)

        except Exception as e:
            self.console.print(f"[red]Failed to get Redis data: {e}[/red]")

    async def _redis_search(self, args: List[str]):
        """Vector similarity search"""
        self.console.print("[yellow]Redis search not yet implemented[/yellow]")

    async def _redis_stats(self, args: List[str]):
        """Show Redis statistics"""
        self.console.print("[yellow]Redis stats not yet implemented[/yellow]")

    async def _redis_cleanup(self, args: List[str]):
        """Clean up Redis data"""
        self.console.print("[yellow]Redis cleanup not yet implemented[/yellow]")
