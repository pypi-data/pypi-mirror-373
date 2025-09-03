from dataclasses import dataclass
from typing import List, Optional

from documente_shared.domain.entities.processing_case import ProcessingCase
from documente_shared.domain.entities.processing_case_filters import ProcessingCaseFilters
from documente_shared.domain.enums.common import DocumentViewFormat

from documente_shared.domain.repositories.processing_case import ProcessingCaseRepository


@dataclass
class MemoryProcessingCaseRepository(ProcessingCaseRepository):
    collection: dict[str, ProcessingCase] = None

    def __post_init__(self):
        self.collection = self.collection or {}

    def find(
        self,
        uuid: str,
        include_items: bool = False,
        include_items_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> Optional[ProcessingCase]:
        if uuid in self.collection:
            return self.collection[uuid]
        return None

    def persist(
        self,
        instance: ProcessingCase,
        persist_items: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> ProcessingCase:
        self.collection[instance.uuid] = instance
        return instance

    def remove(self, instance: ProcessingCase):
        if instance.uuid in self.collection:
            del self.collection[instance.uuid]
        return None

    def filter(self, filters: ProcessingCaseFilters) -> List[ProcessingCase]:
        return []