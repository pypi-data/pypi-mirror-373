"""Placeholder KnowledgePlugin for tests."""

from __future__ import annotations

from typing import List

from ..msa.stage_manager import MSAStageInput, MSAStageResult
from .base_plugin import BaseMSAPlugin


class KnowledgePlugin(BaseMSAPlugin):
    stage_name = "knowledge"

    async def execute(
        self, stage_input: MSAStageInput
    ) -> MSAStageResult:  # pragma: no cover
        return MSAStageResult(
            stage_name=self.stage_name,
            success=True,
            data={"retrieved_facts": [], "knowledge_sources": []},
            insights=["retrieved"],
            confidence_score=0.75,
            processing_time=0.02,
            metadata={},
        )

    def validate_input(self, stage_input: MSAStageInput) -> bool:
        return True

    def get_capabilities(self) -> List[str]:
        return ["knowledge_retrieval", "fact_verification"]
