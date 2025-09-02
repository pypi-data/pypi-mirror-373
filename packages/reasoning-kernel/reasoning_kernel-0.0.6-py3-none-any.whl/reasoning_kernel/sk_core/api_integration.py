"""
Semantic Kernel API Integration
===============================

Simplified API endpoints using Semantic Kernel orchestration.
Replaces the complex existing API system with SK-powered endpoints.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from semantic_kernel import Kernel

from .kernel_factory import ReasoningKernelFactory
from .settings_adapter import SKSettingsAdapter
from .sk_orchestrator import MSAOrchestrator, SequentialReasoningOrchestrator

logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class VignetteRequest(BaseModel):
    """Request model for vignette analysis"""

    vignette: str = Field(..., description="The vignette text to analyze")
    analysis_type: str = Field(
        default="full",
        description="Type of analysis: 'full', 'sequential', 'collaborative'",
    )
    config: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional configuration parameters"
    )


class MSAStageRequest(BaseModel):
    """Request model for individual MSA stage analysis"""

    vignette: str = Field(..., description="The vignette text to analyze")
    stage: str = Field(
        ...,
        description="MSA stage: 'parse', 'knowledge', 'graph', 'synthesis', 'inference'",
    )
    stage_config: Optional[Dict[str, Any]] = Field(
        default=None, description="Stage-specific configuration"
    )


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""

    execution_id: str
    status: str
    results: Dict[str, Any]
    execution_time: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    sk_services: Dict[str, bool]
    timestamp: str


class SKReasoningAPI:
    """
    Semantic Kernel-powered Reasoning API.

    Provides simplified endpoints that leverage SK orchestration
    instead of the complex existing API architecture.
    """

    def __init__(self):
        self.app = FastAPI(
            title="Reasoning Kernel SK API",
            description="Semantic Kernel-powered reasoning and analysis API",
            version="2.0.0",
        )

        # Initialize SK components
        self.settings_adapter = SKSettingsAdapter()
        self.kernel_factory = ReasoningKernelFactory()
        self.kernel: Optional[Kernel] = None
        self.orchestrator: Optional[MSAOrchestrator] = None
        self.sequential_orchestrator: Optional[SequentialReasoningOrchestrator] = None

        # Setup API routes
        self._setup_routes()

    async def initialize(self):
        """Initialize SK kernel and orchestrators"""
        try:
            logger.info("Initializing Semantic Kernel components")

            # Create kernel
            self.kernel = await self.kernel_factory.create_reasoning_kernel()

            # Create orchestrators
            self.orchestrator = MSAOrchestrator(self.kernel)
            self.sequential_orchestrator = SequentialReasoningOrchestrator(self.kernel)

            logger.info("SK API initialization completed successfully")

        except Exception as e:
            logger.error(f"SK API initialization failed: {e}")
            raise

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""

            sk_services = {
                "kernel_initialized": self.kernel is not None,
                "azure_openai": False,
                "redis_memory": False,
            }

            # Check SK services if kernel is available
            if self.kernel:
                try:
                    sk_services["azure_openai"] = (
                        self.kernel.get_service("azure_openai_chat") is not None
                    )
                except Exception:
                    pass

                try:
                    # Simple check for memory services
                    sk_services["redis_memory"] = (
                        "redis" in str(type(self.kernel)).lower()
                    )
                except Exception:
                    pass

            return HealthResponse(
                status="healthy" if self.kernel else "initializing",
                version="2.0.0-sk",
                sk_services=sk_services,
                timestamp=datetime.now().isoformat(),
            )

        @self.app.post("/analyze", response_model=AnalysisResponse)
        async def analyze_vignette(request: VignetteRequest):
            """
            Analyze a vignette using MSA methodology powered by Semantic Kernel.

            Supports different analysis types:
            - 'full': Complete MSA pipeline with all stages
            - 'sequential': Simple sequential execution
            - 'collaborative': Multi-iteration collaborative reasoning
            """

            if not self.orchestrator:
                raise HTTPException(
                    status_code=503,
                    detail="Service not initialized. SK orchestrator unavailable.",
                )

            try:
                logger.info(f"Starting vignette analysis: {request.analysis_type}")

                # Execute based on analysis type
                if request.analysis_type == "collaborative":
                    results = await self.orchestrator.execute_collaborative_reasoning(
                        vignette=request.vignette, collaboration_config=request.config
                    )
                else:
                    results = await self.orchestrator.execute_msa_pipeline(
                        vignette=request.vignette, pipeline_config=request.config
                    )

                return AnalysisResponse(
                    execution_id=results.get("execution_id", "unknown"),
                    status=results.get("pipeline_status", "unknown"),
                    results=results,
                    execution_time=results.get("execution_time"),
                    error=results.get("error"),
                )

            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Analysis failed: {str(e)}"
                )

        @self.app.post("/analyze/stage", response_model=AnalysisResponse)
        async def analyze_stage(request: MSAStageRequest):
            """
            Analyze a vignette using a specific MSA stage only.

            Useful for focused analysis or debugging individual stages.
            """

            if not self.sequential_orchestrator:
                raise HTTPException(
                    status_code=503,
                    detail="Service not initialized. Sequential orchestrator unavailable.",
                )

            try:
                logger.info(f"Starting stage analysis: {request.stage}")

                # Execute single stage analysis
                stage_result = (
                    await self.sequential_orchestrator.execute_stage_analysis(
                        vignette=request.vignette,
                        stage=request.stage,
                        stage_config=json.dumps(request.stage_config or {}),
                    )
                )

                execution_id = (
                    f"stage_{request.stage}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )

                return AnalysisResponse(
                    execution_id=execution_id,
                    status="completed",
                    results={"stage": request.stage, "result": stage_result},
                    execution_time=datetime.now().isoformat(),
                )

            except Exception as e:
                logger.error(f"Stage analysis failed: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Stage analysis failed: {str(e)}"
                )

        @self.app.get("/history")
        async def get_execution_history():
            """Get execution history from orchestrator"""

            if not self.orchestrator:
                raise HTTPException(status_code=503, detail="Service not initialized")

            try:
                history = self.orchestrator.get_execution_history()
                return {
                    "total_executions": len(history),
                    "history": history[-10:],
                }  # Last 10 executions

            except Exception as e:
                logger.error(f"Failed to retrieve history: {e}")
                raise HTTPException(
                    status_code=500, detail=f"History retrieval failed: {str(e)}"
                )

        @self.app.get("/history/latest")
        async def get_latest_execution():
            """Get the most recent execution result"""

            if not self.orchestrator:
                raise HTTPException(status_code=503, detail="Service not initialized")

            try:
                latest = self.orchestrator.get_latest_execution()
                if not latest:
                    raise HTTPException(status_code=404, detail="No executions found")

                return latest

            except Exception as e:
                logger.error(f"Failed to retrieve latest execution: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Latest execution retrieval failed: {str(e)}",
                )

        @self.app.post("/kernel/reload")
        async def reload_kernel():
            """Reload the SK kernel with fresh configuration"""

            try:
                logger.info("Reloading SK kernel")
                await self.initialize()

                return {
                    "status": "reloaded",
                    "timestamp": datetime.now().isoformat(),
                    "kernel_id": str(id(self.kernel)),
                }

            except Exception as e:
                logger.error(f"Kernel reload failed: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Kernel reload failed: {str(e)}"
                )


# Factory function to create the API app
async def create_sk_api_app() -> FastAPI:
    """
    Create and initialize the Semantic Kernel API application.

    Returns:
        Configured FastAPI app with SK integration
    """

    logger.info("Creating SK API application")

    # Create API instance
    api = SKReasoningAPI()

    # Initialize SK components
    await api.initialize()

    logger.info("SK API application created successfully")

    return api.app


# For direct usage
def get_api_instance() -> SKReasoningAPI:
    """Get API instance for direct usage"""
    return SKReasoningAPI()


# Export main components
__all__ = [
    "SKReasoningAPI",
    "VignetteRequest",
    "MSAStageRequest",
    "AnalysisResponse",
    "HealthResponse",
    "create_sk_api_app",
    "get_api_instance",
]
