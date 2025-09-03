# Tools

Utility scripts for repository maintenance and analysis.

## Overview

- dependency_optimizer.py: Analyze and propose optimized dependency groups and versions.
- security_scanner.py: Generate a dependency security report (uses optional tools if installed).
- repository_cleanup.py: Plan and optionally execute repository cleanup (safe by default, dry run).
- examples_cleanup_tool.py: Apply basic non-destructive formatting fixes under examples/.
- setup_daytona.py: Minimal helper for creating a Daytona sandbox (requires DAYTONA_API_KEY).
- test_cleanup_tool.py: Targeted cleanup for integration-style test files and summary report.

## Usage

- Run scripts from anywhere; each script resolves the project root relative to its own location.
- Most scripts are designed to be safe-by-default (dry runs or report generation).

## Examples

- Dependency analysis: python tools/dependency_optimizer.py
- Security scan: python tools/security_scanner.py
- Repo cleanup (dry run): python tools/repository_cleanup.py
- Repo cleanup (execute): python tools/repository_cleanup.py --execute
- Examples formatting pass: python tools/examples_cleanup_tool.py

## Notes

- Some scanners (pip-audit, safety) are optional; install them to enable deeper checks.
- repository_cleanup.py only removes files when run with --execute and explicit confirmation.
