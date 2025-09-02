from agentle.generations.providers.amazon.models.message_start import MessageStart
from agentle.generations.providers.amazon.models.content_block_start import (
    ContentBlockStart,
)
from agentle.generations.providers.amazon.models.content_block_delta import (
    ContentBlockDelta,
)
from agentle.generations.providers.amazon.models.content_block_stop import (
    ContentBlockStop,
)
from agentle.generations.providers.amazon.models.message_stop import MessageStop
from agentle.generations.providers.amazon.models.metadata import Metadata

StreamEvent = (
    MessageStart
    | ContentBlockStart
    | ContentBlockDelta
    | ContentBlockStop
    | MessageStop
    | Metadata
)
