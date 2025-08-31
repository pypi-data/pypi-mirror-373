# Dan's Simple Agent Toolkit (DSAT) Project Overview

This project contains a set of tools to make it easy to create python applications that leverage LLM applications.
It consists of two primary sub-modules, each of which can be used independently:
- **agents**: An abstraction of LLM agents with a factory for create provider specific instances. Also includes a powerful but simple prompt versioning system.
- **scryptorum**: A simple CLI-based agent testing framework for creating and running agentic experiments.

Projects can choose to use just the agent module to have access to the agent abstraction, factory and prompt management. They can also choose to use the scryptorum module to run experiments with agents, or they can use both modules together for a complete agent development and testing framework.

## Agent-Scryptorum Integration

The two modules can be used independently or together. When used together, the agents module provides `AgentExperiment` and `AgentRun` classes that extend scryptorum's base classes:

### AgentExperiment Class
The `AgentExperiment` class (in agents module) extends `scryptorum.Experiment` with agent-specific features:

- **Agent creation**: `experiment.create_agent("agent_name")` with configuration override support
- **Agent config management**: Create, load, update, and delete agent configurations  
- **Automatic snapshotting**: Agent configs automatically copied to milestone runs for reproducibility
- **Enhanced metadata**: Experiment metadata includes agent configurations and availability

### AgentRun Class  
The `AgentRun` class extends `scryptorum.Run` with agent-aware logging:

- **Agent creation logging**: `run.log_agent_created(name, config_data)`
- **Agent invocation logging**: `run.log_agent_invoke(name, prompt, response, duration)`
- **Enhanced LLM logging**: `run.log_llm_call()` supports agent_name, prompt_name, prompt_version

### Clean Architecture
- **No coupling**: Scryptorum has no dependencies on agents module
- **Optional enhancement**: Agents module optionally imports scryptorum for enhanced experiment classes
- **Independent operation**: Each module works perfectly on its own


## Agents
The `agents` module provides a framework for creating and managing LLM agents. 
In the context of this project, an "agent" is a python object bound to an LLM provider and wired up with a prompt and any required tools. Agents typically represent a specific task or role that the LLM can perform, such as answering questions, generating text, or performing specific actions based on user input.

The module includes:
- **Agent Configuration**: A configuration system for setting up agents with specific parameters, such as agent name, prompt, model type, temperature, and other LLM-specific settings. Agent configs are typically stored in JSON or YAML files with many agents demarked by a unique name.
- **Agent Factory**: A factory for creating agents from various providers (e.g., OpenAI, Anthroptic, Vertex, etc.). This allows for easy integration with different LLM providers.
- **Prompt Versioning**: A system for managing and versioning prompts, making it easy to track changes and improvements over time.
- **Agent Abstraction**: A simple abstraction for agents that allows for easy interaction with LLMs, including sending messages and receiving responses.
- **Agent Implementations**: Pre-built implementations of common agent providers.
- **Agent Tools**: each agent config can specific a list of MCP services that the agent has available to it.

### Agent Config
Agents are defined declaratively with configurations (JSON or TOML). The agent config file will be a dict and can have one or more agents defined by key=name value=config.
The values in the agent config are:
- agent_name: str  # unique name of agent within project context
- model_provider: str  # the hosting provider of model / will define which Agent sub-class is used 
- model_family: str  # the overall model family (e.g. OpenAI or Anthropic) - important when using a multi-model host
- model_version: str  # the specific model+version
- prompt: str  # Prompt in format "name:version" or "name:latest" 
- model_parameters: Optional[dict] = None  # settings specific to the model
- provider_auth: Optional[Dict[str, str]] = None  # any auth details needed for the host
- custom_configs: Optional[Dict[str, Any]] = None  # Additional custom configuration for this agent
- tools: Optional[List] = None  # FUTURE: list of all MCP tools available to the agent
- prepend_datetime: Optional[bool] = True  # Whether to prepend current date/time to system prompts

This configuration will be passed into the Agent factory method and used to initialize the agent.

### Prompt System
Prompts are stored in a "prompts" directory (configurable) with each named prompt in its own TOML file (e.g. "my_prompt.toml"). The TOML contains one or more K/V pairs. The key is the prompt version written as "v{#}" (e.g. v1 or v3). The value is a multi-line text string """ """ containing the prompt. The format allows for curly brackets to be used in the prompt (e.g. for sample returns) but also supports placeholder to be filled with python str.format() calls.

The PromptManager class takes the location of the prompts dir and then loads prompts on demand. It uses the name and version to load the prompt. If the version is missing or "latest", it will return the highest number version prompt.

Prompts are defined in the AgentConfig as "name:version" or "name:latest"

#### Automatic DateTime Prepending
By default, agents automatically prepend the current date, time, and timezone to system prompts. This helps provide LLMs with current temporal context. The feature can be controlled via the `prepend_datetime` configuration option:

- **Enabled (default)**: Prepends "Current date and time: YYYY-MM-DD HH:MM:SS TZ\n\n" to system prompts
- **Disabled**: Uses system prompts exactly as stored in prompt files

Example with datetime prepending enabled:
```
Current date and time: 2024-08-30 15:30:45 PST

You are a helpful assistant. Please respond clearly and concisely.
```

## Scryptorum
Scryptorum is a modern, annotation-driven framework for running and tracking LLM experiments. It simplifies development of LLM applications and agents by offering tools to manually or automatically track artifacts and results of experiment runs with minimal boilerplate.
It is designed to work seamlessly with Python projects, allowing you to focus on your research while it handles experiment management, versioning, and logging.

Key features include:
* **Dual run types**: Lightweight trial runs (logs only) vs milestone runs (full versioning)
* **Annotation-driven**: Use `@experiment`, `@metric`, `@timer`, `@llm_call` decorators for automatic tracking
* **CLI-configurable**: Same code runs as trial or milestone based on CLI flags
* **Thread-safe logging**: JSONL format for metrics, timings, and LLM invocations
* **Plugin architecture**: Ready for HTTP server and custom extensions
* **Modern Python**: Built for Python 3.13+ with type hints and clean dependencies

### Core Concepts

Scryptorum organizes your work into a three-level hierarchy:

#### Project
A **project** is a workspace that contains multiple related experiments. Think of it as a research grant or lab.

- **Purpose**: Groups related experiments and provides shared resources
- **Contains**: Multiple experiments, shared data, models, and artifacts
- **Example**: "NLP for Healthcare", "Customer Service AI", "Code Analysis Tools"
- **Lifespan**: Long-lived, evolves over months/years

#### Experiment  
An **experiment** represents a specific research question or hypothesis you're testing. Think of it as a focused study within your broader research.

- **Purpose**: Organizes all attempts at solving a particular problem
- **Contains**: Multiple runs, experiment-specific configs, prompts, and data
- **Examples**: "sentiment_analysis", "document_summarization", "code_generation"
- **Lifespan**: Medium-lived, contains many runs as you iterate and improve

#### Run
A **run** is a single execution of an experiment - one specific attempt with particular parameters, data, or code.

- **Purpose**: Records the results of one specific attempt
- **Types**:
  - **Trial Run**: Quick iterations for development (logs only)
  - **Milestone Run**: Important versions with full snapshots (code, configs, artifacts)
- **Examples**: Testing different prompts, model parameters, or datasets
- **Lifespan**: Immutable once finished
