# PicoAgents [Beta]

A minimal multi-agent framework for educational purposes, accompanying the book "Designing Multi-Agent Systems: Principles, Patterns, and Implementation for AI Agents" by Victor Dibia.

> Note: While the principles in this library are "production-ready" and mirror many of the decisions made in frameworks like AutoGen, Google ADK etc, careful consideration should be given before using it in production environments.

## Overview

PicoAgents demonstrates core multi-agent concepts by building agents and coordination patterns from scratch. It's designed to be:

- **Educational**: Clear, well-documented implementations of core concepts
- **Minimal**: Focused on essential patterns without unnecessary complexity
- **Extensible**: Easy to modify and experiment with different approaches
- **Type-safe**: Full typing support with pyright/mypy

## Installation

```bash
# Install from PyPI (when published)
pip install picoagents

# Or install from source
git clone <repository-url>
cd picoagents
pip install -e .
```

## Quick Start

### Creating a Basic Agent

```python
from picoagents import Agent, get_weather

# Create an agent with tools
agent = Agent(
    name="weather_assistant",
    instructions="You are a helpful weather assistant.",
    model="gpt-4",
    tools=[get_weather]
)

# Use the agent
response = agent.run("What's the weather like in San Francisco?")
print(response)
```

### Sequential Workflow Pattern

```python
from picoagents import Agent, SequentialWorkflow, AgentNode

# Create agents
researcher = Agent("researcher", "You research topics thoroughly.")
writer = Agent("writer", "You write clear, engaging content.")
editor = Agent("editor", "You edit and improve text.")

# Create workflow
workflow = SequentialWorkflow("content_pipeline")
workflow.add_node(AgentNode("research", researcher))
workflow.add_node(AgentNode("write", writer))
workflow.add_node(AgentNode("edit", editor))

# Run workflow
result = workflow.run("Write an article about renewable energy")
```

### Round-Robin Orchestration

```python
from picoagents import Agent, RoundRobinOrchestrator

# Create specialized agents
coder = Agent("coder", "You write clean, efficient code.")
tester = Agent("tester", "You test code and find bugs.")
reviewer = Agent("reviewer", "You review code quality.")

# Create orchestrator
orchestrator = RoundRobinOrchestrator("development_team")
orchestrator.add_agent(coder)
orchestrator.add_agent(tester)
orchestrator.add_agent(reviewer)

# Solve task collaboratively
result = orchestrator.orchestrate("Create a Python function to calculate fibonacci numbers")
```

## Core Concepts

### Agents (Chapter 4)

The foundation of the framework is the `Agent` class that implements:

- **Reasoning**: Integration with language models (OpenAI GPT, etc.)
- **Acting**: Tool calling and execution
- **Memory**: Information storage and retrieval
- **Communication**: Message history and context management

### Workflow Patterns (Chapter 2 - Explicit Control)

Predefined execution paths with deterministic behavior:

- **Sequential**: Linear execution (A → B → C)
- **Conditional**: Branching logic with decision points
- **Parallel**: Concurrent execution with fan-out/fan-in

### Orchestration Patterns (Chapter 2 - Autonomous Control)

Runtime-determined coordination through agent reasoning:

- **Round-Robin**: Simple turn-taking between agents
- **LLM-Based**: AI-driven agent selection and coordination
- **Plan-Based**: Explicit planning with dynamic execution

## Architecture

```
src/picoagents/
├── agents.py          # Core Agent implementation
├── multiagent.py      # High-level system coordination
├── workflow/          # Explicit control patterns
│   ├── base.py        # Base classes and abstractions
│   ├── sequential.py  # Sequential workflow pattern
│   ├── conditional.py # Conditional/branching workflows
│   └── parallel.py    # Parallel execution patterns
└── orchestration/     # Autonomous control patterns
    ├── base.py        # Base orchestration classes
    ├── roundrobin.py  # Round-robin coordination
    ├── llm.py         # LLM-based coordination
    └── planner.py     # Plan-based orchestration
```

## Examples

The `examples/` directory contains implementations from each chapter:

- `chapter04_basic_agent.py` - Building your first agent
- `chapter05_workflow_patterns.py` - Multi-agent workflows
- `chapter06_orchestration.py` - Autonomous coordination
- `advanced_examples.py` - Complex multi-agent systems

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run type checking
pyright

# Run tests
pytest

# Format code
black src/
isort src/
```

## Requirements

- Python 3.9+
- OpenAI API key (set `OPENAI_API_KEY` environment variable)
- Optional: Other LLM providers (configure in agent initialization)

## Contributing

This is an educational framework designed to accompany the book. Contributions should:

1. Maintain clarity and simplicity
2. Include comprehensive documentation
3. Follow the established patterns
4. Include tests and type hints

## License

MIT License - see LICENSE file for details.

## Related Resources

- Book: "Designing Multi-Agent Systems: Principles, Patterns, and Implementation"
- Documentation: [Coming soon]
- Examples: See `examples/` directory

## Citation

If you use this framework in academic work, please cite:

```bibtex
@book{dibia2025multiagent,
  title={Designing Multi-Agent Systems: Principles, Patterns, and Implementation},
  author={Dibia, Victor},
  year={2025},
  publisher={...}
}
```
