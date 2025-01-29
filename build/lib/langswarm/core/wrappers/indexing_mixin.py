from typing import Dict, List

try:
    from langswarm.memory import ChromaDBAdapter
    from langswarm.base.database_adapter import DatabaseAdapter
except ImportError:
    ChromaDBAdapter = None
    DatabaseAdapter = None


class IndexingMixin:
    """
    Mixin to handle multiple indices and backends for indexing and querying.
    Supports pluggable adapters for different backends, with a fallback to local ChromaDB.
    """
    def __init__(self):
        """
        Initialize the IndexingMixin with optional default local ChromaDB in-memory.

        :param default_index_name: str - Name of the default index.
        :param chromadb_directory: str - Directory for local ChromaDB storage.
        """
        self.indices = {}
        self._default_indices = "ls__default"
        self._indexing_is_available = True

        # Attempt to initialize fallback ChromaDB adapter
        if all(var is not None for var in (ChromaDBAdapter, DatabaseAdapter)):
            self.indices[self._default_indices] = ChromaDBAdapter(
                collection_name=self._default_indices
            )
        else:
            self._indexing_is_available = False
            print(
                "ChromaDB is not installed. Indexing features are disabled. "
                "Please install ChromaDB or add a compatible adapter to enable indexing."
            )

    @property
    def indexing_is_available(self):
        """Check if indexing is available."""
        return self._indexing_is_available

    def add_index(self, index_name: str, adapter: DatabaseAdapter):
        """
        Add a new backend adapter.

        :param index_name: str - Name of the index.
        :param adapter: DatabaseAdapter - The adapter instance.
        """
        if not isinstance(adapter, DatabaseAdapter):
            raise ValueError("Adapter must inherit from DatabaseAdapter.")
        
        if index_name in self.indices:
            raise ValueError("Index name already exists. Set another index name.")
            
        self.indices[index_name] = adapter
        self._indexing_is_available = True
        print(f"Index '{index_name}' added successfully.")

    def add_documents(self, docs: List[Dict], index_name=None):
        """
        Add documents to the specified index, or default index if none specified.

        :param docs: List[Dict] - Documents to add.
        :param index_name: str - Name of the index to use.
        """
        if not self.indexing_is_available:
            print("Indexing features are unavailable. Skipping add_documents.")
            return

        index_name = index_name or self._default_index_name
        if index_name not in self.indices:
            print(f"Index '{index_name}' does not exist. Skipping add_documents.")
            return

        adapter = self.indices[index_name]
        adapter.add_documents(docs)

    def query_index(self, query_text: str, index_name=None, filters=None):
        """
        Query a specific index, or the default index if none specified.

        :param query_text: str - The query string.
        :param index_name: str - Name of the index to query.
        :param filters: Dict - Metadata filters (optional).
        :return: List[Dict] - Query results.
        """
        if not self.indexing_is_available:
            print("Indexing features are unavailable. Skipping query_index.")
            return []

        index_name = index_name or self._default_index_name
        if index_name not in self.indices:
            print(f"Index '{index_name}' does not exist. Skipping query_index.")
            return []

        adapter = self.indices[index_name]
        return adapter.query({"query_text": query_text, "filters": filters or {}})

    def delete_index(self, index_name: str):
        """
        Delete an index.

        :param index_name: str - Name of the index to delete.
        """
        if not self.indexing_is_available:
            print("Indexing features are unavailable. Skipping delete_index.")
            return

        if index_name not in self.indices:
            print(f"Index '{index_name}' does not exist. Skipping delete_index.")
            return

        adapter = self.indices.pop(index_name)
        # adapter.delete({"identifier": index_name}) --> ToDo: Adapter do not support deleting full indices yet..
        print(f"Index '{index_name}' deleted.")

    def list_indices(self):
        """List all available indices."""
        if not self.indexing_is_available:
            print("Indexing features are unavailable. Skipping list_indices.")
            return []
        return list(self.indices.keys())
