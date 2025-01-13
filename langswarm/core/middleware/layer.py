# middleware1 = MiddlewareLayer(capability_registry=capability_registry)
# middleware2 = MiddlewareLayer()  # Will reference the same instance as middleware1


import re
import signal
import time
from langswarm.core.log import GlobalLogger


class MiddlewareLayer:
    """
    Middleware layer for routing agent inputs to tools, capabilities, or the agent itself.
    Singleton implementation to ensure a single shared instance.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MiddlewareLayer, cls).__new__(cls)
        return cls._instance

    def __init__(self, capability_registry=None, tools=None):
        if not hasattr(self, "_initialized"):  # Ensures __init__ runs only once
            self.capability_registry = capability_registry
            self.tools = tools or {}
            self._initialized = True  # Mark the instance as initialized

    def add_tool(self, name, handler):
        """
        Add or update a tool.
        :param name: str - Name of the tool.
        :param handler: callable - The function to handle the tool's actions.
        """
        self.tools[name] = handler

    def remove_tool(self, name):
        """
        Remove a tool by name.
        :param name: str - Name of the tool to remove.
        """
        if name in self.tools:
            del self.tools[name]

    def add_capability(self, name, capability):
        """
        Add or update a capability.
        :param name: str - Name of the capability.
        :param capability: callable - The function or object representing the capability.
        """
        if self.capability_registry is not None:
            self.capability_registry[name] = capability

    def remove_capability(self, name):
        """
        Remove a capability by name.
        :param name: str - Name of the capability to remove.
        """
        if self.capability_registry and name in self.capability_registry:
            del self.capability_registry[name]
            
    def process_input(self, agent_input):
        """
        Process agent input and route it appropriately.
        :param agent_input: str - The agent's input.
        :return: str - The result from a tool, capability, or the agent itself.
        """
        self._log_event("Processing agent input", "info", agent_input=agent_input)

        # Detect action type
        action_details = self.parse_action(agent_input)
        if action_details:
            return self._route_action(*action_details)

        # If no action is detected, return input unchanged
        self._log_event("No action detected, forwarding input", "info")
        return agent_input

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

    def _log_event(self, message, level, **metadata):
        """
        Log an event to GlobalLogger.
        :param message: str - Log message.
        :param level: str - Log level.
        :param metadata: dict - Additional log metadata.
        """
        if GlobalLogger.is_initialized():
            GlobalLogger.log_event(message=message, level=level, name="middleware", metadata=metadata)
        else:
            print(f"[Fallback Logger] {level.upper()}: {message} - {metadata}")
