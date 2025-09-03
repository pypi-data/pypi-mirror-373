from abc import ABC, abstractmethod
from typing import Optional, List

from documente_shared.domain.entities.processing_case import ProcessingCase
from documente_shared.domain.entities.processing_case_filters import ProcessingCaseFilters
from documente_shared.domain.enums.common import DocumentViewFormat


class ProcessingCaseRepository(ABC):

    @abstractmethod
    def find(
        self,
        uuid: str,
        include_items: bool = False,
        include_items_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> Optional[ProcessingCase]:
        raise NotImplementedError

    @abstractmethod
    def persist(
        self,
        instance: ProcessingCase,
        persist_items: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> ProcessingCase:
        raise NotImplementedError

    @abstractmethod
    def remove(self, instance: ProcessingCase):
        raise NotImplementedError

    @abstractmethod
    def filter(self, filters: ProcessingCaseFilters) -> List[ProcessingCase]:
        raise NotImplementedError
