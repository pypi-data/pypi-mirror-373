from __future__ import annotations

from fastapi import FastAPI

# Create FastAPI app
app = FastAPI(title="Reasoning Kernel")

# Routers: import locally to avoid circulars if tests patch modules
try:
    from .api.v1.reasoning_endpoints import router as v1_reasoning_router

    app.include_router(v1_reasoning_router)
except Exception:
    pass

try:
    from .api.streaming_endpoints import router as streaming_router

    # Router already defines full /api/v2 paths for websocket
    app.include_router(streaming_router)
except Exception:
    pass

try:
    from .api.visualization_endpoints import router as viz_router

    app.include_router(viz_router, prefix="/api/v2/visualization")
except Exception:
    pass

try:
    from .api.msa_endpoints import router as msa_router

    app.include_router(msa_router)
except Exception:
    pass

try:
    from .api.cache_endpoints import router as cache_router

    app.include_router(cache_router)
except Exception:
    pass
