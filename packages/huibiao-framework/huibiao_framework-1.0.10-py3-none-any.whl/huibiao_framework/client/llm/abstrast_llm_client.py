from abc import ABC, abstractmethod


class AbstractLlmModelClient(ABC):
    @abstractmethod
    async def simple_query(self, content, session_id: str = "") -> str:
        """
        简单的一次性问答
        LLMException
        """
        pass
