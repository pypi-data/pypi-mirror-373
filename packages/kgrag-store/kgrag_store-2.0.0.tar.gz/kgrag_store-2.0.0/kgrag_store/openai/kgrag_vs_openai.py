from memory_agent.openai import MemoryOpenAI
from kgrag_store.kgrag_vector import KGragVectorStore


class KGragVectorStoreOpenAI(KGragVectorStore):
    """
    KGragVectorStoreOpenAI is a vector store implementation that uses
    the OpenAI model for embeddings.
    """
    openai_mem: MemoryOpenAI

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.openai_mem = MemoryOpenAI(**kwargs)

    def embeddings(
        self,
        raw_data
    ) -> list:
        """
        Get embeddings for the provided raw data using the OpenAI model.
        """
        embeddings = [
                self.openai_mem.model_embedding.embed_query(paragraph)
                for paragraph in raw_data.split("\n")
            ]
        return embeddings
