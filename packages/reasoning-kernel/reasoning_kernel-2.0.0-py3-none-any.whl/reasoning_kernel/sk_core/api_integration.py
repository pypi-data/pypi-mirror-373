"""
Semantic Kernel API Integration
===============================

Modern FastAPI integration with enhanced SK architecture and MSA plugins.
Built on top of Tasks 1-5 foundation: unified settings, kernel management,
enhanced plugins, and validated service integration.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from ..config import create_settings
from ..sk_core.kernel_manager import create_kernel

logger = logging.getLogger(__name__)


# Setup basic logging since utils may not be available
def setup_basic_logging(level: str = "INFO"):
    """Setup basic logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


# Request/Response Models
class MSAAnalysisRequest(BaseModel):
    """Request for MSA analysis using enhanced plugins."""

    query: str = Field(..., description="Query to analyze")
    domain: str | None = Field(None, description="Domain context (e.g., 'environmental', 'business')")
    plugin_type: str | None = Field("enhanced", description="Plugin type: 'simple' or 'enhanced'")
    use_ai: bool | None = Field(True, description="Whether to use AI-powered analysis")


class MSAAnalysisResponse(BaseModel):
    """Response from MSA analysis."""

    success: bool = Field(..., description="Whether analysis succeeded")
    result: dict[str, Any] = Field(..., description="Analysis results")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Request metadata")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    components: dict[str, Any] = Field(default_factory=dict, description="Component health")


class KernelFunctionRequest(BaseModel):
    """Request for kernel function execution."""

    plugin_name: str = Field(..., description="Plugin name")
    function_name: str = Field(..., description="Function name")
    arguments: dict[str, Any] = Field(default_factory=dict, description="Function arguments")


class KernelFunctionResponse(BaseModel):
    """Response from kernel function execution."""

    success: bool = Field(..., description="Whether execution succeeded")
    result: Any | None = Field(None, description="Function result")
    error: str | None = Field(None, description="Error message if failed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Execution metadata")


# Global kernel instance
kernel = None
app_settings = None


async def get_kernel():
    """Get the global kernel instance."""
    global kernel
    if kernel is None:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    return kernel


async def get_settings():
    """Get the global settings instance."""
    global app_settings
    if app_settings is None:
        raise HTTPException(status_code=503, detail="Settings not initialized")
    return app_settings


async def create_sk_api_app() -> FastAPI:
    """Create and configure the FastAPI application with SK integration."""
    global kernel, app_settings

    # Initialize settings and kernel
    app_settings = create_settings()
    setup_basic_logging(app_settings.log_level)

    logger.info("🔧 Creating SK-powered API application...")

    # Create FastAPI app
    app = FastAPI(
        title="Reasoning Kernel API",
        description="Semantic Kernel-powered Multi-Stage Analysis API with enhanced MSA plugins",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize kernel
    try:
        logger.info("🧠 Initializing Semantic Kernel...")
        kernel = await create_kernel(app_settings)
        logger.info("✅ Semantic Kernel initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize kernel: {e}")
        raise

    # Register routes
    register_routes(app)

    logger.info("🚀 API application created successfully")
    return app


def register_routes(app: FastAPI) -> None:
    """Register all API routes."""

    @app.get("/", include_in_schema=False)
    async def root():
        """Root endpoint - redirect to docs."""
        return RedirectResponse(url="/docs")

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        try:
            kernel_instance = await get_kernel()
            settings = await get_settings()

            # Check kernel health
            kernel_healthy = kernel_instance is not None

            # Check service health
            service_health = {}
            try:
                # Test if we can get a service
                chat_service = kernel_instance.get_service("azure_openai")
                service_health["azure_openai"] = chat_service is not None
            except Exception:
                service_health["azure_openai"] = False

            components = {
                "kernel": kernel_healthy,
                "settings": settings is not None,
                "services": service_health,
            }

            overall_status = "healthy" if all(components.values()) else "degraded"

            return HealthResponse(status=overall_status, version="2.0.0", components=components)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthResponse(status="unhealthy", version="2.0.0", components={"error": str(e)})

    @app.post("/api/v2/msa/analyze", response_model=MSAAnalysisResponse)
    async def analyze_with_msa(
        request: MSAAnalysisRequest, background_tasks: BackgroundTasks, kernel_instance=Depends(get_kernel)
    ):
        """Analyze query using enhanced MSA plugins."""
        try:
            logger.info(f"🔍 Starting MSA analysis for query: {request.query[:50]}...")

            # Determine which plugin to use
            if request.plugin_type == "simple":
                plugin_name = "MSAReasoningPlugin"
            else:
                plugin_name = "EnhancedMSAReasoningPlugin"

            # Get the plugin
            plugin = None
            for registered_plugin in kernel_instance.plugins:
                if plugin_name in str(type(registered_plugin)):
                    plugin = registered_plugin
                    break

            if plugin is None:
                # Try to import and add the plugin
                if request.plugin_type == "simple":
                    from ..plugins.msa_reasoning_simple import MSAReasoningPlugin

                    plugin = MSAReasoningPlugin()
                else:
                    from ..plugins.msa_reasoning_enhanced import EnhancedMSAReasoningPlugin

                    plugin = EnhancedMSAReasoningPlugin()

                kernel_instance.add_plugin(plugin, plugin_name)
                logger.info(f"✅ Added {plugin_name} to kernel")

            # Execute analysis
            if hasattr(plugin, "analyze"):
                if request.plugin_type == "enhanced" and request.use_ai:
                    # Enhanced plugin with kernel for AI capabilities
                    result = await plugin.analyze(query=request.query, domain=request.domain, kernel=kernel_instance)
                else:
                    # Simple plugin or enhanced without AI
                    result = await plugin.analyze(query=request.query, domain=request.domain)
            else:
                raise HTTPException(status_code=500, detail=f"Plugin {plugin_name} does not have analyze method")

            # Add background task to log successful analysis
            background_tasks.add_task(log_analysis_completion, request.query, result.get("status", "unknown"))

            return MSAAnalysisResponse(
                success=True,
                result=result,
                metadata={
                    "plugin_type": request.plugin_type,
                    "use_ai": request.use_ai,
                    "domain": request.domain,
                    "query_length": len(request.query),
                },
            )

        except Exception as e:
            logger.error(f"MSA analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    @app.post("/api/v2/kernel/execute", response_model=KernelFunctionResponse)
    async def execute_kernel_function(request: KernelFunctionRequest, kernel_instance=Depends(get_kernel)):
        """Execute a kernel function directly."""
        try:
            logger.info(f"⚙️ Executing {request.plugin_name}.{request.function_name}")

            # Get the function from kernel
            try:
                function = kernel_instance.get_function(request.plugin_name, request.function_name)
            except Exception as e:
                raise HTTPException(
                    status_code=404,
                    detail=f"Function {request.plugin_name}.{request.function_name} not found: {str(e)}",
                )

            # Execute the function
            try:
                result = await kernel_instance.invoke(function, **request.arguments)

                # Extract the result value
                if hasattr(result, "value"):
                    result_value = result.value
                else:
                    result_value = str(result)

                return KernelFunctionResponse(
                    success=True,
                    result=result_value,
                    error=None,
                    metadata={
                        "plugin_name": request.plugin_name,
                        "function_name": request.function_name,
                        "arguments": request.arguments,
                    },
                )

            except Exception as e:
                logger.error(f"Function execution failed: {e}")
                return KernelFunctionResponse(
                    success=False,
                    result=None,
                    error=str(e),
                    metadata={
                        "plugin_name": request.plugin_name,
                        "function_name": request.function_name,
                        "arguments": request.arguments,
                    },
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Kernel function execution error: {e}")
            raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

    @app.get("/api/v2/plugins")
    async def list_plugins(kernel_instance=Depends(get_kernel)):
        """List all available plugins and their functions."""
        try:
            plugins_info = []

            for plugin in kernel_instance.plugins:
                plugin_info = {"name": type(plugin).__name__, "functions": []}

                # Get function names from plugin
                for attr_name in dir(plugin):
                    attr = getattr(plugin, attr_name)
                    if callable(attr) and not attr_name.startswith("_") and hasattr(attr, "__annotations__"):
                        plugin_info["functions"].append(
                            {"name": attr_name, "description": getattr(attr, "__doc__", "No description available")}
                        )

                plugins_info.append(plugin_info)

            return {"plugins": plugins_info, "total_plugins": len(plugins_info)}

        except Exception as e:
            logger.error(f"Failed to list plugins: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to list plugins: {str(e)}")


async def log_analysis_completion(query: str, status: str):
    """Background task to log analysis completion."""
    logger.info(f"📊 Analysis completed - Query: {query[:30]}..., Status: {status}")


# Factory function for backwards compatibility
async def create_api_app() -> FastAPI:
    """Create API app - backwards compatibility alias."""
    return await create_sk_api_app()
