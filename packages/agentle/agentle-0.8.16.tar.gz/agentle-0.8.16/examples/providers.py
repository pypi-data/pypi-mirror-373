"""
Providers Example

This example demonstrates how to use different model providers with the Agentle framework.
"""

from agentle.generations.models.message_parts.text import TextPart
from agentle.generations.models.messages.user_message import UserMessage
from agentle.generations.providers.base.generation_provider import GenerationProvider
from agentle.generations.providers.google.google_generation_provider import (
    GoogleGenerationProvider,
)

# Example 1: Create an agent with Google's Gemini model
provider: GenerationProvider = GoogleGenerationProvider()

# Run the Google agent
google_response = provider.generate(
    messages=[
        UserMessage(
            parts=[
                TextPart(
                    text="Explain the concept of neural networks briefly.",
                )
            ]
        )
    ]
)
print("GOOGLE GEMINI RESPONSE:")
print(google_response.text)
print("\n" + "-" * 50 + "\n")
