from typing import Optional

from ..services.azure_doc_intelligence import DocumentIntelligenceHandler
from .base import ConverterWrapper


class DocIntelligenceWrapper(ConverterWrapper):
    def __init__(self):
        super().__init__("Azure Document Intelligence")
        self.converter = DocumentIntelligenceHandler()

    async def convert(self, file_path: str) -> Optional[str]:
        return await self.converter.convert_to_md(file_path)
