import re
import signal
import time
from langswarm.core.log import GlobalLogger

class MiddlewareLayer:
    """
    Middleware layer for routing agent inputs to tools, capabilities, or the agent itself.
    Instance-specific implementation for agent-specific tools and capabilities.
    """
    def __init__(self, tools=None, capabilities=None):
        """
        Initialize the middleware.

        :param tools: dict - Dictionary of tools with their corresponding handlers.
        :param capabilities: dict - Dictionary of capabilities with their corresponding handlers.
        """
        self.tools = tools or {}
        self.capabilities = capabilities or {}

    def process_input(self, agent_input):
        """
        Process agent input and route it appropriately.

        :param agent_input: str - The agent's input.
        :return: Tuple[int, str] - (status_code, result).
        """
        self._log_event("Processing agent input", "info", agent_input=agent_input)

        # Detect action type
        action_details = self.parse_action(agent_input)
        if action_details:
            return self._route_action(*action_details)

        # If no action is detected, return input unchanged
        self._log_event("No action detected, forwarding input", "info")
        return 200, agent_input

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
        :return: Tuple[int, str] - (status_code, result).
        """
        handler = None

        if action_type == "tool":
            handler = self.tools.get(action_name)
        elif action_type == "capability":
            handler = self.capabilities.get(action_name)

        if handler:
            return self._execute_with_timeout(handler, params)

        self._log_event(f"Action not found: {action_name}", "error")
        return 404, f"{action_type.capitalize()} '{action_name}' not found."

    def _execute_with_timeout(self, handler, params, timeout=10):
        """
        Execute a handler with a timeout.

        :param handler: callable - The action handler.
        :param params: dict - Parameters for the handler.
        :param timeout: int - Timeout in seconds.
        :return: Tuple[int, str] - (status_code, result).
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
            return 200, result
        except TimeoutError:
            self._log_event("Action execution timed out", "error")
            return 408, "The action timed out."
        except Exception as e:
            self._log_event(f"Error executing action: {e}", "error")
            return 500, f"An error occurred: {e}"
        finally:
            signal.alarm(0)

    def _log_event(self, message, level, **metadata):
        """
        Log an event to GlobalLogger.

        :param message: str - Log message.
        :param level: str - Log level.
        :param metadata: dict - Additional log metadata.
        """
        GlobalLogger.log_event(message=message, level=level, name="middleware", metadata=metadata)

    def add_tool(self, name, handler):
        """
        Add or update a tool.

        :param name: str - Name of the tool.
        :param handler: callable - The function to handle the tool's actions.
        """
        self.tools[name] = handler

    def add_capability(self, name, capability):
        """
        Add or update a capability.

        :param name: str - Name of the capability.
        :param capability: callable - The function or object representing the capability.
        """
        self.capabilities[name] = capability

    def remove_tool(self, name):
        """
        Remove a tool by name.

        :param name: str - Name of the tool to remove.
        """
        if name in self.tools:
            del self.tools[name]

    def remove_capability(self, name):
        """
        Remove a capability by name.

        :param name: str - Name of the capability to remove.
        """
        if name in self.capabilities:
            del self.capabilities[name]
