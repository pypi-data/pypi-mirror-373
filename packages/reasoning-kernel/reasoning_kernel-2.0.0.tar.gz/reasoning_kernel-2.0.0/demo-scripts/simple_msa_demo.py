#!/usr/bin/env python3
"""
Interactive MSA Demo - Complete Semantic Kernel-based Multi-Stage Analysis
=========================================================================

Usage:
    uv run python simple_msa_demo.py
"""

import asyncio

from reasoning_kernel.sk_core.kernel_factory import ReasoningKernelFactory
from reasoning_kernel.sk_core.sk_orchestrator import MSAOrchestrator


async def main():
    """Simple MSA demo."""
    print("🚀 Simple MSA Demo")
    print("=" * 50)

    try:
        # Initialize SK components
        print("🔧 Initializing Semantic Kernel...")
        kernel_factory = ReasoningKernelFactory()
        kernel = await kernel_factory.create_reasoning_kernel()
        orchestrator = MSAOrchestrator(kernel)

        print("✅ MSA System ready!")
        print("\nExample vignettes:")
        print("1. 'The canoe race was intense with challenging weather conditions'")
        print("2. 'quit' to exit")
        print()

        while True:
            vignette = input("Enter vignette: ").strip()

            if not vignette or vignette.lower() == "quit":
                print("👋 Goodbye!")
                break

            print(f"\n🔄 Analyzing: {vignette[:60]}...")

            try:
                results = await orchestrator.execute_msa_pipeline(vignette)

                print("\n📊 Results:")
                print(f"  Execution ID: {results.get('execution_id', 'N/A')}")
                print(f"  Status: {results.get('pipeline_status', 'unknown')}")
                print(f"  Time: {results.get('execution_time', 'N/A')}s")

                if results.get("parse"):
                    print("  Parse stage: ✅")
                if results.get("knowledge"):
                    print("  Knowledge stage: ✅")
                if results.get("graph"):
                    print("  Graph stage: ✅")
                if results.get("synthesis"):
                    print("  Synthesis stage: ✅")
                if results.get("inference"):
                    print("  Inference stage: ✅")

                print()

            except Exception as e:
                print(f"❌ Analysis failed: {e}")

    except Exception as e:
        print(f"❌ Initialization failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
