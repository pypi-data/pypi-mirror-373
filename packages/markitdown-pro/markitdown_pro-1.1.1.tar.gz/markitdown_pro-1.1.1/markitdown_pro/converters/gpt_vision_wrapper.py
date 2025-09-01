"""
Thin adapter that plugs `GPTVision` into the converters pipeline.

This wrapper selects the appropriate GPT-Vision entrypoint based on the input
file type:

- PDFs → processed page-by-page via the *concurrent* OCR path.
- Images (PNG/JPG/WebP/… or remote URLs) → processed as a single image.

Returns Markdown when successful, or `None` if conversion produced
insufficient content (as determined by `ensure_minimum_content` in the service).
"""

from typing import Optional

from ..common.utils import is_pdf
from ..services.openai_services import GPTVision
from .base import ConverterWrapper


class GPTVisionWrapper(ConverterWrapper):
    """
    Converter facade around `GPTVision`.

    This class satisfies the `ConverterWrapper` interface used by the
    `PDFHandler` pipeline and simply delegates to the underlying `GPTVision`
    service methods.

    Parameters
    ----------
    model_name : str
        Azure OpenAI deployment to use (e.g., "gpt-4.1-mini").
    api_version : str
        Azure OpenAI API version (e.g., "2024-09-01-preview").
    completion_tokens : int
        Maximum number of completion (output) tokens the model may generate.
        This is forwarded to the `AzureChatOpenAI` client inside `GPTVision`.

    Notes
    -----
    - This wrapper does not implement any additional retry or timeout logic;
      those behaviors live inside `GPTVision`.
    - If you need a fallback from the concurrent PDF path to a simpler path,
      add that logic in `convert()` (see inline TODO in that method).
    """

    def __init__(
        self,
        model_name: str = "gpt-4.1-mini",
        api_version: str = "2024-09-01-preview",
        completion_tokens: int = 32000,
    ):
        super().__init__(model_name)
        self.gpt_vision = GPTVision(
            model_name=model_name,
            api_version=api_version,
            completion_tokens=completion_tokens,
        )

    async def convert(self, file_path: str) -> Optional[str]:
        """
        Convert a file to Markdown using GPT-Vision.

        Behavior
        --------
        - If `file_path` is a PDF, invoke the *concurrent* PDF OCR workflow, which
          renders pages to images and processes them in parallel for speed.
        - Otherwise, treat the path as a single image (or URL) and process it directly.

        Parameters
        ----------
        file_path : str
            Local path (or URL for images) to convert.

        Returns
        -------
        Optional[str]
            Markdown string on success, or `None` if no adequate content was produced.
        """
        if is_pdf(file_path):
            # Use the concurrent OCR path for PDFs (page-by-page, parallelized).
            return await self.gpt_vision.process_scanned_pdf_concurrent(file_path)
        # Otherwise, assume it's an image and run single-image OCR/analysis.
        return await self.gpt_vision.process_image(file_path)
