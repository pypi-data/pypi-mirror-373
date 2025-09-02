from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from outerport.client import OuterportClient
    from outerport.client import AsyncOuterportClient


class BaseResource:
    def __init__(self, client: "OuterportClient") -> None:
        self.client = client


class AsyncBaseResource:
    def __init__(self, client: "AsyncOuterportClient") -> None:
        self.client = client
