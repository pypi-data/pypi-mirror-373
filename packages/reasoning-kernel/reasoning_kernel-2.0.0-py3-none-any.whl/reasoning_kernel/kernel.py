"""
Reasoning Kernel - Main Kernel Setup
=====================================

Simplified SK-native kernel following Microsoft Semantic Kernel best practices.
"""

from __future__ import annotations

import logging

from semantic_kernel import Kernel

from .settings import MinimalSettings, Settings

logger = logging.getLogger(__name__)


class ReasoningKernel:
    """Main kernel for reasoning operations following SK best practices."""

    def __init__(self, settings: MinimalSettings | Settings | None = None):
        """Initialize the Reasoning Kernel with plugins and services."""
        from .settings import create_settings

        self.settings = settings or create_settings()
        self.kernel = Kernel()

        # Add AI service
        self._setup_ai_service()

        # Add core plugins
        self._register_plugins()

        logger.info("Reasoning Kernel initialized with simplified SK-native structure")

    def _setup_ai_service(self):
        """Setup AI service with proper Azure OpenAI integration."""
        try:
            # Get the API key - handle both field names (MinimalSettings vs Settings)
            api_key = getattr(self.settings, "azure_openai_key", None) or getattr(
                self.settings, "azure_openai_api_key", None
            )
            endpoint = getattr(self.settings, "azure_openai_endpoint", None)

            # Check if we have Azure OpenAI configuration
            if endpoint and api_key:
                logger.info("Setting up Azure OpenAI service...")

                from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

                # Create Azure OpenAI service
                azure_service = AzureChatCompletion(
                    service_id="azure_openai",
                    deployment_name=getattr(self.settings, "azure_openai_model", "gpt-35-turbo"),
                    endpoint=endpoint,
                    api_key=api_key,
                    api_version=getattr(self.settings, "azure_openai_api_version", "2024-02-01"),
                )

                # Add service to kernel
                self.kernel.add_service(azure_service)
                logger.info("✅ Azure OpenAI service configured successfully")

            else:
                logger.info("Azure OpenAI credentials not available, skipping AI service setup")

        except Exception as e:
            logger.warning(f"AI service setup failed: {e}")
            is_dev = getattr(self.settings, "is_development", lambda: True)
            if callable(is_dev):
                is_dev = is_dev()
            else:
                is_dev = getattr(self.settings, "environment", "development") == "development"

            if not is_dev:
                raise RuntimeError(f"AI service configuration failed: {e}")
            else:
                logger.info("Continuing in development mode without AI service")

    def _register_plugins(self) -> None:
        """Register all plugins with the kernel."""
        try:
            # Always register the simple test plugin (no dependencies)
            logger.info("Attempting to register simple test plugin...")
            from .plugins.simple_test import SimpleTestPlugin

            test_plugin = SimpleTestPlugin()
            self.kernel.add_plugin(test_plugin, "simple_test")
            logger.info("✅ Registered simple test plugin")

            # Try to register simplified MSA reasoning plugin
            logger.info("Attempting to register MSA reasoning plugin...")
            try:
                from .plugins.msa_reasoning_simple import MSAReasoningPlugin

                msa_plugin = MSAReasoningPlugin(self.settings)
                self.kernel.add_plugin(msa_plugin, "msa_reasoning")
                logger.info("✅ Registered simplified MSA reasoning plugin")
            except Exception as e:
                logger.warning(f"❌ MSA plugin registration failed: {e}")

            # Skip Redis-based plugins for now to avoid import issues
            logger.info("Skipping Redis-based plugins to avoid import issues")

        except ImportError as e:
            logger.warning(f"❌ Plugin import error: {e}")
            logger.info("Kernel will operate with limited functionality")
        except Exception as e:
            logger.error(f"❌ Plugin registration failed: {e}")
            logger.info("Kernel will operate with basic functionality")

    async def reason(self, query: str, **kwargs) -> dict:
        """
        Execute reasoning pipeline for a query.

        Args:
            query: The reasoning query
            **kwargs: Additional parameters

        Returns:
            Reasoning results as dictionary
        """
        try:
            # Get the main reasoning function
            function = self.kernel.get_function("msa_reasoning", "analyze")

            # Execute with arguments
            result = await self.kernel.invoke(function, query=query, **kwargs)

            logger.info(f"Reasoning completed for query: {query[:50]}...")
            return result.value if result and hasattr(result, "value") else {"error": "No result returned"}

        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return {"error": str(e), "error_type": type(e).__name__, "query": query, "status": "failed"}

    async def parse_only(self, text: str) -> dict:
        """Execute only the parsing stage."""
        try:
            function = self.kernel.get_function("msa_reasoning", "parse_vignette")
            result = await self.kernel.invoke(function, text=text)
            return result.value if result and hasattr(result, "value") else {"error": "No parsing result"}
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            return {"error": str(e)}

    async def generate_program(self, synthesis: dict, framework: str = "numpyro") -> str:
        """Generate probabilistic program from synthesis."""
        try:
            function = self.kernel.get_function("msa_reasoning", "generate_program_standalone")
            result = await self.kernel.invoke(function, synthesis=synthesis, framework=framework)
            return result.value if result and hasattr(result, "value") else "# Error: No program generated"
        except Exception as e:
            logger.error(f"Program generation failed: {e}")
            return f"# Error generating program: {e}"

    def get_plugin_info(self) -> dict:
        """Get information about loaded plugins."""
        plugins_info = {}
        for plugin_name, plugin in self.kernel.plugins.items():
            functions = list(plugin.functions.keys())
            plugins_info[plugin_name] = {"functions": functions, "function_count": len(functions)}
        return plugins_info


def create_kernel(settings: MinimalSettings | Settings | None = None) -> ReasoningKernel:
    """Factory function to create a configured kernel."""
    return ReasoningKernel(settings)


# For backward compatibility
async def create_async_kernel(settings: MinimalSettings | Settings | None = None) -> ReasoningKernel:
    """Async factory function for backward compatibility."""
    return create_kernel(settings)
