"""
Asynchronous PDF → image → OCR pipeline using Azure OpenAI (Vision via Chat Completions).

Key features
------------
- Fully async, with blocking CPU/I/O work (PyMuPDF, PIL) offloaded via asyncio.to_thread.
- Concurrency control via asyncio.Semaphore with *timed* acquire to avoid deadlocks.
- Per-request hard timeout (LLM call), with retry + exponential backoff (full jitter).
- Per-page hard timeout so a single bad page cannot stall the whole run.
- Deterministic, zero-padded page indices in temp filenames for stable sorting.
- Safe temp file cleanup.

Tuning knobs
------------
- max_concurrency: concurrent pages in flight.
- request_timeout_s: hard cap for *each* LLM call.
- acquire_timeout_s: how long to wait to acquire a concurrency slot.
- page_timeout_s: total time budget per page (wraps process_image).

Usage (typical)
---------------
gpt = GPTVision(model_name="gpt-4.1-mini", api_version="2024-09-01-preview", completion_tokens=4000)
md = await gpt.process_scanned_pdf_concurrent("/path/to/doc.pdf")
"""

import asyncio
import base64
import mimetypes
import os
import random
import re
import tempfile
from contextlib import suppress
from pathlib import Path
from typing import Callable, Iterable, Optional, Tuple, TypeVar

import fitz

# from docling.datamodel.pipeline_options import PictureDescriptionApiOptions
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from PIL import Image as PILImage
from pydantic import SecretStr

from ..common.logger import logger
from ..common.utils import clean_markdown, ensure_minimum_content

T = TypeVar("T")
# -------------------------
# Helpers / constants
# -------------------------

_PNG_DPI = 150
_DEFAULT_CONTENT_TYPE = "image/jpeg"
_RETRY_HTTP_STATUSES = (408, 409, 429, 500, 502, 503, 504)


class GPTVision:
    """
    High-level async wrapper around AzureChatOpenAI for image OCR of PDF pages.

    This class renders PDF pages to PNG, sends them to an Azure OpenAI vision model,
    and returns markdown text per page. It is designed for high-throughput,
    robust processing with timeouts and retries.
    """

    def __init__(
        self,
        model_name: str,
        api_version: str,
        completion_tokens: int,
        max_concurrency: int = 150,
        *,
        request_timeout_s: float = 60.0,
        acquire_timeout_s: float = 60.0,
        page_timeout_s: float = 120.0,
    ):
        """
        Parameters
        ----------
        model_name : str
            Azure OpenAI deployment name (e.g., "gpt-4.1-mini").
        api_version : str
            Azure OpenAI API version (e.g., "2024-09-01-preview").
        completion_tokens : int
            Max completion token budget per call (output-side).
        max_concurrency : int
            Maximum concurrent pages in flight (semaphore).
        request_timeout_s : float
            Hard timeout for a single LLM request attempt.
        acquire_timeout_s : float
            Timeout for acquiring a concurrency slot.
        page_timeout_s : float
            Hard timeout for a single page end-to-end (wrapping process_image).
        """
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        if not azure_endpoint:
            logger.error("AZURE_OPENAI_ENDPOINT environment variable is not set.")
            self.lang_client = None
            return

        api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        if not api_key:
            logger.error("AZURE_OPENAI_API_KEY environment variable is not set.")
            self.lang_client = None
            return

        try:
            self._llm = AzureChatOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=SecretStr(api_key),
                api_version=api_version,
                model=model_name,
                max_tokens=completion_tokens,
                temperature=0,
                cache=False,
            )
            # In this version we use the raw LLM response (string markdown),
            # not structured output. Keep a separate client if you later switch.
            self.lang_client = self._llm
            # self.lang_client = self._llm.with_structured_output(
            #     ImageSchema, strict=True, include_raw=True
            # )

            self.model_name = model_name
            self.completion_tokens = completion_tokens

            # Concurrency / timeouts
            self._semaphore = asyncio.Semaphore(max_concurrency)
            self.request_timeout_s = float(request_timeout_s)
            self.acquire_timeout_s = float(acquire_timeout_s)
            self.page_timeout_s = float(page_timeout_s)

            logger.info("GPT-vision client initialized successfully.")
        except Exception as e:
            logger.warning(f"Failed to initialize GPT-vision client: {e}")
            self.lang_client = None
            self._semaphore = asyncio.Semaphore(1)
            self.request_timeout_s = 60.0
            self.acquire_timeout_s = 30.0
            self.page_timeout_s = 120.0

    # -------------------------
    # Async offloading helpers
    # -------------------------

    async def _to_thread(self, fn: Callable[..., T], *args, **kwargs) -> T:
        """Run a blocking function in a threadpool."""
        return await asyncio.to_thread(fn, *args, **kwargs)

    # -------------------------
    # Image building
    # -------------------------

    async def _build_image_url_block(self, file_or_url: str) -> dict:
        """
        Build an OpenAI vision content part for either a URL or a local image.

        Returns
        -------
        dict
            {"type": "image_url", "image_url": {"url": <http(s) or data: URI>}}
        """
        if isinstance(file_or_url, Path):
            file_or_url = str(file_or_url)

        # Remote URL → pass through
        if re.match(r"^https?://", file_or_url, re.IGNORECASE):
            return {"type": "image_url", "image_url": {"url": file_or_url}}

        # Local file → encode as base64 data: URL
        path = Path(file_or_url)
        if not path.is_file():
            raise ValueError(f"Local file not found: {file_or_url}")

        try:
            content_type, _ = mimetypes.guess_type(file_or_url)
            if not content_type:
                content_type = _DEFAULT_CONTENT_TYPE
                logger.warning(
                    f"Could not determine content type for {file_or_url}, defaulting to {_DEFAULT_CONTENT_TYPE}"
                )

            def _make_b64_jpeg() -> str:
                img = PILImage.open(file_or_url).convert("RGB")
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                    img.save(tmp_file.name, "JPEG")
                    jpeg_path = tmp_file.name
                try:
                    with open(jpeg_path, "rb") as f:
                        return base64.b64encode(f.read()).decode("utf-8")
                finally:
                    with suppress(Exception):
                        os.unlink(jpeg_path)

            b64_data = await self._to_thread(_make_b64_jpeg)
            return {
                "type": "image_url",
                "image_url": {"url": f"data:{content_type};base64,{b64_data}"},
            }
        except Exception as e:
            logger.error(f"Error building image block for {file_or_url}: {e}")
            raise

    # -------------------------
    # LLM invoke with timeout + retry
    # -------------------------

    async def _ainvoke_with_retry(
        self,
        file_or_url: str,
        messages: Iterable[BaseMessage],
        *,
        max_retries: int = 6,
        base_delay: float = 0.5,
        max_delay: float = 20.0,
        retry_http_statuses: Tuple[int, ...] = _RETRY_HTTP_STATUSES,
    ):
        """
        Call self.lang_client.ainvoke with:
        - hard timeout per attempt,
        - exponential backoff (full jitter) on transient errors.
        """
        if not self.lang_client:
            logger.error("GPT-vision client is not initialized.")
            raise ValueError("GPT-vision client is not initialized.")
        attempt = 0
        payload = list(messages)
        while True:
            try:
                async with asyncio.timeout(self.request_timeout_s):
                    response = await self.lang_client.ainvoke(payload)
                if not response:
                    logger.error("No response from GPT-vision client.")
                    return None
                return response
            except asyncio.CancelledError:
                # If caller cancels (shutdown), propagate immediately
                logger.error(f"ainvoke cancelled for {file_or_url}")
                raise
            except asyncio.TimeoutError as e:
                # Treat like transient below
                last_err = e
            except Exception as e:
                if not self._is_transient_error(e, retry_http_statuses):
                    raise
                last_err = e
            attempt += 1
            if attempt > max_retries:
                raise last_err
            cap = min(max_delay, base_delay * (2 ** (attempt - 1)))
            sleep_for = random.uniform(0, cap)
            logger.warning(
                f"ainvoke transient error {file_or_url}: attempt {attempt}/{max_retries}: "
                f"{type(last_err).__name__}: {last_err}. Retrying in {sleep_for:.2f}s"
            )
            await asyncio.sleep(sleep_for)

    @staticmethod
    def _is_transient_error(e: Exception, retry_http_statuses: Tuple[int, ...]) -> bool:
        """
        Heuristic detection of transient errors across httpx/OpenAI/LangChain surfaces.
        """
        # Timeouts are considered transient
        if isinstance(e, (asyncio.TimeoutError, TimeoutError)):
            return True

        msg = str(e).lower()
        if any(
            hint in msg
            for hint in (
                "rate limit",
                "temporarily unavailable",
                "timeout",
                "timed out",
                "connection reset",
            )
        ):
            return True

        status = None
        resp = getattr(e, "response", None)
        if resp is not None:
            status = getattr(resp, "status_code", None)
        if status is None:
            status = getattr(e, "status_code", None)

        code = getattr(e, "code", None) or getattr(getattr(e, "error", None), "code", None)
        if isinstance(code, str) and code.upper() in {
            "RATE_LIMIT_EXCEEDED",
            "SERVER_ERROR",
            "TIMEOUT",
        }:
            return True

        if isinstance(status, int) and status in retry_http_statuses:
            return True

        return False

    # -------------------------
    # Public OCR APIs
    # -------------------------

    async def process_image(self, file_or_url: str, prompt: Optional[str] = None) -> Optional[str]:
        """
        OCR a single image (local path or URL) with the vision model.

        Returns
        -------
        Optional[str]
            Markdown content if present and meets minimum content threshold; otherwise None or "[Timed out]".
        """
        if not self.lang_client:
            logger.error("GPT-vision client is not initialized.")
            raise ValueError("GPT-vision client is not initialized.")

        try:
            image_block = await self._build_image_url_block(file_or_url)
            system_message = SystemMessage(
                content=(
                    "You are an OCR formatter. Output MUST be plain Markdown, not a code block. "
                    "Never use triple backticks or code fences. Use standard Markdown only."
                )
            )

            prompt = prompt or (
                "- Perform faithful OCR: Return compact markdown for the text in the image. "
                "Preserve paragraphs, lists, and tables only if visibly present. No repetition.\n"
                "- Perform Image Analysis: Write a 2-line factual summary of what's depicted "
                "(objects, layout, notable elements). No speculation.\n"
                "Remember: DO NOT use triple backticks or code fences."
            )

            human_message = HumanMessage(content=[{"type": "text", "text": prompt}, image_block])

            # Acquire concurrency slot with a hard timeout
            await asyncio.wait_for(self._semaphore.acquire(), timeout=self.acquire_timeout_s)
            try:
                # The LLM call itself has its own hard timeout & retry
                response = await self._ainvoke_with_retry(
                    file_or_url, [system_message, human_message]
                )
            finally:
                with suppress(Exception):
                    self._semaphore.release()

            if not response:
                logger.error("No response from GPT-vision client.")
                return None

            md_content = str(response.content) if response.content else ""
            return md_content if ensure_minimum_content(md_content) else None

        except asyncio.TimeoutError:
            logger.error(f"process_image: Timed out for {file_or_url}")
            return "[Timed out]"
        except Exception as e:
            logger.error(f"process_image: Error during GPT-vision image OCR for {file_or_url}: {e}")
            return None

    # -------------------------
    # PDF helpers
    # -------------------------

    async def _open_doc(self, file_path: str):
        """Open a PDF document (offloaded to a thread)."""
        return await self._to_thread(fitz.open, file_path)

    async def _load_page(self, doc, idx: int):
        """Load a single PDF page (offloaded to a thread)."""
        return await self._to_thread(doc.load_page, idx)

    async def _page_to_png(self, page, file_name_prefix: Optional[str] = None) -> str:
        """Render a PDF page to a temporary PNG and return the path."""

        def _render_to_png() -> str:
            pix = page.get_pixmap(dpi=_PNG_DPI)
            fd, png_path = tempfile.mkstemp(prefix=file_name_prefix or "", suffix=".png")
            os.close(fd)
            pix.save(png_path)
            return png_path

        return await self._to_thread(_render_to_png)

    async def _safe_unlink(self, path: str):
        """Delete a temporary file safely without raising."""

        def _unlink():
            with suppress(Exception):
                Path(path).unlink(missing_ok=True)

        await self._to_thread(_unlink)

    @staticmethod
    def _zero_padded_index(n: int, total: int) -> str:
        """Return 1-based index n (1..total) zero-padded to width=len(str(total))."""
        width = len(str(total))
        return f"{n:0{width}d}"

    async def process_scanned_pdf_concurrent(self, file_path: str) -> Optional[str]:
        """
        Render each page of a PDF to PNG, OCR concurrently, and return the combined markdown.

        Notes
        -----
        - Each page is processed with a per-page hard timeout (page_timeout_s).
        - Temporary PNGs are cleaned up after each page.
        """
        if not self.lang_client:
            return None

        try:
            doc = await self._open_doc(file_path)
            try:
                num_pages = doc.page_count
                file_stem = Path(file_path).stem
                logger.info(
                    f"process_scanned_pdf_concurrent: Starting concurrent GPT-vision OCR on PDF: '{file_path}'"
                )

                async def ocr_page(page_index: int) -> Tuple[int, str]:
                    """OCR a single page and return (index, markdown_block)."""
                    zero_idx = self._zero_padded_index(page_index + 1, num_pages)
                    try:
                        page = await self._load_page(doc, page_index)
                        png_path = await self._page_to_png(
                            page, file_name_prefix=f"{file_stem}_{zero_idx}_"
                        )
                        try:
                            logger.info(f"ocr_page: {file_stem} - processing page {page_index}")
                            # Per-page hard timeout so one slow page cannot stall the run
                            try:
                                partial_md = await asyncio.wait_for(
                                    self.process_image(png_path), timeout=self.page_timeout_s
                                )
                            except asyncio.TimeoutError:
                                logger.error(
                                    f"ocr_page: {file_stem} - page {page_index} timed out after {self.page_timeout_s}s"
                                )
                                partial_md = "[Timed out]"

                            if partial_md:
                                logger.info(
                                    f"ocr_page: {file_stem} - page {page_index}: returned {len(partial_md)} characters"
                                )
                            else:
                                logger.warning(
                                    f"ocr_page: {file_stem} - page {page_index}: no OCR result"
                                )
                                partial_md = ""
                            return (page_index, f"## Page {page_index + 1}\n\n{partial_md}")
                        finally:
                            await self._safe_unlink(png_path)
                    except Exception as e:
                        logger.error(f"ocr_page: Error processing page {page_index}: {e}")
                        return (page_index, "")

                tasks = [ocr_page(i) for i in range(num_pages)]
                results = await asyncio.gather(*tasks, return_exceptions=False)
                combined_md = clean_markdown(
                    "\n\n".join(block for _, block in sorted(results, key=lambda x: x[0]))
                )
                return combined_md if ensure_minimum_content(combined_md) else None
            finally:
                # Ensure PDF is closed to release file handles
                with suppress(Exception):
                    await self._to_thread(doc.close)
        except Exception as e:
            logger.error(f"Concurrent GPT-vision OCR error for PDF {file_path}: {e}")
            return None


# def azure_openai_vlm_options(
#     endpoint: str, api_key: str, deployment: str, api_version: str, max_tokens: int = 4000
# ) -> PictureDescriptionApiOptions:
#     """
#     Build Docling PictureDescriptionApiOptions for calling Azure OpenAI directly.

#     This is optional if you exclusively use the `GPTVision` class above.
#     """
#     if not endpoint:
#         raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set.")
#     if not api_key:
#         raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set.")
#     if not api_version:
#         raise ValueError("AZURE_OPENAI_API_VERSION environment variable is not set.")

#     url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
#     params = {"max_tokens": max_tokens}
#     headers = {"api-key": api_key, "Content-Type": "application/json"}
#     prompt = "Describe the image in three sentences. Be concise and accurate."

#     return PictureDescriptionApiOptions(
#         url=AnyUrl(url), params=params, headers=headers, prompt=prompt, timeout=60
#     )
