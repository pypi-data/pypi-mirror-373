"""
MSA Prompt Templates Module

This module provides standardized prompt templates for enhanced natural language reasoning
in the unified MSA architecture, based on research patterns from msa-cogsci-2025-data.

Key Components:
- MSAPromptTemplates: Collection of research-validated prompt templates
- MSAPromptManager: Centralized prompt execution and management
- PromptContext: Context management for stage-specific processing
- Examples and demonstrations for all template types

Usage:
    from reasoning_kernel.prompts import get_msa_templates, get_prompt_manager, PromptContext
    
    # Get templates
    templates = get_msa_templates()
    
    # Get prompt manager
    prompt_manager = await get_prompt_manager(gpt5_connector)
    
    # Execute prompt
    context = PromptContext(stage="parse", scenario="...", session_id="...")
    response = await prompt_manager.execute_prompt("parse_causal_structure", context)
"""

from .msa_prompt_templates import (
    get_msa_templates,
    MSAPromptTemplates,
    PromptTemplate,
    PromptType
)

from .prompt_manager import (
    get_prompt_manager,
    MSAPromptManager,
    PromptContext
)

__all__ = [
    # Template system
    "get_msa_templates",
    "MSAPromptTemplates", 
    "PromptTemplate",
    "PromptType",
    
    # Prompt manager
    "get_prompt_manager",
    "MSAPromptManager",
    "PromptContext"
]

# Version info
__version__ = "1.0.0"
__author__ = "Reasoning Kernel Team"
__description__ = "MSA Prompt Templates for Enhanced Natural Language Reasoning"
