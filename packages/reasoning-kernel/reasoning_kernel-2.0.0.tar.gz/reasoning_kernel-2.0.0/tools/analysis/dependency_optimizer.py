#!/usr/bin/env python3
"""
Deprecated entrypoint for dependency optimizer.
This script has moved to tools/optimize_dependencies.py
Use: python tools/optimize_dependencies.py
"""
from pathlib import Path
import sys
import runpy

if __name__ == "__main__":
    print("[DEPRECATED] This script has been renamed.")
    print("Please use: python tools/optimize_dependencies.py")
    print("Redirecting to the new script...\n")

    target = Path(__file__).parent / "optimize_dependencies.py"

    # Check if the target script exists
    if not target.exists():
        print(f"ERROR: Target script not found at {target}")
        print("Please ensure 'optimize_dependencies.py' exists in the tools directory.")
        sys.exit(1)

    # Validate that the target is the expected file in the expected directory
    expected_name = "optimize_dependencies.py"
    expected_dir = Path(__file__).parent.resolve()
    if target.name != expected_name or target.parent.resolve() != expected_dir:
        print("ERROR: Invalid target script path detected.")
        sys.exit(1)

    # Run the new script with the same arguments
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")
