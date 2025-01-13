import re
import signal
import time
from langswarm.core.log import GlobalLogger

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
