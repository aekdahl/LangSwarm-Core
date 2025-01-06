try:
    from llama_index import GPTSimpleVectorIndex, Document
except ImportError:
    GPTSimpleVectorIndex = None

class IndexingMixin:
    def __init__(self, index_path="index.json"):
        self._indexing_is_available = True
        
        if GPTSimpleVectorIndex is None:
            self._indexing_is_available = False
            self.index = None
            print("LlamaIndex not installed. Indexing features are disabled.")
            return
        
        self.index_path = index_path
        try:
            self.index = GPTSimpleVectorIndex.load_from_disk(index_path)
        except FileNotFoundError:
            self.index = GPTSimpleVectorIndex([])
        

    @property
    def indexing_is_available(self):
        """Check if indexin is available."""
        return self._indexing_is_available
    
    def add_documents(self, docs):
        if not self.indexing_is_available:
            print("Indexing features are unavailable.")
            return
        
        documents = [Document(text=doc["text"], metadata=doc.get("metadata", {})) for doc in docs]
        self.index.insert(documents)
        self.index.save_to_disk(self.index_path)

    def query_index(self, query_text, metadata_filter=None):
        """
        Query the index with optional metadata filtering.

        :param query_text: The text query.
        :param metadata_filter: Dictionary of metadata filters (optional).
        :return: Filtered results.
        """
        if not self.indexing_is_available:
            print("Indexing features are unavailable.")
            return []

        # Perform the query
        results = self.index.query(query_text)

        # Apply metadata filtering if specified
        if metadata_filter:
            results = [
                res for res in results
                if all(res.extra_info.get(key) == value for key, value in metadata_filter.items())
            ]
        return self._normalize_results(results)

    def batch_query(self, queries, metadata_filter=None):
        """
        Perform batch queries with optional metadata filtering.

        :param queries: List of text queries.
        :param metadata_filter: Dictionary of metadata filters (optional).
        :return: Dictionary mapping queries to filtered results.
        """
        if not self.indexing_is_available:
            print("Indexing features are unavailable.")
            return {}

        results = {}
        for query in queries:
            query_results = self.query_index(query, metadata_filter)
            results[query] = query_results
        return results

    def _normalize_results(self, results):
        """
        Normalize query results to a consistent format.

        :param results: Raw results from the index.
        :return: List of normalized results.
        """
        return [
            {
                "text": res.text,
                "metadata": res.extra_info,
                "score": getattr(res, "score", None)
            }
            for res in results
        ]
