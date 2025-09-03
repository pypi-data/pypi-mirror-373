from dataclasses import dataclass
from typing import List, Optional

from documente_shared.domain.entities.processing_case_item import ProcessingCaseItem
from documente_shared.domain.entities.processing_case_item_filters import ProcessingCaseItemFilters

from documente_shared.domain.repositories.processing_case_item import ProcessingCaseItemRepository


@dataclass
class MemoryProcessingCaseItemRepository(ProcessingCaseItemRepository):
    collection: dict[str, ProcessingCaseItem] = None

    def __post_init__(self):
        self.collection = self.collection or {}

    def find(
        self,
        uuid: str,
        read_items: bool = False,
    ) -> Optional[ProcessingCaseItem]:
        if uuid in self.collection:
            return self.collection[uuid]
        return None

    def find_by_digest(
        self,
        digest: str,
        read_bytes: bool = False
    ) -> Optional[ProcessingCaseItem]:
        for item in self.collection.values():
            if item.digest == digest:
                return item
        return None


    def persist(
        self,
        instance: ProcessingCaseItem,
        read_bytes: bool = False,
        persist_bytes: bool = False,
    ) -> ProcessingCaseItem:
        self.collection[instance.uuid] = instance
        return instance

    def remove(self, instance: ProcessingCaseItem):
        if instance.uuid in self.collection:
            del self.collection[instance.uuid]
        return None

    def filter(self, filters: ProcessingCaseItemFilters) -> List[ProcessingCaseItem]:
        return []