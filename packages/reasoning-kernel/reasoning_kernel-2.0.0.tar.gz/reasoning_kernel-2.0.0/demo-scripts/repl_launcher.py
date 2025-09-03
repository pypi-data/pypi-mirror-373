#!/usr/bin/env python3
"""
Reasoning Kernel Interactive REPL Launcher

Launch the comprehensive interactive REPL for exploring and debugging
the MSA pipeline with Redis Cloud integration.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reasoning_kernel.cli.repl import main

if __name__ == "__main__":
    main()
