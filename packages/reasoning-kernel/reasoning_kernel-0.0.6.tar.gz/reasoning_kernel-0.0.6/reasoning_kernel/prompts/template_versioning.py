"""
Template Versioning System for MSA Prompt Templates

This module provides versioning and A/B testing capabilities for MSA prompt templates,
enabling continuous improvement and optimization of reasoning quality.
"""

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from reasoning_kernel.prompts.msa_prompt_templates import PromptTemplate

logger = logging.getLogger(__name__)


class VersionStatus(Enum):
    """Status of template versions"""

    DRAFT = "draft"
    TESTING = "testing"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ABTestStatus(Enum):
    """Status of A/B tests"""

    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class TemplateVersion:
    """Version of a prompt template"""

    template_name: str
    version_id: str
    version_number: str
    template: PromptTemplate
    status: VersionStatus
    created_at: datetime
    created_by: str
    description: str
    changelog: List[str]
    performance_metrics: Dict[str, float]
    usage_count: int = 0
    last_used: Optional[datetime] = None


@dataclass
class ABTestConfig:
    """Configuration for A/B testing"""

    test_id: str
    template_name: str
    version_a: str  # Control version
    version_b: str  # Test version
    traffic_split: float  # Percentage for version B (0.0-1.0)
    start_date: datetime
    end_date: datetime
    success_metrics: List[str]
    minimum_sample_size: int
    confidence_level: float = 0.95


@dataclass
class ABTestResult:
    """Result of A/B test"""

    test_id: str
    status: ABTestStatus
    version_a_metrics: Dict[str, float]
    version_b_metrics: Dict[str, float]
    statistical_significance: Dict[str, bool]
    winner: Optional[str]
    confidence_intervals: Dict[str, Tuple[float, float]]
    sample_sizes: Dict[str, int]
    recommendation: str


class TemplateVersionManager:
    """Manager for template versions and A/B testing"""

    def __init__(self):
        self.versions: Dict[str, List[TemplateVersion]] = {}
        self.active_versions: Dict[str, str] = {}  # template_name -> version_id
        self.ab_tests: Dict[str, ABTestConfig] = {}
        self.ab_results: Dict[str, ABTestResult] = {}
        self.version_counter = 0

    def create_version(
        self,
        template_name: str,
        template: PromptTemplate,
        description: str,
        changelog: List[str],
        created_by: str = "system",
    ) -> str:
        """Create a new version of a template"""
        self.version_counter += 1
        version_id = (
            f"{template_name}_v{self.version_counter}_{int(datetime.now().timestamp())}"
        )

        # Determine version number
        existing_versions = self.versions.get(template_name, [])
        if not existing_versions:
            version_number = "1.0.0"
        else:
            # Increment minor version
            latest_version = max(existing_versions, key=lambda v: v.created_at)
            major, minor, patch = latest_version.version_number.split(".")
            version_number = f"{major}.{int(minor) + 1}.0"

        version = TemplateVersion(
            template_name=template_name,
            version_id=version_id,
            version_number=version_number,
            template=template,
            status=VersionStatus.DRAFT,
            created_at=datetime.now(),
            created_by=created_by,
            description=description,
            changelog=changelog,
            performance_metrics={},
        )

        if template_name not in self.versions:
            self.versions[template_name] = []

        self.versions[template_name].append(version)

        logger.info(f"Created version {version_number} for template {template_name}")
        return version_id

    def activate_version(self, template_name: str, version_id: str) -> bool:
        """Activate a specific version of a template"""
        version = self.get_version(template_name, version_id)
        if not version:
            logger.error(f"Version {version_id} not found for template {template_name}")
            return False

        # Deactivate current active version
        if template_name in self.active_versions:
            current_active = self.get_version(
                template_name, self.active_versions[template_name]
            )
            if current_active:
                current_active.status = VersionStatus.DEPRECATED

        # Activate new version
        version.status = VersionStatus.ACTIVE
        self.active_versions[template_name] = version_id

        logger.info(
            f"Activated version {version.version_number} for template {template_name}"
        )
        return True

    def get_version(
        self, template_name: str, version_id: str
    ) -> Optional[TemplateVersion]:
        """Get a specific version of a template"""
        versions = self.versions.get(template_name, [])
        for version in versions:
            if version.version_id == version_id:
                return version
        return None

    def get_active_version(self, template_name: str) -> Optional[TemplateVersion]:
        """Get the active version of a template"""
        if template_name not in self.active_versions:
            return None

        version_id = self.active_versions[template_name]
        return self.get_version(template_name, version_id)

    def get_template_for_execution(
        self, template_name: str, user_id: Optional[str] = None
    ) -> Optional[PromptTemplate]:
        """Get template for execution, considering A/B tests"""
        # Check if there's an active A/B test
        active_test = self._get_active_ab_test(template_name)

        if active_test and user_id:
            # Determine which version to use based on A/B test
            version_id = self._select_ab_test_version(active_test, user_id)
            version = self.get_version(template_name, version_id)
            if version:
                self._record_ab_test_usage(active_test.test_id, version_id)
                return version.template

        # Use active version
        active_version = self.get_active_version(template_name)
        if active_version:
            active_version.usage_count += 1
            active_version.last_used = datetime.now()
            return active_version.template

        return None

    def create_ab_test(
        self,
        template_name: str,
        version_a_id: str,
        version_b_id: str,
        traffic_split: float = 0.5,
        duration_days: int = 7,
        success_metrics: List[str] = None,
        minimum_sample_size: int = 100,
    ) -> str:
        """Create an A/B test between two template versions"""
        if success_metrics is None:
            success_metrics = ["execution_time", "tokens_used", "success_rate"]

        test_id = f"ab_test_{template_name}_{int(datetime.now().timestamp())}"

        config = ABTestConfig(
            test_id=test_id,
            template_name=template_name,
            version_a=version_a_id,
            version_b=version_b_id,
            traffic_split=traffic_split,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            success_metrics=success_metrics,
            minimum_sample_size=minimum_sample_size,
        )

        self.ab_tests[test_id] = config

        # Initialize result tracking
        self.ab_results[test_id] = ABTestResult(
            test_id=test_id,
            status=ABTestStatus.RUNNING,
            version_a_metrics={},
            version_b_metrics={},
            statistical_significance={},
            winner=None,
            confidence_intervals={},
            sample_sizes={"version_a": 0, "version_b": 0},
            recommendation="",
        )

        logger.info(f"Created A/B test {test_id} for template {template_name}")
        return test_id

    def _get_active_ab_test(self, template_name: str) -> Optional[ABTestConfig]:
        """Get active A/B test for a template"""
        current_time = datetime.now()

        for test_config in self.ab_tests.values():
            if (
                test_config.template_name == template_name
                and test_config.start_date <= current_time <= test_config.end_date
            ):
                return test_config

        return None

    def _select_ab_test_version(self, test_config: ABTestConfig, user_id: str) -> str:
        """Select version for A/B test based on user ID"""
        # Use hash of user_id for consistent assignment
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        normalized_hash = (hash_value % 1000) / 1000.0

        if normalized_hash < test_config.traffic_split:
            return test_config.version_b
        else:
            return test_config.version_a

    def _record_ab_test_usage(self, test_id: str, version_id: str):
        """Record usage for A/B test tracking"""
        if test_id not in self.ab_results:
            return

        result = self.ab_results[test_id]
        test_config = self.ab_tests[test_id]

        if version_id == test_config.version_a:
            result.sample_sizes["version_a"] += 1
        elif version_id == test_config.version_b:
            result.sample_sizes["version_b"] += 1

    def record_performance_metrics(
        self, template_name: str, version_id: str, metrics: Dict[str, float]
    ):
        """Record performance metrics for a template version"""
        version = self.get_version(template_name, version_id)
        if not version:
            return

        # Update version metrics
        for metric, value in metrics.items():
            if metric not in version.performance_metrics:
                version.performance_metrics[metric] = []
            version.performance_metrics[metric].append(value)

        # Update A/B test metrics if applicable
        self._update_ab_test_metrics(template_name, version_id, metrics)

    def _update_ab_test_metrics(
        self, template_name: str, version_id: str, metrics: Dict[str, float]
    ):
        """Update A/B test metrics"""
        active_test = self._get_active_ab_test(template_name)
        if not active_test:
            return

        test_result = self.ab_results.get(active_test.test_id)
        if not test_result:
            return

        # Determine which version this is
        if version_id == active_test.version_a:
            target_metrics = test_result.version_a_metrics
        elif version_id == active_test.version_b:
            target_metrics = test_result.version_b_metrics
        else:
            return

        # Update metrics (running average)
        for metric, value in metrics.items():
            if metric in active_test.success_metrics:
                if metric not in target_metrics:
                    target_metrics[metric] = value
                else:
                    # Simple running average (could be improved with proper statistics)
                    target_metrics[metric] = (target_metrics[metric] + value) / 2

    def analyze_ab_test(self, test_id: str) -> ABTestResult:
        """Analyze A/B test results"""
        if test_id not in self.ab_tests or test_id not in self.ab_results:
            raise ValueError(f"A/B test {test_id} not found")

        test_config = self.ab_tests[test_id]
        test_result = self.ab_results[test_id]

        # Check if test has sufficient data
        total_samples = sum(test_result.sample_sizes.values())
        if total_samples < test_config.minimum_sample_size:
            test_result.recommendation = f"Insufficient data: {total_samples}/{test_config.minimum_sample_size} samples"
            return test_result

        # Perform statistical analysis (simplified)
        winner = self._determine_winner(test_result, test_config.success_metrics)
        test_result.winner = winner

        # Generate recommendation
        if winner == "version_b":
            test_result.recommendation = (
                "Version B shows improvement - consider promoting to active"
            )
        elif winner == "version_a":
            test_result.recommendation = (
                "Version A (control) performs better - keep current version"
            )
        else:
            test_result.recommendation = (
                "No significant difference - consider longer test or different metrics"
            )

        # Mark test as completed if past end date
        if datetime.now() > test_config.end_date:
            test_result.status = ABTestStatus.COMPLETED

        return test_result

    def _determine_winner(
        self, test_result: ABTestResult, success_metrics: List[str]
    ) -> Optional[str]:
        """Determine winner based on success metrics (simplified analysis)"""
        version_a_score = 0
        version_b_score = 0

        for metric in success_metrics:
            a_value = test_result.version_a_metrics.get(metric, 0)
            b_value = test_result.version_b_metrics.get(metric, 0)

            # For most metrics, lower is better (execution_time, tokens_used)
            # For success_rate, higher is better
            if metric == "success_rate":
                if b_value > a_value:
                    version_b_score += 1
                elif a_value > b_value:
                    version_a_score += 1
            else:
                if b_value < a_value:
                    version_b_score += 1
                elif a_value < b_value:
                    version_a_score += 1

        if version_b_score > version_a_score:
            return "version_b"
        elif version_a_score > version_b_score:
            return "version_a"
        else:
            return None

    def get_version_history(self, template_name: str) -> List[Dict[str, Any]]:
        """Get version history for a template"""
        versions = self.versions.get(template_name, [])

        history = []
        for version in sorted(versions, key=lambda v: v.created_at, reverse=True):
            history.append(
                {
                    "version_id": version.version_id,
                    "version_number": version.version_number,
                    "status": version.status.value,
                    "created_at": version.created_at.isoformat(),
                    "created_by": version.created_by,
                    "description": version.description,
                    "usage_count": version.usage_count,
                    "last_used": version.last_used.isoformat()
                    if version.last_used
                    else None,
                    "performance_summary": self._summarize_performance(
                        version.performance_metrics
                    ),
                }
            )

        return history

    def _summarize_performance(
        self, metrics: Dict[str, List[float]]
    ) -> Dict[str, float]:
        """Summarize performance metrics"""
        summary = {}
        for metric, values in metrics.items():
            if values:
                summary[f"{metric}_avg"] = sum(values) / len(values)
                summary[f"{metric}_count"] = len(values)
        return summary

    def get_ab_test_report(self, test_id: str) -> Dict[str, Any]:
        """Get comprehensive A/B test report"""
        if test_id not in self.ab_tests:
            return {"error": f"A/B test {test_id} not found"}

        test_config = self.ab_tests[test_id]
        test_result = self.analyze_ab_test(test_id)

        return {
            "test_config": {
                "test_id": test_config.test_id,
                "template_name": test_config.template_name,
                "version_a": test_config.version_a,
                "version_b": test_config.version_b,
                "traffic_split": test_config.traffic_split,
                "start_date": test_config.start_date.isoformat(),
                "end_date": test_config.end_date.isoformat(),
                "success_metrics": test_config.success_metrics,
                "minimum_sample_size": test_config.minimum_sample_size,
            },
            "results": {
                "status": test_result.status.value,
                "sample_sizes": test_result.sample_sizes,
                "version_a_metrics": test_result.version_a_metrics,
                "version_b_metrics": test_result.version_b_metrics,
                "winner": test_result.winner,
                "recommendation": test_result.recommendation,
            },
            "analysis": {
                "total_samples": sum(test_result.sample_sizes.values()),
                "test_duration_days": (datetime.now() - test_config.start_date).days,
                "completion_percentage": min(
                    100,
                    (
                        sum(test_result.sample_sizes.values())
                        / test_config.minimum_sample_size
                    )
                    * 100,
                ),
            },
        }

    def promote_version(self, template_name: str, version_id: str) -> bool:
        """Promote a version to active status"""
        version = self.get_version(template_name, version_id)
        if not version:
            return False

        # Check if version is ready for promotion
        if version.status not in [VersionStatus.TESTING, VersionStatus.DRAFT]:
            logger.warning(
                f"Version {version_id} status {version.status} not suitable for promotion"
            )
            return False

        return self.activate_version(template_name, version_id)

    def rollback_version(self, template_name: str) -> bool:
        """Rollback to previous active version"""
        versions = self.versions.get(template_name, [])
        if len(versions) < 2:
            logger.error(
                f"No previous version available for rollback of {template_name}"
            )
            return False

        # Find previous active version
        active_versions = [v for v in versions if v.status == VersionStatus.DEPRECATED]
        if not active_versions:
            logger.error(f"No previous active version found for {template_name}")
            return False

        # Get most recent deprecated version
        previous_version = max(active_versions, key=lambda v: v.created_at)

        return self.activate_version(template_name, previous_version.version_id)

    def cleanup_old_versions(self, template_name: str, keep_count: int = 5):
        """Clean up old versions, keeping only the most recent ones"""
        versions = self.versions.get(template_name, [])
        if len(versions) <= keep_count:
            return

        # Sort by creation date, keep most recent
        sorted_versions = sorted(versions, key=lambda v: v.created_at, reverse=True)

        # Archive old versions (don't delete active or testing versions)
        for version in sorted_versions[keep_count:]:
            if version.status not in [VersionStatus.ACTIVE, VersionStatus.TESTING]:
                version.status = VersionStatus.ARCHIVED

        logger.info(
            f"Archived {len(sorted_versions) - keep_count} old versions of {template_name}"
        )


# Global version manager instance
_version_manager: Optional[TemplateVersionManager] = None


def get_version_manager() -> TemplateVersionManager:
    """Get the global template version manager"""
    global _version_manager
    if _version_manager is None:
        _version_manager = TemplateVersionManager()
    return _version_manager
