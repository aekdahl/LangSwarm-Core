# Middleware for LangSwarm-Core

## **Overview**
The Middleware layer in the **LangSwarm-Core** module serves as a centralized dispatcher for user inputs. It is designed to analyze inputs, determine whether they should be routed to a tool, a capability, or handled by the agent itself, and ensure seamless integration with the Cortex module.

---

## **Objectives**
1. **Input Analysis**:
   - Identify whether the input is a direct user query or an action that requires a tool or capability.

2. **Action Routing**:
   - Dynamically invoke tools or capabilities based on detected actions.

3. **Agent Fallback**:
   - Pass unhandled queries to the agent for processing.

4. **Cortex Integration**:
   - Log decisions and provide feedback for potential improvements via the Cortex module.

---

## **Architecture**

### **Core Components**
1. **Input Processor**:
   - Parses and interprets user input to detect actions or general queries.

2. **Dispatcher**:
   - Routes actions to the appropriate tools or capabilities.

3. **Agent Fallback**:
   - Forwards unrecognized inputs to the agent for standard processing.

4. **Cortex Integration**:
   - Logs usage data for feedback and optimization.

---

## **Code Implementation**

### **Middleware Class**
```python
class MiddlewareLayer:
    """
    Middleware layer between the user and the agent.
    Analyzes input, routes actions, and determines fallback behavior.
    """
    def __init__(self, agent, capability_registry, tools=None, cortex_logger=None):
        """
        Initialize the middleware.
        :param agent: The main agent.
        :param capability_registry: CapabilityRegistry - The registry of available capabilities.
        :param tools: Dict[str, callable] - Dictionary of tools with their corresponding functions.
        :param cortex_logger: callable or None - Logger for Cortex integration.
        """
        self.agent = agent
        self.capability_registry = capability_registry
        self.tools = tools or {}
        self.cortex_logger = cortex_logger

    def process_input(self, user_input):
        """
        Process user input and determine the appropriate action.
        :param user_input: str - The user's input.
        :return: str - The result from a tool, capability, or the agent.
        """
        # Step 1: Check if input is an action
        action_details = self.parse_action(user_input)
        if action_details:
            action_type, action_name, params = action_details

            # Route to a capability
            if action_type == "capability":
                capability = self.capability_registry.get_capability(action_name)
                if capability:
                    result = capability.run(**params)
                    self.log_to_cortex(action_type, action_name, params, result)
                    return result
                return f"Capability '{action_name}' not found."

            # Route to a tool
            elif action_type == "tool":
                tool = self.tools.get(action_name)
                if tool:
                    result = tool(**params)
                    self.log_to_cortex(action_type, action_name, params, result)
                    return result
                return f"Tool '{action_name}' not found."

        # Step 2: Fallback to agent
        result = self.agent.chat(user_input)
        self.log_to_cortex("agent", "fallback", {"query": user_input}, result)
        return result

    def parse_action(self, user_input):
        """
        Parse the user input to detect actions.
        :param user_input: str - The user's input.
        :return: Tuple[str, str, dict] or None - (action_type, action_name, params) if action detected, else None.
        """
        # Simple action detection logic
        if user_input.startswith("use tool:"):
            parts = user_input[len("use tool:"):].strip().split(" ", 1)
            if len(parts) == 2:
                action_name, params = parts
                return "tool", action_name.strip(), eval(params)  # Convert params string to dict
        elif user_input.startswith("use capability:"):
            parts = user_input[len("use capability:"):].strip().split(" ", 1)
            if len(parts) == 2:
                action_name, params = parts
                return "capability", action_name.strip(), eval(params)  # Convert params string to dict
        return None

    def log_to_cortex(self, action_type, action_name, params, result):
        """
        Log data to the Cortex module for feedback and optimization.
        :param action_type: str - Type of action (tool, capability, agent).
        :param action_name: str - Name of the action.
        :param params: dict - Parameters passed to the action.
        :param result: str - The result of the action.
        """
        if self.cortex_logger:
            log_entry = {
                "action_type": action_type,
                "action_name": action_name,
                "params": params,
                "result": result
            }
            self.cortex_logger(log_entry)
```

---

### **Example Integration**

#### **Initialize Components**
```python
# Capability Registry
capability_registry = CapabilityRegistry()

# Register Capabilities
github_token = "your_github_token"
github_capability = GitHubCodeCapability(github_token)
capability_registry.register_capability(github_capability)

# Define Tools
tools = {
    "search_tool": lambda query: f"Performing search for: {query}",
}

# Cortex Logger
def cortex_logger(log_entry):
    print(f"Logged to Cortex: {log_entry}")

# Agent Initialization
react_agent = ReActAgentWithCapabilities(name="ReActAgent", agent=some_llm_instance, capability_registry=capability_registry)

# Middleware Initialization
middleware = MiddlewareLayer(agent=react_agent, capability_registry=capability_registry, tools=tools, cortex_logger=cortex_logger)
```

#### **Process Input**
**1. Capability Invocation**
```python
user_input = "use capability: GitHubCodeCapability {'action': 'fetch_and_store', 'repo_name': 'openai/langchain', 'file_path': 'langchain/tools/github.py', 'branch': 'main'}"
response = middleware.process_input(user_input)
print(response)
```

**Output**:
```
Code from langchain/tools/github.py in openai/langchain (branch: main) has been processed and stored.
```

**2. Tool Invocation**
```python
user_input = "use tool: search_tool {'query': 'latest trends in AI'}"
response = middleware.process_input(user_input)
print(response)
```

**Output**:
```
Performing search for: latest trends in AI
```

**3. Fallback to Agent**
```python
user_input = "What are the latest advancements in AI?"
response = middleware.process_input(user_input)
print(response)
```

**Output**:
```
<Agent-generated response about advancements in AI>
```

---

## **Features Integrated with Cortex Module**
1. **Action Logging**:
   - Middleware logs all actions (tool, capability, agent fallback) to the Cortex module for tracking and optimization.

2. **Feedback Loops**:
   - Logged data can be used by the Cortex module for:
     - Analyzing agent performance.
     - Identifying frequently used tools or capabilities.
     - Suggesting improvements to workflows.

3. **Extensibility**:
   - New tools and capabilities can be seamlessly added without modifying the middleware logic.

---

## **Next Steps**
1. **Expand Parsing Logic**:
   - Replace simple string parsing with NLP-based intent recognition.

2. **Enhance Cortex Feedback**:
   - Develop mechanisms to act on feedback from the Cortex module (e.g., improving routing).

3. **Advanced Logging**:
   - Log additional metadata, such as execution time and success rates, for deeper insights.

Would you like additional details or refinements for this implementation?



---



# Middleware Layer Implementation for LangSwarm-Core

## Overview
The Middleware layer is designed to analyze agent inputs, dynamically route actions to tools or capabilities, and provide fallback to agents. This implementation includes refined parsing, context management, timeout handling, and logging integration with GlobalLogger.

---

### **Implementation**

#### **middleware_layer.py**
```python
import re
import signal
import time
from langswarm.logging.global_logger import GlobalLogger

class MiddlewareLayer:
    """
    Middleware layer for routing agent inputs to tools, capabilities, or the agent itself.
    """

    def __init__(self, agent, capability_registry, tools=None, memory=None):
        """
        Initialize the middleware.
        :param agent: The main agent.
        :param capability_registry: CapabilityRegistry instance for managing capabilities.
        :param tools: Dictionary of tools with their corresponding functions.
        :param memory: Memory instance for managing context.
        """
        self.agent = agent
        self.capability_registry = capability_registry
        self.tools = tools or {}
        self.memory = memory

    def process_input(self, agent_input):
        """
        Process agent input and route it appropriately.
        :param agent_input: str - The agent's input.
        :return: str - The result from a tool, capability, or the agent itself.
        """
        self._log_event("Processing agent input", "info", agent_input=agent_input)

        # Update memory with agent input
        if self.memory:
            self.memory.save_context({"agent_input": agent_input})

        # Detect action type
        action_details = self.parse_action(agent_input)
        if action_details:
            return self._route_action(*action_details)

        # Fallback to the agent
        return self._agent_fallback(agent_input)

    def parse_action(self, agent_input):
        """
        Parse agent input to detect tools or capabilities.
        :param agent_input: str - The agent's input.
        :return: Tuple[str, str, dict] or None - (action_type, action_name, params).
        """
        tool_match = re.match(r"use tool:\s*(\w+)\s*({.*})", agent_input)
        capability_match = re.match(r"use capability:\s*(\w+)\s*({.*})", agent_input)

        try:
            if tool_match:
                action_name, params = tool_match.groups()
                return "tool", action_name.strip(), eval(params)

            if capability_match:
                action_name, params = capability_match.groups()
                return "capability", action_name.strip(), eval(params)
        except (SyntaxError, ValueError) as e:
            self._log_event(f"Failed to parse action: {e}", "warning")

        return None

    def _route_action(self, action_type, action_name, params):
        """
        Route actions to the appropriate handler.
        :param action_type: str - Type of action (tool or capability).
        :param action_name: str - Name of the action.
        :param params: dict - Parameters for the action.
        :return: str - The result of the action.
        """
        handler = None

        if action_type == "tool":
            handler = self.tools.get(action_name)
        elif action_type == "capability":
            handler = self.capability_registry.get_capability(action_name)

        if handler:
            return self._execute_with_timeout(handler, params)

        self._log_event(f"Action not found: {action_name}", "error")
        return f"{action_type.capitalize()} '{action_name}' not found."

    def _execute_with_timeout(self, handler, params, timeout=10):
        """
        Execute a handler with a timeout.
        :param handler: callable - The action handler.
        :param params: dict - Parameters for the handler.
        :param timeout: int - Timeout in seconds.
        :return: str - The result of the handler.
        """
        def timeout_handler(signum, frame):
            raise TimeoutError("Action execution timed out.")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)

        try:
            start_time = time.time()
            result = handler(**params)
            execution_time = time.time() - start_time
            self._log_event("Action executed successfully", "info", execution_time=execution_time)
            return result
        except TimeoutError:
            self._log_event("Action execution timed out", "error")
            return "The action timed out."
        except Exception as e:
            self._log_event(f"Error executing action: {e}", "error")
            return f"An error occurred: {e}"
        finally:
            signal.alarm(0)

    def _agent_fallback(self, agent_input):
        """
        Fallback to the agent for unhandled inputs.
        :param agent_input: str - The agent's input.
        :return: str - The agent's response.
        """
        result = self.agent.chat(agent_input)
        self._log_event("Agent fallback executed", "info", agent_response=result)
        return result

    def _log_event(self, message, level, **metadata):
        """
        Log an event to GlobalLogger.
        :param message: str - Log message.
        :param level: str - Log level.
        :param metadata: dict - Additional log metadata.
        """
        GlobalLogger.log_event(message=message, level=level, name="middleware", metadata=metadata)
```

---

### **Test Middleware Layer**
#### **test_middleware_layer.py**
```python
import pytest
from langswarm.middleware.middleware_layer import MiddlewareLayer
from unittest.mock import Mock

@pytest.fixture
def mock_agent():
    agent = Mock()
    agent.chat.return_value = "Agent response."
    return agent

@pytest.fixture
def mock_capability_registry():
    registry = Mock()
    registry.get_capability.return_value.run = Mock(return_value="Capability executed.")
    return registry

@pytest.fixture
def middleware(mock_agent, mock_capability_registry):
    return MiddlewareLayer(agent=mock_agent, capability_registry=mock_capability_registry, tools={
        "search_tool": lambda query: f"Searching for: {query}"
    })

def test_tool_routing(middleware):
    response = middleware.process_input("use tool: search_tool {\"query\": \"AI trends\"}")
    assert response == "Searching for: AI trends"

def test_capability_routing(middleware):
    response = middleware.process_input("use capability: test_capability {\"key\": \"value\"}")
    assert response == "Capability executed."

def test_agent_fallback(middleware):
    response = middleware.process_input("Tell me about AI.")
    assert response == "Agent response."

def test_action_timeout(middleware):
    def slow_tool(**params):
        time.sleep(11)
        return "Finished."

    middleware.tools["slow_tool"] = slow_tool
    response = middleware.process_input("use tool: slow_tool {\"param\": \"test\"}")
    assert response == "The action timed out."
```

---

### **Next Steps**
1. **Advanced Parsing**: Extend `parse_action` to use NLP-based parsing.
2. **Cortex Feedback Integration**: Incorporate feedback from Cortex for further optimization.
3. **Enhanced Observability**: Add metrics collection for monitoring middleware performance.

Let me know if further refinements are needed! 🚀

