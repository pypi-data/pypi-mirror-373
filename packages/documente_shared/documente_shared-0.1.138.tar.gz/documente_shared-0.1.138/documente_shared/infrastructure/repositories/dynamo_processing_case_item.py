from typing import Optional, List

from boto3.dynamodb.conditions import Key

from documente_shared.domain.entities.processing_case_item import ProcessingCaseItem
from documente_shared.domain.entities.processing_case_item_filters import ProcessingCaseItemFilters
from documente_shared.domain.enums.common import DocumentViewFormat
from documente_shared.domain.repositories.processing_case_item import ProcessingCaseItemRepository

from documente_shared.infrastructure.dynamo_table import DynamoDBTable


class DynamoProcessingCaseItemRepository(
    DynamoDBTable,
    ProcessingCaseItemRepository,
):
    def find(
        self,
        uuid: str,
        read_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> Optional[ProcessingCaseItem]:
        item = self.get(key={'digest': uuid})
        if item:
            return ProcessingCaseItem.from_dict(item)
        return None

    def find_by_digest(
        self,
        digest: str,
        read_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> Optional[ProcessingCaseItem]:
        item = self.get(key={'digest': digest})
        if item:
            return ProcessingCaseItem.from_dict(item)
        return None

    def persist(
        self,
        instance: ProcessingCaseItem,
        read_bytes: bool = False,
        persist_bytes: bool = False,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> ProcessingCaseItem:
        self.put(instance.to_simple_dict)
        return instance

    def remove(self, instance: ProcessingCaseItem):
        self.delete(key={'case_id': instance.case_id})

    def filter(
        self,
        filters: ProcessingCaseItemFilters,
        view_format: DocumentViewFormat = DocumentViewFormat.PUBLIC_URL,
    ) -> List[ProcessingCaseItem]:
        items = []

        for status in filters.statuses:
            response = self._table.query(
                IndexName='status',
                KeyConditionExpression=Key('status').eq(status.value),
            )
            status_items = response.get('Items', [])
            items.extend(status_items)

        return [
            ProcessingCaseItem.from_dict(item)
            for item in items
        ]
