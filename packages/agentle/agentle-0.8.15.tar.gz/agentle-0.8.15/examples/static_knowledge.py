import os
from dotenv import load_dotenv

from agentle.agents.agent import Agent
from agentle.generations.providers.google.google_generation_provider import (
    GoogleGenerationProvider,
)
from agentle.parsing.parsers.file_parser import FileParser

load_dotenv()

google_provider = GoogleGenerationProvider()

agent = Agent(
    generation_provider=google_provider,
    static_knowledge=[os.path.join(os.path.dirname(__file__), "curriculum.pdf")],
    document_parser=FileParser(
        strategy="high",
        visual_description_provider=google_provider,
        audio_description_provider=google_provider,
    ),
    instructions="Você é uma assistente de IA útil",
)

print(agent.run("Boa noite. quem é o arthur").pretty_formatted())
