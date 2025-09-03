from typing import Optional, List

from boto3.dynamodb.conditions import Key

from documente_shared.domain.entities.document import DocumentProcessing
from documente_shared.domain.enums.document import DocumentProcessingStatus
from documente_shared.domain.repositories.document import DocumentProcessingRepository

from documente_shared.infrastructure.dynamo_table import DynamoDBTable


class DynamoDocumentProcessingRepository(
    DynamoDBTable,
    DocumentProcessingRepository,
):
    def find(self, digest: str, read_bytes: bool = False) -> Optional[DocumentProcessing]:
        item = self.get(key={'digest': digest})
        if item:
            return DocumentProcessing.from_dict(item)
        return None

    def persist(self, instance: DocumentProcessing, read_bytes: bool = False) -> DocumentProcessing:
        self.put(instance.to_simple_dict)
        return instance

    def remove(self, instance: DocumentProcessing):
        self.delete(key={'digest': instance.digest})

    def filter(self, statuses: List[DocumentProcessingStatus]) -> List[DocumentProcessing]:
        items = []

        for status in statuses:
            response = self._table.query(
                IndexName='status',
                KeyConditionExpression=Key('status').eq(status.value),
            )
            status_items = response.get('Items', [])
            items.extend(status_items)

        return [
            DocumentProcessing.from_dict(item)
            for item in items
        ]
