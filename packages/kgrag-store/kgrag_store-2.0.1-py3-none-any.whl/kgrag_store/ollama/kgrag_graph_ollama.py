from kgrag_store.kgrag_graph import KGragGraph
from memory_agent.ollama import AgentOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable


class KGragGraphOllama(KGragGraph):
    """
    KGragGraphOllama is a subclass of KGragGraph that uses the Ollama API
    for natural language processing tasks.
    """
    ollama_agent: AgentOllama

    def __init__(self, **kwargs):
        """
        Initialize the KGragGraphOllama with the provided parameters.
        """
        super().__init__(**kwargs)
        self.ollama_agent = AgentOllama(**kwargs)

    def chain(self, prompt: ChatPromptTemplate) -> RunnableSerializable:
        """
        Get the chain for the Ollama agent.
        Args:
            prompt (ChatPromptTemplate): The prompt to use for the chain.
        """
        return self.ollama_agent.chain(prompt)
