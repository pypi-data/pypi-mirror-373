import logging
from pathlib import Path

import pytest

from markitdown_pro.handlers.pdf_handler import PDFHandler
from tests.fixtures import data_path, pretty_id
from tests.utils import list_files

log = logging.getLogger(__name__)

INCLUDE_EXTENSIONS = [".pdf"]

TEST_FILES_PATH = data_path()
ALL_FILES = list_files(TEST_FILES_PATH, include_ext=INCLUDE_EXTENSIONS, recursive=True)
log.info(f"Found {len(ALL_FILES)} test files in {TEST_FILES_PATH}.")


@pytest.mark.asyncio
@pytest.mark.parametrize("file_path", ALL_FILES, ids=[pretty_id(p) for p in ALL_FILES])
async def test_files(file_path: Path, pdf_handler: PDFHandler):
    log.info(f"Testing file: {file_path}")

    markdown_text = await pdf_handler.handle(str(file_path))
    assert markdown_text is not None, f"Conversion returned None for {file_path.name}"
    assert isinstance(markdown_text, str), f"Output type is not str for {file_path.name}"
