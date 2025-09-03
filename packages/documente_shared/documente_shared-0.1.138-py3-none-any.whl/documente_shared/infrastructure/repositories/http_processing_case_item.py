from dataclasses import dataclass
from typing import List, Optional

from loguru import logger
from requests import Response

from documente_shared.application.payloads import camel_to_snake
from documente_shared.application.query_params import parse_bool_to_str
from documente_shared.domain.entities.processing_case_item import ProcessingCaseItem
from documente_shared.domain.entities.processing_case_item_filters import ProcessingCaseItemFilters
from documente_shared.domain.enums.common import DocumentViewFormat
from documente_shared.domain.repositories.processing_case_item import ProcessingCaseItemRepository
from documente_shared.infrastructure.documente_client import DocumenteClientMixin


@dataclass
class HttpProcessingCaseItemRepository(
    DocumenteClientMixin,
    ProcessingCaseItemRepository,
):
    def find(
        self,
        uuid: str,
        read_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> Optional[ProcessingCaseItem]:
        response = self.session.get(
            url=f"{self.api_url}/v1/processing-case-items/{uuid}/?read_bytes={parse_bool_to_str(read_bytes)}",
        )
        if response.status_code not in [200, 201]:
            return None
        return self._build_processing_case_item(response)

    def find_by_digest(
        self,
        digest: str,
        read_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> Optional[ProcessingCaseItem]:
        params = {
            "read_bytes": parse_bool_to_str(read_bytes),
            "view_format": str(view_format),
        }
        response = self.session.get(
            url=f"{self.api_url}/v1/processing-case-items/{digest}/",
            params=params,
        )
        if response.status_code not in [200, 201]:
            return None
        return self._build_processing_case_item(response)

    def persist(
        self,
        instance: ProcessingCaseItem,
        read_bytes: bool = False,
        persist_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> ProcessingCaseItem:
        logger.info(f"PERSISTING_PROCESSING_CASE_ITEM: data={instance.to_queue_dict}")
        params = {
            "read_bytes": parse_bool_to_str(read_bytes),
            "view_format": str(view_format),
        }
        response: Response = self.session.put(
            url=f"{self.api_url}/v1/processing-case-items/{instance.uuid}/",
            params=params,
            json=(
                instance.to_persist_dict
                if persist_bytes else instance.to_queue_dict
            ),
        )
        if response.status_code not in [200, 201]:
            logger.info(f"PERSISTING_PROCESSING_CASE_ITEM ERROR: data={response.text}")
            return instance
        return self._build_processing_case_item(response)

    def remove(self, instance: ProcessingCaseItem):
        self.session.delete(f"{self.api_url}/v1/processing-case-items/{instance.uuid}/")

    def filter(
        self,
        filters: ProcessingCaseItemFilters,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> List[ProcessingCaseItem]:
        params = {
            "view_format": str(view_format),
        }
        response = self.session.get(
            url=f"{self.api_url}/v1/processing-case-items/",
            params=params,
        )
        if response.status_code not in [200, 201]:
            return []
        raw_response = response.json()
        return [
            ProcessingCaseItem.from_dict(camel_to_snake(item_data))
            for item_data in raw_response.get('data', [])
        ]

    def filter_with_tenant(
        self,
        tenant_slug: str,
        filters: ProcessingCaseItemFilters,
    ) -> List[ProcessingCaseItem]:
        response = self.session.get(f"{self.api_url}/v1/processing-case-items/")
        if response.status_code not in [200, 201]:
            return []
        raw_response = response.json()
        return [
            ProcessingCaseItem.from_dict(camel_to_snake(item_data))
            for item_data in raw_response.get('data', [])
        ]

    @classmethod
    def _build_processing_case_item(cls, response: Response) -> ProcessingCaseItem:
        response_json = response.json()
        instance_data = response_json.get('data', {})
        return ProcessingCaseItem.from_dict(camel_to_snake(instance_data))
