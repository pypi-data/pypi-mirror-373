"""
Module defining the DeveloperMessage class representing messages from developers.
"""

from typing import Literal, Sequence

from rsb.decorators.value_objects import valueobject
from rsb.models.base_model import BaseModel
from rsb.models.field import Field

from agentle.generations.models.message_parts.file import FilePart
from agentle.generations.models.message_parts.text import TextPart
from agentle.generations.tools.tool import Tool


@valueobject
class DeveloperMessage(BaseModel):
    """
    Represents a message from a developer in the system.

    This class can contain a sequence of different message parts including
    text, files, and tools.
    """

    role: Literal["developer"] = Field(
        default="developer",
        description="Discriminator field to identify this as a developer message. Always set to 'developer'.",
    )

    parts: Sequence[TextPart | FilePart | Tool] = Field(
        description="The sequence of message parts that make up this developer message.",
    )

    @property
    def text(self) -> str:
        """
        Returns the concatenated text representation of all parts in this message.

        Returns:
            str: The concatenated text of all message parts.
        """
        return "".join(
            part.text if isinstance(part.text, str) else part.text.text
            for part in self.parts
        )
