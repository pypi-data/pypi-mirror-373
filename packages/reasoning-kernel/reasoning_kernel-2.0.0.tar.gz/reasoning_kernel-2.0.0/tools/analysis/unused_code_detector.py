#!/usr/bin/env python3
"""
Unused Code and Old Files Detector
=================================

Comprehensive tool to detect unused code, duplicate files, and old artifacts
in the Reasoning Kernel codebase. This tool combines multiple detection methods:

1. Vulture for dead Python code detection
2. File system analysis for duplicates and old files
3. Import dependency analysis
4. Pattern-based detection of unused patterns

Based on spec/spec-process-codebase-reorganization.md recommendations.
"""

import ast
import json
import re
import subprocess
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import vulture
except ImportError:
    print("⚠️ vulture not available - installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "vulture"])
    print("⚠️ vulture not available. Attempting to install vulture via pip...")
    print("   Note: You may need administrator/root privileges, and an active internet connection.")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "vulture"])
        import vulture
    except Exception as e:
        print("❌ Failed to install vulture automatically.")
        print("   Possible reasons: insufficient permissions, network issues, or pip misconfiguration.")
        print("   Please try installing vulture manually with:")
        print("       pip install vulture")
        print(f"   Error details: {e}")
        sys.exit(1)


class UnusedCodeDetector:
    """Main class for detecting unused code and old files"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.findings = {
            "duplicate_files": [],
            "dead_code": [],
            "old_files": [],
            "security_risks": [],
            "test_artifacts": [],
            "temporary_files": [],
            "unused_imports": [],
            "unreferenced_functions": [],
        }
        
        # Categories from TASKS.md
        self.files_to_remove = {
            "Security Risks": [
                "fix_secrets.sh",
                ".env.backup", 
                "create_clean_main.sh",
            ],
            
            "Redundant Components": [
                "reasoning_kernel/services/production_redis_manager.py",  # Should consolidate
            ],
            
            "Test Artifacts": [
                "test_*.py",  # Root level test files
                "validate_*.py",  # Validation scripts in root
                "verify_*.py",  # Verification scripts in root
            ],
            
            "Temporary Files": [
                "*.backup",
                "*.tmp", 
                "*.log",
                "__pycache__/",
            ]
        }

    def analyze_codebase(self) -> Dict[str, Any]:
        """Run comprehensive analysis of the codebase"""
        print("🔍 Starting comprehensive unused code analysis...")
        print(f"📁 Root path: {self.root_path}")
        
        # Step 1: Find duplicate files
        self._find_duplicate_files()
        
        # Step 2: Find security risk files
        self._find_security_risk_files()
        
        # Step 3: Find temporary and backup files
        self._find_temporary_files()
        
        # Step 4: Find test artifacts in wrong locations
        self._find_misplaced_test_files()
        
        # Step 5: Run vulture for dead code detection
        self._run_vulture_analysis()
        
        # Step 6: Analyze import dependencies
        self._analyze_unused_imports()
        
        # Step 7: Find old/stale files
        self._find_old_files()
        
        # Step 8: Deduplicate findings
        self._deduplicate_findings()
        
        # Generate comprehensive report
        return self._generate_report()
    
    def _deduplicate_findings(self):
        """Remove duplicate findings from all categories"""
        for category in self.findings:
            if isinstance(self.findings[category], list):
                seen = set()
                unique_findings = []
                
                for finding in self.findings[category]:
                    # Create a unique key based on the finding content
                    if isinstance(finding, dict):
                        # Use the file path as the primary key for deduplication
                        key = finding.get("file", str(finding))
                    else:
                        key = str(finding)
                    
                    if key not in seen:
                        seen.add(key)
                        unique_findings.append(finding)
                
                self.findings[category] = unique_findings

    def _find_duplicate_files(self):
        """Find files with 'copy' or duplicate patterns in their names"""
        print("\n🔍 Scanning for duplicate files...")
        
        duplicate_patterns = [
            r".*copy.*\.(py|md|txt|sh|lock|in)$",
            r".*backup.*\.(py|md|txt|sh)$", 
            r".*old.*\.(py|md|txt|sh)$",
            r".*temp.*\.(py|md|txt|sh)$",
        ]
        
        for pattern in duplicate_patterns:
            for file_path in self.root_path.rglob("*"):
                if file_path.is_file() and re.match(pattern, file_path.name, re.IGNORECASE):
                    # Check if there's a corresponding original file
                    original_name = self._get_original_filename(file_path.name)
                    original_path = file_path.parent / original_name
                    
                    self.findings["duplicate_files"].append({
                        "duplicate_file": str(file_path.relative_to(self.root_path)),
                        "original_exists": original_path.exists(),
                        "original_file": str(original_path.relative_to(self.root_path)) if original_path.exists() else None,
                        "size_bytes": file_path.stat().st_size,
                        "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    })

    def _get_original_filename(self, duplicate_name: str) -> str:
        """Get the likely original filename from a duplicate"""
        # Remove common duplicate patterns
        patterns_to_remove = [
            r"\s*copy\s*",
            r"\s*backup\s*", 
            r"\s*old\s*",
            r"\s*temp\s*",
            r"\s*\(\d+\)\s*",
        ]
        
        original = duplicate_name
        for pattern in patterns_to_remove:
            original = re.sub(pattern, "", original, flags=re.IGNORECASE)
        
        # Clean up any double extensions or spaces
        original = re.sub(r"\s+", " ", original).strip()
        
        return original

    def _find_security_risk_files(self):
        """Find files that pose security risks as identified in TASKS.md"""
        print("\n🔍 Scanning for security risk files...")
        
        security_patterns = [
            "fix_secrets.sh",
            ".env.backup",
            "create_clean_main.sh",
            "*.env.backup",
            "*secrets*",
            "*password*", 
        ]
        
        for pattern in security_patterns:
            for file_path in self.root_path.rglob(pattern):
                if file_path.is_file():
                    # Read first few lines to assess risk
                    risk_level = "MEDIUM"
                    content_preview = ""
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()[:5]
                            content_preview = ''.join(lines)
                            
                            # Check for high-risk patterns
                            high_risk_patterns = [
                                r"password\s*=",
                                r"secret\s*=", 
                                r"api_key\s*=",
                                r"token\s*=",
                                r"credential",
                            ]
                            
                            for risk_pattern in high_risk_patterns:
                                if re.search(risk_pattern, content_preview, re.IGNORECASE):
                                    risk_level = "HIGH"
                                    break
                                    
                    except Exception:
                        content_preview = "[Unable to read file]"
                    
                    self.findings["security_risks"].append({
                        "file": str(file_path.relative_to(self.root_path)),
                        "risk_level": risk_level,
                        "reason": "Contains potential credentials or secrets",
                        "content_preview": content_preview[:200] + "..." if len(content_preview) > 200 else content_preview,
                        "size_bytes": file_path.stat().st_size,
                    })

    def _find_temporary_files(self):
        """Find temporary and backup files"""
        print("\n🔍 Scanning for temporary files...")
        
        temp_patterns = [
            "*.tmp",
            "*.log", 
            "*.backup",
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".pytest_cache",
            ".coverage",
            "*.orig",
            "*.swp",
            "*~",
        ]
        
        for pattern in temp_patterns:
            for file_path in self.root_path.rglob(pattern):
                if file_path.is_file() or (file_path.is_dir() and pattern == "__pycache__"):
                    self.findings["temporary_files"].append({
                        "file": str(file_path.relative_to(self.root_path)),
                        "type": "directory" if file_path.is_dir() else "file", 
                        "pattern": pattern,
                        "size_bytes": self._get_dir_size(file_path) if file_path.is_dir() else file_path.stat().st_size,
                    })

    def _find_misplaced_test_files(self):
        """Find test files that are in the wrong location (should be in tests/)"""
        print("\n🔍 Scanning for misplaced test files...")
        
        test_patterns = [
            "test_*.py",
            "validate_*.py", 
            "verify_*.py",
            "*_test.py",
        ]
        
        for pattern in test_patterns:
            for file_path in self.root_path.rglob(pattern):
                # Skip if already in tests/ directory or subdirectories
                if "tests" in file_path.parts:
                    continue
                    
                if file_path.is_file() and file_path.suffix == ".py":
                    self.findings["test_artifacts"].append({
                        "file": str(file_path.relative_to(self.root_path)),
                        "reason": "Test file in wrong location (should be in tests/)",
                        "suggested_location": f"tests/{file_path.name}",
                        "size_bytes": file_path.stat().st_size,
                    })

    def _run_vulture_analysis(self):
        """Use vulture to detect dead Python code"""
        print("\n🔍 Running vulture dead code analysis...")
        
        try:
            # Create vulture instance with increased recursion limit
            vul = vulture.Vulture()
            
            # Find all Python files in the project, but exclude large directories and venv
            python_files = []
            exclude_patterns = [
                "__pycache__",
                ".venv",
                ".pytest_cache",
                "site-packages",
                "dist",
                "build"
            ]
            
            for file_path in self.root_path.rglob("*.py"):
                if any(pattern in str(file_path) for pattern in exclude_patterns):
                    continue
                python_files.append(file_path)
            
            if not python_files:
                print("⚠️ No Python files found for analysis")
                return
                
            print(f"📊 Analyzing {len(python_files)} Python files...")
            
            # Process files in batches to avoid recursion issues
            batch_size = 50
            for i in range(0, len(python_files), batch_size):
                batch = python_files[i:i + batch_size]
                file_strings = [str(f) for f in batch]
                
                try:
                    # Run vulture on batch
                    vul.scavenge(file_strings)
                except RecursionError:
                    print(f"⚠️ Recursion error processing batch {i//batch_size + 1}, skipping...")
                    continue
                except Exception as e:
                    print(f"⚠️ Error processing batch {i//batch_size + 1}: {e}")
                    continue
            
            # Process results - handle different vulture versions
            try:
                unused_items = vul.get_unused_code()
            except AttributeError:
                # Older vulture versions might use different API
                unused_items = getattr(vul, 'unused_code', [])
            
            for item in unused_items:
                try:
                    # Handle different attribute names across vulture versions
                    line_no = getattr(item, 'lineno', getattr(item, 'line', 'unknown'))
                    file_name = getattr(item, 'filename', getattr(item, 'file', 'unknown'))
                    confidence = getattr(item, 'confidence', 60)
                    item_type = getattr(item, 'typ', getattr(item, 'type', 'unknown'))
                    name = getattr(item, 'name', 'unknown')
                    
                    self.findings["dead_code"].append({
                        "file": str(Path(file_name).relative_to(self.root_path)) if file_name != 'unknown' else "unknown",
                        "name": name,
                        "type": item_type,
                        "line": line_no,
                        "confidence": confidence,
                        "message": f"Unused {item_type}: {name}",
                    })
                except Exception:
                    # If we can't process an individual item, skip it
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error running vulture analysis: {e}")
            traceback.print_exc()
            # Don't add error to dead_code findings

    def _analyze_unused_imports(self):
        """Analyze Python files for unused imports"""
        print("\n🔍 Analyzing unused imports...")
        
        python_files = list(self.root_path.rglob("*.py"))
        
        for py_file in python_files:
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST
                tree = ast.parse(content)
                
                # Find imports
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            for alias in node.names:
                                imports.append(f"{node.module}.{alias.name}")
                
                # Simple check: look for imports that don't appear in the rest of the code
                unused_imports = []
                for imp in imports:
                    # Simple heuristic - check if import name appears elsewhere
                    base_name = imp.split('.')[-1]
                imported_names = set()
                import_statements = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                            imported_names.add(alias.asname if alias.asname else alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            for alias in node.names:
                                full_name = f"{node.module}.{alias.name}"
                                imports.append(full_name)
                                imported_names.add(alias.asname if alias.asname else alias.name)
                imported_names = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                            imported_names.append(alias.asname if alias.asname else alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            for alias in node.names:
                                imports.append(f"{node.module}.{alias.name}")
                                imported_names.append(alias.asname if alias.asname else alias.name)
                
                # Collect all used names in the code
                used_names = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name):
                        used_names.add(node.id)
                
                # Find unused imports by comparing imported names to used names
                unused_imports = []
                for imp, name in import_pairs:
                    if name not in used_names:
                        unused_imports.append(imp)
                
                if unused_imports:
                    self.findings["unused_imports"].append({
                        "file": str(py_file.relative_to(self.root_path)),
                        "unused_imports": unused_imports,
                    })
                    
            except Exception:
                # Skip files that can't be parsed
                continue

    def _find_old_files(self):
        """Find files that haven't been modified in a long time"""
        print("\n🔍 Scanning for old files...")
        
        # Consider files old if not modified in the last 6 months
        cutoff_date = datetime.now() - timedelta(days=180)
        
        for file_path in self.root_path.rglob("*"):
            if file_path.is_file():
                # Skip git files and some common patterns
                if any(part.startswith('.git') for part in file_path.parts):
                    continue
                    
                modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if modified_time < cutoff_date:
                    # Only flag as old if it's a code file or documentation
                    if file_path.suffix in ['.py', '.md', '.txt', '.sh', '.yml', '.yaml', '.json']:
                        self.findings["old_files"].append({
                            "file": str(file_path.relative_to(self.root_path)),
                            "last_modified": modified_time.isoformat(),
                            "age_days": (datetime.now() - modified_time).days,
                            "size_bytes": file_path.stat().st_size,
                        })

    def _get_dir_size(self, directory: Path) -> int:
        """Calculate total size of directory"""
        total = 0
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total += file_path.stat().st_size
        except (OSError, PermissionError):
            pass
        return total

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        print("\n📊 Generating analysis report...")
        
        total_findings = sum(len(category) for category in self.findings.values())
        
        # Calculate file sizes
        duplicate_size = sum(item.get("size_bytes", 0) for item in self.findings["duplicate_files"])
        temp_size = sum(item.get("size_bytes", 0) for item in self.findings["temporary_files"])
        
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "root_path": str(self.root_path),
            "summary": {
                "total_findings": total_findings,
                "duplicate_files": len(self.findings["duplicate_files"]),
                "dead_code_items": len(self.findings["dead_code"]),
                "security_risks": len(self.findings["security_risks"]),
                "test_artifacts": len(self.findings["test_artifacts"]),
                "temporary_files": len(self.findings["temporary_files"]),
                "old_files": len(self.findings["old_files"]),
                "unused_imports": len(self.findings["unused_imports"]),
                "potential_space_savings_bytes": duplicate_size + temp_size,
                "potential_space_savings_mb": round((duplicate_size + temp_size) / 1024 / 1024, 2),
            },
            "findings": self.findings,
            "recommendations": self._generate_recommendations(),
        }
        
        return report

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on findings"""
        recommendations = []
        
        if self.findings["duplicate_files"]:
            recommendations.append({
                "category": "Duplicate Files",
                "priority": "HIGH",
                "action": "Review and remove duplicate files",
                "files": [item["duplicate_file"] for item in self.findings["duplicate_files"]],
                "description": "These files appear to be duplicates and can likely be safely removed after verification.",
            })
        
        if self.findings["security_risks"]:
            high_risk = [item for item in self.findings["security_risks"] if item["risk_level"] == "HIGH"]
            if high_risk:
                recommendations.append({
                    "category": "Security Risks", 
                    "priority": "CRITICAL",
                    "action": "Immediately review and secure or remove files containing credentials",
                    "files": [item["file"] for item in high_risk],
                    "description": "These files may contain credentials or secrets and pose security risks.",
                })
        
        if self.findings["test_artifacts"]:
            recommendations.append({
                "category": "Misplaced Test Files",
                "priority": "MEDIUM", 
                "action": "Move test files to tests/ directory",
                "files": [item["file"] for item in self.findings["test_artifacts"]],
                "description": "These test files should be moved to the tests/ directory for better organization.",
            })
        
        if self.findings["temporary_files"]:
            recommendations.append({
                "category": "Temporary Files",
                "priority": "LOW",
                "action": "Clean up temporary and cache files",
                "files": [item["file"] for item in self.findings["temporary_files"]],
                "description": "These temporary files can be safely removed to free up space.",
            })
        
        return recommendations

    def save_report(self, output_path: Optional[Path] = None) -> Path:
        """Save analysis report to file"""
        if output_path is None:
            output_path = self.root_path / "unused_code_analysis_report.json"
        
        report = self.analyze_codebase()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Report saved to: {output_path}")
        return output_path

    def print_summary(self, report: Dict[str, Any]):
        """Print a human-readable summary of findings"""
        print("\n" + "="*80)
        print("📊 UNUSED CODE ANALYSIS SUMMARY")
        print("="*80)
        
        summary = report["summary"]
        print("\n📈 Analysis Results:")
        print(f"  🔍 Total Findings: {summary['total_findings']}")
        print(f"  📁 Duplicate Files: {summary['duplicate_files']}")
        print(f"  💀 Dead Code Items: {summary['dead_code_items']}")
        print(f"  🔒 Security Risks: {summary['security_risks']}")
        print(f"  🧪 Misplaced Tests: {summary['test_artifacts']}")
        print(f"  🗑️  Temporary Files: {summary['temporary_files']}")
        print(f"  📅 Old Files: {summary['old_files']}")
        print(f"  📦 Files with Unused Imports: {summary['unused_imports']}")
        print(f"  💾 Potential Space Savings: {summary['potential_space_savings_mb']} MB")
        
        print("\n🎯 Priority Recommendations:")
        for rec in report["recommendations"]:
            priority_emoji = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "📝", "LOW": "ℹ️"}
            emoji = priority_emoji.get(rec["priority"], "📝")
            print(f"  {emoji} {rec['priority']}: {rec['action']} ({len(rec['files'])} files)")

    def cleanup_safe_files(self, dry_run: bool = True) -> List[str]:
        """Safely remove files that are definitely safe to remove"""
        removed_files = []
        
        if dry_run:
            print("\n🧪 DRY RUN MODE - No files will actually be removed")
        
        # Safe categories to auto-remove
        safe_categories = ["temporary_files"]
        
        for category in safe_categories:
            for item in self.findings[category]:
                file_path = self.root_path / item["file"]
                
                if file_path.exists():
                    if dry_run:
                        print(f"Would remove: {item['file']}")
                        removed_files.append(item["file"])
                    else:
                        try:
                            if file_path.is_dir():
                                import shutil
                                shutil.rmtree(file_path)
                            else:
                                file_path.unlink()
                            
                            print(f"✅ Removed: {item['file']}")
                            removed_files.append(item["file"])
                        except Exception as e:
                            print(f"❌ Failed to remove {item['file']}: {e}")
        
        return removed_files


def main():
    """Main entry point for the unused code detector"""
    print("Unused Code and Old Files Detector")
    print("=" * 40)
    
    # Get root path
    if len(sys.argv) > 1:
        root_path = Path(sys.argv[1]).resolve()
    else:
        root_path = Path.cwd()
    
    print(f"Analyzing: {root_path}")
    
    # Create detector
    detector = UnusedCodeDetector(root_path)
    
    # Run analysis
    report = detector.analyze_codebase()
    
    # Print summary
    detector.print_summary(report)
    
    # Save full report
    report_path = detector.save_report()
    
    # Optionally clean up safe files
    import argparse
    parser = argparse.ArgumentParser(description='Detect unused code and old files')
    parser.add_argument('--cleanup', action='store_true', help='Actually remove safe files (default is dry-run)')
    parser.add_argument('path', nargs='?', default='.', help='Path to analyze')
    
    if '--cleanup' in sys.argv:
        detector.cleanup_safe_files(dry_run=False)
    else:
        detector.cleanup_safe_files(dry_run=True)


if __name__ == "__main__":
    main()