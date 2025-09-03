# Contributing to MSA Reasoning Engine

Thank you for your interest in contributing to the MSA Reasoning Engine! This document provides guidelines and information for contributors.

## Development Environment

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Qredence/Reasoning-Kernel.git
   cd Reasoning-Kernel
   ```

2. **Install dependencies:**

   ```bash
   uv pip install -e .
   ```

3. **Frontend setup:**

   ```bash
   cd frontend
   npm install
   ```

### IDE Configuration

**Important:** IDE configuration files and local artifacts should not be committed to the repository. Our `.gitignore` file excludes common IDE files including:

- **Visual Studio Code:** `.vscode/`, `.history/`, `*.code-workspace`
- **JetBrains IDEs:** `.idea/`, `*.iml`, `*.ipr`, `*.iws`
- **Vim/Neovim:** `*.swp`, `*.swo`, `.netrwhist`, `Session.vim`
- **Emacs:** `*~`, `\#*\#`, `.emacs.desktop*`, `*.elc`
- **Sublime Text:** `*.sublime-project`, `*.sublime-workspace`
- **Eclipse:** `.project`, `.classpath`, `.settings/`
- **Atom:** `.atom/`

If you need to add IDE-specific configuration that would benefit all contributors, please discuss it in an issue first.

## Development Workflow

### Code Quality

- **Formatting:** Use `black` for Python code formatting (via pre-commit)
- **Type Checking:** Use `mypy` for static type checking (via pre-commit)
- **Linting:** Use `ruff` for Python linting/formatting (via pre-commit)
- **Frontend:** Use `prettier` for JavaScript/TypeScript formatting

### Testing

Run tests before submitting changes:

```bash
# Backend tests
uv pytest tests/ -v

# Frontend tests (if applicable)
cd frontend
npm run test
```

### Building

```bash
# Backend
uv uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload

# Frontend
cd frontend
npm run dev
```

## Submission Guidelines

1. **Fork** the repository
2. **Create** a feature branch from `main`
3. **Make** your changes with clear, focused commits
4. **Test** your changes thoroughly
5. **Submit** a pull request with a clear description

## Questions?

If you have questions about contributing, please open an issue for discussion.
