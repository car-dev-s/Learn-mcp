from config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LLM_PROVIDER,
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)

from .anthropic_provider import AnthropicProvider
from .base import LLMProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider
from .openrouter_provider import OpenRouterProvider


def create_provider() -> LLMProvider:

    provider = LLM_PROVIDER.lower()
    print(f"provider {provider}")

    # ----------------------------------------------
    # OpenAI
    # ----------------------------------------------

    if provider == "openai":

        if not OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured"
            )

        return OpenAIProvider(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL,
        )

    # ----------------------------------------------
    # Gemini
    # ----------------------------------------------

    if provider == "gemini":

        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured"
            )

        return GeminiProvider(
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
        )

    # ----------------------------------------------
    # Claude
    # ----------------------------------------------

    if provider in {
        "claude",
        "anthropic",
    }:

        if not ANTHROPIC_API_KEY:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not configured"
            )

        return AnthropicProvider(
            api_key=ANTHROPIC_API_KEY,
            model=ANTHROPIC_MODEL,
        )

    # ----------------------------------------------
    # OpenRouter
    # ----------------------------------------------

    if provider == "openrouter":

        if not OPENROUTER_API_KEY:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not configured"
            )

        return OpenRouterProvider(
            api_key=OPENROUTER_API_KEY,
            model=OPENROUTER_MODEL,
        )

    # ----------------------------------------------
    # Local Llama
    # ----------------------------------------------

    if provider in {
        "llama",
        "ollama",
    }:

        return OllamaProvider(
            model=OLLAMA_MODEL,
            host=OLLAMA_HOST,
        )

    raise RuntimeError(
        f"Unknown LLM provider: {LLM_PROVIDER}"
    )