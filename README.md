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
from langswarm.core.factory.agents import AgentFactory

# Set environment variables
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'

# Create a LangChain agent
agent = AgentFactory.create(
    name="example_agent",
    agent_type="langchain-openai",
    model="gpt-4"
)

# Use the agent to respond to queries
response = agent.chat("What is LangSwarm?")
print(response)
```

### Memory Integration

LangSwarm-Core supports memory out of the box. Here's how to initialize an agent with memory:

```python
from langswarm.core.factory.agents import AgentFactory
from langchain.memory import ConversationBufferMemory

# Set environment variables
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'

# Define memory for the agent
memory = ConversationBufferMemory()

# Create a LangChain agent with memory using AgentFactory
agent = AgentFactory.create(
    name="memory_agent",
    agent_type="langchain-openai",
    memory=memory,
    model="gpt-4"
)

# Interact with the agent
response1 = agent.chat("What is LangSwarm-Core?")
print(f"Agent: {response1}")

response2 = agent.chat("Can you tell me more about its features?")
print(f"Agent: {response2}")

# Showcase memory retention
response3 = agent.chat("What have we discussed so far?")
print(f"Agent: {response3}")
```

#### Customizing Memory
To use a different LangChain memory type, you can replace ConversationBufferMemory with another memory class. For example:

```python
from langchain.memory import ConversationSummaryMemory

# Create a separate LLM for memory summarization
memory_llm = OpenAI(model="gpt-3.5-turbo", openai_api_key="your-openai-api-key")

# Define the memory module using the summarization LLM
memory = ConversationSummaryMemory(llm=memory_llm)
```

### LangSmith Integration

LangSwarm-Core supports LangSmith out of the box. Here's how to initialize an agent with LangSmith:

```python
from langswarm.core.factory.agents import AgentFactory

# Set environment variables
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key'

# Create a LangChain agent
agent = AgentFactory.create(
    name="example_agent",
    agent_type="langchain-openai",
    langsmith_api_key="your-langsmith-api-key",
    model="gpt-4"
)

# Use the agent to respond to queries
response = agent.chat("What is LangSwarm?")
print(response)
```

### Bring your own agent

LangSwarm-Core supports other agents out of the box. Here's how to wrap an external agent with LangSwarm:

#### Hugging Face

```python
from transformers import pipeline
from langswarm.core.wrappers.generic import AgentWrapper

# Step 1: Create a Hugging Face pipeline
huggingface_agent = pipeline("text-generation", model="gpt2")

# Step 2: Wrap the Hugging Face agent using LangSwarm's AgentWrapper
wrapped_agent = AgentWrapper(
    name="my_agent",
    agent=huggingface_agent,
    memory=None,  # Optional: Add memory support if needed
    is_conversational=True  # Enable conversational context if needed (only for Hugging Face)
)

# Step 3: Interact with the wrapped agent
query = "Explain the concept of modular AI frameworks."
response = wrapped_agent.chat(query)
print(f"User: {query}")
print(f"Agent: {response}")

# Step 4: Add more interactions to showcase memory retention (if enabled)
wrapped_agent.chat("Can you elaborate on the benefits of modularity?")
response = wrapped_agent.chat("What was the initial query?")
print(f"Agent: {response}")

# Step 5: Reset the memory and start a new conversation
wrapped_agent.chat("Let's reset and discuss LangSwarm-Core.", reset=True)
response = wrapped_agent.chat("What is LangSwarm-Core?")
print(f"Agent: {response}")
```

#### Hugging Face
```python
from langchain.llms import OpenAI
from langchain.chains import SimpleSequentialChain, LLMChain
from langchain.prompts import PromptTemplate
from langswarm.core.wrappers.generic import AgentWrapper

# Step 1: Create a LangChain LLM instance
llm = OpenAI(model="gpt-3.5-turbo", openai_api_key="your-openai-api-key")

# Step 2: Build a LangChain pipeline (e.g., a simple sequential chain)
template = PromptTemplate(template="What is {topic}? Explain in detail.")
llm_chain = LLMChain(llm=llm, prompt=template)

# Step 3: Wrap the LangChain agent using LangSwarm's AgentWrapper
wrapped_langchain_agent = AgentWrapper(
    name="langchain_agent",
    agent=llm_chain,
    memory=None,  # Optionally add memory
)

# Step 4: Interact with the wrapped LangChain agent
query = {"topic": "LangSwarm-Core"}
response = wrapped_langchain_agent.chat(query)
print(f"User: What is LangSwarm-Core?")
print(f"Agent: {response}")

# Step 5: Showcase conversational context (if memory is enabled)
wrapped_langchain_agent.chat("Can you summarize your explanation?")
response = wrapped_langchain_agent.chat("What was the topic of discussion?")
print(f"Agent: {response}")

# Step 6: Reset the agent and start a new conversation
wrapped_langchain_agent.chat("Reset and start over.", reset=True)
response = wrapped_langchain_agent.chat({"topic": "modular AI frameworks"})
print(f"Agent: {response}")
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

