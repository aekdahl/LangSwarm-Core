# LangSwarm-Core

LangSwarm-Core is a framework designed to support multi-agent systems using Large Language Models (LLMs). It provides utilities, memory management, logging integration, agent orchestration tools, and a factory-based approach to building robust AI ecosystems with modularity and flexibility.

## Features

- **Agent Factory**: Dynamically create and configure agents for LangChain, OpenAI, Hugging Face, and LlamaIndex.
- **Wrappers**:
  - **Memory Mixin**: Seamless in-memory or external memory integration.
  - **Logging Mixin**: Advanced logging support using LangSmith and fallback loggers.
- **Registry**: A centralized agent registry for managing and accessing agents dynamically.
- **Modular Architecture**: Easily extend the framework by implementing additional mixins, factories, or agent types.

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### From PyPI
  ```bash
  pip install langswarm-core
  ```

---

## Usage

### Quick Start

Here's an example of how to use LangSwarm-Core to create an agent and interact with it:

```python
from core.factory.agents import AgentFactory

# Create a LangChain agent
agent = AgentFactory.create(
    name="example_agent",
    agent_type="langchain-openai",
    memory=[],
    langsmith_api_key="your-langsmith-api-key",
    model="gpt-4"
)

# Use the agent to respond to queries
response = agent.chat("What is LangSwarm?")
print(response)
```

### Memory Integration

LangSwarm-Core supports memory out of the box. Here's how to initialize an agent with memory:

```python
from core.factory.agents import AgentFactory

memory = []  # Initialize in-memory storage

agent = AgentFactory.create(
    name="memory_agent",
    agent_type="langchain-openai",
    memory=memory,
    model="gpt-4"
)

response = agent.chat("Remember this: LangSwarm is awesome.")
print(response)
```

---

## Components

### Factory
The `AgentFactory` provides a simple interface for creating agents:
- Supports LangChain, Hugging Face, OpenAI, and LlamaIndex agents.
- Configurable with memory, logging, and other custom parameters.

### Wrappers
Wrappers extend agent capabilities:
- **MemoryMixin**: Adds memory management functionality.
- **LoggingMixin**: Integrates LangSmith for advanced logging.

### Utilities
Helper functions include:
- Token and cost estimation.
- Text processing and cleaning.
- JSON, YAML, and Python code validation.

### Registry
The `AgentRegistry` provides a centralized way to manage and query all agents created in the system.

---

## Development

### Setting Up the Environment
1. Clone the repository:
   ```bash
   git clone https://github.com/aekdahl/langswarm-core.git
   cd langswarm-core
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Tests
Run tests located in the `tests/` directory using `pytest`:
```bash
pytest
```

---

## File Structure
- `core/wrappers/`: Contains mixins for memory and logging.
- `core/factory/`: Defines the `AgentFactory` for creating agents.
- `core/registry/`: Manages a centralized agent registry.
- `core/utils/`: Provides utility functions for validation, token management, and text processing.

---

## Contributing

We welcome contributions! To get started:
1. Fork the repository.
2. Create a feature branch.
3. Make your changes and write tests.
4. Submit a pull request.

---

## Roadmap

- Add support for additional LLM providers.
- Expand orchestration capabilities with reinforcement learning agents.
- Introduce support for dynamic task allocation and meta-agent coordination.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

LangSwarm-Core relies on several amazing libraries, including:
- [LangChain](https://github.com/hwchase17/langchain)
- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [LlamaIndex](https://github.com/jerryjliu/llama_index)

---

