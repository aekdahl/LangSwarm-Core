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
    def _ensure_initialized(cls):
        """
        Ensure that the logger is initialized. If not, initialize with default settings.
        """
        if cls._logger is None:
            print("Global logger was not initialized. Initializing with default settings.")
            cls.initialize()

    @classmethod
    def log(cls, message, level="info", name="global_log", metadata=None):
        """
        Log a message using the global logger or LangSmith if available.

        Parameters:
        - message (str): The message to log.
        - level (str): The log level (e.g., 'info', 'error').
        - name (str): The name of the log entry.
        - metadata (dict, optional): Metadata for LangSmith logging.
        """
        cls._ensure_initialized()

        if cls._langsmith_tracer:
            cls._log_with_langsmith(message, level, name, metadata)
        else:
            getattr(cls._logger, level.lower(), cls._logger.info)(message)

    @classmethod
    def log_event(cls, *args, **kwargs):
        """
        Alias for the `log` method.
        """
        cls.log(*args, **kwargs)

    @classmethod
    def _log_with_langsmith(cls, message, level, name, metadata):
        """
        Log messages using LangSmith tracer.
        """
        if level == 'error':
            cls._langsmith_tracer.log_error(
                name=name,
                input_data={"message": message},
                output_data={},
                metadata=metadata or {"level": level},
            )
        elif level == 'metric':
            cls._langsmith_tracer.log_metric(
                name=name,
                value=metadata.get("value", 0),
                metadata=metadata or {},
            )
        else:
            cls._langsmith_tracer.log_success(
                name=name,
                input_data={"message": message},
                output_data={},
                metadata=metadata or {"level": level},
            )
