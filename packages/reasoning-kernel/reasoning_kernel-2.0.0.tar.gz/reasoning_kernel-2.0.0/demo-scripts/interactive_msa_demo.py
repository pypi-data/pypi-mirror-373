#!/usr/bin/env python3
"""
Interactive MSA Demo - Complete Semantic Kernel-based Multi-Stage Analysis
=========================================================================

This interactive demonstration shows the full MSA pipeline in action using
the Semantic Kernel framework for cognitive reasoning orchestration.

Usage:
    uv run python interactive_msa_demo.py

Features:
- Interactive vignette input
- Real-time MSA pipeline execution
- Visual stage progression
- Detailed results display
- Execution history tracking
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

from reasoning_kernel.sk_core.api_integration import create_sk_api_app


class InteractiveMSADemo:
    """Interactive demonstration of the MSA pipeline."""

    def __init__(self):
        self.api_app = None
        self.orchestrator = None
        self.session_history = []

    async def initialize(self) -> bool:
        """Initialize the SK-based MSA system."""
        try:
            print("🔧 Initializing Semantic Kernel MSA System...")
            print("-" * 60)

            # Create SK API application
            self.api_app = await create_sk_api_app()

            # Get orchestrator from the API
            self.orchestrator = self.api_app.extra.get("orchestrator")

            if not self.orchestrator:
                print("❌ Failed to get MSA orchestrator from API")
                return False

            print("✅ MSA System initialized successfully!")
            print("   🧠 SK Kernel: Ready")
            print("   🤖 MSA Orchestrator: Ready")
            print(
                "   🔄 Pipeline Stages: 5 (Parse → Knowledge → Graph → Synthesis → Inference)"
            )
            print()

            return True

        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False

    def display_welcome(self):
        """Display welcome banner."""
        print("=" * 80)
        print("🚀 INTERACTIVE MSA DEMONSTRATION")
        print("   Semantic Kernel-based Multi-Stage Analysis Pipeline")
        print("=" * 80)
        print()
        print(
            "This demo showcases the complete 5-stage MSA cognitive reasoning process:"
        )
        print(
            "  📝 Stage 1: Parse     - Extract entities, relationships, and structure"
        )
        print("  🧠 Stage 2: Knowledge - Retrieve domain-specific knowledge")
        print("  🕸️  Stage 3: Graph     - Build hybrid reasoning networks")
        print("  🔄 Stage 4: Synthesis - Integrate findings comprehensively")
        print("  🎯 Stage 5: Inference - Generate probabilistic conclusions")
        print()
        print("Commands:")
        print("  📖 'examples' - Show sample vignettes")
        print("  📊 'history'  - View execution history")
        print("  🚪 'quit'     - Exit demo")
        print()

    def show_examples(self):
        """Show example vignettes."""
        examples = {
            "🚣 Canoe Racing": """
            In the final stretch of the canoe race, Sarah's team was trailing by two boat lengths.
            The wind picked up from the south, creating choppy waters. Sarah adjusted her stroke
            technique, increasing the cadence while her partner focused on steering. Despite fatigue
            setting in, they managed to close the gap, finishing just half a boat length behind
            the leaders in what many called the closest race of the season.
            """.strip(),
            "🏥 Medical Scenario": """
            The patient presented with chest pain that started 2 hours ago during physical exertion.
            The pain is described as crushing and radiates to the left arm. Vital signs show elevated
            blood pressure and heart rate. The ECG reveals ST-segment elevation in leads II, III,
            and aVF. Given the patient's history of smoking and diabetes, immediate intervention
            was considered critical.
            """.strip(),
            "💼 Business Decision": """
            The startup had to decide between two potential markets for their AI product. The first
            market was healthcare, with high barriers to entry but significant revenue potential.
            The second was education technology, with faster adoption cycles but more competition.
            The team had limited resources and needed to choose wisely, as pivoting later would
            be costly and time-consuming.
            """.strip(),
        }

        print("\n📚 EXAMPLE VIGNETTES:")
        print("-" * 40)
        for title, content in examples.items():
            print(f"\n{title}:")
            print(f'"{content}"')
        print()

    def display_stage_progress(self, stage: str, stage_num: int):
        """Display stage execution progress."""
        stages = ["Parse", "Knowledge", "Graph", "Synthesis", "Inference"]
        progress_bar = ""

        for i, s in enumerate(stages, 1):
            if i < stage_num:
                progress_bar += "✅ "
            elif i == stage_num:
                progress_bar += "🔄 "
            else:
                progress_bar += "⭕ "

        print(f"\n🔄 PIPELINE PROGRESS: {progress_bar}")
        print(f"   Currently executing: Stage {stage_num} - {stage}")

    def format_results(self, results: Dict[str, Any]) -> str:
        """Format MSA results for display."""
        if not results:
            return "No results available"

        formatted = f"""
📊 MSA ANALYSIS RESULTS
{'=' * 50}

🆔 Execution ID: {results.get('execution_id', 'N/A')}
⏱️  Execution Time: {results.get('execution_time', 'N/A')}s
📝 Vignette: {results.get('vignette', 'N/A')[:100]}...

📝 STAGE 1 - PARSE:
{self._format_stage_result(results.get('parse', {}))}

🧠 STAGE 2 - KNOWLEDGE:
{self._format_stage_result(results.get('knowledge', {}))}

🕸️  STAGE 3 - GRAPH:
{self._format_stage_result(results.get('graph', {}))}

🔄 STAGE 4 - SYNTHESIS:
{self._format_stage_result(results.get('synthesis', {}))}

🎯 STAGE 5 - INFERENCE:
{self._format_stage_result(results.get('inference', {}))}

✅ Pipeline Status: {results.get('pipeline_status', 'unknown')}
        """.strip()

        return formatted

    def _format_stage_result(self, stage_result: Dict[str, Any]) -> str:
        """Format individual stage result."""
        if not stage_result:
            return "   No data available"

        # If it's a simple dict, format it nicely
        if isinstance(stage_result, dict):
            lines = []
            for key, value in stage_result.items():
                if isinstance(value, list) and value:
                    lines.append(f"   • {key}: {', '.join(str(v) for v in value[:3])}")
                    if len(value) > 3:
                        lines.append(f"     ... and {len(value) - 3} more")
                else:
                    lines.append(f"   • {key}: {str(value)[:100]}")
            return "\n".join(lines) if lines else "   No structured data"

        return f"   {str(stage_result)[:200]}"

    def show_history(self):
        """Display execution history."""
        if not self.session_history:
            print("\n📊 No executions in this session yet.")
            return

        print(f"\n📊 SESSION HISTORY ({len(self.session_history)} executions):")
        print("-" * 60)

        for i, execution in enumerate(self.session_history, 1):
            timestamp = execution.get("timestamp", "Unknown")
            exec_id = execution.get("execution_id", "N/A")
            vignette_preview = execution.get("vignette", "No vignette")[:60]
            status = execution.get("pipeline_status", "unknown")
            exec_time = execution.get("execution_time", "N/A")

            print(f"{i}. {timestamp}")
            print(f"   ID: {exec_id}")
            print(f"   Vignette: {vignette_preview}...")
            print(f"   Status: {status} ({exec_time}s)")
            print()

    async def analyze_vignette(
        self, vignette: str, analysis_mode: str = "full"
    ) -> Optional[Dict[str, Any]]:
        """Analyze a vignette through the MSA pipeline."""
        try:
            print("\n🚀 Starting MSA Analysis...")
            print(f"📖 Vignette: {vignette[:100]}...")
            print(f"🔧 Mode: {analysis_mode}")

            # Execute the pipeline
            results = await self.orchestrator.execute_msa_pipeline(
                vignette, {"analysis_type": analysis_mode}
            )

            # Add to session history
            execution_record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "vignette": vignette,
                **results,
            }
            self.session_history.append(execution_record)

            return results

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return None

    async def run_interactive_session(self):
        """Run the main interactive session."""
        self.display_welcome()

        if not await self.initialize():
            print("❌ Failed to initialize MSA system. Exiting.")
            return

        print("🎯 Ready for analysis! Enter a vignette to analyze or use commands.")
        print("=" * 80)

        while True:
            try:
                print("\n💭 Enter vignette (or command):")
                user_input = input(">>> ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Thanks for using MSA Demo!")
                    break

                elif user_input.lower() == "examples":
                    self.show_examples()
                    continue

                elif user_input.lower() == "history":
                    self.show_history()
                    continue

                elif user_input.lower() == "help":
                    print("\n📖 Commands:")
                    print("  examples - Show sample vignettes")
                    print("  history  - View execution history")
                    print("  help     - Show this help")
                    print("  quit     - Exit demo")
                    continue

                # Analyze the vignette
                results = await self.analyze_vignette(user_input)

                if results:
                    print(self.format_results(results))
                else:
                    print("❌ Analysis failed. Please try again.")

            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Demo ended. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("Please try again or type 'quit' to exit.")


async def main():
    """Main entry point."""
    demo = InteractiveMSADemo()
    await demo.run_interactive_session()


if __name__ == "__main__":
    print("🚀 Starting Interactive MSA Demo...")
    asyncio.run(main())
