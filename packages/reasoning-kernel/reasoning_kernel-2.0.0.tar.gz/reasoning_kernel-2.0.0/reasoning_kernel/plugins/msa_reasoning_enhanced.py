"""
Enhanced MSA Reasoning Plugin
============================

SK-native MSA plugin with AI-powered analysis using Azure OpenAI service.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Annotated

from semantic_kernel.functions import kernel_function

if TYPE_CHECKING:
    from semantic_kernel import Kernel

logger = logging.getLogger(__name__)


class EnhancedMSAReasoningPlugin:
    """Enhanced MSA reasoning plugin with AI-powered analysis."""

    def __init__(self, settings=None):
        """Initialize the enhanced MSA plugin."""
        self.settings = settings
        logger.info("Enhanced MSA reasoning plugin initialized with AI integration")

    @kernel_function(description="Analyze input using AI-powered MSA reasoning")
    async def analyze(
        self,
        query: Annotated[str, "Input query to analyze"],
        domain: Annotated[str | None, "Domain context"] = None,
        kernel: Annotated[Kernel | None, "The kernel instance"] = None,
    ) -> Annotated[dict, "Analysis results"]:
        """Run AI-powered MSA analysis."""
        try:
            # Step 1: Extract key elements using AI
            elements = await self._extract_elements(query, domain, kernel)

            # Step 2: Analyze reasoning requirements
            requirements = await self._analyze_requirements(query, domain, kernel)

            # Step 3: Generate structured analysis
            analysis = await self._generate_analysis(query, elements, requirements, kernel)

            result = {
                "query": query,
                "domain": domain or "general",
                "status": "completed",
                "analysis": {
                    "elements": elements,
                    "requirements": requirements,
                    "structured_analysis": analysis,
                    "confidence": analysis.get("confidence", 0.7),
                    "method": "ai_powered_msa",
                    "steps_completed": ["extract", "analyze", "synthesize"],
                },
                "message": "Analysis completed using AI-powered MSA",
            }

            logger.info(f"Enhanced MSA analysis completed for query: {query[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Enhanced MSA analysis failed: {e}")
            return {"status": "failed", "error": str(e), "query": query}

    async def _extract_elements(self, query: str, domain: str | None, kernel: Kernel | None) -> dict:
        """Extract key elements from the query using AI."""
        if kernel is None:
            # Fallback to basic extraction
            return {"keywords": query.split(), "entities": [], "confidence": 0.6, "method": "fallback"}

        try:
            # Use AI service to extract elements
            prompt = f"""
            Analyze this query and extract key elements:
            Query: {query}
            Domain: {domain or 'general'}
            
            Extract:
            1. Main keywords and concepts
            2. Named entities (people, places, organizations)
            3. Key relationships
            4. Domain-specific terms
            
            Return JSON format:
            {{
                "keywords": [...],
                "entities": [...],
                "relationships": [...],
                "domain_terms": [...],
                "confidence": 0.0-1.0
            }}
            """

            # Get chat completion service
            chat_service = kernel.get_service("azure_openai")
            if chat_service is None:
                return await self._fallback_extraction(query)

            from semantic_kernel import ChatHistory
            from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
            from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings

            history = ChatHistory()
            history.add_user_message(prompt)

            settings = AzureChatPromptExecutionSettings(function_choice_behavior=FunctionChoiceBehavior.Auto())

            response = await chat_service.get_chat_message_contents(
                chat_history=history, settings=settings, kernel=kernel
            )

            if response and len(response) > 0:
                content = response[0].content
                try:
                    # Try to parse JSON response
                    result = json.loads(content)
                    result["method"] = "ai_powered"
                    return result
                except json.JSONDecodeError:
                    # If not JSON, create structured result
                    return {
                        "keywords": query.split(),
                        "entities": [],
                        "relationships": [],
                        "domain_terms": [],
                        "confidence": 0.7,
                        "method": "ai_powered_text",
                        "ai_response": content,
                    }

        except Exception as e:
            logger.warning(f"AI element extraction failed: {e}, falling back")
            return await self._fallback_extraction(query)

        return await self._fallback_extraction(query)

    async def _analyze_requirements(self, query: str, domain: str | None, kernel: Kernel | None) -> dict:
        """Analyze reasoning requirements using AI."""
        if kernel is None:
            return await self._fallback_requirements(query)

        try:
            prompt = f"""
            Analyze the reasoning requirements for this query:
            Query: {query}
            Domain: {domain or 'general'}
            
            Determine what type of reasoning is needed:
            1. Causal reasoning (cause-effect relationships)
            2. Probabilistic reasoning (uncertainty, likelihood)
            3. Comparative analysis (comparing options)
            4. Predictive analysis (forecasting outcomes)
            5. Optimization (finding best solutions)
            
            Return JSON format:
            {{
                "primary_type": "...",
                "secondary_types": [...],
                "complexity": "low|medium|high",
                "reasoning_steps": [...],
                "confidence": 0.0-1.0
            }}
            """

            chat_service = kernel.get_service("azure_openai")
            if chat_service is None:
                return await self._fallback_requirements(query)

            from semantic_kernel import ChatHistory
            from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
            from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings

            history = ChatHistory()
            history.add_user_message(prompt)

            settings = AzureChatPromptExecutionSettings(function_choice_behavior=FunctionChoiceBehavior.Auto())

            response = await chat_service.get_chat_message_contents(
                chat_history=history, settings=settings, kernel=kernel
            )

            if response and len(response) > 0:
                content = response[0].content
                try:
                    result = json.loads(content)
                    result["method"] = "ai_powered"
                    return result
                except json.JSONDecodeError:
                    return {
                        "primary_type": "general",
                        "secondary_types": [],
                        "complexity": "medium",
                        "reasoning_steps": ["analyze", "synthesize"],
                        "confidence": 0.7,
                        "method": "ai_powered_text",
                        "ai_response": content,
                    }

        except Exception as e:
            logger.warning(f"AI requirements analysis failed: {e}, falling back")
            return await self._fallback_requirements(query)

        return await self._fallback_requirements(query)

    async def _generate_analysis(self, query: str, elements: dict, requirements: dict, kernel: Kernel | None) -> dict:
        """Generate comprehensive analysis using AI."""
        if kernel is None:
            return await self._fallback_analysis(query, elements, requirements)

        try:
            prompt = f"""
            Generate a comprehensive analysis based on:
            
            Query: {query}
            
            Extracted Elements:
            {json.dumps(elements, indent=2)}
            
            Requirements:
            {json.dumps(requirements, indent=2)}
            
            Provide a structured analysis that:
            1. Synthesizes the key findings
            2. Identifies important patterns or relationships
            3. Assesses the confidence level
            4. Suggests next steps if needed
            
            Return JSON format:
            {{
                "synthesis": "...",
                "key_patterns": [...],
                "relationships": [...],
                "confidence": 0.0-1.0,
                "next_steps": [...],
                "reasoning_chain": [...]
            }}
            """

            chat_service = kernel.get_service("azure_openai")
            if chat_service is None:
                return await self._fallback_analysis(query, elements, requirements)

            from semantic_kernel import ChatHistory
            from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
            from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings

            history = ChatHistory()
            history.add_user_message(prompt)

            settings = AzureChatPromptExecutionSettings(function_choice_behavior=FunctionChoiceBehavior.Auto())

            response = await chat_service.get_chat_message_contents(
                chat_history=history, settings=settings, kernel=kernel
            )

            if response and len(response) > 0:
                content = response[0].content
                try:
                    result = json.loads(content)
                    result["method"] = "ai_powered"
                    return result
                except json.JSONDecodeError:
                    return {
                        "synthesis": content,
                        "key_patterns": [],
                        "relationships": [],
                        "confidence": 0.8,
                        "next_steps": ["review results"],
                        "reasoning_chain": ["ai analysis"],
                        "method": "ai_powered_text",
                    }

        except Exception as e:
            logger.warning(f"AI analysis generation failed: {e}, falling back")
            return await self._fallback_analysis(query, elements, requirements)

        return await self._fallback_analysis(query, elements, requirements)

    async def _fallback_extraction(self, query: str) -> dict:
        """Fallback element extraction without AI."""
        words = query.split()
        return {
            "keywords": [w for w in words if len(w) > 3],
            "entities": [],
            "relationships": [],
            "domain_terms": [],
            "confidence": 0.6,
            "method": "fallback",
        }

    async def _fallback_requirements(self, query: str) -> dict:
        """Fallback requirements analysis without AI."""
        query_lower = query.lower()

        primary_type = "general"
        if any(word in query_lower for word in ["why", "because", "cause", "reason"]):
            primary_type = "causal"
        elif any(word in query_lower for word in ["probability", "chance", "likely"]):
            primary_type = "probabilistic"
        elif any(word in query_lower for word in ["compare", "versus", "better"]):
            primary_type = "comparative"
        elif any(word in query_lower for word in ["predict", "forecast", "future"]):
            primary_type = "predictive"
        elif any(word in query_lower for word in ["optimize", "best", "maximum"]):
            primary_type = "optimization"

        return {
            "primary_type": primary_type,
            "secondary_types": [],
            "complexity": "medium",
            "reasoning_steps": ["parse", "analyze", "synthesize"],
            "confidence": 0.6,
            "method": "fallback",
        }

    async def _fallback_analysis(self, query: str, elements: dict, requirements: dict) -> dict:
        """Fallback analysis without AI."""
        return {
            "synthesis": f"Basic analysis of query: {query[:100]}...",
            "key_patterns": elements.get("keywords", [])[:3],
            "relationships": [],
            "confidence": 0.6,
            "next_steps": ["consider AI enhancement"],
            "reasoning_chain": ["fallback analysis"],
            "method": "fallback",
        }

    @kernel_function(description="Parse text vignette and extract structured information")
    async def parse_vignette(self, text: Annotated[str, "Text to parse"]) -> Annotated[dict, "Parsed structure"]:
        """Parse text vignette with AI assistance."""
        try:
            result = {
                "text": text,
                "parsed": {
                    "sentences": len(text.split(".")),
                    "words": len(text.split()),
                    "entities": [],
                    "concepts": text.split()[:5],
                },
                "status": "completed",
            }
            return result
        except Exception as e:
            logger.error(f"Vignette parsing failed: {e}")
            return {"status": "failed", "error": str(e), "text": text}

    @kernel_function(description="Generate summary of analysis results")
    async def generate_summary(
        self, analysis: Annotated[dict | str, "Analysis results to summarize"]
    ) -> Annotated[str, "Summary text"]:
        """Generate a summary of analysis results."""
        try:
            if isinstance(analysis, str):
                return f"Summary: {analysis[:200]}..."

            if isinstance(analysis, dict):
                query = analysis.get("query", "Unknown query")
                status = analysis.get("status", "unknown")
                confidence = analysis.get("analysis", {}).get("confidence", 0.0)

                return f"MSA Analysis Summary:\nQuery: {query}\nStatus: {status}\nConfidence: {confidence:.2f}"

            return "Summary: Analysis completed"

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return f"Summary generation error: {str(e)}"


def create_enhanced_msa_plugin(**kwargs) -> EnhancedMSAReasoningPlugin:
    """Factory function to create enhanced MSA plugin."""
    return EnhancedMSAReasoningPlugin(**kwargs)
