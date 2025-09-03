from abc import ABC, abstractmethod
from typing import Optional, List

from documente_shared.domain.entities.document import DocumentProcessing
from documente_shared.domain.enums.document import DocumentProcessingStatus


class DocumentProcessingRepository(ABC):

    @abstractmethod
    def find(self, digest: str, read_bytes: bool = False) -> Optional[DocumentProcessing]:
        raise NotImplementedError

    @abstractmethod
    def persist(self, instance: DocumentProcessing, read_bytes: bool = False) -> DocumentProcessing:
        raise NotImplementedError

    @abstractmethod
    def remove(self, instance: DocumentProcessing):
        raise NotImplementedError

    @abstractmethod
    def filter(self, statuses: List[DocumentProcessingStatus]) -> List[DocumentProcessing]:
        raise NotImplementedError
