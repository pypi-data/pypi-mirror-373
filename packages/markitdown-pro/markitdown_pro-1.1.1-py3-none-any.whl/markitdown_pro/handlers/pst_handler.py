import os
from typing import Any, List, Optional

from .base_handler import BaseHandler

try:
    from libratom.lib.pff import PffArchive  # type: ignore

    HAS_LIBRATOM = True
except ImportError:
    HAS_LIBRATOM = False

from ..common.logger import logger
from ..common.utils import clean_markdown, ensure_minimum_content


class PSTHandler(BaseHandler):
    """
    Convert a `.pst` file into a Markdown summary using `libratom`.

    The handler scans folders and messages, extracts basic headers and bodies,
    and produces a single Markdown document. Designed to plug into a larger
    converter/ingestion pipeline that expects an async `handle(...)` method.
    """

    # File extensions supported by this handler
    extensions = frozenset([".pst"])

    async def handle(self, file_path: str, *args, **kwargs) -> Optional[str]:
        """
        Process a PST file and return a Markdown summary.

        Parameters
        ----------
        file_path : str
            Path to the `.pst` file on disk.

        Returns
        -------
        Optional[str]
            A Markdown document summarizing folders and messages, or:
            - A short Markdown error message if `libratom` is not installed.
            - `None` on fatal errors or if content is insufficient after processing.
        """
        if not HAS_LIBRATOM:
            logger.error("libratom is not installed. PST processing is disabled.")
            return "# Error: `libratom` not installed. Cannot process PST files."

        logger.info(f"PSTHandler: Processing PST file: {file_path!r}")
        try:
            markdown_content = self._process_pst(file_path)
            if markdown_content:
                return markdown_content
            raise RuntimeError(f"PST handler failed or produced insufficient content: {file_path}.")
        except Exception as e:
            logger.error(f"PSTHandler: Unhandled error processing {file_path!r}: {e}")
            return None

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _process_pst(self, file_path: str) -> Optional[str]:
        """
        Parse the PST, extract folders and messages, and assemble Markdown.

        Parameters
        ----------
        file_path : str
            Path to the `.pst` file.

        Returns
        -------
        Optional[str]
            Markdown text on success, or `None` if no messages are found / content
            is deemed insufficient by `ensure_minimum_content`.
        """
        if not os.path.isfile(file_path):
            logger.error(f"PSTHandler: PST file not found: {file_path!r}")
            return None

        parts: List[str] = [f"# PST Archive: {os.path.basename(file_path)}\n"]

        try:
            # libratom's PffArchive is a context manager
            with PffArchive(file_path) as archive:
                for folder in archive.folders():
                    folder_name = folder.name or "(Unnamed Folder)"
                    parts.append(f"\n## Folder: {folder_name}\n")

                    for idx, message in enumerate(folder.messages(), start=1):
                        try:
                            msg_md = self._process_message(message, idx)
                            if msg_md:
                                parts.extend(msg_md)
                        except Exception as e:
                            logger.error(
                                f"PSTHandler: Error processing message {idx} in folder {folder_name!r}: {e}"
                            )
                            parts.append(f"### Error processing message {idx}: {e}")

            final_md = clean_markdown("\n\n".join(parts))
            return final_md if ensure_minimum_content(final_md) else None

        except Exception as e:
            logger.error(f"PSTHandler: Error opening or scanning PST archive {file_path!r}: {e}")
            return None

    def _process_message(self, message: Any, message_count: int) -> Optional[List[str]]:
        """
        Convert a single `libratom` message into Markdown blocks.

        Parameters
        ----------
        message : Any
            Message object returned by libratom (`pypff` under the hood).
        message_count : int
            1-based index of the message within its folder, used for display.

        Returns
        -------
        Optional[List[str]]
            A list of Markdown lines/blocks describing the message, or `None` on error.

        Notes
        -----
        - Body extraction prefers `plain_text_body`, then falls back to `html_body`, then `rtf_body`.
        - Attachments are **not** currently extracted (TODO).
        """
        try:
            subject = getattr(message, "subject", None) or "(No Subject)"
            sender = "Unknown Sender"
            date_ = "Unknown Date"

            # Extract transport headers if available (bytes or str)
            try:
                headers = getattr(message, "transport_headers", None)
                if headers:
                    if isinstance(headers, bytes):
                        headers = headers.decode(errors="replace")
                    for line in str(headers).splitlines():
                        low = line.lower()
                        if low.startswith("from:"):
                            sender = line.split(":", 1)[1].strip() or sender
                        elif low.startswith("date:"):
                            date_ = line.split(":", 1)[1].strip() or date_
            except Exception as header_err:
                logger.warning(
                    f"PSTHandler: Error parsing headers for message {message_count}: {header_err}"
                )

            # Extract body content (bytes → str with replacement)
            body_content = ""
            try:
                if getattr(message, "plain_text_body", None):
                    body_content = message.plain_text_body.decode(errors="replace")
                elif getattr(message, "html_body", None):
                    body_content = message.html_body.decode(errors="replace")
                elif getattr(message, "rtf_body", None):
                    body_content = message.rtf_body.decode(errors="replace")
            except Exception as body_err:
                logger.warning(
                    f"PSTHandler: Error decoding body for message {message_count}: {body_err}"
                )

            # Compose Markdown block
            body_text = (body_content or "").strip() or "[No body text]"
            md_parts = [
                f"### Message {message_count}",
                f"**Subject:** {subject}",
                f"**From:** {sender}",
                f"**Date:** {date_}",
                "",
                "```",  # keep body verbatim; change to a Markdown quote if preferred
                body_text,
                "```",
            ]

            # TODO: Attachments — iterate `message.attachments()` if available,
            # extract metadata and (optionally) dump filenames or inline text.

            return md_parts

        except Exception as e:
            logger.error(f"PSTHandler: Error composing Markdown for message {message_count}: {e}")
            return None
