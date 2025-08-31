from dotenv import load_dotenv
from agentle.generations.providers.cerebras.cerebras_generation_provider import (
    CerebrasGenerationProvider,
)

load_dotenv()

provider = CerebrasGenerationProvider()

generation = provider.generate_by_prompt(
    prompt="Hello, world!",
)

print(generation.text)
