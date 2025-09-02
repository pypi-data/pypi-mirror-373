from typing import TypedDict

from agentle.generations.providers.amazon.models.image_block import ImageBlock


# Image content block
class ImageContent(TypedDict):
    image: ImageBlock
