from agentle.generations.providers.amazon.models.cache_point_content import (
    CachePointContent,
)
from agentle.generations.providers.amazon.models.document_content import (
    DocumentContent,
)
from agentle.generations.providers.amazon.models.guardrail_content import (
    GuardrailContent,
)
from agentle.generations.providers.amazon.models.image_content import ImageContent
from agentle.generations.providers.amazon.models.reasoning_content import (
    ReasoningContent,
)
from agentle.generations.providers.amazon.models.text_content import TextContent
from agentle.generations.providers.amazon.models.tool_result_content import (
    ToolResultContent,
)
from agentle.generations.providers.amazon.models.tool_use_content import (
    ToolUseContent,
)
from agentle.generations.providers.amazon.models.video_content import VideoContent

ContentBlock = (
    TextContent
    | ImageContent
    | DocumentContent
    | VideoContent
    | ToolUseContent
    | ToolResultContent
    | GuardrailContent
    | CachePointContent
    | ReasoningContent
)
