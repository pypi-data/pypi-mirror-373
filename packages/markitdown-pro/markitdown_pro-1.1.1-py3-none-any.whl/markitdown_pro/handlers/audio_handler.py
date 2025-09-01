from __future__ import annotations

from typing import Optional

from ..common.logger import logger
from ..common.utils import ensure_minimum_content
from ..converters.azure_speech_wrapper import AzureSpeechWrapper
from ..converters.base import ConverterWrapper
from ..converters.markitdown_wrapper import MarkItDownWrapper
from ..handlers.base_handler import BaseHandler


class AudioHandler(BaseHandler):
    """
    Convert audio files to Markdown by trying two converters in order:

      1) **MarkItDown** — fast local extractor (works when the file format is supported).
      2) **Azure Speech** — cloud speech-to-text fallback for actual audio transcription.

    The first converter that yields non-trivial Markdown (as determined by
    `ensure_minimum_content`) is returned. If both fail, `None` is returned.

    Notes
    -----
    - `AzureSpeechWrapper` should expose `async convert(file_path: str) -> Optional[str]`
      and return Markdown (or plain text) of the transcription.
    - This handler runs converters **sequentially** to avoid unnecessary API calls.
    """

    extensions = frozenset(
        {
            ".mp3",
            ".wav",
            ".ogg",
            ".flac",
            ".m4a",
            ".aac",
            ".wma",
            ".webm",
            ".opus",
        }
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.markitdown = MarkItDownWrapper()
        self.azure_speech = AzureSpeechWrapper()

        self._pipeline: list[tuple[ConverterWrapper, str]] = [
            (self.markitdown, "MarkItDown"),
            (self.azure_speech, "Azure Speech"),
        ]

    async def handle(self, file_path: str, *args, **kwargs) -> Optional[str]:
        """
        Convert an audio file to Markdown by trying MarkItDown first,
        then falling back to Azure Speech-to-Text.

        Parameters
        ----------
        file_path : str
            Path to the audio file.

        Returns
        -------
        Optional[str]
            Markdown content if successful; otherwise `None`.
        """
        logger.info(f"AudioHandler: Processing '{file_path}'")

        for converter, name in self._pipeline:
            logger.info(f"AudioHandler: Trying {name} for '{file_path}'")
            try:
                md = await converter.convert(file_path)
                if md and ensure_minimum_content(md):
                    logger.info(f"AudioHandler: {name} succeeded for '{file_path}'")
                    return md
                logger.debug(f"AudioHandler: {name} returned insufficient content")
            except Exception as e:
                logger.error(f"AudioHandler: {name} failed for '{file_path}': {e}")

        logger.error(
            f"AudioHandler: All converters failed or produced insufficient content for '{file_path}'"
        )
        return None
