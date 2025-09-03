"""
Simplified MSA Reasoning Plugin
===============================

Minimal MSA plugin focusing on plugin architecture completion.
"""

from __future__ import annotations

import logging
from typing import Annotated

from semantic_kernel.functions import kernel_function

logger = logging.getLogger(__name__)


class MSAReasoningPlugin:
    """
    Simplified MSA reasoning plugin for testing plugin architecture.

    This version focuses on SK-native patterns without external dependencies.
    """

    def __init__(self, settings=None):
        """Initialize simplified MSA plugin."""
        self.settings = settings
        logger.info("MSA reasoning plugin initialized in simplified mode")

    @kernel_function(description="Analyze input using simplified MSA reasoning")
    async def analyze(
        self,
        query: Annotated[str, "Input query to analyze"],
        domain: Annotated[str | None, "Domain context"] = None,
    ) -> Annotated[dict, "Analysis results"]:
        """Run simplified MSA analysis on the input query."""
        try:
            logger.info(f"Running simplified MSA analysis for query: {query[:50]}...")

            # Basic MSA analysis with mock data for plugin testing
            result = {
                "query": query,
                "domain": domain or "general",
                "status": "completed",
                "analysis": {
                    "keywords": query.split(),
                    "entities": [],
                    "reasoning_type": "general",
                    "confidence": 0.7,
                    "method": "simplified_msa",
                    "plugin_version": "simple",
                },
                "message": f"Simplified MSA analysis completed for query in {domain or 'general'} domain",
            }

            logger.info("Simplified MSA analysis completed successfully")
            return result

        except Exception as e:
            logger.error(f"Simplified MSA analysis failed: {e}")
            return {"status": "failed", "error": str(e), "query": query, "method": "simplified_msa"}

    @kernel_function(description="Parse text vignette and extract basic information")
    async def parse_vignette(self, text: Annotated[str, "Text to parse"]) -> Annotated[dict, "Parsed structure"]:
        """Parse text vignette with basic text processing."""
        try:
            result = {
                "text": text,
                "parsed": {
                    "sentences": len([s for s in text.split(".") if s.strip()]),
                    "words": len(text.split()),
                    "characters": len(text),
                    "first_words": text.split()[:5] if text.split() else [],
                },
                "status": "completed",
                "method": "simplified_parsing",
            }
            logger.info(f"Parsed vignette with {result['parsed']['sentences']} sentences")
            return result
        except Exception as e:
            logger.error(f"Vignette parsing failed: {e}")
            return {"status": "failed", "error": str(e), "text": text}

    @kernel_function(description="Generate summary of analysis results")
    async def generate_summary(
        self, analysis: Annotated[dict | str, "Analysis results to summarize"]
    ) -> Annotated[str, "Summary text"]:
        """Generate a basic summary of analysis results."""
        try:
            if isinstance(analysis, str):
                return f"Summary: {analysis[:200]}..."

            if isinstance(analysis, dict):
                query = analysis.get("query", "Unknown query")
                status = analysis.get("status", "unknown")
                method = analysis.get("method", "unknown")

                if status == "completed":
                    confidence = analysis.get("analysis", {}).get("confidence", 0.0)
                    return f"MSA Analysis Summary:\nQuery: {query}\nMethod: {method}\nStatus: {status}\nConfidence: {confidence:.2f}"
                else:
                    error = analysis.get("error", "Unknown error")
                    return f"Analysis Failed:\nQuery: {query}\nError: {error}"

            return "Summary: Analysis completed with unknown format"

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return f"Summary generation error: {str(e)}"


def create_msa_plugin(**kwargs) -> MSAReasoningPlugin:
    """Factory function to create simplified MSA plugin."""
    return MSAReasoningPlugin(**kwargs)
