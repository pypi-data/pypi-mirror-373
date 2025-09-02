from typing import TypedDict

from agentle.generations.providers.amazon.models.s3_location import S3Location


class S3Source(TypedDict):
    s3Location: S3Location
