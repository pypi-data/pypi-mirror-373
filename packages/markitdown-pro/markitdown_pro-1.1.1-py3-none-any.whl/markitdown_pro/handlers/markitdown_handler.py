import asyncio
from typing import Optional

from markitdown import MarkItDown

from ..common.isolated_worker import run_in_process_with_timeout
from ..common.logger import logger
from ..common.utils import ensure_minimum_content
from .base_handler import BaseHandler


def _mkd_convert_child_proc(file_path: str) -> str:
    """
    Executed in the child process. Creates its own MarkItDown instance
    to avoid pickling issues and returns plain markdown text.
    """
    mkd = MarkItDown()
    result = mkd.convert(file_path)
    return result.markdown


class MarkItDownHandler(BaseHandler):
    """
    Async adapter around MarkItDown.

    - `handle(...)` is async and returns a Markdown string (or None on failure).
    - The blocking conversion runs in a supervised child process (wrapped in
      `asyncio.to_thread` so it won't block the event loop). On timeout, the
      child process is terminated.
    """

    extensions = frozenset({".csv", ".docx", ".xlsx", ".pptx", ".pdf"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout_seconds = kwargs.get("timeout_seconds", 60.0)

    async def handle(self, file_path: str, *args, **kwargs) -> Optional[str]:
        """
        Asynchronously convert a supported file to Markdown.

        Parameters
        ----------
        file_path : str
            Path to the input file (.csv, .docx, .xlsx, .pptx).

        Returns
        -------
        str
            Markdown content, or an empty string on error / insufficient content.
        """
        logger.info(f"MarkItDownHandler: Processing '{file_path}'")
        try:
            markdown = await asyncio.to_thread(
                run_in_process_with_timeout,
                _mkd_convert_child_proc,
                file_path,
                timeout_seconds=self.timeout_seconds,
            )
            if not ensure_minimum_content(markdown):
                raise RuntimeError(f"MarkItDownHandler: Insufficient content for '{file_path}'")

            return markdown

        except TimeoutError as e:
            logger.error(f"MarkItDownHandler: Timeout for '{file_path}': {e}")
            return None
        except Exception as e:
            logger.error(f"MarkItDownHandler: Error processing '{file_path}': {e}")
            return None
