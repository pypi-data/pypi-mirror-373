"""
Examples and Demonstrations of MSA Prompt Templates

This module provides comprehensive examples of how to use the MSA prompt templates
for enhanced natural language reasoning in the unified architecture.
"""

import asyncio
import json
from typing import Dict, Any

from reasoning_kernel.prompts.prompt_manager import get_prompt_manager, PromptContext
from reasoning_kernel.prompts.msa_prompt_templates import get_msa_templates


class MSAPromptExamples:
    """Examples and demonstrations of MSA prompt template usage"""
    
    def __init__(self):
        self.templates = get_msa_templates()
        self.prompt_manager = None
    
    async def initialize(self, gpt5_connector=None):
        """Initialize with GPT-5 connector"""
        self.prompt_manager = await get_prompt_manager(gpt5_connector)
    
    async def demonstrate_parse_stage(self, scenario: str) -> Dict[str, Any]:
        """Demonstrate parse stage prompt templates"""
        print("🔍 PARSE STAGE DEMONSTRATION")
        print("=" * 50)
        
        context = PromptContext(
            stage="parse",
            scenario=scenario,
            session_id="demo_session",
            enhanced_mode=True,
            verbose=True
        )
        
        results = {}
        
        # 1. Causal Structure Analysis
        print("\n1. Causal Structure Analysis")
        print("-" * 30)
        
        causal_response = await self.prompt_manager.execute_prompt(
            "parse_causal_structure",
            context,
            context="Demonstration of causal structure analysis"
        )
        
        results["causal_structure"] = {
            "response": causal_response.content,
            "tokens_used": causal_response.usage.get("total_tokens", 0),
            "response_time": causal_response.response_time
        }
        
        print(f"✅ Generated causal structure description ({causal_response.usage.get('total_tokens', 0)} tokens)")
        
        # 2. Entity Extraction
        print("\n2. Entity and Causal Factor Extraction")
        print("-" * 40)
        
        entity_response = await self.prompt_manager.execute_prompt(
            "entity_extraction",
            context,
            natural_description=causal_response.content[:500]  # Use first part of causal structure
        )
        
        results["entities"] = {
            "response": entity_response.content,
            "tokens_used": entity_response.usage.get("total_tokens", 0),
            "response_time": entity_response.response_time
        }
        
        print(f"✅ Extracted entities and factors ({entity_response.usage.get('total_tokens', 0)} tokens)")
        
        # 3. Concept Trace Generation
        print("\n3. Concept Trace with Dependencies")
        print("-" * 35)
        
        concept_response = await self.prompt_manager.execute_prompt(
            "concept_trace_generation",
            context,
            natural_description=causal_response.content,
            entities=["entity1", "entity2"],  # Would be parsed from entity_response
            causal_factors=["factor1", "factor2"]  # Would be parsed from entity_response
        )
        
        results["concept_trace"] = {
            "response": concept_response.content,
            "tokens_used": concept_response.usage.get("total_tokens", 0),
            "response_time": concept_response.response_time
        }
        
        print(f"✅ Generated concept trace ({concept_response.usage.get('total_tokens', 0)} tokens)")
        
        return results
    
    async def demonstrate_knowledge_stage(self, scenario: str, parse_results: Dict[str, Any]) -> Dict[str, Any]:
        """Demonstrate knowledge stage prompt templates"""
        print("\n\n🧠 KNOWLEDGE STAGE DEMONSTRATION")
        print("=" * 50)
        
        context = PromptContext(
            stage="knowledge",
            scenario=scenario,
            session_id="demo_session",
            enhanced_mode=True,
            verbose=True,
            previous_results={"parse": {"data": parse_results}}
        )
        
        results = {}
        
        # 1. Background Knowledge Synthesis
        print("\n1. Background Knowledge Synthesis")
        print("-" * 35)
        
        background_response = await self.prompt_manager.execute_prompt(
            "background_knowledge",
            context,
            entities=["student", "exam", "performance"],
            concepts=["ability", "effort", "outcome"],
            domain="education",
            previous_analysis=str(parse_results)
        )
        
        results["background_knowledge"] = {
            "response": background_response.content,
            "tokens_used": background_response.usage.get("total_tokens", 0),
            "response_time": background_response.response_time
        }
        
        print(f"✅ Synthesized background knowledge ({background_response.usage.get('total_tokens', 0)} tokens)")
        
        # 2. Knowledge Integration
        print("\n2. Multi-Source Knowledge Integration")
        print("-" * 40)
        
        integration_response = await self.prompt_manager.execute_prompt(
            "knowledge_synthesis",
            context,
            retrieved_knowledge="External knowledge sources...",
            background_knowledge=background_response.content,
            domain_context="Educational assessment scenario",
            quality_criteria="Accuracy, relevance, completeness",
            confidence_assessment="High confidence in domain knowledge"
        )
        
        results["knowledge_integration"] = {
            "response": integration_response.content,
            "tokens_used": integration_response.usage.get("total_tokens", 0),
            "response_time": integration_response.response_time
        }
        
        print(f"✅ Integrated knowledge sources ({integration_response.usage.get('total_tokens', 0)} tokens)")
        
        return results
    
    async def demonstrate_confidence_assessment(self, scenario: str, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Demonstrate confidence assessment template"""
        print("\n\n📊 CONFIDENCE ASSESSMENT DEMONSTRATION")
        print("=" * 50)
        
        context = PromptContext(
            stage="assessment",
            scenario=scenario,
            session_id="demo_session",
            enhanced_mode=True,
            verbose=True
        )
        
        # Confidence Assessment
        print("\n1. Comprehensive Confidence Analysis")
        print("-" * 40)
        
        confidence_response = await self.prompt_manager.execute_prompt(
            "confidence_assessment",
            context,
            analysis_results=json.dumps(all_results, indent=2),
            stage="overall",
            metrics={"stages_completed": 2, "total_tokens": 1500, "processing_time": 45.2}
        )
        
        result = {
            "response": confidence_response.content,
            "tokens_used": confidence_response.usage.get("total_tokens", 0),
            "response_time": confidence_response.response_time
        }
        
        print(f"✅ Assessed confidence and reliability ({confidence_response.usage.get('total_tokens', 0)} tokens)")
        
        return result
    
    async def demonstrate_final_synthesis(self, scenario: str, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Demonstrate final synthesis template"""
        print("\n\n🎯 FINAL SYNTHESIS DEMONSTRATION")
        print("=" * 50)
        
        context = PromptContext(
            stage="synthesis",
            scenario=scenario,
            session_id="demo_session",
            enhanced_mode=True,
            verbose=True
        )
        
        # Final Answer Synthesis
        print("\n1. Comprehensive Final Answer")
        print("-" * 35)
        
        synthesis_response = await self.prompt_manager.execute_prompt(
            "final_synthesis",
            context,
            stage_results=json.dumps(all_results, indent=2),
            insights=["High conceptual complexity", "Strong causal relationships", "Moderate uncertainty"],
            confidence_score=0.82,
            session_context="Educational assessment analysis",
            user_requirements="Comprehensive analysis with actionable insights"
        )
        
        result = {
            "response": synthesis_response.content,
            "tokens_used": synthesis_response.usage.get("total_tokens", 0),
            "response_time": synthesis_response.response_time
        }
        
        print(f"✅ Generated final synthesis ({synthesis_response.usage.get('total_tokens', 0)} tokens)")
        
        return result
    
    async def run_complete_demonstration(self, scenario: str = None) -> Dict[str, Any]:
        """Run complete demonstration of MSA prompt templates"""
        if scenario is None:
            scenario = """
            BACKGROUND
            In this model, students are being evaluated for their science class, which has a two part exam 
            that combines their performance on a written exam and a laboratory portion. These exams are 
            completed in pairs, so sets of students collectively take evaluations.

            CONDITIONS
            In the first evaluation, Barbara and Ajax passed.
            In the second evaluation, Barbara and Lou failed.
            In the third evaluation, Barbara and Casey passed.
            In the fourth evaluation, Lou and Casey passed.

            QUERIES
            Query 1: Out of 100 random students, where do you think Barbara ranks in terms of intrinsic memorization ability?
            Query 2: How well do you think Barbara performed on the laboratory portion in the second evaluation?
            Query 3: In a new evaluation, who would do better, Barbara and Lou or Casey and Ajax?
            """
        
        print("🚀 MSA PROMPT TEMPLATES COMPLETE DEMONSTRATION")
        print("=" * 60)
        print(f"Scenario: {scenario[:100]}...")
        
        all_results = {}
        
        try:
            # Parse Stage
            parse_results = await self.demonstrate_parse_stage(scenario)
            all_results["parse"] = parse_results
            
            # Knowledge Stage
            knowledge_results = await self.demonstrate_knowledge_stage(scenario, parse_results)
            all_results["knowledge"] = knowledge_results
            
            # Confidence Assessment
            confidence_results = await self.demonstrate_confidence_assessment(scenario, all_results)
            all_results["confidence"] = confidence_results
            
            # Final Synthesis
            synthesis_results = await self.demonstrate_final_synthesis(scenario, all_results)
            all_results["synthesis"] = synthesis_results
            
            # Summary
            print("\n\n📈 DEMONSTRATION SUMMARY")
            print("=" * 50)
            
            total_tokens = sum(
                stage_data.get("tokens_used", 0) 
                for stage_results in all_results.values() 
                for stage_data in (stage_results.values() if isinstance(stage_results, dict) else [stage_results])
                if isinstance(stage_data, dict)
            )
            
            total_time = sum(
                stage_data.get("response_time", 0) 
                for stage_results in all_results.values() 
                for stage_data in (stage_results.values() if isinstance(stage_results, dict) else [stage_results])
                if isinstance(stage_data, dict)
            )
            
            print(f"✅ Total tokens used: {total_tokens}")
            print(f"✅ Total processing time: {total_time:.2f}s")
            print(f"✅ Stages completed: {len(all_results)}")
            print(f"✅ Templates demonstrated: {sum(len(stage) if isinstance(stage, dict) else 1 for stage in all_results.values())}")
            
            return all_results
            
        except Exception as e:
            print(f"❌ Demonstration failed: {e}")
            return {"error": str(e), "partial_results": all_results}
    
    def display_template_catalog(self):
        """Display catalog of available templates"""
        print("📚 MSA PROMPT TEMPLATE CATALOG")
        print("=" * 50)
        
        templates_by_type = {}
        for template_name in self.templates.list_templates():
            template_info = self.templates.get_template_info(template_name)
            template_type = template_info.get("type", "unknown")
            
            if template_type not in templates_by_type:
                templates_by_type[template_type] = []
            
            templates_by_type[template_type].append({
                "name": template_name,
                "description": template_info.get("description", ""),
                "variables": template_info.get("variables", []),
                "thinking_effort": template_info.get("thinking_effort", "medium"),
                "max_tokens": template_info.get("max_tokens", 1024)
            })
        
        for template_type, templates in templates_by_type.items():
            print(f"\n🔧 {template_type.upper().replace('_', ' ')} TEMPLATES")
            print("-" * 40)
            
            for template in templates:
                print(f"  📝 {template['name']}")
                print(f"     Description: {template['description']}")
                print(f"     Variables: {', '.join(template['variables'][:3])}{'...' if len(template['variables']) > 3 else ''}")
                print(f"     Thinking Effort: {template['thinking_effort']} | Max Tokens: {template['max_tokens']}")
                print()


async def run_demonstration():
    """Run the complete MSA prompt templates demonstration"""
    examples = MSAPromptExamples()
    
    # Initialize without GPT-5 connector for demonstration
    await examples.initialize()
    
    # Display template catalog
    examples.display_template_catalog()
    
    # Note: Actual demonstration would require GPT-5 connector
    print("\n💡 NOTE: Full demonstration requires GPT-5 connector initialization")
    print("   Use: await examples.initialize(gpt5_connector) with actual connector")


if __name__ == "__main__":
    asyncio.run(run_demonstration())
