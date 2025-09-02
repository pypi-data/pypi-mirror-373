"""
MSA Agents using Semantic Kernel
================================

Transforms the existing MSA pipeline stages into Semantic Kernel plugins and functions.
Provides structured reasoning through MSA methodology using SK's function calling.
"""

import json
import logging
from typing import Annotated, Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions import kernel_function

from .azure_responses_adapter import chat_text_via_responses, get_reasoning_config_from_env, use_responses_api

logger = logging.getLogger(__name__)


class MSAParsePlugin:
    """MSA Parse stage as SK plugin - Extract key elements from vignettes"""

    def __init__(self, kernel: Optional[Kernel] = None):
        self.kernel = kernel

    async def _chat_with_ai(
        self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000
    ) -> str:
        """Helper method to make chat completion calls with proper settings"""
        if not self.kernel:
            return ""

        try:
            # Prefer Responses API when enabled (for GPT-5/reasoning models)
            if use_responses_api():
                text = await chat_text_via_responses(
                    prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    reasoning=get_reasoning_config_from_env(),
                )
                if text:
                    return text

            chat_service = self.kernel.get_service("azure_openai_chat")

            # Create execution settings for Azure OpenAI
            execution_settings = OpenAIChatPromptExecutionSettings(
                max_tokens=max_tokens, temperature=temperature
            )

            # Create chat history
            chat_history = ChatHistory()
            chat_history.add_user_message(prompt)

            # Get response with proper settings
            response = await chat_service.get_chat_message_content(
                chat_history=chat_history, settings=execution_settings
            )
            return response.content
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return ""

    @kernel_function(
        name="parse_vignette",
        description="Parse and extract structured elements from a reasoning vignette",
    )
    async def parse_vignette(
        self,
        vignette: Annotated[str, "The vignette text to parse and analyze"],
        extraction_mode: Annotated[
            str, "Extraction mode: 'detailed', 'summary', 'causal'"
        ] = "detailed",
    ) -> str:
        """Parse reasoning vignettes to extract structured elements"""

        logger.info(f"Parsing vignette in {extraction_mode} mode")

        if self.kernel:
            prompt = f"""
            Parse this vignette and extract structured information as JSON:

            Vignette: {vignette}

            Extract the following based on mode '{extraction_mode}':
            1. Entities: People, objects, concepts mentioned
            2. Relationships: How entities relate to each other
            3. Causal Structure: What causes what
            4. Probabilistic Elements: Uncertainties, chances, probabilities
            5. Temporal Sequence: Order of events

            Return as clean JSON only.
            """

            response = await self._chat_with_ai(prompt)
            if response:
                return response

        # Fallback structured response
        fallback_result = {
            "entities": ["extracted from vignette"],
            "relationships": ["entity1 -> entity2"],
            "causal_structure": ["cause -> effect"],
            "probabilistic_elements": ["uncertainty identified"],
            "temporal_sequence": ["event1", "event2"],
            "extraction_mode": extraction_mode,
        }

        logger.info(f"Fallback parse result: {fallback_result}")
        return json.dumps(fallback_result)


class MSAKnowledgePlugin:
    """MSA Knowledge stage as SK plugin - Retrieve and apply domain knowledge"""

    def __init__(self, kernel: Optional[Kernel] = None):
        self.kernel = kernel

    async def _chat_with_ai(
        self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000
    ) -> str:
        """Helper method to make chat completion calls with proper settings"""
        if not self.kernel:
            return ""

        try:
            if use_responses_api():
                text = await chat_text_via_responses(
                    prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    reasoning=get_reasoning_config_from_env(),
                )
                if text:
                    return text

            chat_service = self.kernel.get_service("azure_openai_chat")

            # Create execution settings for Azure OpenAI
            execution_settings = OpenAIChatPromptExecutionSettings(
                max_tokens=max_tokens, temperature=temperature
            )

            # Create chat history
            chat_history = ChatHistory()
            chat_history.add_user_message(prompt)

            # Get response with proper settings
            response = await chat_service.get_chat_message_content(
                chat_history=chat_history, settings=execution_settings
            )
            return response.content
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return ""

    @kernel_function(
        name="retrieve_domain_knowledge",
        description="Retrieve relevant domain knowledge for reasoning context",
    )
    async def retrieve_domain_knowledge(
        self,
        context: Annotated[str, "The reasoning context requiring domain knowledge"],
        domain: Annotated[
            str, "Specific domain: 'cognitive', 'causal', 'probabilistic', 'general'"
        ] = "general",
    ) -> str:
        """Retrieve domain-specific knowledge for reasoning"""

        logger.info(f"Retrieving {domain} domain knowledge")

        if self.kernel:
            prompt = f"""
            Provide relevant domain knowledge for this reasoning context:

            Context: {context}
            Domain: {domain}

            Focus on principles, patterns, and relevant background knowledge
            that would help with reasoning in this domain.

            Return structured knowledge as JSON.
            """

            response = await self._chat_with_ai(prompt)
            if response:
                return response

        # Fallback knowledge
        return json.dumps(
            {
                "principles": ["domain principle"],
                "patterns": ["known pattern"],
                "background": "general knowledge",
            }
        )


class MSAGraphPlugin:
    """MSA Graph stage as SK plugin - Build and analyze reasoning graphs"""

    def __init__(self, kernel: Optional[Kernel] = None):
        self.kernel = kernel

    async def _chat_with_ai(
        self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000
    ) -> str:
        """Helper method to make chat completion calls with proper settings"""
        if not self.kernel:
            return ""

        try:
            if use_responses_api():
                text = await chat_text_via_responses(
                    prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    reasoning=get_reasoning_config_from_env(),
                )
                if text:
                    return text

            chat_service = self.kernel.get_service("azure_openai_chat")

            # Create execution settings for Azure OpenAI
            execution_settings = OpenAIChatPromptExecutionSettings(
                max_tokens=max_tokens, temperature=temperature
            )

            # Create chat history
            chat_history = ChatHistory()
            chat_history.add_user_message(prompt)

            # Get response with proper settings
            response = await chat_service.get_chat_message_content(
                chat_history=chat_history, settings=execution_settings
            )
            return response.content
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return ""

    @kernel_function(
        name="build_reasoning_graph",
        description="Build a comprehensive reasoning graph from parsed elements",
    )
    async def build_reasoning_graph(
        self,
        parsed_elements: Annotated[str, "JSON string of parsed vignette elements"],
        graph_type: Annotated[
            str, "Type of graph: 'causal', 'probabilistic', 'conceptual', 'hybrid'"
        ] = "hybrid",
    ) -> str:
        """Build reasoning graph from parsed elements"""

        logger.info(f"Building {graph_type} reasoning graph")

        if self.kernel:
            prompt = f"""
            Build a reasoning graph from these parsed elements:

            Parsed Elements: {parsed_elements}
            Graph Type: {graph_type}

            Create a comprehensive graph structure with:
            1. Nodes: Key concepts, entities, events
            2. Edges: Relationships, causality, dependencies
            3. Properties: Confidence, strength, temporal ordering
            4. Clusters: Related concept groups

            Return as structured graph data in JSON format.
            """

            response = await self._chat_with_ai(prompt)
            if response:
                return response

        # Fallback graph
        return json.dumps(
            {
                "nodes": [
                    {"id": "node1", "type": "concept"},
                    {"id": "node2", "type": "entity"},
                ],
                "edges": [
                    {
                        "from": "node1",
                        "to": "node2",
                        "type": "relates_to",
                        "strength": 0.7,
                    }
                ],
                "clusters": ["cluster1"],
                "graph_type": graph_type,
            }
        )


class MSASynthesisPlugin:
    """MSA Synthesis stage as SK plugin - Synthesize findings and draw conclusions"""

    def __init__(self, kernel: Optional[Kernel] = None):
        self.kernel = kernel

    async def _chat_with_ai(
        self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000
    ) -> str:
        """Helper method to make chat completion calls with proper settings"""
        if not self.kernel:
            return ""

        try:
            if use_responses_api():
                text = await chat_text_via_responses(
                    prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    reasoning=get_reasoning_config_from_env(),
                )
                if text:
                    return text

            chat_service = self.kernel.get_service("azure_openai_chat")

            # Create execution settings for Azure OpenAI
            execution_settings = OpenAIChatPromptExecutionSettings(
                max_tokens=max_tokens, temperature=temperature
            )

            # Create chat history
            chat_history = ChatHistory()
            chat_history.add_user_message(prompt)

            # Get response with proper settings
            response = await chat_service.get_chat_message_content(
                chat_history=chat_history, settings=execution_settings
            )
            return response.content
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return ""

    @kernel_function(
        name="synthesize_findings",
        description="Synthesize findings from multiple MSA stages into coherent conclusions",
    )
    async def synthesize_findings(
        self,
        parse_results: Annotated[str, "Results from parse stage"],
        knowledge_results: Annotated[str, "Results from knowledge stage"],
        graph_results: Annotated[str, "Results from graph stage"],
        synthesis_mode: Annotated[
            str, "Synthesis approach: 'comprehensive', 'focused', 'summary'"
        ] = "comprehensive",
    ) -> str:
        """Synthesize findings from all MSA stages"""

        logger.info(f"Synthesizing findings in {synthesis_mode} mode")

        if self.kernel:
            prompt = f"""
            Synthesize these MSA stage findings into coherent conclusions:

            Parse Results: {parse_results}
            Knowledge Results: {knowledge_results}
            Graph Results: {graph_results}

            Mode: {synthesis_mode}

            Create a comprehensive synthesis that:
            1. Integrates findings across stages
            2. Identifies key insights and patterns
            3. Draws logical conclusions
            4. Highlights confidence levels
            5. Notes areas of uncertainty or conflict

            Return as structured synthesis in JSON format.
            """

            response = await self._chat_with_ai(prompt)
            if response:
                return response

        # Fallback synthesis
        return json.dumps(
            {
                "key_insights": ["insight 1", "insight 2"],
                "conclusions": ["conclusion with 85% confidence"],
                "evidence_strength": "moderate",
                "uncertainty_areas": ["area needing more evidence"],
                "synthesis_mode": synthesis_mode,
            }
        )

    @kernel_function(
        name="synthesize_reasoning",
        description="Synthesize reasoning from multiple MSA stages",
    )
    async def synthesize_reasoning(
        self,
        parsed_data: Annotated[str, "Parsed stage result (JSON string)"],
        knowledge_data: Annotated[str, "Knowledge stage result (JSON string)"],
        graph_data: Annotated[str, "Graph stage result (JSON string)"],
        confidence_threshold: Annotated[
            float, "Confidence threshold for synthesis (0.0-1.0)"
        ] = 0.6,
    ) -> str:
        """Synthesize reasoning from all MSA stages (orchestrator compatibility).

        Note: confidence_threshold is accepted for compatibility with orchestrator
        but currently not used directly in the synthesis prompt.
        """
        # Map orchestrator argument names to the core synthesize_findings signature
        return await self.synthesize_findings(
            parsed_data, knowledge_data, graph_data, "comprehensive"
        )


class MSAInferencePlugin:
    """MSA Inference stage as SK plugin - Make probabilistic inferences and predictions"""

    def __init__(self, kernel: Optional[Kernel] = None):
        self.kernel = kernel

    async def _chat_with_ai(
        self, prompt: str, temperature: float = 0.3, max_tokens: int = 1000
    ) -> str:
        """Helper method to make chat completion calls with proper settings"""
        if not self.kernel:
            return ""

        try:
            if use_responses_api():
                text = await chat_text_via_responses(
                    prompt, temperature=temperature, max_tokens=max_tokens
                )
                if text:
                    return text

            chat_service = self.kernel.get_service("azure_openai_chat")

            # Create execution settings for Azure OpenAI
            execution_settings = OpenAIChatPromptExecutionSettings(
                max_tokens=max_tokens, temperature=temperature
            )

            # Create chat history
            chat_history = ChatHistory()
            chat_history.add_user_message(prompt)

            # Get response with proper settings
            response = await chat_service.get_chat_message_content(
                chat_history=chat_history, settings=execution_settings
            )
            return response.content
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return ""

    @kernel_function(
        name="make_probabilistic_inference",
        description="Make probabilistic inferences based on synthesized findings",
    )
    async def make_probabilistic_inference(
        self,
        synthesis_results: Annotated[str, "Results from synthesis stage"],
        inference_target: Annotated[str, "What to make inferences about"],
        confidence_threshold: Annotated[
            float, "Minimum confidence threshold (0.0-1.0)"
        ] = 0.6,
    ) -> str:
        """Make probabilistic inferences from synthesized findings"""

        logger.info(f"Making probabilistic inference for: {inference_target}")

        if self.kernel:
            prompt = f"""
            Make probabilistic inferences based on these synthesized findings:

            Synthesis Results: {synthesis_results}
            Inference Target: {inference_target}
            Confidence Threshold: {confidence_threshold}

            Generate:
            1. Probability estimates for key outcomes
            2. Confidence intervals where appropriate
            3. Uncertainty quantification
            4. Alternative scenarios
            5. Risk assessments

            Return as structured probabilistic analysis in JSON.
            """

            response = await self._chat_with_ai(prompt)
            if response:
                return response

        # Fallback inference
        return json.dumps(
            {
                "primary_inference": {
                    "outcome": "likely scenario",
                    "probability": 0.75,
                    "confidence": 0.8,
                },
                "alternatives": [
                    {"outcome": "alternative scenario", "probability": 0.25}
                ],
                "uncertainty_factors": ["factor 1", "factor 2"],
                "confidence_threshold": confidence_threshold,
            }
        )

    @kernel_function(
        name="generate_probabilistic_inferences",
        description="Generate probabilistic inferences for orchestrator",
    )
    async def generate_probabilistic_inferences(
        self,
        synthesis_data: Annotated[str, "Synthesis stage result (JSON string)"],
        inference_type: Annotated[
            str, "Type/target of inference, e.g., 'bayesian' or domain target"
        ] = "general outcomes",
    ) -> str:
        """Generate probabilistic inferences (orchestrator compatibility).

        Maps orchestrator-provided parameters to the core inference function.
        """
        return await self.make_probabilistic_inference(
            synthesis_data, inference_type, 0.6
        )
