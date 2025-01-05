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

    def query_index(self, query_text):
        if not self.indexing_is_available:
            print("Indexing features are unavailable.")
            return []
        
        return self.index.query(query_text)
