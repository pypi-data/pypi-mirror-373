from abc import ABC, abstractmethod
from typing import Optional, List

from documente_shared.domain.entities.processing_case_item import ProcessingCaseItem
from documente_shared.domain.entities.processing_case_item_filters import ProcessingCaseItemFilters
from documente_shared.domain.enums.common import DocumentViewFormat


class ProcessingCaseItemRepository(ABC):

    @abstractmethod
    def find(
        self,
        uuid: str,
        read_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> Optional[ProcessingCaseItem]:
        raise NotImplementedError

    @abstractmethod
    def find_by_digest(
        self,
        digest: str,
        read_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> Optional[ProcessingCaseItem]:
        raise NotImplementedError

    @abstractmethod
    def persist(
        self,
        instance: ProcessingCaseItem,
        read_bytes: bool = False,
        persist_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> ProcessingCaseItem:
        raise NotImplementedError

    @abstractmethod
    def remove(self, instance: ProcessingCaseItem):
        raise NotImplementedError

    @abstractmethod
    def filter(
        self,
        filters: ProcessingCaseItemFilters,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> List[ProcessingCaseItem]:
        raise NotImplementedError
