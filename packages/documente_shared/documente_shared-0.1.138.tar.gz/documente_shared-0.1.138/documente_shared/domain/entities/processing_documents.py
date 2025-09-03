from dataclasses import dataclass
from typing import Optional

from documente_shared.domain.entities.in_memory_document import InMemoryDocument


@dataclass
class ProcessedDocuments(object):
    processed_csv: Optional[InMemoryDocument] = None
    processed_xlsx: Optional[InMemoryDocument] = None
    processed_json: Optional[InMemoryDocument] = None
