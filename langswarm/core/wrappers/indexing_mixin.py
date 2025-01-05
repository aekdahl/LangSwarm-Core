try:
    from llama_index import GPTSimpleVectorIndex, Document
    LLAMA_INDEX_AVAILABLE = True
except ImportError:
    LLAMA_INDEX_AVAILABLE = False

class IndexingMixin:
    def __init__(self, index_path="index.json"):
        if not LLAMA_INDEX_AVAILABLE:
            self.index = None
            print("LlamaIndex not installed. Indexing features are disabled.")
            return
        
        self.index_path = index_path
        try:
            self.index = GPTSimpleVectorIndex.load_from_disk(index_path)
        except FileNotFoundError:
            self.index = GPTSimpleVectorIndex([])

    def add_documents(self, docs):
        if not LLAMA_INDEX_AVAILABLE:
            print("Indexing features are unavailable.")
            return
        
        documents = [Document(text=doc["text"], metadata=doc.get("metadata", {})) for doc in docs]
        self.index.insert(documents)
        self.index.save_to_disk(self.index_path)

    def query_index(self, query_text):
        if not LLAMA_INDEX_AVAILABLE:
            print("Indexing features are unavailable.")
            return []
        
        return self.index.query(query_text)
