class IndexingMixin:
    def __init__(self, index_path="index.json"):
        self._indexing_is_available = True
        
        if GPTSimpleVectorIndex is None:
            self._indexing_is_available = False
            self.indices = {}
            print("LlamaIndex not installed. Indexing features are disabled.")
            return

        self.index_path = index_path
        self.indices = {"default": self._load_or_create_index(index_path)}

    def _load_or_create_index(self, path):
        try:
            return GPTSimpleVectorIndex.load_from_disk(path)
        except FileNotFoundError:
            return GPTSimpleVectorIndex([])

    @property
    def indexing_is_available(self):
        """Check if indexing is available."""
        return self._indexing_is_available

    def add_documents(self, docs, index_name="default"):
        if not self.indexing_is_available:
            print("Indexing features are unavailable.")
            return

        if index_name not in self.indices:
            self.indices[index_name] = GPTSimpleVectorIndex([])

        documents = [Document(text=doc["text"], metadata=doc.get("metadata", {})) for doc in docs]
        self.indices[index_name].insert(documents)
        self.indices[index_name].save_to_disk(self.index_path)

    def query_index(self, query_text, index_name="default", metadata_filter=None):
        if not self.indexing_is_available:
            print("Indexing features are unavailable.")
            return []

        if index_name not in self.indices:
            print(f"Index '{index_name}' not found.")
            return []

        results = self.indices[index_name].query(query_text)

        if metadata_filter:
            results = [
                res for res in results
                if all(res.extra_info.get(key) == value for key, value in metadata_filter.items())
            ]
        return self._normalize_results(results)

    def _normalize_results(self, results):
        return [
            {
                "text": res.text,
                "metadata": res.extra_info,
                "score": getattr(res, "score", None)
            }
            for res in results
        ]

    def list_indices(self):
        """List available indices."""
        return list(self.indices.keys())
