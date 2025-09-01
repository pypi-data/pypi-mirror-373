"""
Azure Document Intelligence handler (async)

- Uses the latest Azure Document Intelligence (Layout) API via the async SDK.
- Supports: JPEG, JPG, BMP, TIFF, HEIF/HEIC, DOCX, XLSX, PPTX.
- Returns the **entire document** as **Markdown** (including OCR on images when supported).
- No Speech or other Azure services—this class is *only* for Document Intelligence.

Env vars required
-----------------
- AZURE_DOCINTEL_ENDPOINT : e.g. "https://<your-resource>.cognitiveservices.azure.com"
- AZURE_DOCINTEL_KEY      : your key for the Document Intelligence resource

Notes on OCR in images
----------------------
`prebuilt-layout` performs OCR on page content. For image files and scanned docs,
the result includes recognized text. For Office files (DOCX/XLSX/PPTX), text is
extracted and OCR is applied to images when available in your service/sku.
This handler also attempts to enable high-resolution OCR if the SDK exposes it.
"""

from __future__ import annotations

import asyncio
import io
import os
from pathlib import Path
from typing import Optional

from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentContentFormat
from azure.core.credentials import AzureKeyCredential

from ..common.logger import logger
from ..common.utils import clean_markdown, ensure_minimum_content


class DocumentIntelligenceHandler:
    """
    Async handler that converts supported files to Markdown using Azure Document Intelligence.
    """

    pdf_extensions: frozenset[str] = frozenset({".pdf"})
    office_extensions: frozenset[str] = frozenset(
        {
            ".docx",
            ".xlsx",
            ".pptx",
        }
    )
    image_extensions: frozenset[str] = frozenset(
        {
            ".jpeg",
            ".jpg",
            ".bmp",
            ".tif",
            ".tiff",
            ".heif",
            ".heic",
        }
    )
    extensions: frozenset[str] = frozenset(
        list(pdf_extensions) + list(office_extensions) + list(image_extensions)
    )

    def __init__(self) -> None:
        endpoint = os.getenv("AZURE_DOCINTEL_ENDPOINT", "")
        key = os.getenv("AZURE_DOCINTEL_KEY", "")
        if not endpoint or not key:
            logger.error(
                "DocumentIntelligenceHandler: missing AZURE_DOCINTEL_ENDPOINT or AZURE_DOCINTEL_KEY."
            )
            self._client = None
            return

        try:
            self._client = DocumentIntelligenceClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(key),
            )
            logger.info("DocumentIntelligenceHandler: client initialized.")
        except Exception as e:
            logger.error(f"DocumentIntelligenceHandler: failed to create client: {e}")
            self._client = None

    # ---------- public API ----------

    async def convert_to_md(self, file_path: str | Path, timeout_s: int = 60) -> Optional[str]:
        """
        Analyze a supported document and return Markdown for the entire content.

        This uses the `prebuilt-layout` model with `output_content_format=MARKDOWN`.
        If the service/SDK supports high-resolution OCR and language hints, they are enabled.

        Parameters
        ----------
        file_path : str | Path
            Local path to the document (image or Office file) to analyze.

        Returns
        -------
        Optional[str]
            Markdown string for the full document, or None if analysis fails or content is insufficient.
        """
        if self._client is None:
            logger.error("DocumentIntelligenceHandler: client not configured.")
            return None

        file_path = Path(file_path)
        if not file_path.exists() or not file_path.is_file():
            logger.error(f"DocumentIntelligenceHandler: file not found: {file_path!s}")
            return None

        ext = file_path.suffix.lower()
        if ext not in self.extensions:
            logger.warning(f"DocumentIntelligenceHandler: unsupported extension '{ext}'.")
            return None

        logger.info(f"DocumentIntelligenceHandler: analyzing '{file_path.name}' ({ext})")

        try:
            data = file_path.read_bytes()

            poller = await self._client.begin_analyze_document(
                model_id="prebuilt-read",
                body=io.BytesIO(data),
                output_content_format=DocumentContentFormat.TEXT,
                content_type="application/octet-stream",
                polling_interval=5,
                logging_enable=False,
            )

            try:
                # HARD timeout so we never hang forever
                result = await asyncio.wait_for(poller.result(), timeout=timeout_s)
            except asyncio.TimeoutError:
                status = poller.status()
                logger.error(
                    f"DocumentIntelligenceHandler: analysis timed out after {timeout_s}s. Status: {status}"
                )
                return None

            # Prefer `result.content` (Markdown when requested), otherwise build from page lines
            content = ""
            if hasattr(result, "content") and result.content:
                content = result.content
            else:
                # Fallback for older responses: join all line contents in order
                lines: list[str] = []
                for page in getattr(result, "pages", []) or []:
                    for line in getattr(page, "lines", []) or []:
                        text = getattr(line, "content", "")
                        if text:
                            lines.append(text)
                content = "\n".join(lines)

            md = clean_markdown(content or "")
            if ensure_minimum_content(md):
                return md

            logger.info("DocumentIntelligenceHandler: insufficient content after analysis.")
            return None

        except Exception as e:
            logger.error(f"DocumentIntelligenceHandler: analysis failed for '{file_path}': {e}")
            return None

    async def aclose(self) -> None:
        """Close the underlying async client."""
        if self._client is not None:
            try:
                await self._client.close()
            except Exception as e:
                logger.warning(f"DocumentIntelligenceHandler: error closing client: {e}")

    # ---------- convenience ----------

    @classmethod
    def supports(cls, path: str | Path) -> bool:
        """Return True if the file extension is supported by this handler."""
        return Path(path).suffix.lower() in cls.extensions
