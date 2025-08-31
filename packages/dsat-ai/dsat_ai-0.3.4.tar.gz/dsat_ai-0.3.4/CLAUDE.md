# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `dsat` (Dan's Simple Agent Toolkit), a Python project using uv for dependency management. Refer to the `docs/` directory for detailed documentation on the project structure, usage, and features.

The project consists of two main modules:
- **agents**: Provides an abstraction for LLM agents, including a factory for creating provider
- **scryptorum**: A CLI-based framework for running and tracking LLM experiments.

## Development Commands

- **Install dependencies**: `uv sync`
- **Install with dev dependencies**: `uv sync --extra dev`
- **Install with server support**: `uv sync --extra server`
- **Run the example**: `python main.py`
- **Run CLI commands**: `python -m dsat.cli.commands <command>`
- **Format code**: `black src/`
- **Lint code**: `ruff check src/`

## Configuration

### Environment Variables

- **SCRYPTORUM_EXPERIMENTS_DIR**: Default directory for scryptorum experiments (default: `./experiments`)

### Project Integration

Scryptorum integrates with existing Python projects:
- **Initialization**: `scryptorum init` creates `.scryptorum` config file in your Python project
- **Auto-detection**: CLI commands automatically find projects via `.scryptorum` file
- **Flexible structure**: Experiment tracking can be stored anywhere (separate drive, shared storage, etc.)
- **Code separation**: Your Python code stays in your package, tracking data in scryptorum project

### Directory Structure

```
your_python_package/              # Your normal Python project
├── src/your_package/
│   └── experiments/             # Your experiment code
├── .scryptorum                  # Points to scryptorum project
└── pyproject.toml              # Dependencies include scryptorum

~/research/                      # Configurable scryptorum location  
└── your_package/               # Scryptorum project (tracks experiments)
    ├── experiments/
    │   └── experiment_name/    # Experiment tracking data
    └── data/                   # Shared experiment data
```

## Project Structure

- `main.py` - Example usage demonstrating both decorator and manual APIs
- `src/scryptorum/` - Main framework code
  - `core/` - Core experiment and run management
    - `experiment.py` - Experiment class and project creation
    - `runs.py` - TrialRun and MilestoneRun classes  
    - `decorators.py` - Annotation-driven experiment framework
  - `execution/` - Execution engine and utilities
    - `runner.py` - Runner class and BaseRunnable
  - `cli/` - Command-line interface
  - `plugins/` - Plugin architecture (HTTP server ready)

## Key Features

- **Dual run types**: TrialRun (logs only) vs MilestoneRun (full versioning)
- **Annotation-driven**: `@experiment`, `@metric`, `@timer`, `@llm_call` decorators
- **Thread-safe logging**: JSONL format for metrics, timings, and events
- **Plugin architecture**: Ready for HTTP server and other extensions
- **Modern Python**: Python 3.12+, type hints, async-ready

## Dependencies

- `pathlib>=1.0.1` - Path manipulation utilities  
- `python-dotenv>=1.1.0` - Environment variable loading
- Optional: `fastapi` + `uvicorn` for HTTP server plugin
- Dev: `pytest`, `black`, `ruff` for testing and code quality

## Usage Patterns

1. **Decorator-based**: Use `@experiment` decorator on functions
2. **Class-based**: Extend `BaseRunnable` with prepare/run/score/cleanup methods  
3. **Manual**: Create `Experiment` and `Run` objects directly