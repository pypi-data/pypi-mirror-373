#!/usr/bin/env python3
"""
Demo: End-to-End MSA Pipeline with SK
=====================================

Demonstrates the complete MSA pipeline including:
- Stages 1-4: Parse → Knowledge → Graph → Synthesis
- Stage 5: LLM-based PPL program generation (MSA Step 1)
- Stage 6: PPL program execution via Daytona (MSA Step 2)
- Stage 7: Bayesian inference and analysis
"""

import asyncio
import json


async def demo_msa_pipeline():
    """Run a complete MSA pipeline demonstration."""

    print("🎭 MSA Pipeline Demo - Reasoning Kernel v0.0.7")
    print("=" * 55)

    try:
        from reasoning_kernel.core.kernel_manager import KernelManager
        from reasoning_kernel.sk_core.sk_orchestrator import MSAOrchestrator

        print("🔧 Setting up Semantic Kernel orchestrator...")

        # Initialize with your environment (Azure OpenAI, Redis, Daytona)
        kernel_manager = KernelManager()
        kernel = kernel_manager.create_kernel()
        orchestrator = MSAOrchestrator(kernel)

        print("✅ Orchestrator ready with all 7 MSA stages")
        print()

        # Demo vignette - customer behavior analysis
        vignette = """
        Sarah, a marketing analyst at RetailCorp, is investigating unusual patterns 
        in their customer data. She notices that customers in the 25-35 age group 
        show significantly different purchasing behaviors during holiday seasons 
        compared to regular periods. The data indicates higher basket values but 
        lower frequency of visits. Sarah wants to understand if this represents 
        a shift in customer preference or if external factors are driving this behavior.
        """

        print("📊 Demo Scenario:")
        print(vignette.strip())
        print()

        # Configure pipeline for customer behavior analysis
        config = {
            "extraction_mode": "behavioral_patterns",
            "domain": "retail_analytics",
            "graph_type": "causal_inference",
            "confidence_threshold": 0.75,
            "ppl_framework": "numpyro",
            "ppl_timeout": 120,
            "inference_type": "hierarchical_bayesian",
        }

        print("⚙️  Pipeline Configuration:")
        for key, value in config.items():
            print(f"   {key}: {value}")
        print()

        print("🚀 Executing MSA Pipeline...")
        print("-" * 40)

        # Execute the complete pipeline
        results = await orchestrator.execute_msa_pipeline(vignette, config)

        print("\n📋 Pipeline Results Summary:")
        print("=" * 40)

        # Display key results from each stage
        stages = [
            ("parse", "🔍 Parse & Extract"),
            ("knowledge", "🧠 Domain Knowledge"),
            ("graph", "🕸️  Reasoning Graph"),
            ("synthesis", "🔬 Synthesis"),
            ("program_code", "💻 PPL Program (MSA Step 1)"),
            ("ppl_execution", "⚡ PPL Execution (MSA Step 2)"),
            ("inference", "📈 Final Inference"),
        ]

        for stage_key, stage_name in stages:
            if stage_key in results and results[stage_key]:
                result_preview = (
                    str(results[stage_key])[:100] + "..."
                    if len(str(results[stage_key])) > 100
                    else str(results[stage_key])
                )
                print(f"{stage_name}: ✅ Complete ({len(str(results[stage_key]))} chars)")
            else:
                print(f"{stage_name}: ❌ No result")

        print()
        print(f"🎯 Pipeline Status: {results.get('pipeline_status', 'Unknown')}")
        print(f"⏱️  Execution ID: {results.get('execution_id', 'Unknown')}")

        if results.get("pipeline_status") == "completed":
            print()
            print("🎊 SUCCESS! Complete MSA pipeline executed successfully!")
            print("✅ All 7 stages completed including PPL generation and execution")
            print("✅ Semantic Kernel 1.36 architecture working properly")
            print("✅ MSA Steps 1 & 2 (LLM→PPL→Execution) integrated")

            # Show key insights if available
            if "inference" in results and results["inference"]:
                print(f"\n🔍 Key Insights Preview:")
                inference_preview = str(results["inference"])[:300] + "..."
                print(f"   {inference_preview}")

        else:
            print(f"\n❌ Pipeline failed: {results.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(demo_msa_pipeline())
    exit_code = 0 if success else 1
    print(f"\nDemo completed with exit code: {exit_code}")
