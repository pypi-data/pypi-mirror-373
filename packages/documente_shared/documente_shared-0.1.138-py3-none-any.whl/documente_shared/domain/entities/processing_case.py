from dataclasses import dataclass
from datetime import datetime, tzinfo
from typing import Optional, List

from documente_shared.application.time_utils import get_datetime_from_data
from documente_shared.domain.constants import la_paz_tz
from documente_shared.domain.entities.processing_case_item import ProcessingCaseItem
from documente_shared.domain.enums.common import ProcessingStatus
from documente_shared.domain.enums.processing_case import ProcessingCaseType


@dataclass
class ProcessingCase(object):
    uuid: str
    name: str
    tenant_slug: str
    status: ProcessingStatus
    case_type: ProcessingCaseType
    enqueued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    feedback: Optional[list | dict] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None
    items: Optional[List[ProcessingCaseItem]] = None

    def __post_init__(self):
        self.items = self.items or []

    def __eq__(self, other: 'ProcessingCase') -> bool:
        if not other:
            return False

        return (
            self.uuid == other.uuid
            and self.name == other.name
            and self.status == other.status
            and self.case_type == other.case_type
            and self.enqueued_at == other.enqueued_at
            and self.started_at == other.started_at
            and self.failed_at == other.failed_at
            and self.feedback == other.feedback
            and self.completed_at == other.completed_at
            and self.metadata == other.metadata
        )

    @property
    def strategy_id(self) ->str:
        return str(self.case_type)

    @property
    def is_procesable(self) -> bool:
        return self.items and len(self.items) > 0

    @property
    def is_bcp_microcredito(self) -> bool:
        return self.case_type and self.case_type.is_bcp_microcredito

    @property
    def is_univida_soat(self) -> bool:
        return self.case_type and self.case_type.is_univida_soat

    @property
    def to_dict(self) -> dict:
        return {
            'uuid': self.uuid,
            'tenant_slug': self.tenant_slug,
            'name': self.name,
            'status': str(self.status),
            'case_type': (
                str(self.case_type)
                if self.case_type else None
            ),
            'enqueued_at': self.enqueued_at.isoformat() if self.enqueued_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'failed_at': self.failed_at.isoformat() if self.failed_at else None,
            'feedback': self.feedback,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.metadata,
            'items': [item.to_dict for item in self.items],
        }

    @property
    def to_queue_dict(self) -> dict:
        data = self.to_dict
        data["items"] = [
            item.to_queue_dict for item in self.items
        ]
        return data

    @property
    def to_persist_dict(self) -> dict:
        persist_data = self.to_dict
        persist_data["items"] = [
            item.to_dict for item in self.items
        ]
        return persist_data

    @property
    def procesable_items(self) -> List[ProcessingCaseItem]:
        return [
            item for item in self.items
            if item.status in [
                ProcessingStatus.PENDING,
                ProcessingStatus.ENQUEUED,
            ]
        ]

    @property
    def has_procesable_items(self) -> bool:
        return len(self.procesable_items) > 0

    def pending(self, timezone: tzinfo = la_paz_tz):
        self.status = ProcessingStatus.PENDING
        self.started_at = None

    def enqueue(self, timezone: tzinfo = la_paz_tz):
        self.status = ProcessingStatus.ENQUEUED
        self.enqueued_at = datetime.now(tz=timezone)

    def processing(self, timezone: tzinfo = la_paz_tz):
        self.status = ProcessingStatus.PROCESSING
        self.started_at = datetime.now(tz=timezone)

    def failed(
        self,
        error_message: Optional[str] = None,
        timezone: tzinfo = la_paz_tz,
    ):
        self.status = ProcessingStatus.FAILED
        self.failed_at = datetime.now(tz=timezone)

    def completed(self, timezone: tzinfo = la_paz_tz):
        self.status = ProcessingStatus.COMPLETED
        self.completed_at = datetime.now(tz=timezone)

    def deleted(self):
        self.status = ProcessingStatus.DELETED

    def refresh_status(self):
        if not self.items:
            return

        item_statuses = [item.status for item in self.items]

        if any(status == ProcessingStatus.FAILED for status in item_statuses):
            self.status = ProcessingStatus.INCOMPLETE
        elif any(status == ProcessingStatus.PROCESSING for status in item_statuses):
            self.status = ProcessingStatus.PROCESSING
        elif all(status == ProcessingStatus.COMPLETED for status in item_statuses):
            self.status = ProcessingStatus.COMPLETED
        elif all(status == ProcessingStatus.PENDING for status in item_statuses):
            self.status = ProcessingStatus.PENDING
        else:
            self.status = ProcessingStatus.PENDING



    @classmethod
    def from_dict(cls, data: dict) -> 'ProcessingCase':
        return cls(
            uuid=data.get('uuid'),
            name=data.get('name'),
            tenant_slug=data.get('tenant_slug'),
            status=ProcessingStatus.from_value(data.get('status')),
            case_type=(
                ProcessingCaseType.from_value(data.get('case_type'))
                if data.get('case_type') else None
            ),
            enqueued_at=get_datetime_from_data(input_datetime=data.get('enqueued_at')),
            started_at=get_datetime_from_data(input_datetime=data.get('started_at')),
            failed_at=get_datetime_from_data(input_datetime=data.get('failed_at')),
            feedback=data.get('feedback'),
            metadata=data.get('metadata', {}),
            completed_at=get_datetime_from_data(input_datetime=data.get('completed_at')),
            items=[
                ProcessingCaseItem.from_dict(item_dict)
                for item_dict in data.get('items', [])
            ],
        )

    @classmethod
    def from_persist_dict(cls, data: dict) -> 'ProcessingCase':
        instance = cls.from_dict(data)
        instance.items = [
            ProcessingCaseItem.from_persist_dict(item_dict)
            for item_dict in data.get('items', [])
        ]
        return instance

