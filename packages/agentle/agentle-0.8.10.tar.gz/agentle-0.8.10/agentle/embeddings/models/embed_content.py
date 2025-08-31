from rsb.models.base_model import BaseModel

from agentle.embeddings.models.embedding import Embedding


class EmbedContent(BaseModel):
    embeddings: Embedding
