from typing import Dict, List
from langswarm.memory import ChromaDBAdapter
from langswarm.base.database_adapter import DatabaseAdapter


class IndexingMixin:
    """
    Mixin to handle multiple indices and backends for indexing and querying.
    Supports pluggable adapters for different backends, with a fallback to local ChromaDB.
    """
    def __init__(self, default_index_name="default", chromadb_directory="chroma_data"):
        """
        Initialize the IndexingMixin with optional default local ChromaDB.

        :param default_index_name: str - Name of the default index.
        :param chromadb_directory: str - Directory for local ChromaDB storage.
        """
        self.adapters = {}
        self.indices = {}
        self._default_index_name = default_index_name
        self._indexing_is_available = True

        # Attempt to initialize fallback ChromaDB adapter
        try:
            self._local_chromadb_adapter = ChromaDBAdapter(
                collection_name=self._default_index_name,
                persist_directory=chromadb_directory,
            )
            self.adapters["local_chroma"] = self._local_chromadb_adapter
            self.indices[default_index_name] = self._local_chromadb_adapter
        except ImportError:
            self._indexing_is_available = False
            self._local_chromadb_adapter = None
            print(
                "ChromaDB is not installed. Indexing features are disabled. "
                "Please install ChromaDB or add a compatible adapter to enable indexing."
            )

    @property
    def indexing_is_available(self):
        """Check if indexing is available."""
        return self._indexing_is_available

    def add_adapter(self, adapter_name: str, adapter: DatabaseAdapter):
        """
        Add a new backend adapter.

        :param adapter_name: str - Name of the adapter.
        :param adapter: DatabaseAdapter - The adapter instance.
        """
        if not isinstance(adapter, DatabaseAdapter):
            raise ValueError("Adapter must inherit from DatabaseAdapter.")
        self.adapters[adapter_name] = adapter
        self._indexing_is_available = True
        print(f"Adapter '{adapter_name}' added successfully.")

    def create_index(self, index_name: str, adapter_name: str):
        """
        Create a new index using the specified adapter.

        :param index_name: str - Name of the index.
        :param adapter_name: str - Name of the adapter to use.
        """
        if not self.indexing_is_available:
            print("Indexing features are unavailable.")
            return

        if adapter_name not in self.adapters:
            raise ValueError(f"Adapter '{adapter_name}' is not registered.")
        self.indices[index_name] = self.adapters[adapter_name]
        print(f"Index '{index_name}' created using adapter '{adapter_name}'.")

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
        adapter.delete({"identifier": index_name})
        print(f"Index '{index_name}' deleted.")

    def list_indices(self):
        """List all available indices."""
        if not self.indexing_is_available:
            print("Indexing features are unavailable. Skipping list_indices.")
            return []
        return list(self.indices.keys())
