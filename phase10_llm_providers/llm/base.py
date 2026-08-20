from abc import ABC, abstractmethod

from .models import LLMResponse


class LLMProvider(ABC):

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> LLMResponse:
        """
        Send the conversation to the model.

        The provider is responsible for converting
        our generic message/tool format into the
        provider-specific format.
        """
        raise NotImplementedError