"""
Reasoning Chains Utilities
==========================

Utilities for managing and processing reasoning chains in the MSA pipeline.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ChainType(Enum):
    """Types of reasoning chains"""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    ITERATIVE = "iterative"


@dataclass
class ChainStep:
    """Individual step in a reasoning chain"""

    step_id: str
    step_type: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    success: bool = False
    error_message: Optional[str] = None
    processing_time: float = 0.0


@dataclass
class ReasoningChain:
    """
    Represents a chain of reasoning steps

    Used to track the flow of reasoning through different stages
    and maintain context between processing steps.
    """

    chain_id: str
    chain_type: ChainType
    steps: List[ChainStep]
    metadata: Dict[str, Any]

    def __init__(self, chain_id: str, chain_type: ChainType = ChainType.SEQUENTIAL):
        self.chain_id = chain_id
        self.chain_type = chain_type
        self.steps = []
        self.metadata = {}

    def add_step(self, step: ChainStep) -> None:
        """Add a step to the reasoning chain"""
        self.steps.append(step)

    def get_step(self, step_id: str) -> Optional[ChainStep]:
        """Get a specific step by ID"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    def get_successful_steps(self) -> List[ChainStep]:
        """Get all successful steps"""
        return [step for step in self.steps if step.success]

    def get_failed_steps(self) -> List[ChainStep]:
        """Get all failed steps"""
        return [step for step in self.steps if not step.success]

    def is_complete(self) -> bool:
        """Check if the chain is complete (all steps successful)"""
        return len(self.steps) > 0 and all(step.success for step in self.steps)

    def get_total_processing_time(self) -> float:
        """Get total processing time for all steps"""
        return sum(step.processing_time for step in self.steps)

    def get_chain_summary(self) -> Dict[str, Any]:
        """Get a summary of the reasoning chain"""
        return {
            "chain_id": self.chain_id,
            "chain_type": self.chain_type.value,
            "total_steps": len(self.steps),
            "successful_steps": len(self.get_successful_steps()),
            "failed_steps": len(self.get_failed_steps()),
            "is_complete": self.is_complete(),
            "total_processing_time": self.get_total_processing_time(),
            "metadata": self.metadata,
        }


class ChainManager:
    """Manages multiple reasoning chains"""

    def __init__(self):
        self.chains: Dict[str, ReasoningChain] = {}

    def create_chain(
        self, chain_id: str, chain_type: ChainType = ChainType.SEQUENTIAL
    ) -> ReasoningChain:
        """Create a new reasoning chain"""
        chain = ReasoningChain(chain_id, chain_type)
        self.chains[chain_id] = chain
        return chain

    def get_chain(self, chain_id: str) -> Optional[ReasoningChain]:
        """Get a reasoning chain by ID"""
        return self.chains.get(chain_id)

    def remove_chain(self, chain_id: str) -> bool:
        """Remove a reasoning chain"""
        if chain_id in self.chains:
            del self.chains[chain_id]
            return True
        return False

    def get_all_chains(self) -> List[ReasoningChain]:
        """Get all reasoning chains"""
        return list(self.chains.values())

    def get_chains_summary(self) -> Dict[str, Any]:
        """Get summary of all chains"""
        return {
            "total_chains": len(self.chains),
            "chains": [chain.get_chain_summary() for chain in self.chains.values()],
        }


def create_msa_reasoning_chain(session_id: str) -> ReasoningChain:
    """Create a reasoning chain for MSA pipeline execution"""
    chain = ReasoningChain(f"msa_{session_id}", ChainType.SEQUENTIAL)
    chain.metadata = {
        "pipeline_type": "msa",
        "session_id": session_id,
        "created_at": None,  # Will be set when chain starts
    }
    return chain


def create_chain_step(
    step_id: str, step_type: str, input_data: Dict[str, Any]
) -> ChainStep:
    """Create a new chain step"""
    return ChainStep(step_id=step_id, step_type=step_type, input_data=input_data)
