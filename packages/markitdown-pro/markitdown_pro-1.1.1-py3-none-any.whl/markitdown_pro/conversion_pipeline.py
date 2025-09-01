"""
ConversionPipeline
==================

Async orchestrator that converts a single input document into Markdown by
dispatching to a specialized handler based on file extension.

Highlights
----------
- Clean separation of concerns: this class only **routes** to handlers and
  performs minimal I/O (temp file writes for URL/stream sources).
- Handlers are responsible for performing the actual conversion and must expose
  an async `handle(file_path: str) -> Optional[str]` API returning Markdown.
- Supports local files, HTTP/HTTPS URLs (downloaded to a temp file), and
  in-memory byte streams.

Notes
-----
- URL download uses `httpx` if available (fully async). If `httpx` is not
  installed, it falls back to `requests` executed in a background thread to
  keep the event loop responsive.
- After conversion, content is validated with `ensure_minimum_content(...)`.
  If an `output_md` path is provided, the Markdown is written there and also
  returned.

Environment
-----------
- Some handlers (e.g., Azure-based ones) may require environment variables.
  This pipeline does not manage those; it only instantiates and calls handlers.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

import httpx

from .common.logger import logger
from .common.utils import detect_extension, ensure_minimum_content
from .handlers.audio_handler import AudioHandler
from .handlers.base_handler import BaseHandler
from .handlers.email_handler import EmailHandler
from .handlers.epub_handler import EPUBHandler
from .handlers.image_handler import ImageHandler
from .handlers.ipynb_handler import IpynbHandler
from .handlers.markitdown_handler import MarkItDownHandler
from .handlers.markup_handler import MarkupHandler
from .handlers.office_handler import OfficeHandler
from .handlers.pdf_handler import PDFHandler
from .handlers.pst_handler import PSTHandler

# from .handlers.tabular_handler import TabularHandler
from .handlers.text_handler import TextHandler


def _write_md(path: str | Path, content: str) -> str:
    """
    Write Markdown `content` to `path`, creating parent directories if needed.
    Returns the same `content` for convenient chaining.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return content


class ConversionPipeline:
    """
    Convert arbitrary documents to Markdown by dispatching to a format-specific handler.

    Handlers are selected via a mapping of file extensions (lowercase, with
    leading dot) to handler instances. Each handler encapsulates the concrete
    extraction/ocr logic for its domain (PDF, Office, images, etc.).
    """

    def __init__(self) -> None:
        # Instantiate handlers (each must implement `async handle(file_path: str) -> Optional[str]`)
        self.pdf_handler = PDFHandler()
        self.audio_handler = AudioHandler()
        self.image_handler = ImageHandler()
        self.text_handler = TextHandler()
        # self.tabular_handler = TabularHandler()
        self.markup_handler = MarkupHandler()
        self.office_handler = OfficeHandler()
        self.epub_handler = EPUBHandler()
        self.email_handler = EmailHandler()
        self.pst_handler = PSTHandler()
        self.ipynb_handler = IpynbHandler()
        self.markitdown_handler = MarkItDownHandler()

        # Map extensions to handlers (normalized lowercase with dot)
        self.handlers_mapping: dict[str, BaseHandler] = {
            # PDFs
            ".pdf": self.pdf_handler,
            # Audio
            ".mp3": self.audio_handler,
            ".wav": self.audio_handler,
            # ".ogg": self.audio_handler,
            # ".flac": self.audio_handler,
            # ".m4a": self.audio_handler,
            # ".aac": self.audio_handler,
            # ".wma": self.audio_handler,
            # ".webm": self.audio_handler,
            # ".opus": self.audio_handler,
            # Images
            ".bmp": self.image_handler,
            ".gif": self.image_handler,
            ".heic": self.image_handler,
            ".jpeg": self.image_handler,
            ".jpg": self.image_handler,
            ".png": self.image_handler,
            ".prn": self.image_handler,
            ".svg": self.image_handler,
            ".tiff": self.image_handler,
            ".webp": self.image_handler,
            ".heif": self.image_handler,
            # Plain/code text
            ".txt": self.text_handler,
            ".md": self.text_handler,
            ".py": self.text_handler,
            ".go": self.text_handler,
            # Tabular (via MarkItDown)
            ".csv": self.markitdown_handler,
            ".tsv": self.markitdown_handler,
            # Office/Spreadsheet/Slides
            ".xls": self.office_handler,
            ".xlsx": self.office_handler,
            ".doc": self.office_handler,
            ".docx": self.office_handler,
            ".odt": self.office_handler,
            ".rtf": self.office_handler,
            ".ppt": self.office_handler,
            ".pptx": self.office_handler,
            # Markup/serialization
            ".html": self.markup_handler,
            ".htm": self.markup_handler,
            ".xml": self.markup_handler,
            ".json": self.markup_handler,
            ".ndjson": self.markup_handler,
            ".yaml": self.markup_handler,
            ".yml": self.markup_handler,
            # Others
            ".epub": self.epub_handler,
            ".eml": self.email_handler,
            ".p7s": self.email_handler,
            ".msg": self.email_handler,
            ".pst": self.pst_handler,
            ".ipynb": self.ipynb_handler,
        }

    # ---------------------------------------------------------------------
    # Public APIs
    # ---------------------------------------------------------------------

    async def convert_document_to_md(
        self, file_path: str | Path, output_md: Optional[str | Path] = None
    ) -> Optional[str]:
        """
        Convert a **local file** to Markdown.

        Parameters
        ----------
        file_path : str | Path
            Path to the local file.
        output_md : str | Path | None
            If provided, write the resulting Markdown to this path and also return it.

        Returns
        -------
        Optional[str]
            Markdown content on success; `None` if conversion produced insufficient content.
        """
        file_path = Path(file_path)
        if not file_path.is_file():
            raise ValueError(f"The provided path '{file_path}' is not a valid file.")

        logger.debug(f"convert_document_to_md: Converting '{file_path}' -> '{output_md}'")

        # Determine extension (can be content-aware if your detect_extension supports it)
        extension = detect_extension(str(file_path)).lower()
        handler = self.handlers_mapping.get(extension)

        if not handler:
            logger.error(f"No specific handler found for '{extension}'. Aborting.")
            raise RuntimeError(f"No handler for extension '{extension}'.")

        try:
            md_content = await handler.handle(str(file_path))
            if not md_content or not ensure_minimum_content(md_content):
                return None

            logger.debug(
                f"convert_document_to_md: {file_path} returned {len(md_content)} characters"
            )
            return _write_md(output_md, md_content) if output_md else md_content

        except Exception as e:
            logger.error(f"Error in handler for extension {extension}: {e}")
            raise

    async def convert_document_from_url(
        self, url: str, output_md: Optional[str | Path] = None
    ) -> Optional[str]:
        """
        Download a document from `url` to a temporary file, then convert to Markdown.

        Notes
        -----
        - Uses `httpx` if installed (async). Otherwise falls back to `requests`
          executed in a thread (non-blocking for the event loop).
        - The temp file suffix is `.download`. If your `detect_extension` relies
          only on file extension, consider enhancing it to sniff MIME/content.
        """
        logger.info(f"convert_document_from_url: Downloading '{url}'")

        # Write to a temporary file (keeping a generic suffix)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".download") as tmp:
            local_path = Path(tmp.name)

            async with httpx.AsyncClient(follow_redirects=True) as client:
                async with client.stream("GET", url, timeout=None) as resp:
                    resp.raise_for_status()
                    async for chunk in resp.aiter_bytes():
                        tmp.write(chunk)
                    tmp.flush()
        try:
            return await self.convert_document_to_md(local_path, output_md=output_md)  # type: ignore[name-defined]
        finally:
            # Always remove the temporary file, even if conversion fails
            local_path.unlink(missing_ok=True)

    async def convert_document_from_stream(
        self, stream, extension: str, output_md: Optional[str | Path] = None
    ) -> Optional[str]:
        """
        Convert an in-memory byte stream to Markdown.

        Parameters
        ----------
        stream : io.BytesIO or any file-like object supporting `.read()`
            The binary stream to persist temporarily and convert.
        extension : str
            File extension (with or without leading dot). Used for temp file suffix.
        output_md : str | Path | None
            If provided, writes the Markdown to this path and also returns it.

        Returns
        -------
        Optional[str]
            Markdown content on success; `None` if conversion produced insufficient content.
        """
        from io import BytesIO

        ext = extension if extension.startswith(".") else f".{extension}"
        logger.debug(
            "convert_document_from_stream: Converting from stream with extension '%s'", ext
        )

        if not hasattr(stream, "read"):
            raise ValueError("Stream must provide a .read() method")
        if not isinstance(stream, BytesIO):
            # If you want to be strict about BytesIO only, keep this check.
            # Otherwise, remove it to allow any readable binary stream.
            pass

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(stream.read())
            tmp.flush()
            local_path = Path(tmp.name)

        try:
            return await self.convert_document_to_md(local_path, output_md=output_md)
        finally:
            local_path.unlink(missing_ok=True)
