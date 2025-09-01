"""
AzureSpeechService
==================

Converts audio files to Markdown using Azure Cognitive Services Speech.

Features
--------
- Continuous recognition (handles long audio files end-to-end).
- Auto language detection across a configurable set of locales.
- Async-friendly: the blocking Speech SDK work runs in a worker thread.
- Hard timeout so a bad file never hangs your pipeline.
- Clean Markdown output (with optional timestamps).

Requirements
------------
Env vars:
- AZURE_SPEECH_KEY
- AZURE_SPEECH_REGION

Install:
- pip install azure-cognitiveservices-speech

Notes
-----
The Speech SDK for Python is synchronous/callback-based; even the async-looking
methods return futures that block when you `.get()`. We therefore run the
recognition flow in a thread via `asyncio.to_thread`.
"""

from __future__ import annotations

import asyncio
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import azure.cognitiveservices.speech as speechsdk

from ..common.logger import logger
from ..common.utils import clean_markdown, ensure_minimum_content

# --- helpers -----------------------------------------------------------------


def _format_ts_hrs_mins_secs(seconds: float) -> str:
    """Return a HH:MM:SS timestamp for readability."""
    seconds = max(0, int(seconds))
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _ticks_to_seconds(ticks: int) -> float:
    """Speech SDK offsets are in 100-ns ticks."""
    return ticks / 10_000_000.0


@dataclass
class TranscriptionResult:
    text: str
    detected_language: Optional[str] = None
    segments: Optional[List[Tuple[float, str]]] = None  # (start_seconds, text)


# --- service -----------------------------------------------------------------


class AzureSpeechService:
    """
    Wraps Azure Speech-to-Text to produce Markdown transcripts.

    Usage
    -----
    svc = AzureSpeechService()
    md = await svc.handle("path/to/audio.mp3")

    Behavior
    --------
    - Uses continuous recognition to process the entire file.
    - If `languages` is provided, uses auto-detection across those locales.
      (Otherwise Speech SDK defaults apply.)
    - Returns Markdown string or None on failure/insufficient content.
    """

    # Supported audio extensions (lowercase with dot)
    extensions = frozenset(
        {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac", ".wma", ".webm", ".opus"}
    )

    def __init__(self) -> None:
        key = os.getenv("AZURE_SPEECH_KEY", "")
        region = os.getenv("AZURE_SPEECH_REGION", "")

        if not key or not region:
            logger.error("AzureSpeechService: missing AZURE_SPEECH_KEY or AZURE_SPEECH_REGION.")
            self._speech_config = None
            return

        try:
            cfg = speechsdk.SpeechConfig(subscription=key, region=region)
            # Recommended defaults: enable punctuation, set profanity masking as needed.
            # (These are defaults nowadays, but properties are shown for clarity.)
            # cfg.set_property(speechsdk.PropertyId.SpeechServiceResponse_JsonResult, "true")
            self._speech_config = cfg
        except Exception as e:
            logger.error(f"AzureSpeechService: failed to create SpeechConfig: {e}")
            self._speech_config = None

    # Public API ---------------------------------------------------------------

    async def convert_to_md(
        self,
        file_path: str | Path,
        *,
        languages: Optional[List[str]] = ["en-US", "es-ES", "fr-FR", "zh-CN", "it-IT"],
        include_timestamps: bool = False,
        timeout_s: float = 900.0,  # 15 minutes hard cap; tune to your needs
    ) -> Optional[str]:
        """
        Transcribe `file_path` to Markdown.

        Parameters
        ----------
        file_path : str | Path
            Local path to an audio file (wav, mp3, ogg, flac, m4a, aac, wma, webm, opus).
        languages : list[str] | None
            Optional list of BCP-47 locales for auto language detection,
            e.g. ["en-US", "es-ES", "fr-FR"]. If omitted, SDK defaults apply.
        include_timestamps : bool
            If True, each line includes a HH:MM:SS timestamp.
        timeout_s : float
            Hard timeout for the full recognition run.

        Returns
        -------
        Optional[str]
            Markdown transcript, or None on failure/insufficient content.
        """
        if self._speech_config is None:
            logger.error("AzureSpeechService: service not configured.")
            return None

        src = Path(file_path)
        if not src.is_file():
            logger.error(f"AzureSpeechService: file not found: {src}")
            return None

        if src.suffix.lower() not in self.extensions:
            logger.warning(f"AzureSpeechService: unsupported audio extension '{src.suffix}'.")
            return None

        # Run the blocking SDK flow in a worker thread and enforce a hard timeout.
        try:
            result: TranscriptionResult = await asyncio.wait_for(
                asyncio.to_thread(self._transcribe_sync, src, languages),
                timeout=timeout_s,
            )
        except asyncio.TimeoutError:
            logger.error(f"AzureSpeechService: timed out after {timeout_s}s for {src.name}")
            return None
        except Exception as e:
            logger.error(f"AzureSpeechService: transcription failed for '{src.name}': {e}")
            return None

        # Build Markdown
        lines: List[str] = [f"# Transcript: {src.name}"]
        if result.detected_language:
            lines.append(f"*Detected language:* `{result.detected_language}`")
        lines.append("")  # blank line

        if include_timestamps and result.segments:
            for start_sec, text in result.segments:
                ts = _format_ts_hrs_mins_secs(start_sec)
                lines.append(f"- **{ts}** {text}")
        else:
            # single paragraph form
            lines.append(result.text.strip())

        md = clean_markdown("\n".join(lines))
        return md if ensure_minimum_content(md) else None

    # Internal (runs in a worker thread) --------------------------------------

    def _transcribe_sync(self, path: Path, languages: Optional[List[str]]) -> TranscriptionResult:
        """
        Continuous recognition of a file using the Speech SDK.

        This function *blocks* and is intended to be called via `asyncio.to_thread`.
        """
        if not self._speech_config:
            raise RuntimeError("AzureSpeechService not configured.")

        audio_config = speechsdk.AudioConfig(filename=str(path))

        # Auto language detection if languages provided
        auto_lang_cfg = None
        if languages:
            try:
                auto_lang_cfg = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
                    languages=languages
                )
            except Exception as e:
                logger.warning(f"AzureSpeechService: invalid languages {languages}: {e}")

        recognizer = speechsdk.SpeechRecognizer(
            speech_config=self._speech_config,
            audio_config=audio_config,
            auto_detect_source_language_config=auto_lang_cfg,
        )

        detected_language: Optional[str] = None
        segments: List[Tuple[float, str]] = []
        full_text_parts: List[str] = []
        done = threading.Event()

        def _on_recognized(evt: speechsdk.SessionEventArgs):  # type: ignore[override]
            nonlocal detected_language
            res = getattr(evt, "result", None)
            if not res:
                return
            if res.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = (res.text or "").strip()
                if not text:
                    return
                # Detect language (if auto detection is enabled)
                try:
                    lang = res.properties.get(
                        speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
                    )
                    if lang:
                        detected_language = lang
                except Exception:
                    pass
                # Offset in 100ns ticks → seconds
                start_sec = _ticks_to_seconds(getattr(res, "offset", 0))
                segments.append((start_sec, text))
                full_text_parts.append(text)
            elif res.reason == speechsdk.ResultReason.NoMatch:
                # No speech recognized in this segment; ignore
                pass

        def _on_canceled(evt):
            reason = getattr(evt, "reason", None)
            details = getattr(evt, "error_details", None)
            logger.warning(f"AzureSpeechService: recognition canceled: {reason} ({details})")
            done.set()

        def _on_session_stopped(_):
            done.set()

        recognizer.recognized.connect(_on_recognized)  # type: ignore[attr-defined]
        recognizer.canceled.connect(_on_canceled)  # type: ignore[attr-defined]
        recognizer.session_stopped.connect(_on_session_stopped)  # type: ignore[attr-defined]

        try:
            recognizer.start_continuous_recognition_async().get()
            # Wait until session stops or is canceled; Speech SDK will stop when file ends.
            done.wait()  # block in this thread
            recognizer.stop_continuous_recognition_async().get()
        finally:
            # Best-effort cleanup (SDK manages most resources itself)
            try:
                recognizer.session_stopped.disconnect(_on_session_stopped)  # type: ignore[attr-defined]
                recognizer.canceled.disconnect(_on_canceled)  # type: ignore[attr-defined]
                recognizer.recognized.disconnect(_on_recognized)  # type: ignore[attr-defined]
            except Exception:
                pass

        text = " ".join(full_text_parts).strip()
        return TranscriptionResult(
            text=text, detected_language=detected_language, segments=segments
        )
