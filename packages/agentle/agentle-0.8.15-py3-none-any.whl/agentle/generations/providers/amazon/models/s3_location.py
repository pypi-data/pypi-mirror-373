from typing import NotRequired, TypedDict


class S3Location(TypedDict):
    uri: str
    bucketOwner: NotRequired[str]
