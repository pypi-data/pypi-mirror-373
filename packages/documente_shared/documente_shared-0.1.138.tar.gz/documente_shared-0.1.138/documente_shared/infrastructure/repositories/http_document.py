from dataclasses import dataclass
from typing import List, Optional

from loguru import logger
from requests import Response

from documente_shared.application.payloads import camel_to_snake
from documente_shared.application.query_params import parse_bool_to_str
from documente_shared.domain.entities.document import DocumentProcessing
from documente_shared.domain.enums.document import DocumentProcessingStatus
from documente_shared.domain.repositories.document import DocumentProcessingRepository
from documente_shared.infrastructure.documente_client import DocumenteClientMixin


@dataclass
class HttpDocumentProcessingRepository(
    DocumenteClientMixin,
    DocumentProcessingRepository,
):
    def find(self, digest: str, read_bytes: bool = False) -> Optional[DocumentProcessing]:
        params = {
            "read_bytes": parse_bool_to_str(read_bytes),
        }
        response = self.session.get(
            url=f"{self.api_url}/v1/documents/{digest}/",
            params=params,
        )
        if response.status_code not in [200, 201]:
            return None
        return self._build_document_processing(response)

    def persist(self, instance: DocumentProcessing, read_bytes: bool = False) -> DocumentProcessing:
        logger.info(f"PERSISTING_DOCUMENT: data={instance.to_simple_dict}")
        params = {
            "read_bytes": parse_bool_to_str(read_bytes),
        }
        response = self.session.put(
            url=f"{self.api_url}/v1/documents/{instance.digest}/",
            params=params,
            json=instance.to_simple_dict,
        )
        if response.status_code not in [200, 201]:
            raise Exception(f'Error persisting document processing: {response.text}')
        return self._build_document_processing(response)
    
    def remove(self, instance: DocumentProcessing):
        self.session.delete(f"{self.api_url}/v1/documents/{instance.digest}/")
        
    def filter(self, statuses: List[DocumentProcessingStatus]) -> List[DocumentProcessing]:
        response = self.session.get(f"{self.api_url}/v1/documents/?statuses={statuses}")
        if response.status_code not in [200, 201]:
            return []
        raw_response = response.json()
        return [
            DocumentProcessing.from_dict(camel_to_snake(item['documentProcessing']))
            for item in raw_response.get('data', [])
        ]

    
    @classmethod
    def _build_document_processing(cls, response: Response) -> DocumentProcessing:
        response_json = response.json()
        instance_data = response_json.get('data', {})
        return DocumentProcessing.from_dict(camel_to_snake(instance_data))
    
    