from memory_agent.ollama import MemoryOllama
from kgrag_store.kgrag_vector import KGragVectorStore


class KGragVectorStoreOllama(KGragVectorStore):
    """
    KGragVectorStoreOllama is a vector store implementation that uses
    the Ollama model for embeddings.
    """

    ollama_mem: MemoryOllama

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ollama_mem = MemoryOllama(**kwargs)

    def embeddings(
        self,
        raw_data
    ) -> list:
        """
        Get embeddings for the provided raw data using the Ollama model.
        """
        embeddings = [
                self.ollama_mem.model_embedding.embed_query(paragraph)
                for paragraph in raw_data.split("\n")
            ]
        return embeddings
