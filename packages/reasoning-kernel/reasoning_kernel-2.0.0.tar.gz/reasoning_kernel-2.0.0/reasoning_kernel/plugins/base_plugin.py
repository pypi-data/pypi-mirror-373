"""Base plugin interfaces for MSA plugins used in tests."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from reasoning_kernel.msa.stage_manager import MSAStageInput, MSAStageResult


class BaseMSAPlugin(ABC):
    """Abstract base class for MSA stage plugins."""

    @abstractmethod
    async def execute(
        self, stage_input: MSAStageInput
    ) -> MSAStageResult:  # pragma: no cover - interface
        """Execute stage logic and return a result."""

    def validate_input(
        self, stage_input: MSAStageInput
    ) -> bool:  # pragma: no cover - default impl
        return True

    def get_capabilities(self) -> List[str]:  # pragma: no cover - default impl
        return []

    def get_stage_name(self) -> str:  # pragma: no cover - default impl
        return self.__class__.__name__.replace("Plugin", "").lower()


# Re-export for convenience in tests
MSAStageResult = MSAStageResult
