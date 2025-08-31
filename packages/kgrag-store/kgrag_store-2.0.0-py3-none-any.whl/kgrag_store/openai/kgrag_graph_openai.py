from kgrag_store.kgrag_graph import KGragGraph
from memory_agent.openai import AgentOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable


class KGragGraphOpenAI(KGragGraph):
    """
    KGragGraphOpenAI is a subclass of KGragGraph that uses the OpenAI API
    for natural language processing tasks.
    """

    openai_agent: AgentOpenAI

    def __init__(self, **kwargs):
        """
        Initialize the KGragGraphOpenAI with the provided parameters.
        """
        super().__init__(**kwargs)
        self.openai_agent = AgentOpenAI(**kwargs)

    def chain(self, prompt: ChatPromptTemplate) -> RunnableSerializable:
        """
        Get the chain for the OpenAI agent.
        Args:
            prompt (ChatPromptTemplate): The prompt to use for the chain.
        """
        return self.openai_agent.chain(prompt)
