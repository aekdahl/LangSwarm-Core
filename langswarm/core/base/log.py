import logging

try:
    from langsmith import LangSmithTracer
except ImportError:
    LangSmithTracer = None

class GlobalLogger:
    """
    Singleton class for managing global logging with optional LangSmith integration.
    """

    _logger = None
    _langsmith_tracer = None

    @classmethod
    def initialize(cls, name="GlobalLogger", langsmith_api_key=None):
        """
        Initialize the global logger.

        Parameters:
        - name (str): Name of the logger.
        - langsmith_api_key (str, optional): API key for LangSmith. If provided, sets up LangSmith logging.
        """
        if cls._logger is None:
            cls._logger = logging.getLogger(name)
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            cls._logger.addHandler(handler)
            cls._logger.setLevel(logging.INFO)
            print("Global logger initialized.")

        if langsmith_api_key and cls._langsmith_tracer is None:
            cls._langsmith_tracer = LangSmithTracer(api_key=langsmith_api_key)
            print("LangSmith tracer added to global logger.")

    @classmethod
    def log(cls, message, level="info", metadata=None):
        """
        Log a message using the global logger or LangSmith if available.

        Parameters:
        - message (str): The message to log.
        - level (str): The log level (e.g., 'info', 'error').
        - metadata (dict, optional): Metadata for LangSmith logging.
        """
        if cls._langsmith_tracer:
            cls._langsmith_tracer.log_success(
                name="global_log",
                input_data={"message": message},
                output_data={},
                metadata=metadata or {},
            )
        else:
            getattr(cls._logger, level.lower(), cls._logger.info)(message)
