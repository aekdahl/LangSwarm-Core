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

