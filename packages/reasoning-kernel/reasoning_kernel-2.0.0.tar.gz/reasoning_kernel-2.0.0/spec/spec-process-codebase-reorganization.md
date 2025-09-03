---
title: Reasoning Kernel Codebase Reorganization Process Specification
version: 1.0
date_created: 2025-08-15
owner: Reasoning Kernel Team
tags: [process, reorganization, technical-debt, migration, codebase]
---

## Introduction

This specification defines the process for reorganizing the Reasoning Kernel codebase to address technical debt, consolidate duplicate functionality, and establish a clean architecture foundation for the MSA reasoning system. It provides a systematic approach to migrate from the current scattered structure to a well-organized, maintainable codebase.

## 1. Purpose & Scope

- Purpose: Define a systematic process for reorganizing the Reasoning Kernel codebase while maintaining functionality and implementing pending features from the TODO backlog.
- Scope: Root directory cleanup, module consolidation, test organization, legacy code removal, dependency optimization, and migration automation for the entire reasoning-kernel repository.
- Audience: Development team, AI coding agents performing reorganization tasks, and maintainers implementing the MSA architecture.
- Assumptions: Git version control, Python 3.10-3.12 environment, existing test coverage >80%, and ability to create feature branches for migration work.

## 2. Definitions

- Legacy Code: Deprecated endpoints, old architecture patterns, and unused implementations identified for removal.
- Module Consolidation: Process of merging related functionality scattered across multiple files into cohesive modules.
- Dead Code: Code with zero test coverage and no references from active components.
- Migration Script: Automated tool for moving files, updating imports, and validating structure during reorganization.
- Technical Debt: Accumulated shortcuts, duplications, and organizational issues that impede development velocity.

## 3. Requirements, Constraints & Guidelines

- REQ-001: All file moves shall preserve git history using `git mv` commands.
- REQ-002: Test coverage shall be maintained at >80% throughout reorganization process.
- REQ-003: Backward compatibility shall be maintained for public APIs during transition.
- REQ-004: Each reorganization phase shall be completed in a separate git branch with full validation.
- REQ-005: Import path updates shall be automated and validated by running test suite.
- REQ-006: Documentation shall be updated to reflect new structure before merge.
- SEC-001: No secrets or credentials shall be exposed during file reorganization.
- CON-001: Migration shall not exceed 2-week timeline to minimize disruption.
- CON-002: Zero downtime requirement for production deployments during migration.
- GUD-001: Create backup before starting any reorganization phase.
- GUD-002: Use automated validation scripts to verify structure integrity.
- PAT-001: Follow established directory naming conventions from successful Python projects.

## 4. Interfaces & Data Contracts

### 4.1 Migration Script Interface

```python
class CodebaseMigrator:
    def backup_current_state(self) -> Path:
        """Create timestamped backup before migration"""
        
    def move_test_files(self) -> List[MigrationResult]:
        """Move root test files to tests/ subdirectories"""
        
    def consolidate_redis_managers(self) -> ConsolidationResult:
        """Merge multiple Redis managers into unified structure"""
        
    def update_imports(self, moved_files: List[FilePath]) -> ImportUpdateResult:
        """Update all import statements for moved modules"""
        
    def validate_migration(self) -> ValidationResult:
        """Run tests and linting to ensure migration success"""
```

### 4.2 Directory Structure Target

```text
app/
├── reasoning/              # Core reasoning engine (REQ-001)
│   ├── kernel.py          # Main reasoning orchestrator
│   ├── triggers.py        # Exploration trigger detection
│   └── world_models.py    # World model management
├── agents/                 # Semantic Kernel agents
│   ├── thinking_kernel.py # ThinkingReasoningKernel
│   ├── modular_msa_agent.py # ModularMSAAgent
│   └── reasoning_agent.py # ProbabilisticReasoningAgent
├── storage/               # Unified storage layer
│   ├── redis_manager.py   # Consolidated Redis management
│   └── adapters/          # Specialized adapters
└── plugins/               # Consolidated plugin architecture
    ├── reasoning/         # MSA pipeline plugins
    ├── exploration/       # Thinking exploration plugins
    └── knowledge/         # Knowledge retrieval plugins
```

### 4.3 Phase Execution Contract

```python
@dataclass
class PhaseResult:
    phase_name: str
    files_moved: List[str]
    imports_updated: List[str]
    tests_passing: bool
    coverage_maintained: bool
    backup_created: str
    rollback_available: bool
```

## 5. Acceptance Criteria

- AC-001: Given root directory test files, when Phase 1 executes, then all test files are moved to appropriate tests/ subdirectories with preserved git history.
- AC-002: Given multiple Redis managers, when consolidation completes, then a single unified RedisManager class provides all functionality with adapter pattern for specialization.
- AC-003: Given updated import paths, when validation runs, then all tests pass and no import errors occur.
- AC-004: Given completed reorganization, when coverage analysis runs, then test coverage remains >80% across all modules.
- AC-005: Given migration completion, when documentation is reviewed, then all file paths and references are updated to reflect new structure.

## 6. Test Automation Strategy

- Test Levels: Pre-migration validation, per-phase testing, post-migration integration testing
- Frameworks: pytest for test execution, coverage.py for coverage analysis, vulture for dead code detection
- Test Data Management: Use migration fixtures and mock data that can be easily moved with reorganization
- CI/CD Integration: Create reorganization branch with automated testing on each phase commit
- Coverage Requirements: Maintain >80% coverage; fail migration if coverage drops below threshold
- Performance Testing: Benchmark import times and startup performance before/after reorganization

## 7. Rationale & Context

The current codebase suffers from organic growth patterns that created:

- 6 test files in root directory causing confusion for new developers
- 4 separate Redis managers with overlapping functionality creating maintenance burden
- Scattered documentation across multiple locations reducing discoverability
- Legacy deprecated endpoints still consuming development attention
- Module organization that doesn't reflect the MSA architecture principles

This reorganization addresses technical debt while positioning the codebase for the pending ThinkingReasoningKernel implementation and hierarchical world model features.

## 8. Dependencies & External Integrations

### External Systems

- EXT-001: Git repository - Required for preserving file history during moves
- EXT-002: CI/CD pipeline - Must be updated for new directory structure

### Third-Party Services

- SVC-001: Code coverage service - For validating coverage maintenance
- SVC-002: Static analysis tools - vulture, mypy, black for code quality

### Infrastructure Dependencies

- INF-001: Development environment - Python 3.10-3.12 with all dependencies
- INF-002: Testing infrastructure - pytest, coverage.py, and all test dependencies

### Data Dependencies

- DAT-001: Git history preservation - All file moves must maintain git blame and history
- DAT-002: Configuration files - pyproject.toml, .env templates must be updated

### Technology Platform Dependencies

- PLT-001: Python package management - uv or pip for dependency resolution after reorganization
- PLT-002: IDE support - Ensure new structure works with common IDEs and language servers

## 9. Examples & Edge Cases

```python
# Example migration script usage
migrator = CodebaseMigrator()

# Create backup before starting
backup_path = migrator.backup_current_state()
print(f"Backup created: {backup_path}")

# Phase 1: Move test files
phase1_result = migrator.move_test_files()
assert phase1_result.tests_passing
assert phase1_result.coverage_maintained

# Consolidate Redis managers
consolidation_result = migrator.consolidate_redis_managers()
if not consolidation_result.success:
    migrator.rollback_to_backup(backup_path)
    
# Update all imports automatically
import_result = migrator.update_imports(phase1_result.files_moved)
assert len(import_result.failed_updates) == 0

# Final validation
validation = migrator.validate_migration()
assert validation.all_tests_pass
assert validation.coverage >= 0.80
```

### Edge Cases

- Circular import dependencies when moving modules
- Test files that reference moved modules by absolute path
- Documentation that embeds file paths as examples
- IDE configuration files that specify module paths
- Docker or deployment scripts with hardcoded paths

## 10. Validation Criteria

- VC-001: All automated tests pass after each migration phase
- VC-002: Test coverage analysis shows ≥80% coverage maintained
- VC-003: Static analysis (mypy, vulture) passes with zero critical issues
- VC-004: Import dependency graph has no circular dependencies
- VC-005: Documentation build succeeds with no broken internal links
- VC-006: Development setup instructions work for new developer onboarding

## 11. Related Specifications / Further Reading

- spec-architecture-msa-reasoning-kernel.md
- plan/codebase-reorganization-plan.md
- plan/TODO.txt
- docs/full-system.md
- tests/README.md
- CONTRIBUTING.md
