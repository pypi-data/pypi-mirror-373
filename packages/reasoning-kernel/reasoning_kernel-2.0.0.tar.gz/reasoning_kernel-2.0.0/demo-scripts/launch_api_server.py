#!/usr/bin/env python3
"""
FastAPI Server Launcher for SK-Powered MSA API
==============================================

Launches the Semantic Kernel-powered Multi-Stage Analysis API server.
"""

import asyncio
import sys
from pathlib import Path

import uvicorn

# Add reasoning_kernel to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


async def main():
    """Launch the FastAPI server"""
    try:
        from reasoning_kernel.sk_core.api_integration import create_sk_api_app

        print("🚀 Starting SK-powered MSA API server...")
        print("=" * 60)

        # Create the app
        print("🔧 Initializing SK API...")
        app = await create_sk_api_app()

        print("✅ SK API initialized successfully!")
        print("🌐 Starting server on http://localhost:8000")
        print("📚 API docs available at: http://localhost:8000/docs")
        print("❤️  Health check: http://localhost:8000/health")

        # Configuration for the server
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False,  # Disable reload since we have async initialization
        )

        server = uvicorn.Server(config)
        await server.serve()

    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested by user")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("🚀 SK-MSA API Server")
    print("=" * 40)
    asyncio.run(main())
