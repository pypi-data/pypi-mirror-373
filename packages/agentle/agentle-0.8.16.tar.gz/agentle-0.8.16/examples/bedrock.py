import logging
from agentle.generations.providers.ollama.ollama_generation_provider import (
    OllamaGenerationProvider,
)


logging.basicConfig(level=logging.CRITICAL)


provider = OllamaGenerationProvider(host="http://localhost:11434")

generation = provider.generate_by_prompt("Hello!")

print(generation)
