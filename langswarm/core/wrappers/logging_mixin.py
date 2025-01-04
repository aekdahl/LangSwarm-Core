from typing import Any, Optional
import logging

try:
    from langsmith import LangSmithTracer
except ImportError:
    LangSmithTracer = None


class LoggingMixin:
    """
    Mixin for managing logging, including LangSmith integration.
    """

    def _initialize_logger(self, name: str, agent: Any, langsmith_api_key: Optional[str]) -> None:
        """
        Initialize logging, prioritizing LangSmith if available.
        
        Parameters:
        - name (str): The name of the logger.
        - agent (Any): The agent to check for existing LangSmith integration.
        - langsmith_api_key (Optional[str]): API key for LangSmith, if provided.

        Returns:
        - None
        """
        self.logger = None
        self.langsmith_tracer = None

        # Check if the agent already has a LangSmith tracer
        if hasattr(agent, "tracer") and isinstance(agent.tracer, LangSmithTracer):
            self.langsmith_tracer = agent.tracer
            self.logger = agent.tracer  # Use LangSmith tracer as logger
            print(f"LangSmith tracer found for agent {name}. Using it for logging.")
            return

        # Initialize LangSmith if API key is provided
        if langsmith_api_key:
            self.langsmith_tracer = LangSmithTracer(api_key=langsmith_api_key)
            print(f"LangSmith tracer initialized for agent {name}.")
            if hasattr(agent, "tracer"):
                agent.tracer = self.langsmith_tracer
            self.logger = self.langsmith_tracer
            return

        # Fallback to standard logging
        import logging
        self.logger = logging.getLogger(name)
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        print(f"Fallback logger initialized for agent {name}.")

    def log_event(self, message: str, level: str = "info", name: str = "custom_log", value: Any = 0, metadata: dict = None):
        """
        Log events using the appropriate logging mechanism.

        Parameters:
        - message (str): The log message.
        - level (str): The log level (e.g., "info", "error").
        """
        if self.langsmith_tracer:
            if level == 'error':
                self.langsmith_tracer.log_error(
                    name=str(name),
                    input_data={},
                    output_data={"message": message},
                    metadata = {**{"level": level}, **metadata}
                )
            elif level == 'metric':
                self.langsmith_tracer.log_metric(
                    name=str(name),
                    value=value,
                    metadata = {**{"run_type": "cost"}, **metadata}
                )
            else:
                self.langsmith_tracer.log_success(
                    name="custom_log",
                    input_data={},
                    output_data={"message": message},
                    metadata = {**{"level": level}, **metadata}
                )
        else:
            getattr(self.logger, level.lower(), self.logger.info)(message)
