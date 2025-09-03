from dataclasses import dataclass
from typing import List, Optional

from loguru import logger
from requests import Response

from documente_shared.application.payloads import camel_to_snake
from documente_shared.application.query_params import parse_bool_to_str
from documente_shared.domain.entities.processing_case import ProcessingCase
from documente_shared.domain.entities.processing_case_filters import ProcessingCaseFilters
from documente_shared.domain.enums.common import DocumentViewFormat
from documente_shared.domain.repositories.processing_case import ProcessingCaseRepository
from documente_shared.infrastructure.documente_client import DocumenteClientMixin


@dataclass
class HttpProcessingCaseRepository(
    DocumenteClientMixin,
    ProcessingCaseRepository,
):
    def find(
        self,
        uuid: str,
        include_items: bool = False,
        include_items_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> Optional[ProcessingCase]:
        params = {
            "view_format": str(view_format),
        }
        response = self.session.get(
            url=f"{self.api_url}/v1/processing-cases/{uuid}/",
            params=params,
        )
        if response.status_code not in [200, 201]:
            return None
        return self._build_processing_case(response)

    def persist(
        self,
        instance: ProcessingCase,
        persist_items: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> ProcessingCase:
        logger.info(f"PERSISTING_PROCESSING_CASE: data={instance.to_queue_dict}")
        params = {
            "persist_items": parse_bool_to_str(persist_items),
            "view_format": str(view_format),
        }
        response = self.session.put(
            url=f"{self.api_url}/v1/processing-cases/{instance.uuid}/",
            params=params,
            json=instance.to_dict,
        )
        if response.status_code not in [200, 201]:
            raise Exception(f'Error persisting processing case: {response.text}')
        return self._build_processing_case(response)

    def remove(self, instance: ProcessingCase):
        self.session.delete(f"{self.api_url}/v1/processing-cases/{instance.uuid}/")

    def filter(self, filters: ProcessingCaseFilters) -> List[ProcessingCase]:
        response = self.session.get(
            url=f"{self.api_url}/v1/processing-cases/",
            headers={
                "X-Tenant": filters.tenant_slug,
            }
        )
        if response.status_code not in [200, 201]:
            return []
        raw_response = response.json()
        return [
            ProcessingCase.from_persist_dict(camel_to_snake(item_data))
            for item_data in raw_response.get('data', [])
        ]


    @classmethod
    def _build_processing_case(cls, response: Response) -> ProcessingCase:
        response_json = response.json()
        instance_data = response_json.get('data', {})
        return ProcessingCase.from_persist_dict(camel_to_snake(instance_data))