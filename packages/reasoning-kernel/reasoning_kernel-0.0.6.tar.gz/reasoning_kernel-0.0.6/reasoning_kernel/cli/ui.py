"""
Rich Terminal UI Components for REPL

This module provides comprehensive UI components for the Reasoning Kernel REPL,
including panels, progress indicators, tables, and interactive elements.
"""

from typing import Any, Dict, List, Optional

from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


class REPLInterface:
    """
    Rich terminal UI interface for the Reasoning Kernel REPL

    Provides professional, color-coded displays for:
    - Startup banners and status messages
    - MSA pipeline progress and results
    - Redis data visualization
    - Error handling and debugging
    - Help and documentation
    """

    def __init__(self, console: Console):
        """Initialize the UI interface"""
        self.console = console

    def show_startup_banner(self):
        """Display the startup banner"""
        banner_text = Text()
        banner_text.append("🧠 ", style="bold blue")
        banner_text.append("Reasoning Kernel", style="bold cyan")
        banner_text.append(" Interactive REPL", style="bold white")

        subtitle = Text()
        subtitle.append(
            "Enhanced MSA Architecture with Redis Cloud Integration", style="dim cyan"
        )

        version_info = Text()
        version_info.append("Version 2.0.0 • ", style="dim")
        version_info.append("Multi-Stage Analysis Pipeline", style="dim green")

        banner_panel = Panel(
            Align.center(Group(banner_text, subtitle, "", version_info)),
            style="bold blue",
            padding=(1, 2),
        )

        self.console.print()
        self.console.print(banner_panel)
        self.console.print()

    def show_initialization_success(self, redis_url: str, session_id: str):
        """Display successful initialization"""
        success_table = Table(show_header=False, box=None, padding=(0, 1))
        success_table.add_column("Component", style="bold green")
        success_table.add_column("Status", style="green")
        success_table.add_column("Details", style="dim")

        success_table.add_row("✅ Redis Connection", "Connected", redis_url)
        success_table.add_row(
            "✅ MSA Integration", "Initialized", "All stages available"
        )
        success_table.add_row("✅ Session", "Active", f"ID: {session_id}")
        success_table.add_row("✅ Vector Indices", "Ready", "4 indices available")

        panel = Panel(
            success_table,
            title="[bold green]🚀 Initialization Complete",
            border_style="green",
        )

        self.console.print(panel)

    def show_help_hint(self):
        """Show initial help hint"""
        hint = Text()
        hint.append("💡 ", style="yellow")
        hint.append("Type ", style="dim")
        hint.append("/help", style="bold cyan")
        hint.append(" for commands, ", style="dim")
        hint.append("/reason <scenario>", style="bold cyan")
        hint.append(" to start reasoning, or ", style="dim")
        hint.append("/exit", style="bold cyan")
        hint.append(" to quit", style="dim")

        self.console.print(hint)
        self.console.print()

    def show_help(self):
        """Display comprehensive help"""
        help_layout = Layout()
        help_layout.split_column(
            Layout(name="header", size=3),
            Layout(name="commands"),
            Layout(name="footer", size=3),
        )

        # Header
        header = Panel(
            Align.center(Text("Reasoning Kernel REPL Commands", style="bold cyan")),
            style="cyan",
        )
        help_layout["header"].update(header)

        # Commands table
        commands_table = Table(show_header=True, header_style="bold magenta")
        commands_table.add_column("Command", style="bold cyan", width=20)
        commands_table.add_column("Description", style="white", width=40)
        commands_table.add_column("Example", style="dim", width=30)

        # Core reasoning commands
        commands_table.add_row(
            "/reason <scenario>",
            "Execute complete MSA pipeline",
            "/reason 'Patient has fever and cough'",
        )
        commands_table.add_row(
            "/parse <text>",
            "Parse text and extract entities",
            "/parse 'The patient is 45 years old'",
        )
        commands_table.add_row(
            "/knowledge <query>",
            "Search knowledge base",
            "/knowledge --domain=medical fever",
        )
        commands_table.add_row(
            "/graph <entities>",
            "Build relationship graph",
            "/graph patient,symptoms,diagnosis",
        )
        commands_table.add_row(
            "/synthesis <spec>",
            "Generate probabilistic model",
            "/synthesis --framework=numpyro",
        )
        commands_table.add_row(
            "/inference <model>",
            "Run probabilistic inference",
            "/inference --samples=2000",
        )

        # Redis commands
        commands_table.add_section()
        commands_table.add_row(
            "/redis list", "List Redis keys", "/redis list --pattern=kb:*"
        )
        commands_table.add_row(
            "/redis get <key>", "Retrieve Redis data", "/redis get kb:medical_001"
        )
        commands_table.add_row(
            "/redis search <query>",
            "Vector similarity search",
            "/redis search 'respiratory symptoms'",
        )
        commands_table.add_row(
            "/redis stats", "Show Redis statistics", "/redis stats --domain=medical"
        )

        # Utility commands
        commands_table.add_section()
        commands_table.add_row(
            "/confidence <analysis>",
            "Show confidence metrics",
            "/confidence --breakdown",
        )
        commands_table.add_row(
            "/explain <operation>", "Explain reasoning steps", "/explain last_inference"
        )
        commands_table.add_row(
            "/debug <stage>", "Enable debugging", "/debug --level=trace synthesis"
        )
        commands_table.add_row("/status", "Show system status", "/status")
        commands_table.add_row(
            "/export <format>",
            "Export session data",
            "/export json --file=session.json",
        )
        commands_table.add_row("/clear", "Clear screen", "/clear")
        commands_table.add_row("/exit", "Exit REPL", "/exit")

        help_layout["commands"].update(
            Panel(commands_table, title="Available Commands")
        )

        # Footer
        footer_text = Text()
        footer_text.append("📖 Use ", style="dim")
        footer_text.append("/help <command>", style="bold cyan")
        footer_text.append(" for detailed help on specific commands", style="dim")

        footer = Panel(Align.center(footer_text), style="dim")
        help_layout["footer"].update(footer)

        self.console.print(help_layout)

    def show_error(self, message: str, details: Optional[str] = None):
        """Display error message with optional details"""
        error_text = Text()
        error_text.append("❌ ", style="bold red")
        error_text.append("Error: ", style="bold red")
        error_text.append(message, style="red")

        if details:
            error_content = Group(
                error_text,
                "",
                Text("Details:", style="bold yellow"),
                Text(details, style="dim"),
            )
        else:
            error_content = error_text

        panel = Panel(error_content, title="[bold red]Error", border_style="red")

        self.console.print(panel)

    def show_goodbye(self):
        """Display goodbye message"""
        goodbye_text = Text()
        goodbye_text.append("👋 ", style="bold blue")
        goodbye_text.append(
            "Thank you for using Reasoning Kernel REPL!", style="bold cyan"
        )

        panel = Panel(Align.center(goodbye_text), style="blue", padding=(1, 2))

        self.console.print()
        self.console.print(panel)
        self.console.print()

    # --- Enhanced UX helpers ---
    def stream_narrative(self, title: str, lines: List[str], speed: float = 0.03):
        """Stream a narrative with smooth, readable pacing."""
        header = Panel(Text(title, style="bold cyan"), border_style="cyan")
        self.console.print(header)
        for line in lines:
            self.console.print(Text(line))

    def show_confidence_meter(self, label: str, score: float, justification: str = ""):
        """Render a compact confidence meter and optional justification."""
        score = max(0.0, min(1.0, float(score)))
        bar_len = 20
        filled = int(bar_len * score)
        bar = (
            "[green]"
            + "█" * filled
            + "[/green]"
            + "[dim]"
            + "·" * (bar_len - filled)
            + "[/dim]"
        )
        tbl = Table(show_header=False, box=None)
        tbl.add_column("k", width=16)
        tbl.add_column("v")
        tbl.add_row("Confidence", f"{bar}  [bold]{score:.2f}[/bold]")
        if justification:
            tbl.add_row("Why", f"[dim]{justification}[/dim]")
        self.console.print(Panel(tbl, title=f"{label}", border_style="green"))

    def show_reasoning_tree(self, title: str, tree_spec: Dict[str, Any]):
        """Display an expandable reasoning tree from a nested dict structure.
        tree_spec: {"text": str, "children": [tree_spec, ...]}
        """

        def build(node):
            t = Tree(node.get("text", ""))
            for child in node.get("children", []) or []:
                t.add(build(child))
            return t

        root = build(tree_spec)
        self.console.print(Panel(root, title=title, border_style="magenta"))

    def show_evidence_map(self, hypotheses: List[Dict[str, Any]]):
        """Visualize mapping from evidence -> reasoning -> conclusion.
        hypotheses: [{"hypothesis": str, "evidence": [ ... ], "support": float, "notes": str}]
        """
        tbl = Table(show_header=True, header_style="bold magenta")
        tbl.add_column("Hypothesis", style="cyan", width=28)
        tbl.add_column("Evidence", style="white")
        tbl.add_column("Support", style="green", width=10)
        for h in hypotheses:
            ev = "\n".join([f"• {e}" for e in h.get("evidence", [])]) or "—"
            tbl.add_row(h.get("hypothesis", ""), ev, f"{h.get('support', 0.0):.2f}")
        self.console.print(Panel(tbl, title="Evidence Mapping", border_style="cyan"))

    def show_contextual_help(self, context: Dict[str, Any]):
        """Adaptive help based on current pipeline state and last result."""
        tips = []
        if context.get("last_command") == "/reason":
            tips.append("Try /explain last to see stage-by-stage narratives.")
            tips.append("Use /export json to save results.")
            tips.append("Run /confidence --breakdown for factor-level metrics.")
        if context.get("last_domain"):
            tips.append(
                f"Knowledge search: /knowledge '{context['last_domain']} query'"
            )
        tips = tips or ["Type /help for all commands", "Use Tab for completions"]
        body = "\n".join([f"• {t}" for t in tips])
        self.console.print(
            Panel(Text(body), title="Contextual Help", border_style="blue")
        )

    def show_replay_steps(self, steps: List[Dict[str, str]]):
        """Show a compact replay of reasoning steps with timestamps."""
        tbl = Table(show_header=True, header_style="bold magenta")
        tbl.add_column("Time", style="dim", width=10)
        tbl.add_column("Stage", style="cyan", width=16)
        tbl.add_column("Action", style="white")
        for s in steps:
            tbl.add_row(s.get("t", "—"), s.get("stage", "—"), s.get("text", ""))
        self.console.print(Panel(tbl, title="Reasoning Replay", border_style="yellow"))
