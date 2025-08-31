from typing import Literal, NotRequired, TypedDict


class _Retries(TypedDict):
    max_attempts: NotRequired[int]
    mode: Literal["standard", "adaptive"] | str


class BotoConfig(TypedDict):
    connect_timeout: NotRequired[int]
    read_timeout: NotRequired[int]
    retries: _Retries
    max_pool_connections: NotRequired[int]
