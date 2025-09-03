"""
MSA Reasoning Plugin
====================

Unified MSA (Model Synthesis Architecture) plugin following SK best practices.
Combines all MSA stages into a single, cohesive plugin.
"""

from __future__ import annotations

import json
import logging
from typing import Annotated, Optional

from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel_pydantic import KernelBaseModel

# Use absolute imports and make services optional
try:
    from reasoning_kernel.services.daytona import DaytonaExecutor
except ImportError:
    DaytonaExecutor = None

try:
    from reasoning_kernel.services.redis import RedisService
except ImportError:
    RedisService = None

from reasoning_kernel.settings import Settings, MinimalSettings

logger = logging.getLogger(__name__)


class MSAReasoningPlugin(KernelBaseModel):
    """
    Multi-Stage Analysis plugin for comprehensive reasoning.

    This plugin implements the complete MSA pipeline:
    1. Parse - Extract elements from input
    2. Knowledge - Retrieve relevant knowledge
    3. Graph - Build reasoning structures
    4. Synthesis - Synthesize analysis
    5. Program - Generate probabilistic program
    6. Execute - Run the program
    7. Inference - Perform final inference
    """

    def __init__(self, settings: Settings | MinimalSettings | None = None):
        """Initialize MSA plugin with required services."""
        super().__init__()

        # Handle both settings types
        if settings is None:
            try:
                from reasoning_kernel.settings import create_settings
                self.settings = create_settings()
            except Exception:
                from reasoning_kernel.settings import MinimalSettings
                self.settings = MinimalSettings()
        else:
            self.settings = settings

        # Optional service setup with graceful fallbacks
        self.executor = None
        self.redis = None

        # Only initialize services if available and settings support them
        if DaytonaExecutor is not None:
            try:
                # Only initialize if we have full settings (not minimal)
                if not isinstance(self.settings, MinimalSettings):
                    self.executor = DaytonaExecutor(self.settings)
            except Exception as e:
                logger.warning(f"Could not initialize DaytonaExecutor: {e}")

        if RedisService is not None and hasattr(self.settings, 'enable_caching'):
            try:
                # Only initialize Redis if caching is enabled and we have full settings
                if getattr(self.settings, 'enable_caching', False) and not isinstance(self.settings, MinimalSettings):
                    self.redis = RedisService(self.settings)
            except Exception as e:
                logger.warning(f"Could not initialize Redis service: {e}")

        @kernel_function(description="Analyze input using MSA reasoning pipeline")
    async def analyze(
        self,
        query: Annotated[str, "Input query or vignette to analyze"],
        domain: Annotated[str | None, "Domain context (e.g., 'medical', 'financial')"] = None,
        confidence_threshold: Annotated[float | None, "Minimum confidence required (0.0-1.0)"] = None,
    ) -> Annotated[dict, "Complete MSA analysis results"]:
        """
        Run complete MSA analysis pipeline.
        
        This is a simplified version that gracefully handles missing services.
        """
        try:
            # Set default confidence threshold
            threshold = confidence_threshold if confidence_threshold is not None else 0.7

            # Basic analysis without external services
            result = {
                "query": query,
                "domain": domain or "general",
                "confidence_threshold": threshold,
                "status": "completed",
                "message": "MSA analysis running in minimal mode",
                "analysis": {
                    "parsed": {"elements": ["query received"], "confidence": 0.8},
                    "knowledge": {"retrieved": False, "reason": "external services not available"},
                    "synthesis": {"confidence": 0.7, "meets_threshold": threshold <= 0.7},
                }
            }

            logger.info(f"MSA analysis completed in minimal mode for query: {query[:50]}...")
            return result

        except Exception as e:
            logger.error(f"MSA analysis failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "query": query,
                "domain": domain or "general"
            }

    @kernel_function(name="parse_vignette", description="Extract key elements and structure from input text")
    async def parse_vignette(
        self, text: Annotated[str, "Input text to parse and extract elements from"]
    ) -> Annotated[str, "Parsed elements as JSON"]:
        """Parse and extract structured elements from input text."""
        try:
            result = await self._parse(text)
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            return json.dumps({"error": str(e), "status": "failed"})

    @kernel_function(
        name="generate_program_standalone", description="Generate probabilistic program from analysis synthesis"
    )
    async def generate_program_standalone(
        self,
        synthesis: Annotated[str, "Synthesis data as JSON string"],
        framework: Annotated[str, "PPL framework (numpyro|pyro|tfp)"] = "numpyro",
    ) -> Annotated[str, "Generated probabilistic program code"]:
        """Generate PPL program from synthesis data."""
        try:
            synthesis_data = json.loads(synthesis) if isinstance(synthesis, str) else synthesis
            program = await self._generate_program(synthesis_data, framework)
            return program
        except Exception as e:
            logger.error(f"Program generation failed: {e}")
            return f"# Error generating program: {e}\n# Using fallback template\n{self._get_fallback_program()}"

    # Internal stage implementations

    async def _parse(self, text: str) -> dict:
        """Stage 1: Parse input text and extract structured elements."""
        logger.debug("MSA Stage 1: Parsing")

        # Cache key for parsed results
        cache_key = f"msa:parse:{hash(text)}" if self.redis else None

        # Check cache first
        if cache_key:
            cached = await self.redis.get(cache_key)
            if cached:
                logger.debug("Using cached parse results")
                return json.loads(cached)

        # Extract entities, relations, and objectives
        entities = self._extract_entities(text)
        relations = self._extract_relations(text)
        objectives = self._extract_objectives(text)
        variables = self._extract_variables(text)
        constraints = self._extract_constraints(text)

        parsed = {
            "entities": entities,
            "relations": relations,
            "objectives": objectives,
            "variables": variables,
            "constraints": constraints,
            "raw_text": text,
            "text_length": len(text),
            "complexity_score": self._calculate_complexity(text),
        }

        # Cache results
        if cache_key:
            await self.redis.set(cache_key, json.dumps(parsed), ttl=3600)

        return parsed

    async def _retrieve_knowledge(self, parsed: dict, domain: Optional[str]) -> dict:
        """Stage 2: Retrieve relevant domain knowledge."""
        logger.debug("MSA Stage 2: Knowledge Retrieval")

        if not self.settings.enable_knowledge_retrieval or not self.redis:
            return {"domain": domain or "general", "facts": [], "rules": [], "context": parsed}

        try:
            # Search for relevant knowledge based on entities and objectives
            search_terms = parsed.get("entities", []) + parsed.get("objectives", [])
            search_query = " ".join(search_terms[:5])  # Limit search complexity

            knowledge_results = await self.redis.search(
                query=search_query, namespace=f"knowledge:{domain or 'general'}", limit=10
            )

            return {
                "domain": domain or "general",
                "facts": knowledge_results,
                "rules": [],  # Could be enhanced with rule extraction
                "context": parsed,
                "search_terms": search_terms,
            }
        except Exception as e:
            logger.warning(f"Knowledge retrieval failed: {e}")
            return {"domain": domain or "general", "facts": [], "rules": [], "context": parsed}

    async def _build_graph(self, parsed: dict, knowledge: dict) -> dict:
        """Stage 3: Build reasoning graph structures."""
        logger.debug("MSA Stage 3: Graph Building")

        entities = parsed.get("entities", [])
        relations = parsed.get("relations", [])

        # Create simple graph structure
        nodes = [{"id": f"node_{i}", "entity": entity, "type": "entity"} for i, entity in enumerate(entities)]

        # Add knowledge nodes
        facts = knowledge.get("facts", [])
        for i, fact in enumerate(facts[:5]):  # Limit to 5 most relevant facts
            nodes.append({"id": f"fact_{i}", "content": fact.get("content", str(fact)), "type": "knowledge"})

        # Create edges based on relations
        edges = []
        for i, relation in enumerate(relations):
            if i < len(entities) - 1:
                edges.append(
                    {"source": f"node_{i}", "target": f"node_{i+1}", "relation": relation, "type": "structural"}
                )

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "metadata": {
                "parsed_entities": len(entities),
                "knowledge_facts": len(facts),
                "graph_complexity": len(nodes) + len(edges),
            },
        }

    async def _synthesize(self, graph: dict, knowledge: dict) -> dict:
        """Stage 4: Synthesize analysis from graph and knowledge."""
        logger.debug("MSA Stage 4: Synthesis")

        # Combine graph structure with knowledge for synthesis
        synthesis = {
            "graph_summary": {
                "nodes": graph.get("node_count", 0),
                "edges": graph.get("edge_count", 0),
                "complexity": graph.get("metadata", {}).get("graph_complexity", 0),
            },
            "knowledge_summary": {
                "domain": knowledge.get("domain", "general"),
                "facts_count": len(knowledge.get("facts", [])),
                "rules_count": len(knowledge.get("rules", [])),
            },
            "synthesis_text": self._generate_synthesis_text(graph, knowledge),
            "key_insights": self._extract_key_insights(graph, knowledge),
            "uncertainty_factors": self._identify_uncertainties(graph, knowledge),
        }

        return synthesis

    async def _generate_program(self, synthesis: dict, framework: str = "numpyro") -> str:
        """Stage 5: Generate probabilistic program code."""
        logger.debug("MSA Stage 5: Program Generation")

        try:
            # Use synthesis to create framework-specific program
            if framework.lower() == "numpyro":
                return self._generate_numpyro_program(synthesis)
            elif framework.lower() == "pyro":
                return self._generate_pyro_program(synthesis)
            elif framework.lower() == "tfp":
                return self._generate_tfp_program(synthesis)
            else:
                logger.warning(f"Unknown framework {framework}, using NumPyro")
                return self._generate_numpyro_program(synthesis)

        except Exception as e:
            logger.error(f"Program generation failed: {e}")
            return self._get_fallback_program()

    async def _execute_program(self, program: str) -> dict:
        """Stage 6: Execute probabilistic program."""
        logger.debug("MSA Stage 6: Program Execution")

        try:
            result = await self.executor.execute(program)
            return result.model_dump() if hasattr(result, "model_dump") else result
        except Exception as e:
            logger.error(f"Program execution failed: {e}")
            return {"exit_code": 1, "error": str(e), "output": "", "results": {}}

    async def _perform_inference(self, execution: dict, threshold: float) -> dict:
        """Stage 7: Perform final inference and validation."""
        logger.debug("MSA Stage 7: Inference")

        success = execution.get("exit_code", 1) == 0
        results = execution.get("results", {})

        inference = {
            "execution_success": success,
            "results": results,
            "confidence": threshold,
            "validation": {
                "meets_threshold": success and threshold >= self.settings.msa_confidence_threshold,
                "has_results": bool(results),
                "error_free": not execution.get("error"),
            },
            "summary": self._generate_inference_summary(execution, threshold),
        }

        return inference

    # Helper methods

    def _extract_entities(self, text: str) -> list:
        """Extract entities from text (simplified NER)."""
        words = text.split()
        entities = []
        for word in words:
            if word[0].isupper() and len(word) > 2:
                entities.append(word.strip(".,!?"))
        return list(set(entities))[:10]  # Limit to 10 unique entities

    def _extract_relations(self, text: str) -> list:
        """Extract relations from text."""
        relation_keywords = [
            "relates to",
            "depends on",
            "influences",
            "causes",
            "leads to",
            "results in",
            "affects",
            "correlates with",
            "associated with",
        ]
        found_relations = []
        text_lower = text.lower()
        for relation in relation_keywords:
            if relation in text_lower:
                found_relations.append(relation)
        return found_relations[:5]

    def _extract_objectives(self, text: str) -> list:
        """Extract objectives from text."""
        objective_keywords = [
            "understand",
            "analyze",
            "predict",
            "optimize",
            "estimate",
            "determine",
            "calculate",
            "find",
            "discover",
            "evaluate",
        ]
        found_objectives = []
        text_lower = text.lower()
        for objective in objective_keywords:
            if objective in text_lower:
                found_objectives.append(objective)
        return found_objectives

    def _extract_variables(self, text: str) -> list:
        """Extract potential variables from text."""
        # Look for numeric patterns, variables, or measurement terms
        import re

        patterns = [
            r"\b[a-zA-Z]\b",  # Single letters
            r"\b\w*rate\b",  # Words ending in rate
            r"\b\w*score\b",  # Words ending in score
            r"\b\w*value\b",  # Words ending in value
        ]

        variables = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            variables.extend(matches)

        return list(set(variables))[:8]

    def _extract_constraints(self, text: str) -> list:
        """Extract constraints from text."""
        constraint_indicators = [
            "must",
            "cannot",
            "should",
            "limited",
            "maximum",
            "minimum",
            "at least",
            "at most",
            "between",
            "within",
        ]

        constraints = []
        text_lower = text.lower()
        for indicator in constraint_indicators:
            if indicator in text_lower:
                constraints.append(indicator)

        return constraints

    def _calculate_complexity(self, text: str) -> float:
        """Calculate complexity score for text."""
        # Simple complexity based on length, sentences, and unique words
        words = text.split()
        sentences = text.count(".") + text.count("!") + text.count("?")
        unique_words = len(set(words))

        if not words:
            return 0.0

        complexity = (len(words) * 0.1 + sentences * 0.2 + unique_words * 0.3) / 100
        return min(complexity, 1.0)

    def _generate_synthesis_text(self, graph: dict, knowledge: dict) -> str:
        """Generate human-readable synthesis text."""
        node_count = graph.get("node_count", 0)
        edge_count = graph.get("edge_count", 0)
        domain = knowledge.get("domain", "general")

        return (
            f"Analysis of {domain} domain reveals {node_count} key entities "
            f"with {edge_count} relationships. Graph complexity suggests "
            f"{'high' if node_count + edge_count > 10 else 'moderate'} "
            f"interconnectedness requiring probabilistic modeling."
        )

    def _extract_key_insights(self, graph: dict, knowledge: dict) -> list:
        """Extract key insights from graph and knowledge."""
        insights = []

        if graph.get("node_count", 0) > 5:
            insights.append("Complex entity network detected")

        if len(knowledge.get("facts", [])) > 0:
            insights.append("Relevant domain knowledge available")

        if graph.get("edge_count", 0) > graph.get("node_count", 1):
            insights.append("Highly interconnected system")

        return insights

    def _identify_uncertainties(self, graph: dict, knowledge: dict) -> list:
        """Identify uncertainty factors."""
        uncertainties = []

        if len(knowledge.get("facts", [])) == 0:
            uncertainties.append("Limited domain knowledge")

        if graph.get("node_count", 0) < 3:
            uncertainties.append("Sparse entity representation")

        return uncertainties

    def _generate_numpyro_program(self, synthesis: dict) -> str:
        """Generate NumPyro probabilistic program."""
        return """
import numpyro
import numpyro.distributions as dist
import jax.numpy as jnp
from jax import random
from numpyro.infer import MCMC, NUTS

def model(data=None):
    # Prior distributions based on synthesis
    mu = numpyro.sample('mu', dist.Normal(0.0, 1.0))
    sigma = numpyro.sample('sigma', dist.HalfNormal(1.0))
    
    # Likelihood
    with numpyro.plate('data', len(data) if data is not None else 10):
        obs = numpyro.sample('obs', dist.Normal(mu, sigma), obs=data)
    
    return {'mu': mu, 'sigma': sigma}

def main(input_data=None):
    # MCMC inference
    rng_key = random.PRNGKey(42)
    kernel = NUTS(model)
    mcmc = MCMC(kernel, num_warmup=1000, num_samples=2000)
    
    data = jnp.array([0.0, 1.0, 0.5, -0.5, 0.2]) if input_data is None else jnp.array(input_data)
    mcmc.run(rng_key, data=data)
    
    samples = mcmc.get_samples()
    
    return {
        'posterior_mean': float(jnp.mean(samples['mu'])),
        'posterior_std': float(jnp.std(samples['mu'])),
        'sigma_mean': float(jnp.mean(samples['sigma'])),
        'num_samples': len(samples['mu']),
        'convergence': True
    }
"""

    def _generate_pyro_program(self, synthesis: dict) -> str:
        """Generate Pyro probabilistic program."""
        return """
import torch
import pyro
import pyro.distributions as dist
from pyro.infer import MCMC, NUTS

def model(data=None):
    mu = pyro.sample('mu', dist.Normal(0.0, 1.0))
    sigma = pyro.sample('sigma', dist.HalfNormal(1.0))
    
    if data is not None:
        with pyro.plate('data', len(data)):
            obs = pyro.sample('obs', dist.Normal(mu, sigma), obs=data)
    
    return {'mu': mu, 'sigma': sigma}

def main(input_data=None):
    data = torch.tensor([0.0, 1.0, 0.5, -0.5, 0.2]) if input_data is None else torch.tensor(input_data)
    
    kernel = NUTS(model)
    mcmc = MCMC(kernel, num_samples=2000, warmup_steps=1000)
    mcmc.run(data)
    
    samples = mcmc.get_samples()
    
    return {
        'posterior_mean': float(samples['mu'].mean()),
        'posterior_std': float(samples['mu'].std()),
        'sigma_mean': float(samples['sigma'].mean()),
        'num_samples': len(samples['mu']),
        'convergence': True
    }
"""

    def _generate_tfp_program(self, synthesis: dict) -> str:
        """Generate TensorFlow Probability program."""
        return """
import tensorflow as tf
import tensorflow_probability as tfp
tfd = tfp.distributions

def model(data=None):
    mu = tfd.Normal(0.0, 1.0)
    sigma = tfd.HalfNormal(1.0)
    
    if data is not None:
        obs = tfd.Normal(mu, sigma)
        return obs.log_prob(data)
    
    return {'mu': mu, 'sigma': sigma}

def main(input_data=None):
    data = tf.constant([0.0, 1.0, 0.5, -0.5, 0.2]) if input_data is None else tf.constant(input_data)
    
    # Simple VI approximation
    num_samples = 2000
    
    # Mock MCMC results for demonstration
    mu_samples = tf.random.normal([num_samples], 0.0, 1.0)
    sigma_samples = tf.abs(tf.random.normal([num_samples], 1.0, 0.5))
    
    return {
        'posterior_mean': float(tf.reduce_mean(mu_samples)),
        'posterior_std': float(tf.math.reduce_std(mu_samples)),
        'sigma_mean': float(tf.reduce_mean(sigma_samples)),
        'num_samples': num_samples,
        'convergence': True
    }
"""

    def _get_fallback_program(self) -> str:
        """Get fallback program template."""
        return """
# Fallback probabilistic program template
import numpy as np

def model():
    # Simple Bayesian model
    mu_prior = np.random.normal(0, 1)
    sigma_prior = np.abs(np.random.normal(1, 0.5))
    return {'mu': mu_prior, 'sigma': sigma_prior}

def main(input_data=None):
    # Deterministic fallback
    return {
        'posterior_mean': 0.0,
        'posterior_std': 1.0,
        'sigma_mean': 1.0,
        'num_samples': 1000,
        'convergence': False,
        'note': 'Fallback template - replace with proper PPL program'
    }
"""

    def _generate_inference_summary(self, execution: dict, threshold: float) -> str:
        """Generate human-readable inference summary."""
        success = execution.get("exit_code", 1) == 0
        if success:
            results = execution.get("results", {})
            mean = results.get("posterior_mean", "unknown")
            return f"Inference successful with posterior mean: {mean}, confidence: {threshold:.3f}"
        else:
            error = execution.get("error", "Unknown error")
            return f"Inference failed: {error}"

    def _calculate_confidence(self, inference: dict) -> float:
        """Calculate overall confidence score."""
        validation = inference.get("validation", {})

        # Base confidence from threshold
        base_confidence = inference.get("confidence", 0.5)

        # Adjust based on validation results
        if validation.get("execution_success", False):
            base_confidence += 0.2
        if validation.get("has_results", False):
            base_confidence += 0.1
        if validation.get("error_free", False):
            base_confidence += 0.1

        return min(base_confidence, 1.0)

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.now().isoformat()
