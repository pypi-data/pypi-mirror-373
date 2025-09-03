"""Placeholder SynthesisPlugin for tests."""

from __future__ import annotations

from typing import List

from ..msa.stage_manager import MSAStageInput, MSAStageResult
from .base_plugin import BaseMSAPlugin


class SynthesisPlugin(BaseMSAPlugin):
    stage_name = "synthesis"

    async def execute(
        self, stage_input: MSAStageInput
    ) -> MSAStageResult:  # pragma: no cover
        return MSAStageResult(
            stage_name=self.stage_name,
            success=True,
            data={
                "probabilistic_program": "def model(): pass",
                "variables": [],
                "model_structure": {"nodes": 0, "edges": 0},
            },
            insights=["synthesized"],
            confidence_score=0.7,
            processing_time=0.03,
            metadata={},
        )

    def validate_input(self, stage_input: MSAStageInput) -> bool:
        return True

    def get_capabilities(self) -> List[str]:
        return ["program_generation", "model_synthesis"]
