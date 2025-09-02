"""
CLI module for the Reasoning Kernel.

Lightweight package init that avoids importing heavy optional modules at import time.
This keeps the CLI entrypoints working even if optional integrations aren't installed.
"""

# Optional imports: keep failures non-fatal to allow core CLI to work
try:  # commands are lightweight and safe
    from .commands import CommandRegistry  # type: ignore
except Exception:  # pragma: no cover - optional during minimal CLI operation
    CommandRegistry = None  # type: ignore

try:  # REPL may depend on optional integrations
    from .repl import ReasoningREPL  # type: ignore
except Exception:  # pragma: no cover - optional during minimal CLI operation
    ReasoningREPL = None  # type: ignore

try:  # UI is optional for headless usage
    from .ui import REPLInterface  # type: ignore
except Exception:  # pragma: no cover - optional during minimal CLI operation
    REPLInterface = None  # type: ignore

__all__ = ["ReasoningREPL", "CommandRegistry", "REPLInterface"]
