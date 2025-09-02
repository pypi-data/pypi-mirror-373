"""
Reasoning Kernel Factory using Semantic Kernel
==============================================

Creates and configures Semantic Kernel instances for the Reasoning Kernel.
Integrates with existing .env configuration and provides simplified kernel creation.
"""

import logging
from typing import Any, Dict, Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
from semantic_kernel.core_plugins import MathPlugin, TextPlugin, TimePlugin

from .settings_adapter import SKSettingsAdapter

logger = logging.getLogger(__name__)


class ReasoningKernelFactory:
    """Factory for creating configured Semantic Kernel instances for reasoning"""

    def __init__(self):
        self.settings_adapter = SKSettingsAdapter()
        self._kernel_cache: Optional[Kernel] = None

    async def create_reasoning_kernel(
        self,
        use_reasoning: bool = True,
        enable_memory: bool = True,
        enable_plugins: bool = True,
        force_recreate: bool = False,
    ) -> Kernel:
        """Create a kernel with reasoning capabilities"""

        if self._kernel_cache and not force_recreate:
            return self._kernel_cache

        try:
            kernel = Kernel()

            # Add AI services in order of preference
            await self._add_ai_services(kernel, use_reasoning)

            # Add core plugins if enabled
            if enable_plugins:
                await self._add_core_plugins(kernel)

            # Cache the kernel
            self._kernel_cache = kernel

            logger.info("Reasoning kernel created successfully")
            return kernel

        except Exception as e:
            logger.error(f"Failed to create reasoning kernel: {e}")
            raise

    async def _add_ai_services(
        self, kernel: Kernel, use_reasoning: bool = True
    ) -> None:
        """Add AI services to the kernel"""

        # Priority 1: Azure OpenAI (with GPT-5 reasoning support)
        azure_config = self.settings_adapter.get_azure_openai_config()
        if azure_config.api_key and azure_config.endpoint:
            try:
                service = AzureChatCompletion(
                    service_id=azure_config.service_id,
                    api_key=azure_config.api_key,
                    endpoint=azure_config.endpoint,
                    deployment_name=azure_config.deployment_name or azure_config.model,
                    api_version=azure_config.api_version,
                )

                kernel.add_service(service)
                logger.info(
                    f"Added Azure OpenAI service: {azure_config.deployment_name}"
                )
                return

            except Exception as e:
                logger.warning(f"Failed to add Azure OpenAI service: {e}")

        # Priority 2: OpenAI
        openai_config = self.settings_adapter.get_openai_config()
        if openai_config and openai_config.api_key:
            try:
                service = OpenAIChatCompletion(
                    service_id=openai_config.service_id,
                    api_key=openai_config.api_key,
                    ai_model_id=openai_config.model,
                )
                kernel.add_service(service)
                logger.info(f"Added OpenAI service: {openai_config.model}")
                return

            except Exception as e:
                logger.warning(f"Failed to add OpenAI service: {e}")

        raise RuntimeError(
            "No AI services could be configured. Check your API keys in .env file."
        )

    async def _add_core_plugins(self, kernel: Kernel) -> None:
        """Add core SK plugins"""
        try:
            # Core plugins for reasoning support
            kernel.add_plugin(TextPlugin(), plugin_name="text")
            kernel.add_plugin(MathPlugin(), plugin_name="math")
            kernel.add_plugin(TimePlugin(), plugin_name="time")

            logger.info("Added core plugins")

        except Exception as e:
            logger.warning(f"Failed to add some core plugins: {e}")
            # Continue - plugins are optional

    def get_msa_config(self) -> Dict[str, Any]:
        """Get MSA-specific configuration"""
        return self.settings_adapter.get_msa_config()

    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags"""
        return self.settings_adapter.get_feature_flags()

    def clear_cache(self) -> None:
        """Clear the kernel cache"""
        self._kernel_cache = None
        logger.info("Kernel cache cleared")


# Global factory instance
_factory: Optional[ReasoningKernelFactory] = None


async def create_reasoning_kernel(
    use_reasoning: bool = True,
    enable_memory: bool = True,
    enable_plugins: bool = True,
    force_recreate: bool = False,
) -> Kernel:
    """Convenience function to create a reasoning kernel"""
    global _factory

    if _factory is None:
        _factory = ReasoningKernelFactory()

    return await _factory.create_reasoning_kernel(
        use_reasoning=use_reasoning,
        enable_memory=enable_memory,
        enable_plugins=enable_plugins,
        force_recreate=force_recreate,
    )


async def get_kernel_factory() -> ReasoningKernelFactory:
    """Get the global kernel factory"""
    global _factory

    if _factory is None:
        _factory = ReasoningKernelFactory()

    return _factory
