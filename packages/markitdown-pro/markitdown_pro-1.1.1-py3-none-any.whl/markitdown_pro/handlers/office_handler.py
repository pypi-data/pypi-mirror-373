from typing import Optional

from ..common.logger import logger
from ..common.utils import ensure_minimum_content
from ..converters.azure_doc_intel_wrapper import DocIntelligenceWrapper
from ..converters.base import ConverterWrapper
from ..converters.markitdown_wrapper import MarkItDownWrapper
from ..converters.unstructured_wrapper import UnstructuredWrapper
from .base_handler import BaseHandler


class OfficeHandler(BaseHandler):
    """
    Convert Office documents to Markdown by trying a series of converters in order:

      1) MarkItDown (fast, local parsing for Office formats)
      2) Azure Document Intelligence (cloud extraction + OCR for embedded images)
      3) Unstructured (robust fallback parser)

    The first converter that returns non-trivial Markdown (as judged by
    `ensure_minimum_content`) wins. If all fail, `None` is returned.

    Notes
    -----
    - All converters are expected to expose an async `convert(file_path: str) -> Optional[str]`.
    - This handler is intentionally sequential to keep behavior predictable and to
      avoid unnecessary API calls when earlier options succeed.
    """

    # Supported Office-like extensions (lowercase with dot)
    extensions = frozenset({".doc", ".docx", ".odt", ".rtf", ".ppt", ".pptx"})

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Ordered, fastest → most comprehensive
        self.markitdown = MarkItDownWrapper()
        self.doc_intelligence = DocIntelligenceWrapper()
        self.unstructured = UnstructuredWrapper()

        # (converter, human_readable_name) in the exact order to try
        self._pipeline: list[tuple[ConverterWrapper, str]] = [
            (self.markitdown, "MarkItDown"),
            (self.doc_intelligence, "Azure Document Intelligence"),
            (self.unstructured, "Unstructured"),
        ]

    async def handle(self, file_path: str, *args, **kwargs) -> Optional[str]:
        """
        Convert an Office document to Markdown by trying the configured pipeline in order.

        Parameters
        ----------
        file_path : str
            Path to the document to convert.

        Returns
        -------
        Optional[str]
            Markdown text if any converter succeeds with sufficient content; otherwise `None`.
        """
        logger.info(f"OfficeHandler: Processing '{file_path}'")

        for converter, name in self._pipeline:
            try:
                logger.info(f"OfficeHandler: Trying {name} for '{file_path}'")
                md = await converter.convert(file_path)
                if md and ensure_minimum_content(md):
                    logger.info(f"OfficeHandler: {name} succeeded for '{file_path}'")
                    return md
                logger.debug(
                    f"OfficeHandler: {name} returned insufficient content for '{file_path}'"
                )
            except Exception as e:
                # Log and continue to the next converter
                converter_name = getattr(converter, "name", name)
                logger.error(f"OfficeHandler: {converter_name} failed for '{file_path}': {e}")

        logger.error(
            f"OfficeHandler: All converters failed or produced insufficient content for '{file_path}'"
        )
        return None
