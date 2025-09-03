#!/usr/bin/env python3
"""
Safe Cleanup Tool for Removing Old and Duplicate Files
=====================================================

This tool safely removes files that are clearly duplicates or outdated
based on the analysis from unused_code_detector.py. It follows the
recommendations from TASKS.md and the codebase reorganization spec.
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class SafeFileCleanup:
    """Tool for safely cleaning up identified old and duplicate files"""
    
    def __init__(self, root_path: Path, report_path: Path = None):
        self.root_path = root_path
        self.report_path = report_path or root_path / "unused_code_analysis_report.json"
        self.report_data = None
        
        # Files that are definitely safe to remove based on TASKS.md
        self.safe_to_remove_patterns = [
            "* copy.*",  # Files with "copy" in name that have originals
            "*.backup",
            "*.tmp",
            "__pycache__/",
            ".pytest_cache/",
            "*.pyc",
            "*.pyo",
        ]

    def load_report(self) -> bool:
        """Load the analysis report"""
        try:
            with open(self.report_path, 'r') as f:
                self.report_data = json.load(f)
            return True
        except Exception as e:
            print(f"❌ Error loading report: {e}")
            return False

    def get_safe_duplicate_files(self) -> List[Dict[str, Any]]:
        """Get duplicate files that are safe to remove"""
        safe_files = []
        
        if not self.report_data:
            return safe_files
            
        for duplicate in self.report_data["findings"]["duplicate_files"]:
            # Safe to remove if original exists
            if duplicate.get("original_exists", False):
                safe_files.append(duplicate)
        
        return safe_files

    def get_misplaced_test_files(self) -> List[Dict[str, Any]]:
        """Get test files that should be moved to tests/ directory"""
        if not self.report_data:
            return []
        
        return self.report_data["findings"]["test_artifacts"]

    def cleanup_duplicate_files(self, dry_run: bool = True) -> List[str]:
        """Remove duplicate files that have confirmed originals"""
        removed_files = []
        safe_duplicates = self.get_safe_duplicate_files()
        
        if not safe_duplicates:
            print("✅ No safe duplicate files to remove")
            return removed_files
            
        print(f"\n🔍 Found {len(safe_duplicates)} safe duplicate files to remove:")
        
        for duplicate in safe_duplicates:
            file_path = self.root_path / duplicate["duplicate_file"]
            
            if not file_path.exists():
                print(f"⚠️ File not found: {duplicate['duplicate_file']}")
                continue
                
            size_mb = duplicate["size_bytes"] / 1024 / 1024
            print(f"  - {duplicate['duplicate_file']} ({size_mb:.2f} MB)")
            
            if dry_run:
                print(f"    [DRY RUN] Would remove: {file_path}")
                removed_files.append(duplicate["duplicate_file"])
            else:
                try:
                    file_path.unlink()
                    print(f"    ✅ Removed: {file_path}")
                    removed_files.append(duplicate["duplicate_file"])
                except Exception as e:
                    print(f"    ❌ Failed to remove {file_path}: {e}")
        
        return removed_files

    def move_test_files(self, dry_run: bool = True) -> List[str]:
        """Move misplaced test files to tests/ directory"""
        moved_files = []
        misplaced_tests = self.get_misplaced_test_files()
        
        if not misplaced_tests:
            print("✅ No misplaced test files found")
            return moved_files
            
        print(f"\n🔍 Found {len(misplaced_tests)} misplaced test files:")
        
        tests_dir = self.root_path / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        for test_file in misplaced_tests:
            source_path = self.root_path / test_file["file"]
            target_path = self.root_path / test_file["suggested_location"]
            
            if not source_path.exists():
                print(f"⚠️ Source file not found: {test_file['file']}")
                continue
                
            print(f"  - {test_file['file']} -> {test_file['suggested_location']}")
            
            if dry_run:
                print(f"    [DRY RUN] Would move: {source_path} -> {target_path}")
                moved_files.append(test_file["file"])
            else:
                try:
                    # Create target directory if needed
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file
                    shutil.move(str(source_path), str(target_path))
                    print(f"    ✅ Moved: {source_path} -> {target_path}")
                    moved_files.append(test_file["file"])
                except Exception as e:
                    print(f"    ❌ Failed to move {source_path}: {e}")
        
        return moved_files

    def show_security_risks(self):
        """Display security risk files for manual review"""
        if not self.report_data:
            return
            
        security_risks = self.report_data["findings"]["security_risks"]
        
        if not security_risks:
            print("✅ No security risk files found")
            return
            
        print(f"\n🔒 Found {len(security_risks)} files with potential security risks:")
        print("⚠️ These require MANUAL review before removal:")
        
        for risk_file in security_risks:
            print(f"  - {risk_file['file']} ({risk_file['risk_level']} risk)")
            print(f"    Reason: {risk_file['reason']}")
            if 'content_preview' in risk_file:
                preview = risk_file['content_preview'][:100] + "..." if len(risk_file['content_preview']) > 100 else risk_file['content_preview']
                print(f"    Preview: {preview}")
            print()

    def generate_cleanup_summary(self, removed_files: List[str], moved_files: List[str]) -> Dict[str, Any]:
        """Generate a summary of cleanup actions taken"""
        summary = {
            "cleanup_timestamp": datetime.now().isoformat(),
            "removed_files": removed_files,
            "moved_files": moved_files,
            "total_actions": len(removed_files) + len(moved_files),
        }
        
        # Calculate space saved
        if self.report_data:
            space_saved = 0
            for duplicate in self.report_data["findings"]["duplicate_files"]:
                if duplicate["duplicate_file"] in removed_files:
                    space_saved += duplicate["size_bytes"]
            
            summary["space_saved_bytes"] = space_saved
            summary["space_saved_mb"] = round(space_saved / 1024 / 1024, 2)
        
        return summary

    def run_cleanup(self, dry_run: bool = True, include_test_moves: bool = False) -> Dict[str, Any]:
        """Run the complete cleanup process"""
        print("Safe File Cleanup Tool")
        print("=" * 40)
        
        if dry_run:
            print("🧪 DRY RUN MODE - No actual changes will be made")
        else:
            print("🔧 LIVE MODE - Files will be modified!")
            confirm = input("⚠️  Are you sure you want to proceed with file modifications? This action is irreversible. Type 'yes' to continue: ")
            if confirm.strip().lower() != "yes":
                print("❌ Aborted by user. No changes were made.")
                return {"aborted": True}
            
        if not self.load_report():
            return {"error": "Could not load analysis report"}
        
        print(f"📊 Analysis report loaded from: {self.report_path}")
        
        # Clean up duplicate files
        removed_files = self.cleanup_duplicate_files(dry_run)
        
        # Move test files if requested
        moved_files = []
        if include_test_moves:
            moved_files = self.move_test_files(dry_run)
        
        # Show security risks for manual review
        self.show_security_risks()
        
        # Generate summary
        summary = self.generate_cleanup_summary(removed_files, moved_files)
        
        print("\n📊 Cleanup Summary:")
        print(f"  🗑️ Files removed: {len(removed_files)}")
        print(f"  📦 Files moved: {len(moved_files)}")
        print(f"  💾 Space saved: {summary.get('space_saved_mb', 0)} MB")
        
        if not dry_run:
            # Save cleanup log
            log_path = self.root_path / "cleanup_log.json"
            with open(log_path, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"  📄 Cleanup log saved to: {log_path}")
        
        return summary


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Safely clean up old and duplicate files')
    parser.add_argument('path', nargs='?', default='.', help='Path to analyze (default: current directory)')
    parser.add_argument('--report', help='Path to analysis report JSON file')
    parser.add_argument('--execute', action='store_true', help='Actually perform cleanup (default is dry-run)')
    parser.add_argument('--move-tests', action='store_true', help='Also move misplaced test files')
    
    args = parser.parse_args()
    
    root_path = Path(args.path).resolve()
    report_path = Path(args.report) if args.report else None
    
    cleanup_tool = SafeFileCleanup(root_path, report_path)
    
    # Run cleanup
    result = cleanup_tool.run_cleanup(
        dry_run=not args.execute,
        include_test_moves=args.move_tests
    )
    
    if "error" in result:
        print(f"❌ {result['error']}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())