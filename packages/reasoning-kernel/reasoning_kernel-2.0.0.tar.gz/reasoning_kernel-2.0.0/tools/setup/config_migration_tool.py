#!/usr/bin/env python3
"""
Configuration Migration Tool
===========================

Tool to migrate the existing codebase to use the new unified configuration system.
Analyzes the codebase for scattered configuration usage and provides migration guidance.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json
import argparse


class ConfigMigrationAnalyzer:
    """Analyzes codebase for configuration usage patterns that need migration"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.pattern_findings: Dict[str, List[Tuple[str, int, str]]] = {}

        # Patterns to find scattered configuration usage
        self.patterns = {
            "os_getenv": r'os\.getenv\(["\']([^"\']+)["\'](?:,\s*["\']?([^"\']*)["\']?)?\)',
            "os_environ": r'os\.environ(?:\.get)?\[["\']([^"\']+)["\']\]',
            "settings_access": r"settings\.(\w+)",
            "direct_env": r'["\']([A-Z_][A-Z0-9_]*)["\'].*(?:getenv|environ)',
            "hardcoded_config": r'(host|port|timeout|url|key|secret)\s*=\s*["\']([^"\']+)["\']',
        }

        # File extensions to analyze
        self.extensions = {".py"}

        # Directories to skip
        self.skip_dirs = {".venv", "__pycache__", ".git", "node_modules", ".pytest_cache"}

    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the entire codebase for migration opportunities"""
        print(f"🔍 Analyzing codebase at: {self.root_path}")

        # Scan all Python files
        python_files = self._find_python_files()
        print(f"📁 Found {len(python_files)} Python files to analyze")

        # Analyze each file
        for file_path in python_files:
            self._analyze_file(file_path)

        # Generate migration report
        migration_report = self._generate_migration_report()

        return migration_report

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the codebase"""
        python_files = []

        for root, dirs, files in os.walk(self.root_path):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]

            for file in files:
                if any(file.endswith(ext) for ext in self.extensions):
                    python_files.append(Path(root) / file)

        return python_files

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single file for configuration patterns"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\\n")

            # Check each pattern
            for pattern_name, pattern_regex in self.patterns.items():
                matches = re.finditer(pattern_regex, content, re.IGNORECASE)

                for match in matches:
                    # Find line number
                    line_start = content[: match.start()].count("\\n") + 1
                    line_content = lines[line_start - 1].strip()

                    # Store finding
                    if pattern_name not in self.pattern_findings:
                        self.pattern_findings[pattern_name] = []

                    self.pattern_findings[pattern_name].append(
                        (str(file_path.relative_to(self.root_path)), line_start, line_content)
                    )

        except Exception as e:
            print(f"⚠️ Error analyzing {file_path}: {e}")

    def _generate_migration_report(self) -> Dict[str, Any]:
        """Generate comprehensive migration report"""
        total_findings = sum(len(findings) for findings in self.pattern_findings.values())

        report = {
            "summary": {
                "total_files_analyzed": len(self._find_python_files()),
                "total_configuration_references": total_findings,
                "patterns_found": len(self.pattern_findings),
                "migration_priority": self._calculate_migration_priority(),
            },
            "detailed_findings": {},
            "migration_recommendations": self._generate_recommendations(),
            "configuration_inventory": self._inventory_configurations(),
        }

        # Add detailed findings
        for pattern_name, findings in self.pattern_findings.items():
            report["detailed_findings"][pattern_name] = {
                "count": len(findings),
                "description": self._get_pattern_description(pattern_name),
                "locations": [
                    {"file": file_path, "line": line_number, "code": code_line}
                    for file_path, line_number, code_line in findings[:10]  # Limit to first 10
                ],
            }

        return report

    def _calculate_migration_priority(self) -> str:
        """Calculate migration priority based on findings"""
        total_findings = sum(len(findings) for findings in self.pattern_findings.values())

        if total_findings > 100:
            return "HIGH - Many scattered configuration references found"
        elif total_findings > 50:
            return "MEDIUM - Moderate configuration consolidation needed"
        elif total_findings > 10:
            return "LOW - Some configuration cleanup opportunities"
        else:
            return "MINIMAL - Configuration already well-organized"

    def _get_pattern_description(self, pattern_name: str) -> str:
        """Get human-readable description of configuration pattern"""
        descriptions = {
            "os_getenv": "Direct os.getenv() calls that should use config system",
            "os_environ": "Direct os.environ access that should be centralized",
            "settings_access": "Settings object access that may need updating",
            "direct_env": "Environment variable references to review",
            "hardcoded_config": "Hardcoded configuration values to centralize",
        }
        return descriptions.get(pattern_name, "Configuration pattern to review")

    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate specific migration recommendations"""
        recommendations = []

        # Add recommendations based on findings
        if "os_getenv" in self.pattern_findings:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Environment Variables",
                    "title": "Migrate os.getenv() calls to configuration system",
                    "description": f"Found {len(self.pattern_findings['os_getenv'])} direct os.getenv() calls",
                    "action": "Replace with get_config().{section}.{field} or environment-specific configs",
                }
            )

        if "hardcoded_config" in self.pattern_findings:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Hardcoded Values",
                    "title": "Move hardcoded configuration to config system",
                    "description": f"Found {len(self.pattern_findings['hardcoded_config'])} hardcoded config values",
                    "action": "Move values to ApplicationConfig models and environment files",
                }
            )

        if "settings_access" in self.pattern_findings:
            recommendations.append(
                {
                    "priority": "LOW",
                    "category": "Settings Migration",
                    "title": "Update settings object usage",
                    "description": f"Found {len(self.pattern_findings['settings_access'])} settings access patterns",
                    "action": "Review settings usage and migrate to new config structure if needed",
                }
            )

        return recommendations

    def _inventory_configurations(self) -> Dict[str, List[str]]:
        """Create inventory of configuration keys found"""
        inventory = {"environment_variables": set(), "configuration_keys": set(), "potential_secrets": set()}

        # Extract environment variable names
        for pattern_name, findings in self.pattern_findings.items():
            if pattern_name in ["os_getenv", "os_environ"]:
                for _, _, code_line in findings:
                    # Extract variable names from code
                    matches = re.findall(r'["\']([A-Z_][A-Z0-9_]*)["\']', code_line)
                    for match in matches:
                        inventory["environment_variables"].add(match)

                        # Check if potentially sensitive
                        if any(
                            keyword in match.lower() for keyword in ["key", "secret", "password", "token", "credential"]
                        ):
                            inventory["potential_secrets"].add(match)

        # Convert sets to lists for JSON serialization
        return {k: list(v) for k, v in inventory.items()}


class ConfigMigrationTool:
    """Main migration tool for configuration system"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.analyzer = ConfigMigrationAnalyzer(root_path)

    def run_analysis(self, output_file: str | None = None) -> None:
        """Run migration analysis and generate report"""
        print("🚀 Starting Configuration Migration Analysis")
        print("=" * 50)

        # Run analysis
        report = self.analyzer.analyze_codebase()

        # Display summary
        self._display_summary(report)

        # Display detailed findings
        self._display_findings(report)

        # Display recommendations
        self._display_recommendations(report)

        # Save report to file
        if output_file:
            self._save_report(report, output_file)
            print(f"\\n📄 Detailed report saved to: {output_file}")

        print("\\n✅ Configuration migration analysis complete!")

    def _display_summary(self, report: Dict) -> None:
        """Display analysis summary"""
        summary = report["summary"]

        print("📊 Analysis Summary:")
        print(f"   Files analyzed: {summary['total_files_analyzed']}")
        print(f"   Configuration references: {summary['total_configuration_references']}")
        print(f"   Migration priority: {summary['migration_priority']}")
        print()

    def _display_findings(self, report: Dict) -> None:
        """Display detailed findings"""
        print("🔍 Configuration Patterns Found:")

        for pattern_name, pattern_data in report["detailed_findings"].items():
            print(f"\\n   {pattern_name}: {pattern_data['count']} occurrences")
            print(f"      {pattern_data['description']}")

            if pattern_data["locations"]:
                print("      Sample locations:")
                for loc in pattern_data["locations"][:3]:  # Show first 3
                    print(f"        📁 {loc['file']}:{loc['line']} - {loc['code'][:80]}...")

    def _display_recommendations(self, report: Dict) -> None:
        """Display migration recommendations"""
        print("\\n💡 Migration Recommendations:")

        for rec in report["migration_recommendations"]:
            print(f"\\n   [{rec['priority']}] {rec['title']}")
            print(f"      Category: {rec['category']}")
            print(f"      {rec['description']}")
            print(f"      Action: {rec['action']}")

    def _save_report(self, report: Dict, output_file: str) -> None:
        """Save detailed report to JSON file"""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ Error saving report: {e}")

    def generate_migration_guide(self, output_file: str = "CONFIGURATION_MIGRATION_GUIDE.md") -> None:
        """Generate markdown migration guide"""
        guide_content = self._create_migration_guide()

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(guide_content)
            print(f"📚 Migration guide generated: {output_file}")
        except Exception as e:
            print(f"⚠️ Error generating guide: {e}")

    def _create_migration_guide(self) -> str:
        """Create markdown migration guide content"""
        return """# Configuration System Migration Guide

## Overview

This guide helps migrate from scattered configuration usage to the unified configuration management system.

## Migration Steps

### 1. Update Environment Variable Access

**Before:**
```python
import os
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
```

**After:**
```python
from reasoning_kernel.core.config_manager import get_redis_config

redis_config = get_redis_config()
redis_host = redis_config.host
redis_port = redis_config.port
```

### 2. Replace Direct Settings Access

**Before:**
```python
from reasoning_kernel.core.config import settings
if settings.debug:
    print("Debug mode enabled")
```

**After:**
```python
from reasoning_kernel.core.config_manager import get_config, is_debug_enabled

if is_debug_enabled():
    print("Debug mode enabled")
```

### 3. Use Environment-Specific Configuration

**Before:**
```python
# Scattered environment checks
if os.getenv("ENVIRONMENT") == "production":
    timeout = 60
else:
    timeout = 30
```

**After:**
```python
from reasoning_kernel.core.config_manager import get_config

config = get_config()
if config.is_production():
    timeout = config.msa.reasoning_timeout
else:
    timeout = config.msa.reasoning_timeout
```

### 4. Migrate Hardcoded Values

**Before:**
```python
# Hardcoded configuration
REDIS_TTL = 3600
MAX_RETRIES = 3
```

**After:**
```python
from reasoning_kernel.core.config_manager import get_redis_config, get_config

redis_config = get_redis_config()
REDIS_TTL = redis_config.ttl_seconds

config = get_config()
MAX_RETRIES = config.azure_openai.max_retries
```

### 5. Update Service Initialization

**Before:**
```python
redis_client = Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    password=os.getenv("REDIS_PASSWORD")
)
```

**After:**
```python
from reasoning_kernel.core.config_manager import get_redis_config

redis_config = get_redis_config()
redis_client = Redis(
    host=redis_config.host,
    port=redis_config.port,
    password=redis_config.password,
    ssl=redis_config.ssl
)
```

## Configuration Sections

| Section | Purpose | Access Function |
|---------|---------|-----------------|
| `redis` | Redis configuration | `get_redis_config()` |
| `azure_openai` / `openai` | OpenAI settings | `get_openai_config()` |
| `msa` | MSA engine settings | `get_msa_config()` |
| `security` | Security configuration | `get_config().security` |
| `monitoring` | Logging/monitoring | `get_config().monitoring` |

## Environment Files

Create environment-specific configuration files:

- `.env.development` - Development settings
- `.env.production` - Production settings  
- `.env.test` - Testing settings

## Migration Checklist

- [ ] Replace `os.getenv()` calls with config system
- [ ] Move hardcoded values to configuration models
- [ ] Update service initialization to use config objects
- [ ] Create environment-specific config files
- [ ] Test configuration loading in each environment
- [ ] Update documentation for new config usage
- [ ] Remove deprecated configuration patterns

## Benefits After Migration

- **Centralized Configuration**: All settings in one place
- **Type Safety**: Pydantic validation ensures correct types
- **Environment Awareness**: Easy environment-specific overrides
- **Documentation**: Self-documenting configuration schema
- **Security**: Integrated credential management
- **Hot Reload**: Development environment config changes

## Need Help?

Refer to the configuration manager documentation or run the migration analysis tool for specific guidance.
"""


def main():
    """Main entry point for migration tool"""
    parser = argparse.ArgumentParser(description="Configuration Migration Analysis Tool")
    parser.add_argument("--root-path", type=str, default=".", help="Root path of the codebase to analyze")
    parser.add_argument("--output", type=str, help="Output file for detailed JSON report")
    parser.add_argument("--generate-guide", action="store_true", help="Generate migration guide markdown file")

    args = parser.parse_args()

    # Initialize migration tool
    root_path = Path(args.root_path).resolve()
    migration_tool = ConfigMigrationTool(root_path)

    # Run analysis
    migration_tool.run_analysis(args.output)

    # Generate guide if requested
    if args.generate_guide:
        migration_tool.generate_migration_guide()


if __name__ == "__main__":
    main()
