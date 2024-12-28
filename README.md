# LangSwarm-Core

LangSwarm-Core is a framework designed to support multi-agent systems using Large Language Models (LLMs). It provides utilities, memory management, logging integration, and agent orchestration tools to build robust AI ecosystems with modularity and flexibility.

## Features

- **Agent Wrappers**: Easily integrate with LangChain, OpenAI, Hugging Face, and LlamaIndex agents.
- **Memory Management**: Support for in-memory or external memory, with customizable options.
- **Logging**: Seamless integration with LangSmith for advanced logging and tracing.
- **Factory Design**: Create and manage multiple agents with configurable setups.
- **Utilities**: Helper functions for token management, text cleaning, and cost estimation.
- **Registry**: Centralized agent registry to manage and access agents dynamically.

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### From PyPI
Coming soon!

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

### Wrappers
Wrappers add modular capabilities such as:
- Memory management (`MemoryMixin`)
- Logging integration (`LoggingMixin`)

### Utilities
Helper functions for:
- Token and cost estimation
- Text processing
- JSON and YAML validation

### Factory
Use the `AgentFactory` to easily create and configure agents:
```python
agent = AgentFactory.create(
    name="example",
    agent_type="llamaindex",
    documents=["Sample text for indexing"]
)
```

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
Tests are located in the `tests/` directory. Run them using `pytest`:
```bash
pytest
```

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
- Develop CLI tools for managing agents.

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

Feel free to modify this to better fit your specific project details or branding!
