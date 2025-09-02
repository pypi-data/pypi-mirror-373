"""Compatibility layer for agent orchestration tests.

Provides lightweight stubs for AgentOrchestrator, AgentConfig, AgentRole, AgentTask, AgentState
and simple in-memory communication primitives used by tests.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentRole(str, Enum):
    COORDINATOR = "coordinator"
    WORKER = "worker"
    SPECIALIST = "specialist"


@dataclass
class AgentConfig:
    agent_id: str
    role: AgentRole
    capabilities: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 1


@dataclass
class AgentTask:
    task_id: str
    task_type: str
    payload: Dict[str, Any] = field(default_factory=dict)


class AgentState(str, Enum):
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"


@dataclass
class AgentResult:
    task_id: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.state: AgentState = AgentState.CREATED
        self._results: Dict[str, AgentResult] = {}

    async def initialize(self) -> bool:
        self.state = AgentState.READY
        return True

    async def start(self) -> bool:
        self.state = AgentState.RUNNING
        return True

    async def stop(self) -> bool:
        self.state = AgentState.STOPPED
        return True

    async def assign_task(self, task: AgentTask) -> bool:
        # Minimal processing: echo payload
        await asyncio.sleep(0)
        data = {"processed_data": task.payload, "processing_type": task.payload.get("processing_type")}
        if task.task_type == "coordinate_workflow":
            data = {"workflow_type": task.payload.get("workflow_type", "unknown"), **task.payload}
        self._results[task.task_id] = AgentResult(task_id=task.task_id, success=True, data=data)
        return True

    async def get_task_result(self, task_id: str) -> Optional[AgentResult]:
        return self._results.get(task_id)


class AgentOrchestrator:
    def __init__(self):
        self._running = False
        self._coordinator_task: Optional[asyncio.Task] = None
        self._agents: Dict[str, BaseAgent] = {}

    async def initialize(self) -> bool:
        self._running = True
        self._coordinator_task = asyncio.create_task(asyncio.sleep(0))
        return True

    async def shutdown(self) -> None:
        self._running = False
        if self._coordinator_task and not self._coordinator_task.done():
            self._coordinator_task.cancel()

    async def register_agent(self, agent: BaseAgent) -> bool:
        await agent.initialize()
        self._agents[agent.config.agent_id] = agent
        return True

    async def start_agent(self, agent_id: str) -> bool:
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        return await agent.start()

    async def stop_agent(self, agent_id: str) -> bool:
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        return await agent.stop()

    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        agent = self._agents.get(agent_id)
        if not agent:
            return {"agent_id": agent_id, "state": "unknown", "role": "unknown"}
        return {"agent_id": agent_id, "state": agent.state.value, "role": agent.config.role.value}

    async def assign_task_to_agent(self, agent_id: str, task: AgentTask) -> bool:
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        return await agent.assign_task(task)

    async def broadcast_task(self, task: AgentTask) -> List[str]:
        assigned = []
        for agent_id, agent in self._agents.items():
            ok = await agent.assign_task(task)
            if ok:
                assigned.append(agent_id)
        return assigned

    async def get_system_health(self) -> Dict[str, Any]:
        running = sum(1 for a in self._agents.values() if a.state == AgentState.RUNNING)
        status = "healthy" if running == len(self._agents) else ("degraded" if running > 0 else "critical")
        return {"status": status, "total_agents": len(self._agents), "running_agents": running}


# Simple communication stubs used in tests
class AgentMessage:
    def __init__(
        self,
        message_id: str,
        sender_id: str,
        recipient_id: Optional[str],
        message_type: str,
        payload: Dict[str, Any],
        timestamp: float,
        ttl_seconds: int | None = None,
    ):
        self.message_id = message_id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.message_type = message_type
        self.payload = payload
        self.timestamp = timestamp
        self.ttl_seconds = ttl_seconds


class MessageBroker:
    def __init__(self):
        self._agents: Dict[str, List[AgentMessage]] = {}

    async def initialize(self) -> bool:
        return True

    async def shutdown(self) -> None:
        return None

    async def register_agent(self, agent_id: str) -> bool:
        if agent_id in self._agents:
            return False
        self._agents[agent_id] = []
        return True

    async def send_message(self, message: AgentMessage) -> bool:
        if (
            message.ttl_seconds is not None
            and (message.timestamp + message.ttl_seconds) < asyncio.get_event_loop().time()
        ):
            return False
        if message.recipient_id is None:
            # broadcast
            await self.broadcast_message(message)
            return True
        if message.recipient_id not in self._agents:
            return False
        self._agents[message.recipient_id].append(message)
        return True

    async def broadcast_message(self, message: AgentMessage) -> int:
        delivered = 0
        for agent_id in self._agents.keys():
            self._agents[agent_id].append(message)
            delivered += 1
        return delivered

    async def receive_messages(self, agent_id: str) -> List[AgentMessage]:
        return list(self._agents.get(agent_id, []))


class AgentCommunicator:
    def __init__(self, agent_id: str, broker: MessageBroker):
        self.agent_id = agent_id
        self.broker = broker

    async def send_message(
        self, recipient_id: str, message_type: str, payload: Dict[str, Any]
    ) -> Optional[AgentMessage]:
        msg = AgentMessage(
            message_id=f"msg_{self.agent_id}_to_{recipient_id}",
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            message_type=message_type,
            payload=payload,
            timestamp=asyncio.get_event_loop().time(),
        )
        await self.broker.send_message(msg)
        return msg

    async def receive_messages(self) -> List[AgentMessage]:
        return await self.broker.receive_messages(self.agent_id)


# Specialized agents
class CoordinatorAgent(BaseAgent):
    pass


class WorkerAgent(BaseAgent):
    pass


class SpecialistAgent(BaseAgent):
    def __init__(self, config: AgentConfig, domain: str):
        super().__init__(config)
        self.domain = domain
