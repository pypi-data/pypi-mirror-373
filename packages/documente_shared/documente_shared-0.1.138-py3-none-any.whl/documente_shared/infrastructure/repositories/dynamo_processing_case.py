from typing import Optional, List

from boto3.dynamodb.conditions import Key

from documente_shared.domain.entities.processing_case import ProcessingCase
from documente_shared.domain.entities.processing_case_filters import ProcessingCaseFilters
from documente_shared.domain.enums.common import DocumentViewFormat
from documente_shared.domain.repositories.processing_case import ProcessingCaseRepository

from documente_shared.infrastructure.dynamo_table import DynamoDBTable


class DynamoProcessingCaseRepository(
    DynamoDBTable,
    ProcessingCaseRepository,
):
    def find(
        self,
        uuid: str,
        include_items: bool = False,
        include_items_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> Optional[ProcessingCase]:
        item = self.get(key={'uuid': uuid})
        if item:
            return ProcessingCase.from_dict(item)
        return None

    def persist(
        self,
        instance: ProcessingCase,
        persist_items: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> ProcessingCase:
        self.put(instance.to_persist_dict)
        return instance

    def remove(self, instance: ProcessingCase):
        self.delete(key={'uuid': instance.uuid})

    def filter(self, filters: ProcessingCaseFilters) -> List[ProcessingCase]:
        items = []

        for status in filters.statuses:
            response = self._table.query(
                IndexName='status',
                KeyConditionExpression=Key('status').eq(status.value),
            )
            status_items = response.get('Items', [])
            items.extend(status_items)

        return [
            ProcessingCase.from_dict(item)
            for item in items
        ]
