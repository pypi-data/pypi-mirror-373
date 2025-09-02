# Reasoning-Kernel

Model Synthesis Architecture (MSA) for advanced AI reasoning

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Semantic Kernel](https://img.shields.io/badge/Semantic%20Kernel-1.35.3-purple)](https://github.com/microsoft/semantic-kernel)
[![Status](https://img.shields.io/badge/Status-Beta-yellow)](https://github.com/Qredence/Reasoning-Kernel)

[Documentation](./docs/README.md) • [Quickstart](#quickstart) • [Examples](#examples) • [API](#api)

> [!NOTE]
> This project is actively evolving. Interfaces may change before v1.0. Follow the docs for up-to-date usage.

## Overview

Reasoning-Kernel is a production-ready reasoning engine implementing the Model Synthesis Architecture (MSA) with Semantic Kernel integration, comprehensive cloud services, and enhanced natural language reasoning capabilities.

### 🚀 Unified Architecture with Semantic Kernel Integration

- **Semantic Kernel Orchestration**: Advanced planning, plugin management, and multi-agent coordination
- **MSA Plugin Architecture**: Each MSA stage as SK plugin with cloud integration
- **Multi-Agent Capabilities**: GroupChat patterns and specialized agents for complex reasoning
- **Cloud-Native Design**: Optimized for Redis Cloud, Daytona Cloud, and GPT-5 via Azure OpenAI
- **Simplified Module Structure**: Clear separation of concerns with minimal dependencies

### 🧠 Enhanced Natural Language Reasoning

- **MSA Research Patterns**: Integrated findings from msa-cogsci-2025-data repository
- **Natural Language Descriptions**: Causal structure analysis with comprehensive explanations
- **Concept Trace Generation**: Dependency mapping with topological sorting
- **Semantic Kernel Planning**: Advanced workflow orchestration and dynamic plan generation
- **Multi-Agent Collaboration**: Specialized agents for reasoning, exploration, and coordination

### ☁️ Cloud Service Integration

- **Redis Cloud**: Vector embeddings storage, knowledge graph caching, session persistence
- **Daytona Cloud**: Secure sandbox execution for NumPyro/JAX probabilistic computations
- **GPT-5 (Azure OpenAI)**: High thinking effort, automatic summarization, robust error handling

### 🏗️ Unified Architecture

- **Core**: Semantic Kernel integration, orchestration, plugin registry, agent management
- **Plugins**: MSA stages as SK plugins (parse, knowledge, graph, synthesis, inference)
- **Agents**: Multi-agent system components for specialized reasoning tasks
- **Cloud**: Integrated cloud service connectors with health monitoring
- **API/CLI**: Rich interfaces with SK-powered capabilities

## Quickstart

## Migration & Developer docs

If you migrated from a legacy kernel or are developing new SK agents, see:

- `docs/migration-from-legacy.md` - migration steps and checklist
- `docs/development/sk-agent-development.md` - how to build and register SK plugins
- `docs/development/testing-guide.md` - run tests and CI guidance

Prerequisites

- Python 3.10–3.13
- Azure OpenAI or Google AI key (choose one)
- Optional: Redis 7+ for vector memory

Install

```bash
git clone https://github.com/Qredence/Reasoning-Kernel.git
cd Reasoning-Kernel
uv venv && source .venv/bin/activate
uv pip install -e .
```

Configure environment (create .env or export)

```bash
# Azure OpenAI (example)
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY="your-key"
AZURE_OPENAI_DEPLOYMENT="gpt-4"
AZURE_OPENAI_API_VERSION="2024-12-01-preview"

# Or Google AI
GOOGLE_AI_API_KEY="your-gemini-key"

# Optional
REDIS_URL="redis://localhost:6379"
DEVELOPMENT=true
```

Run

```bash
# Start API
uv run uvicorn reasoning_kernel.main:app --reload --port 8000

# Use the Unified Architecture CLI
python -m reasoning_kernel.cli.enhanced_cli analyze "Analyze market volatility causes" --enhanced --verbose

# Check system health (includes SK and cloud services)
python -m reasoning_kernel.cli.enhanced_cli health

# View configuration
python -m reasoning_kernel.cli.enhanced_cli config

# Advanced usage with Semantic Kernel planning
python -m reasoning_kernel.cli.enhanced_cli analyze "Your scenario here" --use-planning --stages parse,knowledge

# Multi-agent orchestration
python -m reasoning_kernel.cli.enhanced_cli analyze "Complex scenario" --use-multi-agent --output json
```

## Examples

- Minimal script: `examples/enhanced_msa_demo.py`, `examples/msa_system_demo.py`
- Batch: `examples/batch_queries.json` and CLI batch commands
- Demos: see `examples/demos/` and top-level example scripts

> [!TIP]
> For quick recipes, see `docs/getting-started/quickstart.md` and `docs/examples/tutorials.mdx`.

## API

Start the server

```bash
uv run uvicorn reasoning_kernel.main:app --reload --port 8000
```

Sample requests (v1 stable; v2 included when available)

```bash
# v1 MSA reasoning
curl -sS -X POST http://localhost:8000/api/v1/reason \
    -H "Content-Type: application/json" \
    -d '{"query":"Analyze system failure"}'

# v2 endpoints (if present in your build)
curl -sS -X POST http://localhost:8000/api/v2/reasoning/analyze \
    -H "Content-Type: application/json" \
    -d '{"query":"Market volatility analysis"}'
```

## Architecture

- Orchestration: Semantic Kernel + plugin/manager pattern
- Pipeline: Parse → Knowledge → Graph → Synthesis → Inference
- Memory: Unified Redis service with optional PostgreSQL persistence
- Interfaces: FastAPI (v1 always; v2 when present), CLI (Click)
- Observability: Structured logging via structlog; optional OTEL extras

More in `docs/architecture/overview.md` and `docs/architecture/component_reference.mdx`.

## Configuration

### Simplified Architecture Configuration

The simplified architecture uses centralized cloud services configuration:

```bash
# Redis Cloud (Knowledge Stage)
REDIS_CLOUD_HOST=your-redis-cloud-host.com
REDIS_CLOUD_PORT=6379
REDIS_CLOUD_PASSWORD=your_redis_cloud_password
REDIS_CLOUD_USERNAME=default
REDIS_CLOUD_SSL=true
REDIS_CLOUD_VECTOR_INDEX=knowledge_vectors

# Daytona Cloud (Inference Stage)
DAYTONA_CLOUD_ENDPOINT=https://api.daytona.io
DAYTONA_CLOUD_API_KEY=your_daytona_api_key
DAYTONA_CLOUD_WORKSPACE_ID=your_workspace_id
DAYTONA_MEMORY_LIMIT=4Gi
DAYTONA_CPU_LIMIT=2
DAYTONA_TIMEOUT_SECONDS=300

# GPT-5 via Azure OpenAI (All LLM Tasks)
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5
AZURE_OPENAI_MODEL=gpt-5
AZURE_OPENAI_THINKING_EFFORT=high
AZURE_OPENAI_ENABLE_SUMMARY=true

# Global Settings
ENABLE_CLOUD_SERVICES=true
FALLBACK_TO_LOCAL=true
REASONING_KERNEL_ENV=development
REASONING_KERNEL_LOG_LEVEL=INFO
```

### Configuration Validation

Check your configuration:

```bash
python -m reasoning_kernel_simplified.ui.cli config
python -m reasoning_kernel_simplified.ui.cli health
```

### Legacy Configuration

Configuration is loaded via dotenv + Pydantic settings.

Key vars

- Azure: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_API_VERSION
- Google: GOOGLE_AI_API_KEY
- Memory: REDIS_URL, optional PostgreSQL vars if enabled
- Server: DEVELOPMENT=true to enable reload

Developer docs:

- Configuration guide: docs/development/configuration_guide.md
- Running locally: docs/development/running_locally.md

See docs/development/configuration_guide.md for up-to-date details.

## Development

```bash
uv pip install -e ".[dev]"
pre-commit install
uv run pytest -q
uv run ruff check . && uv run black . && uv run mypy reasoning_kernel/
```

Useful targets

- CLI help: `uv run reasoning-kernel --help`
- Batch: `uv run reasoning-kernel batch process -h`
- Sessions/history/memory commands available via CLI groups

## Troubleshooting

- Missing Azure keys: ensure required AZURE_OPENAI_* are set (see CLI error hints)
- Import errors for optional features (Daytona, v2 routers): install extras and rebuild environment
- Redis connection issues: verify REDIS_URL and that Redis is reachable

Check `docs/troubleshooting/common-issues.md` for more.

## Documentation

See `docs/README.md` for a complete guide: getting started, architecture, API, CLI, plugins, deployment, and operations.

---

## 📄 License

Copyright 2025 Qredence

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

```text
http://www.apache.org/licenses/LICENSE-2.0
```

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

See [LICENSE](LICENSE) for the full license text.

---

## 🙏 Acknowledgments

- **Microsoft Semantic Kernel Team** - For the excellent orchestration framework and agent patterns
- **NumPyro/JAX Teams** - For probabilistic programming infrastructure
- **FastAPI Team** - For the modern web framework
- **Google Gemini Team** - For advanced AI models and thinking modes
- **Daytona Team** - For secure sandbox execution environment
- **Open Source Community** - For continuous support and contributions

---

## 📞 Support & Contact

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/Qredence/Reasoning-Kernel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Qredence/Reasoning-Kernel/discussions)
- **Email**: <support@qredence.ai>
- **Twitter**: [@qredence](https://twitter.com/qredence)

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Qredence/Reasoning-Kernel&type=Date)](https://star-history.com/#Qredence/Reasoning-Kernel&Date)

---

**Built with ❤️ by [Qredence](https://qredence.ai) for the AI reasoning community**

[⬆ Back to top](#reasoning-kernel)
