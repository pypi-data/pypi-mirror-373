from pathlib import Path
from typing import Optional


class BaseHandler:
    extensions: frozenset = frozenset()
    pipeline: Optional[list] = None

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    async def is_valid(cls, file_path: str) -> bool:
        return Path(file_path).is_file() and Path(file_path).suffix in cls.extensions

    async def handle(self, file_path, *args, **kwargs) -> Optional[str]:
        raise NotImplementedError("You must implement the handle method")
