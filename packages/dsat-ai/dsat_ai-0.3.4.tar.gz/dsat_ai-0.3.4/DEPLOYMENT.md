# PyPI Deployment Guide

This guide explains how to deploy `dsat-ai` to PyPI.

## Prerequisites

1. Create accounts on PyPI:
   - Test PyPI: https://test.pypi.org/account/register/
   - Production PyPI: https://pypi.org/account/register/

2. Install deployment tools:
   ```bash
   pip install build twine
   ```

3. Configure API tokens:
   ```bash
   # Create ~/.pypirc
   [distutils]
   index-servers = 
     pypi
     testpypi
   
   [pypi]
   username = __token__
   password = <your-pypi-api-token>
   
   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = <your-test-pypi-api-token>
   ```

## Building the Package

```bash
# Clean previous builds
rm -rf dist/ build/

# Build the package
python -m build
```

This creates:
- `dist/dsat_ai-0.1.0.tar.gz` (source distribution)
- `dist/dsat_ai-0.1.0-py3-none-any.whl` (wheel distribution)

## Testing the Package

### Upload to Test PyPI

```bash
python -m twine upload --repository testpypi dist/*
```

### Install from Test PyPI

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ dsat-ai
```

### Test Installation

```python
# Test basic imports
from dsat import Agent, AgentConfig, experiment, metric, timer

# Test CLI
dsat --help
scryptorum --help
```

## Production Deployment

### Upload to PyPI

```bash
python -m twine upload dist/*
```

### Verify Installation

```bash
pip install dsat-ai
```

## Version Management

1. Update version in `pyproject.toml`:
   ```toml
   [project]
   version = "0.1.1"  # Increment version
   ```

2. Update version in `src/dsat/__init__.py`:
   ```python
   __version__ = "0.1.1"
   ```

3. Create git tag:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

## Package Features

The `dsat-ai` package provides:

### CLI Commands
- `dsat`: Main DSAT CLI
- `scryptorum`: Experiment management CLI

### Core Modules
- `dsat.agents`: Multi-provider LLM agents
- `dsat.scryptorum`: Experiment tracking framework

### Optional Dependencies
- `dsat-ai[all]`: All provider dependencies
- `dsat-ai[anthropics]`: Anthropic Claude support
- `dsat-ai[google]`: Google Vertex AI support
- `dsat-ai[ollama]`: Ollama local model support
- `dsat-ai[server]`: HTTP server capabilities
- `dsat-ai[dev]`: Development tools

## Installation Examples

```bash
# Basic installation
pip install dsat-ai

# With all providers
pip install dsat-ai[all]

# With specific providers
pip install dsat-ai[anthropics,google]

# Development installation
pip install dsat-ai[dev]
```

## Usage Examples

```python
# Basic agent usage
from dsat import Agent, AgentConfig

config = AgentConfig(
    agent_name="assistant",
    model_provider="anthropic",
    model_family="claude",
    model_version="claude-3-5-haiku-latest",
    prompt="helper:v1"
)

agent = Agent.create(config)
response = agent.invoke("Hello!")

# Experiment tracking
from dsat import experiment, metric

@experiment(name="my_experiment")
def run_experiment():
    result = some_computation()
    accuracy = evaluate(result)
    return accuracy

@metric(name="accuracy", metric_type="accuracy")
def evaluate(result):
    return 0.95
```