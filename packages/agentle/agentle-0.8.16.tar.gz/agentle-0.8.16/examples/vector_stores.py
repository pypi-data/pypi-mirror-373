from agentle.agents.agent import Agent
from agentle.embeddings.providers.google.google_embedding_provider import (
    GoogleEmbeddingProvider,
)
from agentle.vector_stores.qdrant_vector_store import QdrantVectorStore

curriculum_store = QdrantVectorStore(
    default_collection_name="test_collection",  # important to store in state because the Agent will not know which collection to search.
    embedding_provider=GoogleEmbeddingProvider(
        vertexai=True, project="unicortex", location="global"
    ),
    detailed_agent_description="Stores curriculum information.",
)

curriculum_agent = Agent(vector_stores=[curriculum_store])

agent_response = curriculum_agent.run(
    "I need to know a person that can Lead my AI team. Anyone that might help us?"
    + "Ther person MUST know how to program in COBOL. That is a DISCLASSIFYING requirement."
)

print(agent_response.pretty_formatted())
