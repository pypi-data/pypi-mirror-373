"""
Daytona Sandbox Manager - High-Level Sandbox Lifecycle Management
================================================================

Manages multiple Daytona sandboxes with advanced lifecycle management,
resource monitoring, snapshot management, and volume operations.
Provides orchestration layer for complex sandbox workflows.
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from reasoning_kernel.services.daytona_service import DaytonaService
from reasoning_kernel.services.daytona_service import SandboxConfig
from reasoning_kernel.services.daytona_service import SandboxStatus
from reasoning_kernel.services.unified_redis_service import UnifiedRedisService
import structlog


logger = structlog.get_logger(__name__)


@dataclass
class SandboxMetrics:
    """Metrics for sandbox performance and resource usage"""

    sandbox_id: str
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    disk_usage_mb: float = 0.0
    network_bytes_in: int = 0
    network_bytes_out: int = 0
    execution_time_seconds: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for storage"""
        return {
            "sandbox_id": self.sandbox_id,
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_usage_mb": self.memory_usage_mb,
            "disk_usage_mb": self.disk_usage_mb,
            "network_bytes_in": self.network_bytes_in,
            "network_bytes_out": self.network_bytes_out,
            "execution_time_seconds": self.execution_time_seconds,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class SandboxSession:
    """Represents an active sandbox session with metadata"""

    session_id: str
    sandbox_id: str
    user_id: Optional[str] = None
    purpose: str = "general"
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    status: SandboxStatus = SandboxStatus.INITIALIZING
    config: SandboxConfig = field(default_factory=SandboxConfig)
    tags: Set[str] = field(default_factory=set)
    metrics: Optional[SandboxMetrics] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for storage"""
        return {
            "session_id": self.session_id,
            "sandbox_id": self.sandbox_id,
            "user_id": self.user_id,
            "purpose": self.purpose,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "status": self.status.value,
            "config": {
                "cpu_limit": self.config.cpu_limit,
                "memory_limit_mb": self.config.memory_limit_mb,
                "execution_timeout": self.config.execution_timeout,
                "python_version": self.config.python_version,
            },
            "tags": list(self.tags),
            "metrics": self.metrics.to_dict() if self.metrics else None,
        }


class DaytonaSandboxManager:
    """
    High-level manager for Daytona sandbox lifecycle operations.

    Features:
    - Multi-sandbox management with session tracking
    - Resource monitoring and metrics collection
    - Automatic cleanup and resource optimization
    - Snapshot and volume management
    - Health monitoring and fault tolerance
    """

    def __init__(
        self,
        redis_service: UnifiedRedisService,
        default_config: Optional[SandboxConfig] = None,
        max_concurrent_sandboxes: int = 10,
        cleanup_interval_seconds: int = 300,  # 5 minutes
        session_timeout_minutes: int = 60,
    ):
        """
        Initialize the sandbox manager.

        Args:
            redis_service: Redis service for session storage and caching
            default_config: Default sandbox configuration
            max_concurrent_sandboxes: Maximum number of concurrent sandboxes
            cleanup_interval_seconds: Interval for cleanup operations
            session_timeout_minutes: Timeout for inactive sessions
        """
        self.redis = redis_service
        self.default_config = default_config or SandboxConfig()
        self.max_concurrent_sandboxes = max_concurrent_sandboxes
        self.cleanup_interval = cleanup_interval_seconds
        self.session_timeout = timedelta(minutes=session_timeout_minutes)

        # Session management
        self.active_sessions: Dict[str, SandboxSession] = {}
        self.session_lock = asyncio.Lock()

        # Daytona service instances (one per sandbox)
        self.daytona_services: Dict[str, DaytonaService] = {}

        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.monitoring_task: Optional[asyncio.Task] = None

        logger.info(
            "DaytonaSandboxManager initialized",
            max_concurrent=max_concurrent_sandboxes,
            cleanup_interval=cleanup_interval_seconds,
            session_timeout_minutes=session_timeout_minutes,
        )

    async def start(self) -> None:
        """Start background tasks for cleanup and monitoring"""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_worker())
            logger.info("Started cleanup worker")

        if self.monitoring_task is None:
            self.monitoring_task = asyncio.create_task(self._monitoring_worker())
            logger.info("Started monitoring worker")

    async def stop(self) -> None:
        """Stop background tasks and cleanup resources"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                logger.debug("Cleanup task cancelled")
            except Exception as e:
                logger.error("Error stopping cleanup task", error=str(e))
            self.cleanup_task = None

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                logger.debug("Monitoring task cancelled")
            except Exception as e:
                logger.error("Error stopping monitoring task", error=str(e))
            self.monitoring_task = None

        # Cleanup all active sessions
        async with self.session_lock:
            for session in self.active_sessions.values():
                await self._cleanup_session(session.session_id)

        logger.info("DaytonaSandboxManager stopped")

    async def create_session(
        self,
        user_id: Optional[str] = None,
        purpose: str = "general",
        config: Optional[SandboxConfig] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Create a new sandbox session.

        Args:
            user_id: User identifier for the session
            purpose: Purpose/description of the session
            config: Custom sandbox configuration
            tags: Tags for categorizing the session

        Returns:
            Session ID for the created session

        Raises:
            ValueError: If maximum concurrent sandboxes exceeded
        """
        async with self.session_lock:
            # Check concurrent sandbox limit
            if len(self.active_sessions) >= self.max_concurrent_sandboxes:
                raise ValueError(f"Maximum concurrent sandboxes ({self.max_concurrent_sandboxes}) exceeded")

            # Generate session ID
            session_id = str(uuid4())

            # Create Daytona service for this session
            sandbox_config = config or self.default_config
            daytona_service = DaytonaService(sandbox_config)

            # Create sandbox
            success = await daytona_service.create_sandbox()
            if not success:
                raise RuntimeError("Failed to create sandbox")

            # Get sandbox ID from service
            sandbox_id = daytona_service.current_sandbox.get("id", "unknown")

            # Create session object
            session = SandboxSession(
                session_id=session_id,
                sandbox_id=sandbox_id,
                user_id=user_id,
                purpose=purpose,
                config=sandbox_config,
                tags=set(tags or []),
                status=SandboxStatus.READY,
            )

            # Store session and service
            self.active_sessions[session_id] = session
            self.daytona_services[session_id] = daytona_service

            # Persist session to Redis
            await self._persist_session(session)

            logger.info(
                "Created sandbox session",
                session_id=session_id,
                sandbox_id=sandbox_id,
                user_id=user_id,
                purpose=purpose,
            )

            return session_id

    async def get_session(self, session_id: str) -> Optional[SandboxSession]:
        """
        Get session information by session ID.

        Args:
            session_id: Session identifier

        Returns:
            SandboxSession object or None if not found
        """
        async with self.session_lock:
            session = self.active_sessions.get(session_id)
            if session:
                # Update last activity
                session.last_activity = datetime.now()
                await self._persist_session(session)
            return session

    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        status: Optional[SandboxStatus] = None,
        tags: Optional[List[str]] = None,
    ) -> List[SandboxSession]:
        """
        List active sessions with optional filtering.

        Args:
            user_id: Filter by user ID
            status: Filter by sandbox status
            tags: Filter by tags (session must have all specified tags)

        Returns:
            List of matching SandboxSession objects
        """
        async with self.session_lock:
            sessions = list(self.active_sessions.values())

            # Apply filters
            if user_id:
                sessions = [s for s in sessions if s.user_id == user_id]

            if status:
                sessions = [s for s in sessions if s.status == status]

            if tags:
                tag_set = set(tags)
                sessions = [s for s in sessions if tag_set.issubset(s.tags)]

            return sessions

    async def execute_code(
        self,
        session_id: str,
        code: str,
        timeout_seconds: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Execute code in the specified sandbox session.

        Args:
            session_id: Session identifier
            code: Python code to execute
            timeout_seconds: Execution timeout override

        Returns:
            Execution result dictionary

        Raises:
            ValueError: If session not found or invalid
            RuntimeError: If execution fails
        """
        async with self.session_lock:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            if session.status != SandboxStatus.READY:
                raise ValueError(f"Session {session_id} is not ready (status: {session.status.value})")

            service = self.daytona_services.get(session_id)
            if not service:
                raise RuntimeError(f"Daytona service not found for session {session_id}")

        # Update session status
        session.status = SandboxStatus.RUNNING
        session.last_activity = datetime.now()
        await self._persist_session(session)

        try:
            # Execute code
            start_time = time.time()
            result = await service.execute_code(code, int(timeout_seconds) if timeout_seconds else None)
            execution_time = time.time() - start_time

            # Update metrics
            if not session.metrics:
                session.metrics = SandboxMetrics(session.sandbox_id)
            session.metrics.execution_time_seconds += execution_time
            session.metrics.last_updated = datetime.now()

            # Update session status
            session.status = SandboxStatus.READY
            await self._persist_session(session)

            logger.info(
                "Code execution completed",
                session_id=session_id,
                execution_time=execution_time,
                result_keys=list(result.keys()) if isinstance(result, dict) else None,
            )

            return {
                "exit_code": result.exit_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": result.execution_time,
                "status": result.status.value if hasattr(result.status, "value") else str(result.status),
                "resource_usage": result.resource_usage,
                "metadata": result.metadata,
            }

        except Exception as e:
            # Update session status on failure
            session.status = SandboxStatus.FAILED
            await self._persist_session(session)

            logger.error(
                "Code execution failed",
                session_id=session_id,
                error=str(e),
            )
            raise RuntimeError(f"Code execution failed: {str(e)}") from e

    async def create_snapshot(self, session_id: str, snapshot_name: str) -> str:
        """
        Create a snapshot of the sandbox.

        Args:
            session_id: Session identifier
            snapshot_name: Name for the snapshot

        Returns:
            Snapshot ID

        Raises:
            ValueError: If session not found
            RuntimeError: If snapshot creation fails
        """
        async with self.session_lock:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            # For now, return a placeholder - snapshot functionality to be implemented
            snapshot_id = f"snapshot_{session_id}_{int(time.time())}"

            logger.info(
                "Snapshot creation requested (not yet implemented)",
                session_id=session_id,
                snapshot_id=snapshot_id,
                snapshot_name=snapshot_name,
            )

            return snapshot_id

    async def list_snapshots(self, session_id: str) -> List[Dict[str, Any]]:
        """
        List snapshots for the session.

        Args:
            session_id: Session identifier

        Returns:
            List of snapshot information dictionaries

        Raises:
            ValueError: If session not found
        """
        async with self.session_lock:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            # For now, return empty list - snapshot functionality to be implemented
            logger.info(
                "Snapshot listing requested (not yet implemented)",
                session_id=session_id,
            )

            return []

    async def destroy_session(self, session_id: str) -> None:
        """
        Destroy a sandbox session and cleanup resources.

        Args:
            session_id: Session identifier

        Raises:
            ValueError: If session not found
        """
        async with self.session_lock:
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")

            # Remove from active sessions
            del self.active_sessions[session_id]

            # Cleanup Daytona service
            service = self.daytona_services.pop(session_id, None)
            if service:
                # For now, just log cleanup - proper cleanup to be implemented
                logger.info("Service cleanup requested", session_id=session_id)

            # Remove from Redis
            if self.redis.redis_client:
                await self.redis.redis_client.delete(f"sandbox_session:{session_id}")
            else:
                logger.warning("Redis client not available for session cleanup", session_id=session_id)

            logger.info(
                "Session destroyed",
                session_id=session_id,
                sandbox_id=session.sandbox_id,
            )

    async def get_metrics(self, session_id: str) -> Optional[SandboxMetrics]:
        """
        Get metrics for a session.

        Args:
            session_id: Session identifier

        Returns:
            SandboxMetrics object or None if session not found
        """
        async with self.session_lock:
            session = self.active_sessions.get(session_id)
            return session.metrics if session else None

    async def _cleanup_worker(self) -> None:
        """Background worker for cleaning up expired sessions"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._perform_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in cleanup worker", error=str(e))
                await asyncio.sleep(60)  # Wait before retrying

    async def _monitoring_worker(self) -> None:
        """Background worker for monitoring sandbox health and metrics"""
        while True:
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                await self._perform_monitoring()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in monitoring worker", error=str(e))
                await asyncio.sleep(60)  # Wait before retrying

    async def _perform_cleanup(self) -> None:
        """Perform cleanup of expired sessions"""
        async with self.session_lock:
            now = datetime.now()
            expired_sessions = []

            for session_id, session in self.active_sessions.items():
                if now - session.last_activity > self.session_timeout:
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                logger.info("Cleaning up expired session", session_id=session_id)
                await self._cleanup_session(session_id)

    async def _perform_monitoring(self) -> None:
        """Perform health monitoring and metrics collection"""
        async with self.session_lock:
            for session_id, session in self.active_sessions.items():
                try:
                    service = self.daytona_services.get(session_id)
                    if service and service.daytona_available:
                        # Collect basic metrics (would need to be implemented in DaytonaService)
                        # For now, just update last activity
                        session.last_activity = datetime.now()
                        await self._persist_session(session)
                except Exception as e:
                    logger.warning(
                        "Error monitoring session",
                        session_id=session_id,
                        error=str(e),
                    )

    async def _cleanup_session(self, session_id: str) -> None:
        """Cleanup a specific session"""
        session = self.active_sessions.pop(session_id, None)
        if session:
            service = self.daytona_services.pop(session_id, None)
            if service:
                # For now, just log cleanup - proper cleanup to be implemented
                logger.info("Service cleanup requested", session_id=session_id)

            # Remove from Redis
            if self.redis.redis_client:
                await self.redis.redis_client.delete(f"sandbox_session:{session_id}")
            else:
                logger.warning("Redis client not available for session cleanup", session_id=session_id)

    async def _persist_session(self, session: SandboxSession) -> None:
        """Persist session to Redis"""
        try:
            session_data = session.to_dict()
            if self.redis.redis_client:
                await self.redis.redis_client.set(
                    f"sandbox_session:{session.session_id}",
                    json.dumps(session_data),
                    ex=self.session_timeout.total_seconds(),
                )
            else:
                logger.warning("Redis client not available for session persistence", session_id=session.session_id)
        except Exception as e:
            logger.warning(
                "Failed to persist session to Redis",
                session_id=session.session_id,
                error=str(e),
            )
