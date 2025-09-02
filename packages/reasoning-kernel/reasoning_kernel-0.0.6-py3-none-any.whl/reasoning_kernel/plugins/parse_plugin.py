"""Placeholder ParsePlugin for tests.

Tests patch this class via unittest.mock; provide minimal default behavior.
"""

from __future__ import annotations

from typing import List

from ..msa.stage_manager import MSAStageInput, MSAStageResult
from .base_plugin import BaseMSAPlugin


class ParsePlugin(BaseMSAPlugin):
    stage_name = "parse"

    async def execute(
        self, stage_input: MSAStageInput
    ) -> MSAStageResult:  # pragma: no cover - simple default
        return MSAStageResult(
            stage_name=self.stage_name,
            success=True,
            data={"entities": [], "concepts": []},
            insights=["parsed"],
            confidence_score=0.8,
            processing_time=0.01,
            metadata={},
        )

    def validate_input(self, stage_input: MSAStageInput) -> bool:
        return bool(stage_input.scenario)

    def get_capabilities(self) -> List[str]:
        return ["entity_extraction", "concept_identification"]
