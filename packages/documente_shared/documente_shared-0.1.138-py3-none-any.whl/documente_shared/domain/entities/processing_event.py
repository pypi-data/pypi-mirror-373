from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from documente_shared.application.time_utils import get_datetime_from_data
from documente_shared.domain.entities.document import DocumentProcessing
from documente_shared.domain.entities.processing_case import ProcessingCase
from documente_shared.domain.enums.common import ProcessingType


@dataclass
class ProcessingEvent(object):
    processing_type: ProcessingType
    instance: DocumentProcessing | ProcessingCase | None
    timestamp: Optional[datetime] = None

    def __eq__(self, other: 'ProcessingEvent') -> bool:
        if not other:
            return False

        return (
            self.processing_type == other.processing_type
            and self.instance == other.instance
        )

    @property
    def is_processing_case(self) -> bool:
        return self.processing_type == ProcessingType.PROCESSING_CASE

    @property
    def is_document(self) -> bool:
        return self.processing_type == ProcessingType.DOCUMENT

    @property
    def uuid(self) -> Optional[str]:
        if self.is_document:
            return self.instance.digest
        elif self.is_processing_case:
            return self.instance.uuid
        return None

    @property
    def to_dict(self) -> dict:
        return {
            'processing_type': str(self.processing_type),
            'instance': self.instance.to_dict,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }

    @property
    def to_queue_dict(self) -> dict:
        dict_data = self.to_dict
        dict_data['instance'] = self.instance.to_queue_dict
        return dict_data

    @classmethod
    def from_dict(cls, data: dict) -> 'ProcessingEvent':
        processing_type = ProcessingType.from_value(data.get('processing_type'))

        if processing_type.is_document:
            processing_instance = DocumentProcessing.from_dict(data.get('instance'))
        elif processing_type.is_processing_case:
            processing_instance = ProcessingCase.from_dict(data.get('instance'))
        else:
            processing_instance = None

        return cls(
            processing_type=processing_type,
            instance=processing_instance,
            timestamp=get_datetime_from_data(input_datetime=data.get('timestamp')),
        )
