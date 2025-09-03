# AGENTS.md

Agent-focused reference for working on the Reasoning-Kernel codebase. This complements README.md and gives coding agents exact, runnable commands and workflows.

## Project overview

- Purpose: Production-ready reasoning engine implementing the Model Synthesis Architecture (MSA) with Microsoft Semantic Kernel orchestration, FastAPI API layer, CLI, and optional cloud integrations (Azure OpenAI, Redis Cloud, Daytona).
- Key tech: Python 3.10–3.13, FastAPI, Uvicorn, Semantic Kernel, NumPyro/JAX, Redis, structlog, pytest.
- Interfaces:
  - CLI entry point: `reasoning-kernel`
  - FastAPI server (async app factory via SK): see `launch_api_server.py` and `reasoning_kernel/sk_core/api_integration.py`
  - Tests in `tests/` with helpers and a consolidated runner `tests/run_tests.py`

## Setup commands

- Clone and enter repo:

```bash
git clone https://github.com/Qredence/Reasoning-Kernel.git
cd Reasoning-Kernel
```

- Create virtual env with uv and install:

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pre-commit install
```

- Environment configuration (create `.env` or export vars). Minimum for local non-cloud runs is none; to enable cloud-backed features set as needed:

```bash
# Azure OpenAI (example)
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY="your-key"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-5"
AZURE_OPENAI_API_VERSION="2024-02-15-preview"

# Or Google AI
GOOGLE_AI_API_KEY="your-gemini-key"

# Optional services
REDIS_URL="redis://localhost:6379"
DEVELOPMENT=true
```

## Development workflow

- Check version and CLI help:

```bash
uv run reasoning-kernel --version
uv run reasoning-kernel --help
```

- Quick single query (text output by default):

```bash
uv run reasoning-kernel reason "Analyze market volatility causes" -o text -v
```

- Interactive chat mode:

```bash
uv run reasoning-kernel chat -v
```

- Analyze a file or inline content:

```bash
uv run reasoning-kernel analyze -f examples/batch_queries.json -o json
uv run reasoning-kernel analyze "Analyze this document..." -o text
```

- Start API server (recommended):

```bash
# Uses the async app factory in reasoning_kernel/sk_core/api_integration.py
uv run python launch_api_server.py
```

- Alternative FastAPI start (only if you wire a module path exposing `app`):

```bash
# Not required in this repo; prefer launch_api_server.py
uv run uvicorn reasoning_kernel.main:app --reload --port 8000
```

## Testing instructions

- Run all tests quickly via consolidated runner:

```bash
uv run python tests/run_tests.py all -v --fast
```

- Full suite (unit, api, msa, redis, plus integration/performance):

```bash
uv run python tests/run_tests.py all -v
```

- Coverage with unit tests:

```bash
uv run python tests/run_tests.py unit -v --coverage
```

- Direct pytest usage:

```bash
# All tests
uv run pytest -q
# Unit tests only
uv run pytest tests/unit -q
# Focus by keyword
uv run pytest -k "pipeline" -q
```

- Common locations and naming:
  - Tests live under `tests/` and subfolders (`unit/`, `integration/`, `performance/`, `msa/`, `services/`, `api/`, `smoke/`).
  - Pytest discovery uses patterns from `pyproject.toml` (files: `test_*.py` or `*_test.py`).

## Code style and type checks

- Format, lint, sort imports, and type-check:

```bash
uv run ruff check .
uv run black .
uv run isort .
uv run mypy reasoning_kernel/
```

- Pre-commit (recommended before commits/PRs):

```bash
uv run pre-commit run -a
```

## Build and packaging

- Build sdist/wheel (hatchling backend):

```bash
uv run python -m build
```

- Verify artifacts:

```bash
uv run twine check dist/*
```

## Deployment (summary)

- Production deployment is documented in `docs/DEPLOYMENT.md` (Docker, K8s, Cloud Run). For a simple local production-like run:

```bash
# Ensure .env is set with required secrets
uv run python launch_api_server.py
# Then reverse proxy or expose port 8000 per your platform
```

- Health and docs (when server is running):

```text
GET http://localhost:8000/health
Open http://localhost:8000/docs
```

## Security considerations

- Never commit secrets. Use `.env` and environment variables for:
  - Azure OpenAI: `AZURE_OPENAI_*`
  - Google: `GOOGLE_AI_API_KEY`
  - Redis: `REDIS_URL` or Redis Cloud vars
- Prefer local fallback modes during development; cloud keys enable richer functionality but are optional for basic CLI and most tests.
- Follow least-privilege for any cloud service keys used in CI/local.

## Pull request checklist

- Branch from the active development branch.
- Ensure quality gates are green locally:

```bash
uv run ruff check .
uv run black --check .
uv run isort --check-only .
uv run mypy reasoning_kernel/
uv run pytest -q
```

- Include/adjust tests for changed behavior.
- Keep commits focused; add brief rationale in PR description.

## Debugging and troubleshooting

- Missing Azure/Google keys: CLI will fall back and warn; set env vars if you need remote LLMs.
- Redis connection issues: verify `REDIS_URL` and connectivity; many flows work without Redis in dev.
- If `uvicorn reasoning_kernel.main:app` fails: use `uv run python launch_api_server.py` which constructs the app via SK.
- Verbose CLI output helps: add `-v` and use `-o json` to inspect structured fields.

## Project structure (high level)

```text
reasoning_kernel/            # Library/package code
  cli/                       # CLI entry and REPL support
  sk_core/                   # Semantic Kernel integration and FastAPI app factory
  ...
launch_api_server.py         # Async FastAPI server launcher
tests/                       # Test suites and helpers
examples/                    # Demos and scenarios
benchmarks/                  # Performance tools/results
```

## Notes for agents

- Prefer `uv run` to ensure the environment is consistent with `pyproject.toml`.
- For API work, import and use `create_sk_api_app()` from `reasoning_kernel/sk_core/api_integration.py` or run `launch_api_server.py`—don’t assume a static module path for `app`.
- Use the consolidated test runner for reliable subsets/markers: `tests/run_tests.py`.
