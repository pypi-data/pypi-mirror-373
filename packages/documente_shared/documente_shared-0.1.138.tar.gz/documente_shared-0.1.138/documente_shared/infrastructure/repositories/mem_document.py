from dataclasses import dataclass
from typing import List, Optional

from documente_shared.domain.entities.document import DocumentProcessing
from documente_shared.domain.enums.common import DocumentViewFormat
from documente_shared.domain.enums.document import DocumentProcessingStatus
from documente_shared.domain.repositories.document import DocumentProcessingRepository


@dataclass
class MemoryDocumentProcessingRepository(DocumentProcessingRepository):
    collection: dict[str, DocumentProcessing] = None

    def __post_init__(self):
        self.collection = self.collection or {}

    def find(
        self,
        digest: str,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> Optional[DocumentProcessing]:
        if digest in self.collection:
            return self.collection[digest]
        return None


    def persist(
        self,
        instance: DocumentProcessing,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> DocumentProcessing:
        self.collection[instance.digest] = instance
        return instance

    def remove(self, instance: DocumentProcessing):
        if instance.digest in self.collection:
            del self.collection[instance.digest]
        return None

    def filter(self, statuses: List[DocumentProcessingStatus]) -> List[DocumentProcessing]:
        items = []
        for status in statuses:
            items.extend(
                [item for item in self.collection.values() if item.status == status]
            )
        return items