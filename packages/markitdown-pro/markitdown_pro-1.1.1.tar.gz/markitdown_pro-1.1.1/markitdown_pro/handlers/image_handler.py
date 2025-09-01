from typing import Optional

from ..common.logger import logger
from ..common.utils import ensure_minimum_content
from ..converters.gpt_vision_wrapper import GPTVisionWrapper
from .base_handler import BaseHandler


class ImageHandler(BaseHandler):
    extensions = frozenset(
        [
            ".bmp",
            ".gif",
            ".heic",
            ".jpeg",
            ".jpg",
            ".png",
            ".prn",
            ".svg",
            ".tiff",
            ".webp",
            ".heif",
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gpt_vision = GPTVisionWrapper()

    async def handle(self, file_path, *args, **kwargs) -> Optional[str]:
        """
        Handles image files by converting them to Markdown using GPT Vision.

        Args:
            file_path: Path to the image file.

        Returns:
            Markdown string representing the image content (OCR and analysis),
            or an error message.
        """
        logger.info(f"Processing image file: {file_path}")
        try:
            md_content = await self.gpt_vision.convert(file_path)
            if md_content and ensure_minimum_content(md_content):
                return md_content
            else:
                raise RuntimeError(f"Image conversion failed or insufficient content: {file_path}")
        except Exception as e:
            logger.error(f"Error handling image file '{file_path}': {e}")
            return None
