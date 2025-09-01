import asyncio
from enum import Enum
from typing import Optional

import fitz

from ..common.logger import logger
from ..common.utils import ensure_minimum_content
from ..converters.azure_doc_intel_wrapper import DocIntelligenceWrapper
from ..converters.gpt_vision_wrapper import GPTVisionWrapper
from ..converters.markitdown_wrapper import MarkItDownWrapper
from ..converters.pymupdf_wrapper import PyMuPDFWrapper
from ..converters.unstructured_wrapper import UnstructuredWrapper
from .base_handler import BaseHandler


class PDFType(Enum):
    """
    Simple classification of a PDF based on page contents.

    - TEXT_ONLY:        Every page has "enough" extractable text; no pages contain images.
    - TEXT_PLUS_IMAGES: At least one page contains text and at least one page contains images.
    - ALL_IMAGES:       Every page has at least one image and no page has "enough" text
                        (typical of scanned/image-only PDFs).
    """

    TEXT_ONLY = "TEXT_ONLY"
    TEXT_PLUS_IMAGES = "TEXT_PLUS_IMAGES"
    ALL_IMAGES = "ALL_IMAGES"


class PDFHandler(BaseHandler):
    """
    Orchestrates PDF → Markdown conversion by trying a sequence of converters
    chosen from a text-oriented pipeline or an image/OCR pipeline depending
    on a quick content scan of the PDF.

    The flow is:
      1) `_detect_pdf_type` runs a fast pass over the PDF (offloaded to a thread)
         to count text-bearing and image-bearing pages.
      2) Based on the detected `PDFType`, choose a pipeline:
           - TEXT_ONLY:         text pipeline
           - ALL_IMAGES:        image pipeline (OCR)
           - TEXT_PLUS_IMAGES:  text pipeline, then image pipeline as fallback
      3) Iterate the chosen converters in order until one returns acceptable Markdown.

    Notes:
    - Converters MUST implement an async `convert(file_path: str) -> Optional[str]`.
    - `ensure_minimum_content` is used to filter out trivial/empty results.
    """

    # File extensions handled by this handler
    extensions = frozenset([".pdf"])

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Text-first converters (fastest/cheapest first, progressively more robust)
        self.markitdown = MarkItDownWrapper()
        self.unstructured = UnstructuredWrapper()
        self.pymu = PyMuPDFWrapper()
        self.azure_docint = DocIntelligenceWrapper()

        # OCR-based converter for scanned/image-only PDFs
        self.gpt_vision = GPTVisionWrapper()

        # Pipelines in the order they should be attempted
        self.text_pipeline = [self.markitdown, self.unstructured, self.pymu, self.azure_docint]
        self.image_pipeline = [self.gpt_vision]

    async def handle(self, file_path: str, *args, **kwargs) -> Optional[str]:
        """
        Convert a PDF to Markdown by selecting and executing the appropriate pipeline.

        Parameters
        ----------
        file_path : str
            Absolute or relative path to a `.pdf` file.

        Returns
        -------
        Optional[str]
            Markdown produced by the first successful converter in the chosen pipeline,
            or `None` if all converters fail.
        """
        try:
            pdf_type = await self._detect_pdf_type(file_path)

            # Choose pipeline based on detected content type
            if pdf_type == PDFType.TEXT_ONLY:
                pipeline = self.text_pipeline
            elif pdf_type == PDFType.ALL_IMAGES:
                pipeline = self.image_pipeline
            elif pdf_type == PDFType.TEXT_PLUS_IMAGES:
                pipeline = self.text_pipeline + self.image_pipeline
            else:
                # Fallback to text pipeline if detection returned an unexpected value
                pipeline = self.text_pipeline

            # Try converters in order until one returns acceptable content
            for converter in pipeline:
                logger.info(f"Trying {converter.name} for PDF {file_path}")
                try:
                    md_content = await converter.convert(file_path)
                    if md_content and ensure_minimum_content(md_content):
                        return md_content
                except Exception as e:
                    logger.error(f"Converter {converter.name} failed for PDF {file_path}: {e}")

            # Nothing worked
            raise RuntimeError(f"PDF conversion failed with all converters for {file_path}")

        except Exception as e:
            logger.error(f"Error handling PDF '{file_path}': {e}")
            return None

    async def _detect_pdf_type(self, file_path: str) -> PDFType:
        """
        Quickly scan the PDF to decide which pipeline to run.

        Heuristic
        ---------
        - A page is considered to have "text" if the extracted text length ≥ `min_text_length_threshold`.
        - A page is considered to have "images" if `page.get_images(full=True)` returns any entries.
        - The final classification is derived from counts across all pages.

        Parameters
        ----------
        file_path : str
            Path to the input PDF.

        Returns
        -------
        PDFType
            Classification result used to pick the processing pipeline.

        Raises
        ------
        Exception
            If the file cannot be opened or scanned.
        """
        min_text_length_threshold = 50  # tune as needed for your corpus

        try:

            def _scan() -> PDFType:
                # PyMuPDF is synchronous and CPU-bound; run it in a worker thread.
                with fitz.open(file_path) as doc:
                    total_pages = doc.page_count
                    pages_with_text = 0
                    pages_with_images = 0

                    for page_index in range(total_pages):
                        page = doc.load_page(page_index)
                        if not page:
                            continue

                        # Text detection (simple length threshold)
                        page_text = page.get_text().strip()
                        if len(page_text) >= min_text_length_threshold:
                            pages_with_text += 1

                        # Image presence detection
                        if page.get_images(full=True):
                            pages_with_images += 1

                    logger.debug(
                        f"PDFHandler: Pages with text for {file_path}: {pages_with_text}/{total_pages}"
                    )
                    logger.debug(
                        f"PDFHandler: Pages with images for {file_path}: {pages_with_images}/{total_pages}"
                    )

                    is_text_only = pages_with_text == total_pages and pages_with_images == 0
                    is_all_images = pages_with_images == total_pages and pages_with_text == 0
                    has_text_and_images = pages_with_text > 0 and pages_with_images > 0

                    if is_text_only:
                        return PDFType.TEXT_ONLY
                    elif is_all_images:
                        return PDFType.ALL_IMAGES
                    elif has_text_and_images:
                        return PDFType.TEXT_PLUS_IMAGES
                    else:
                        # Mixed/uncertain cases default to text+images to maximize recall.
                        return PDFType.TEXT_PLUS_IMAGES

            # Offload the blocking scan
            return await asyncio.to_thread(_scan)

        except Exception as e:
            logger.error(f"Error analyzing PDF '{file_path}': {e}")
            # Re-raise so callers can distinguish detection failures from conversion failures
            raise
