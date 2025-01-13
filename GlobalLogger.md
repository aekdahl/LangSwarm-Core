# GlobalLogger for LangSwarm

## **Overview**
The **GlobalLogger** in LangSwarm is a centralized logging utility designed to provide consistent, structured, and flexible logging across the entire LangSwarm ecosystem. It enables:

1. **Centralized Logging**:
   - Unified logging for all agents, tools, and capabilities.
   - Enhanced observability and traceability.

2. **Integration with LangSmith**:
   - Automatic integration with LangSmith for agents that support it.

3. **Support for Non-Agent Logs**:
   - Allows logging for system-level operations and components outside individual agents.

4. **Customizable Logging Levels**:
   - Supports standard logging levels (`info`, `warning`, `error`, `critical`, `debug`).

5. **Dynamic Metadata**:
   - Enrich log entries with context-specific metadata.

---

## **Features**

### **1. Centralized Initialization**
The **GlobalLogger** is initialized once and can be accessed globally across the LangSwarm ecosystem.

```python
from langswarm.logging.global_logger import GlobalLogger

# Initialize the logger
GlobalLogger.initialize(api_key="YOUR_LANGSMITH_API_KEY")
```

### **2. Integration with LangSmith**
- Automatically uses LangSmith for agents if they are initialized with LangSmith-enabled LLMs.
- Provides a fallback logger if LangSmith is not available or configured.

### **3. Flexible Usage**
- Logs can be tied to specific agents, tools, or capabilities.
- Supports standalone logging for non-agent-specific tasks.

```python
# Log a message with metadata
GlobalLogger.log_event(
    message="A new capability was invoked",
    level="info",
    name="capability_logger",
    value=42,
    metadata={"capability": "GitHubCodeCapability"}
)
```

### **4. Context-Aware Logs**
- Automatically associates logs with their source (e.g., agent, tool, or capability).
- Option to add custom metadata for enhanced traceability.

---

## **How to Use GlobalLogger**

### **Step 1: Initialization**
Before using the GlobalLogger, initialize it during application setup:

```python
from langswarm.logging.global_logger import GlobalLogger

# Initialize GlobalLogger (typically in your application entry point)
GlobalLogger.initialize(api_key="YOUR_LANGSMITH_API_KEY")
```

- If LangSmith is not available, GlobalLogger will default to using Python's `logging` module.

---

### **Step 2: Logging Events**
#### **Log a Simple Event**

```python
GlobalLogger.log_event(
    message="Agent has started",
    level="info",
    name="agent_lifecycle"
)
```

#### **Log with Metadata**

```python
GlobalLogger.log_event(
    message="Fetching data from GitHub",
    level="debug",
    name="github_capability",
    metadata={"repo": "openai/langchain", "branch": "main"}
)
```

#### **Custom Levels and Values**

```python
GlobalLogger.log_event(
    message="High memory usage detected",
    level="warning",
    name="system_monitor",
    value=85.5,  # Memory usage percentage
    metadata={"threshold": 80}
)
```

---

### **Step 3: Integrate with LangSwarm Components**

#### **Agent Integration**
If an agent supports LangSmith, it will automatically use LangSmith for logging. Otherwise, GlobalLogger serves as the fallback logger.

```python
from langswarm.core.wrappers.generic import AgentWrapper
from langswarm.logging.global_logger import GlobalLogger

agent = AgentWrapper(name="TestAgent", agent=some_llm_instance)
GlobalLogger.log_event(
    message="Agent initialized successfully",
    level="info",
    name="agent_logger",
    metadata={"agent_name": agent.name}
)
```

#### **Middleware Integration**
GlobalLogger can be used in middleware to log tool and capability invocations:

```python
class MiddlewareLayer:
    def __init__(self, agent, capability_registry):
        self.agent = agent
        self.capability_registry = capability_registry

    def process_input(self, user_input):
        GlobalLogger.log_event(
            message=f"Processing input: {user_input}",
            level="info",
            name="middleware",
            metadata={"user_input": user_input}
        )

        # Handle input routing...
```

---

### **Step 4: Monitor Logs**
- If using LangSmith, logs can be monitored in the LangSmith dashboard.
- For fallback logging, logs are written to the standard output or a file (as configured in Python’s logging).

---

## **Best Practices**

1. **Initialize Early**:
   - Initialize GlobalLogger as part of your application’s startup process.

2. **Use Metadata**:
   - Always include relevant metadata to provide context for your logs.

3. **Avoid Over-Logging**:
   - Use appropriate log levels to prevent clutter and ensure meaningful insights.

4. **Leverage LangSmith**:
   - If available, utilize LangSmith’s advanced logging and tracing features for enhanced observability.

5. **Standardize Logging Across Teams**:
   - Define consistent logging formats and levels for all components of LangSwarm.

---

## **Advanced Features**

### **Custom Log Handlers**
Extend GlobalLogger to integrate with third-party logging platforms like Datadog or Elasticsearch:

```python
from langswarm.logging.global_logger import GlobalLogger

class CustomHandler:
    def handle(self, log_entry):
        # Custom logic to process and send logs
        print("Custom log handler:", log_entry)

GlobalLogger.add_handler(CustomHandler())
```

---

## **Troubleshooting**

1. **Log Entries Not Showing Up**:
   - Ensure GlobalLogger is initialized before use.
   - Check if the LangSmith API key is correctly configured.

2. **Fallback Logger in Use**:
   - If LangSmith is unavailable, ensure the Python logging configuration meets your needs.

3. **Custom Metadata Not Appearing**:
   - Verify that metadata keys and values are correctly formatted.

---

## **Next Steps**

1. Explore how GlobalLogger integrates with Cortex for feedback loops.
2. Extend logging to support asynchronous workflows.
3. Introduce pre-configured dashboards for LangSmith monitoring.

---

For further assistance or to contribute to LangSwarm-Core, visit the [GitHub Repository](https://github.com/aekdahl/LangSwarm-Core).

