from typing import Optional, List


class Reference:

    def __init__(
        self,
        url: str,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        if url is None:
            raise AttributeError("url cannot be None")
        self.source = source
        self.tags = tags
        self.url = url
