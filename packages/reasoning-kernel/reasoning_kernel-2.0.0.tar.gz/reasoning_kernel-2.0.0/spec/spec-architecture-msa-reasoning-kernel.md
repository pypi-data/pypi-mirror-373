---
title: MSA Reasoning Kernel Architecture Specification
version: 1.0
date_created: 2025-08-15
owner: Reasoning Kernel Team
tags: [architecture, app, msa, semantic-kernel, fastapi]
---

# Introduction

This specification defines the architecture for the Model Synthesis Architecture (MSA) Reasoning Kernel used in the Reasoning-Kernel repository. It formalizes the five-stage pipeline, orchestration patterns, interfaces, configuration, and testing requirements so Generative AI agents and developers can implement, extend, and verify components consistently.

## 1. Purpose & Scope

- Purpose: Provide an unambiguous, machine-readable architecture contract for the MSA Reasoning Kernel and its integrations (Semantic Kernel, Redis, Daytona sandbox, FastAPI API layers).
- Scope: FastAPI app startup lifecycle, v1 MSAEngine and v2 ReasoningKernel orchestrators, plugin/stage interfaces, streaming callbacks, environment/config, and testing patterns.
- Audience: AI coding agents, maintainers, contributors building stages, plugins, endpoints, or integrations.
- Assumptions: Python 3.10–3.12, async-first design, external services mocked in tests, Semantic Kernel available at runtime (with graceful fallbacks).

## 2. Definitions

- MSA: Model Synthesis Architecture – five-stage reasoning pipeline.
- ReasoningKernel: v2 orchestrator implementing the five MSA stages end-to-end with callbacks.
- MSAEngine: v1 pipeline wrapper used where v2 is unavailable.
- StageDescriptor: Data structure describing a pipeline stage (predicate, exec_factory, payload).
- ReasoningResult: Aggregate result object holding stage outputs, timings, confidences, traces.
- KernelManager: Component configuring and exposing Semantic Kernel services.
- Daytona Sandbox: Secure execution environment for synthesis/inference operations.
- MCP Redis Cloud: Vendored Model Context Protocol server for Redis Cloud integration.

## 3. Requirements, Constraints & Guidelines

- REQ-001: The system shall implement five stages: parse, retrieve, graph, synthesize, infer.
- REQ-002: Each stage shall update `ReasoningResult` and record timing and confidence.
- REQ-003: Stage execution shall be guarded by a predicate to avoid invalid transitions.
- REQ-004: Streaming callbacks shall be supported: `on_stage_start`, `on_stage_complete`, `on_thinking_sentence`, `on_sandbox_event`.
- REQ-005: The FastAPI app shall attach initialized components to `app.state` during lifespan.
- REQ-006: Semantic Kernel initialization shall be centralized via `KernelManager`.
- REQ-007: Redis memory and retrieval services shall be created via factory and support config via env.
- REQ-008: CORS configuration shall disallow wildcard origins in production.
- REQ-009: Tests shall mock external services; no network calls in unit tests.
- SEC-001: Secrets shall be loaded via `.env` and not committed; sensitive logs must be avoided.
- CON-001: Supported Python versions: >=3.10,<3.13; 3.13+ is unsupported.
- CON-002: Async-first APIs; long-running tasks must be awaitable and time-limited.
- GUD-001: Use structured logging (structlog or logging wrapper) with contextual fields.
- PAT-001: Introduce new stages by defining `StageDescriptor` and updating `ReasoningResult` consistently.

## 4. Interfaces & Data Contracts

### 4.1 ReasoningKernel (v2)

- Input: `vignette: str`, `data: Optional[Dict[str, Any]]`, `session_id: Optional[str]`, optional callbacks.
- Output: `ReasoningResult` with fields:
  - `parsed_vignette`, `retrieval_context`, `dependency_graph`, `probabilistic_program`, `inference_result`
  - `stage_timings: Dict[str, float]`, `stage_confidences: Dict[str, float]`
  - `thinking_process: List[str]`, `reasoning_sentences: List[str]`, `step_by_step_analysis: Dict[str, List[str]]`
  - `overall_confidence: float`, `success: bool`, `error_message: Optional[str]`

### 4.2 StageDescriptor

- Fields: `name: str`, `stage: ReasoningStage`, `exec_factory: () -> awaitable`, `completion_payload: (Any) -> Dict`, optional `predicate: (ReasoningResult) -> bool`, optional `sandbox_events: Dict[str,str]`.

### 4.3 Callbacks

- `on_stage_start(stage_name: str)` -> Awaitable[None]
- `on_stage_complete(stage_name: str, payload: Dict[str, Any])` -> Awaitable[None]
- `on_thinking_sentence(sentence: str)` -> Awaitable[None]
- `on_sandbox_event(event: Dict[str, Any])` -> Awaitable[None]

### 4.4 App Lifespan State

- `app.state.kernel_manager: KernelManager`
- `app.state.msa_engine: MSAEngine`
- `app.state.reasoning_kernel: Optional[ReasoningKernel]`
- `app.state.redis_memory`, `app.state.redis_retrieval`
- `app.state.db_manager`

### 4.5 Configuration (Env Vars)

- Gemini: `GOOGLE_AI_API_KEY`, `GOOGLE_AI_GEMINI_MODEL_ID`, `GOOGLE_AI_EMBEDDING_MODEL_ID`
- Azure OpenAI: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`
- Redis: `REDIS_URL` or `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_DB`
- Logging: `LOG_LEVEL`, `LOG_FORMAT`; CORS: `ALLOWED_ORIGINS`

## 5. Acceptance Criteria

- AC-001: Given a valid vignette, when `ReasoningKernel.reason()` runs, then all applicable stages execute in order and `ReasoningResult` contains populated stage fields, timings, confidences, and `success=True`.
- AC-002: Given missing dependencies for v2, when the app starts, then v1 MSAEngine endpoints remain operational and v2 routes are skipped without crashing.
- AC-003: Given wildcard `ALLOWED_ORIGINS` in production, when app starts, then startup fails with a descriptive error.
- AC-004: Given tests are executed, when running `pytest`, then external services are mocked and tests complete without network calls.
- AC-005: Given Redis URL with extraneous shell text (e.g., `export REDIS_URL=...`), when parsed, then a clean `redis://...` URL is extracted and used.

## 6. Test Automation Strategy

- Test Levels: Unit and Integration (no real external calls). E2E optional via mocked services.
- Frameworks: pytest (+ pytest-asyncio), unittest.mock/AsyncMock.
- Test Data Management: Factory functions and dataclass builders for stage outputs; no persistent DB state.
- CI/CD Integration: Run `pytest -q` on PRs; static analysis via Datadog SARIF optional.
- Coverage Requirements: Ensure tests cover stage predicates, timing/confidence propagation, and callback firing.
- Performance Testing: Use `--durations=10` locally to identify slow tests; keep runtime under seconds.

## 7. Rationale & Context

- Five-stage pipeline enables separation of concerns and targeted retries/fallbacks.
- StageDescriptor pattern provides declarative flow with predicates and event hooks.
- App lifespan centralizes DI, ensuring endpoints and services share initialized instances.
- Strict env handling and CORS policy reduce misconfiguration risks in production.

## 8. Dependencies & External Integrations

### External Systems

- EXT-001: Redis – in-memory store for memory/retrieval services; required at runtime for memory features.

## Purpose & Scope

### Third-Party Services

- SVC-001: Gemini or Azure OpenAI – LLM providers for parsing, graphing, and synthesis prompts.
- SVC-002: Daytona Sandbox – secure execution for synthesis/inference operations.

### Infrastructure Dependencies

- INF-001: FastAPI app server (Uvicorn) – async runtime and routing.

### Data Dependencies

- DAT-001: Vector embeddings storage in Redis (via MCP Redis integration where applicable).

### Technology Platform Dependencies

- PLT-001: Python >=3.10,<3.13; AsyncIO.

### Compliance Dependencies

- COM-001: Secrets management via environment variables; no secrets in logs or SCM.

## 9. Examples & Edge Cases

```python
# StageDescriptor example when adding a new "validate" stage
validate_desc = StageDescriptor(
    name="validate",
    stage=ReasoningStage.GRAPH,  # or a new enum value
    predicate=lambda r: r.dependency_graph is not None,
    exec_factory=lambda: validation_plugin.validate_graph(r.dependency_graph),
    completion_payload=lambda res: {"validation_status": getattr(res, "status", "unknown")},
)

# Callback usage in streaming
result = await rk.reason_with_streaming(
    vignette,
    session_id="s1",
    on_stage_start=lambda s: ws.send_json({"event": "stage_start", "name": s}),
    on_stage_complete=lambda s,p: ws.send_json({"event": "stage_complete", "name": s, **p}),
    on_thinking_sentence=lambda t: ws.send_text(t),
)
```

## 10. Validation Criteria

- VC-001: Lint/typecheck pass for orchestrator and new stages.
- VC-002: Unit tests cover success/error paths per stage and callbacks.
- VC-003: Server boot with and without v2 kernel; routes behave as expected.
- VC-004: CORS policy enforced according to environment.

## 11. Related Specifications / Further Reading

- docs/full-system.md
- docs/core_concepts.md
- tests/README.md
- app/reasoning_kernel.py
- app/main.py
- app/agents/thinking_kernel.py
