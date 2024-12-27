import logging

try:
    from langsmith.tracers.helpers import traceable, log_error
    from langsmith.wrappers import wrap_openai
    from langsmith import LangSmithTracer
except ImportError:
    traceable = None
    log_error = None
    wrap_openai = None
    LangSmithTracer = None


class LoggingMixin:
    """
    Mixin for managing LangSmith logging and fallback logging.
    """

    def _initialize_logger(self, name: str, langsmith_api_key: Optional[str]) -> logging.Logger:
        """
        Initialize a logger for the agent, with LangSmith integration if available.

        Parameters:
        - name (str): The name of the logger.
        - langsmith_api_key (str): API key for LangSmith, if enabled.

        Returns:
        - Logger instance.
        """
        self.langsmith_enabled = langsmith_api_key is not None and traceable is not None
        self.langsmith_tracer = None

        if self.langsmith_enabled and LangSmithTracer:
            self.langsmith_tracer = LangSmithTracer(api_key=langsmith_api_key)

        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _log_error(self, error_message: str):
        """
        Log errors to LangSmith or fallback logger.

        Parameters:
        - error_message (str): The error message to log.
        """
        if self.langsmith_enabled and self.langsmith_tracer and log_error:
            self.langsmith_tracer.log_error(error_message, name=self.name, run_type="error")
        else:
            self.logger.error(f"Error in {self.name}: {error_message}")
