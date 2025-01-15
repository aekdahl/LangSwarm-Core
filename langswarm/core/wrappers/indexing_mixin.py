class IndexingMixin:
    """
    Mixin to handle multiple indices and backends for indexing and querying.
    Supports pluggable adapters for different backends.
    """

    def __init__(self, adapters=None):
        """
        Initialize the IndexingMixin with support for multiple indices and backends.

        :param adapters: Dict[str, DatabaseAdapter] - A dictionary of adapters for various backends.
        """
        self.adapters = adapters or {}
        self.indices = {}  # Tracks indices by name and their associated adapter
        self._indexing_is_available = bool(self.adapters)

        if not self._indexing_is_available:
            print("No adapters available. Indexing features are disabled.")

    @property
    def indexing_is_available(self):
        """Check if indexing is available."""
        return self._indexing_is_available

    def add_adapter(self, adapter_name, adapter):
        """
        Add a new backend adapter.

        :param adapter_name: str - Name of the adapter.
        :param adapter: DatabaseAdapter - The adapter instance.
        """
        if not isinstance(adapter, DatabaseAdapter):
            raise ValueError("Adapter must inherit from DatabaseAdapter.")
        self.adapters[adapter_name] = adapter
        print(f"Adapter '{adapter_name}' added successfully.")

    def create_index(self, index_name, adapter_name, config=None):
        """
        Create a new index using the specified adapter.

        :param index_name: str - Name of the index.
        :param adapter_name: str - Name of the adapter to use.
        :param config: dict - Configuration for the index creation (optional).
        """
        if adapter_name not in self.adapters:
            raise ValueError(f"Adapter '{adapter_name}' is not registered.")

        adapter = self.adapters[adapter_name]
        adapter.connect(config or {})
        self.indices[index_name] = adapter
        print(f"Index '{index_name}' created using adapter '{adapter_name}'.")

    def add_documents(self, docs, index_name):
        """
        Add documents to the specified index.

        :param docs: List[dict] - Documents to add.
        :param index_name: str - Name of the index to use.
        """
        if index_name not in self.indices:
            raise ValueError(f"Index '{index_name}' does not exist.")

        adapter = self.indices[index_name]
        adapter.add_documents(docs)

    def query_index(self, query_text, index_name, filters=None):
        """
        Query a specific index.

        :param query_text: str - The query string.
        :param index_name: str - Name of the index to query.
        :param filters: dict - Metadata filters (optional).
        :return: List[dict] - Query results.
        """
        if index_name not in self.indices:
            raise ValueError(f"Index '{index_name}' does not exist.")

        adapter = self.indices[index_name]
        return adapter.query({"query_text": query_text, "filters": filters or {}})

    def delete_index(self, index_name):
        """
        Delete an index.

        :param index_name: str - Name of the index to delete.
        """
        if index_name not in self.indices:
            raise ValueError(f"Index '{index_name}' does not exist.")

        adapter = self.indices.pop(index_name)
        adapter.delete({"identifier": index_name})
        print(f"Index '{index_name}' deleted.")

    def list_indices(self):
        """List all available indices."""
        return list(self.indices.keys())
