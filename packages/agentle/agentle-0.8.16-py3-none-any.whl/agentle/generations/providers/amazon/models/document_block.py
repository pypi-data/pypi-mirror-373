from typing import Literal, TypedDict

from agentle.generations.providers.amazon.models.bytes_source import BytesSource
from agentle.generations.providers.amazon.models.s3_source import S3Source


class DocumentBlock(TypedDict):
    format: Literal["pdf", "csv", "doc", "docx", "xls", "xlsx", "html", "txt", "md"]
    name: str
    source: BytesSource | S3Source
