#!/usr/bin/env python3
"""
Semantic Kernel Integration Main Script
=======================================

Main entry point for the Semantic Kernel-based reasoning system.
Replaces the complex orchestrator.py with simplified SK-powered architecture.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add both sk_core and reasoning_kernel to Python path to enable imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(parent_dir))

# Import SK components
from .api_integration import create_sk_api_app
from .kernel_factory import ReasoningKernelFactory
from .sk_orchestrator import MSAOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_sk_integration():
    """
    Test the Semantic Kernel integration with a sample vignette.
    Demonstrates the complete MSA pipeline using SK.
    """

    logger.info("Starting SK Integration Test")

    try:
        # Create SK components
        logger.info("Creating SK kernel factory")
        kernel_factory = ReasoningKernelFactory()

        logger.info("Creating reasoning kernel")
        kernel = await kernel_factory.create_reasoning_kernel()

        logger.info("Creating MSA orchestrator")
        orchestrator = MSAOrchestrator(kernel)

        # Test vignette (CogSci 2025 style)
        test_vignette = """
        Sarah is deciding between two job offers. Company A offers a higher salary but requires
        a long commute. Company B offers a lower salary but allows remote work. Sarah values
        work-life balance but also needs to pay off student loans quickly. She's heard that
        Company A has high employee turnover, but Company B is a startup with uncertain future.
        Sarah has been unemployed for 3 months and is feeling financial pressure.
        """

        logger.info("Executing MSA pipeline on test vignette")

        # Execute MSA pipeline
        results = await orchestrator.execute_msa_pipeline(
            vignette=test_vignette,
            pipeline_config={
                "extraction_mode": "all",
                "domain": "cognitive",
                "graph_type": "hybrid",
                "confidence_threshold": 0.7,
                "inference_type": "bayesian",
            },
        )

        logger.info(f"MSA execution completed: {results.get('pipeline_status')}")

        # Display results
        print("\n" + "=" * 60)
        print("SEMANTIC KERNEL MSA RESULTS")
        print("=" * 60)

        print(f"Execution ID: {results.get('execution_id')}")
        print(f"Status: {results.get('pipeline_status')}")
        print(f"Execution Time: {results.get('execution_time')}")

        # Show stage results (truncated for readability)
        for stage in ["parse", "knowledge", "graph", "synthesis", "inference"]:
            stage_result = results.get(stage, "Not executed")
            if isinstance(stage_result, str) and len(stage_result) > 200:
                stage_result = stage_result[:200] + "..."
            print(f"\n{stage.upper()} Stage:")
            print(f"  {stage_result}")

        print("\n" + "=" * 60)
        print("SK INTEGRATION TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)

        return True

    except Exception as e:
        logger.error(f"SK integration test failed: {e}")
        print(f"\nERROR: {e}")
        return False


async def run_api_server():
    """
    Run the Semantic Kernel API server.
    Replacement for the complex existing API system.
    """

    logger.info("Starting SK API Server")

    try:
        # Create SK-powered API
        app = await create_sk_api_app()

        # Import uvicorn here to avoid import issues
        import uvicorn

        logger.info("SK API Server starting on http://localhost:8000")
        print("\n" + "=" * 50)
        print("SEMANTIC KERNEL API SERVER")
        print("=" * 50)
        print("Server: http://localhost:8000")
        print("Docs: http://localhost:8000/docs")
        print("Health: http://localhost:8000/health")
        print("=" * 50)

        # Run the server
        config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    except ImportError:
        logger.error("uvicorn not installed. Install with: pip install uvicorn")
        print("ERROR: uvicorn required for API server")
        print("Install with: pip install uvicorn")
        return False

    except Exception as e:
        logger.error(f"API server failed: {e}")
        print(f"ERROR: API server failed: {e}")
        return False


async def run_interactive_session():
    """
    Run interactive session for testing MSA analysis.
    Allows users to input vignettes and see MSA results.
    """

    logger.info("Starting Interactive SK MSA Session")

    try:
        # Create SK components
        kernel_factory = ReasoningKernelFactory()
        kernel = await kernel_factory.create_reasoning_kernel()
        orchestrator = MSAOrchestrator(kernel)

        print("\n" + "=" * 50)
        print("INTERACTIVE MSA ANALYSIS SESSION")
        print("Powered by Semantic Kernel")
        print("=" * 50)
        print("Enter vignettes for MSA analysis.")
        print("Type 'quit' to exit, 'help' for commands.")
        print("=" * 50)

        while True:
            print("\nEnter your vignette (or command):")
            user_input = input("> ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            elif user_input.lower() == "help":
                print("\nCommands:")
                print("  help - Show this help")
                print("  quit - Exit the session")
                print("  history - Show execution history")
                print("  latest - Show latest execution result")
                print("  Or enter a vignette for analysis")
                continue
            elif user_input.lower() == "history":
                history = orchestrator.get_execution_history()
                print(f"\nExecution History ({len(history)} total):")
                for i, exec_result in enumerate(history[-5:], 1):
                    print(
                        f"  {i}. {exec_result.get('execution_id')} - {exec_result.get('pipeline_status')}"
                    )
                continue
            elif user_input.lower() == "latest":
                latest = orchestrator.get_latest_execution()
                if latest:
                    print(f"\nLatest Execution: {latest.get('execution_id')}")
                    print(f"Status: {latest.get('pipeline_status')}")
                else:
                    print("\nNo previous executions found.")
                continue
            elif len(user_input) < 10:
                print("Please enter a longer vignette (at least 10 characters).")
                continue

            # Execute MSA analysis
            print(f"\nAnalyzing vignette ({len(user_input)} chars)...")

            try:
                results = await orchestrator.execute_msa_pipeline(
                    vignette=user_input,
                    pipeline_config={
                        "extraction_mode": "all",
                        "domain": "cognitive",
                        "confidence_threshold": 0.6,
                    },
                )

                # Display results
                print("\n--- MSA ANALYSIS RESULTS ---")
                print(f"Execution ID: {results.get('execution_id')}")
                print(f"Status: {results.get('pipeline_status')}")

                # Show key insights from synthesis
                synthesis_result = results.get("synthesis", "")
                if "conclusions" in synthesis_result:
                    print("\nKey Insights:")
                    print(f"  {synthesis_result[:300]}...")
                else:
                    print("\nSynthesis Result:")
                    print(f"  {synthesis_result[:200]}...")

            except Exception as e:
                print(f"Analysis failed: {e}")

    except Exception as e:
        logger.error(f"Interactive session failed: {e}")
        print(f"ERROR: Interactive session failed: {e}")


def main():
    """
    Main entry point for SK integration.

    Usage:
        python sk_main.py test      # Run integration test
        python sk_main.py api       # Start API server
        python sk_main.py interact  # Interactive session
        python sk_main.py           # Show help
    """

    if len(sys.argv) < 2:
        print("Semantic Kernel Reasoning System")
        print("=" * 40)
        print("Usage:")
        print("  python sk_main.py test      # Test SK integration")
        print("  python sk_main.py api       # Start API server")
        print("  python sk_main.py interact  # Interactive session")
        print("  python sk_main.py help      # Show this help")
        return

    command = sys.argv[1].lower()

    if command == "test":
        success = asyncio.run(test_sk_integration())
        sys.exit(0 if success else 1)
    elif command == "api":
        asyncio.run(run_api_server())
    elif command in ["interact", "interactive"]:
        asyncio.run(run_interactive_session())
    elif command == "help":
        print(__doc__)
    else:
        print(f"Unknown command: {command}")
        print("Use 'python sk_main.py help' for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
