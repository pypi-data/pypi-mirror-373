import json
from dataclasses import dataclass
from datetime import datetime, tzinfo
from decimal import Decimal
from typing import Optional, List

from documente_shared.application.files import (
    remove_slash_from_path,
    get_filename_from_path,
    remove_extension,
)
from documente_shared.application.numbers import normalize_number
from documente_shared.application.time_utils import get_datetime_from_data
from documente_shared.domain.constants import la_paz_tz
from documente_shared.domain.entities.document_metadata import DocumentProcessingMetadata
from documente_shared.domain.enums.document import (
    DocumentProcessingStatus,
    DocumentProcessingCategory,
    DocumentProcessingSubCategory,
    DocumentProcessingSource,
)


@dataclass
class DocumentProcessing(object):
    digest: str
    status: DocumentProcessingStatus
    category: DocumentProcessingCategory
    file_path: Optional[str] = None
    file_auxiliar_path: Optional[str] = None
    file_bytes: Optional[bytes] = None
    sub_category: Optional[DocumentProcessingSubCategory] = None
    uploaded_from: Optional[DocumentProcessingSource] = None
    locked_by_admin: Optional[bool] = False
    processed_csv_path: Optional[str] = None
    processed_csv_bytes: Optional[bytes] = None
    processed_xlsx_path: Optional[str] = None
    processed_xlsx_bytes: Optional[bytes] = None
    processed_json_path: Optional[str] = None
    processed_json_bytes: Optional[bytes] = None
    processed_metadata_path: Optional[str] = None
    processing_time: Optional[Decimal] = None
    processing_accuracy: Optional[Decimal] = None
    issued_at: Optional[datetime] = None
    uploaded_at: Optional[datetime] = None
    enqueued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failed_reason: Optional[str] = None
    feedback: Optional[list | dict] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None
    document_size: Optional[Decimal] = None
    document_pages: Optional[int] = None
    metadata_items: Optional[List[DocumentProcessingMetadata]] = None

    def __post_init__(self):
        self.metadata_items = self.metadata_items or []

    @property
    def strategy_id(self) -> str:
        return str(self.category)

    @property
    def is_pending(self) -> bool:
        return self.status == DocumentProcessingStatus.PENDING

    @property
    def is_enqueued(self) -> bool:
        return self.status == DocumentProcessingStatus.ENQUEUED

    @property
    def is_processing(self) -> bool:
        return self.status == DocumentProcessingStatus.PROCESSING

    @property
    def is_completed(self) -> bool:
        return self.status == DocumentProcessingStatus.COMPLETED

    @property
    def is_incomplete(self) -> bool:
        return self.status == DocumentProcessingStatus.INCOMPLETE

    @property
    def is_failed(self) -> bool:
        return self.status == DocumentProcessingStatus.FAILED
    
    @property
    def is_inreview(self) -> bool:
        return self.status == DocumentProcessingStatus.IN_REVIEW

    @property
    def is_circular(self) -> bool:
        return self.category and self.category.is_circular

    @property
    def is_desgravamen(self) -> bool:
        return self.category and self.category.is_desgravamen
    
    @property
    def is_valid(self) -> bool:
        return all([
            self.digest,
            self.status,
            self.file_path,
        ])

    @property
    def is_finished(self) -> bool:
        return self.status in [
            DocumentProcessingStatus.COMPLETED,
            DocumentProcessingStatus.FAILED,
        ]
    @property
    def file_key(self) -> str:
        return remove_slash_from_path(self.file_path)

    @property
    def processed_csv_key(self) -> str:
        return remove_slash_from_path(self.processed_csv_path)

    @property
    def processed_xlsx_key(self) -> str:
        return remove_slash_from_path(self.processed_xlsx_path)

    @property
    def processed_json_key(self) -> str:
        return remove_slash_from_path(self.processed_json_path)

    @property
    def processed_csv_filename(self) -> str:
        return get_filename_from_path(self.processed_csv_path)

    @property
    def processed_xlsx_filename(self) -> str:
        return get_filename_from_path(self.processed_xlsx_path)

    @property
    def processed_json_filename(self) -> str:
        return get_filename_from_path(self.processed_json_path)

    @property
    def processed_metadata_key(self) -> str:
        return remove_slash_from_path(self.processed_metadata_path)

    @property
    def extended_filename(self) -> str:
        if not self.file_path:
            return ''
        return self.file_path.split('/')[-1]

    @property
    def raw_file_name(self) -> str:
        return remove_extension(self.extended_filename)

    @property
    def filename(self) -> str:
        filename_with_extension = self.extended_filename
        return filename_with_extension.split('.')[0]

    @property
    def metadata_items_bytes(self) -> bytes:
        metadata_items = [
            metadata_item.to_dict
            for metadata_item in self.metadata_items
        ]
        return json.dumps(metadata_items).encode('utf-8')

    @property
    def has_original_file(self) -> bool:
        return bool(self.file_path) and self.file_bytes

    @property
    def has_processed_csv(self) -> bool:
        return bool(self.processed_csv_path) and self.processed_csv_bytes

    @property
    def has_processed_xlsx(self) -> bool:
        return bool(self.processed_xlsx_path) and self.processed_xlsx_bytes

    @property
    def has_processed_json(self) -> bool:
        return bool(self.processed_json_path) and self.processed_json_bytes

    @property
    def has_processed_metadata(self) -> bool:
        return bool(self.processed_metadata_path) and self.metadata_items

    def pending(self, timezone: tzinfo = la_paz_tz):
        self.status = DocumentProcessingStatus.PENDING
        self.started_at = None
        self.uploaded_at = datetime.now(tz=timezone)

    def enqueue(self, timezone: tzinfo = la_paz_tz):
        self.status = DocumentProcessingStatus.ENQUEUED
        self.enqueued_at = datetime.now(tz=timezone)

    def processing(self, timezone: tzinfo = la_paz_tz):
        self.status = DocumentProcessingStatus.PROCESSING
        self.started_at = datetime.now(tz=timezone)

    def failed(
        self,
        error_message: Optional[str] = None,
        timezone: tzinfo = la_paz_tz,
    ):
        self.failed_reason = error_message
        self.status = DocumentProcessingStatus.FAILED
        self.failed_at = datetime.now(tz=timezone)

    def completed(self, timezone: tzinfo = la_paz_tz):
        self.status = DocumentProcessingStatus.COMPLETED
        self.completed_at = datetime.now(tz=timezone)
        self.failed_reason = None

    def incomplete(self, timezone: tzinfo = la_paz_tz):
        self.status = DocumentProcessingStatus.INCOMPLETE
        self.completed_at = datetime.now(tz=timezone)

    def deleted(self):
        self.status = DocumentProcessingStatus.DELETED
    
    def in_review(self):
        self.status = DocumentProcessingStatus.IN_REVIEW
    
    def has_pages_mt(self, pages: int = 100) -> bool:
        return self.document_pages and self.document_pages >= pages
    
    def has_pages_lt(self, pages: int = 100) -> bool:
        return self.document_pages and self.document_pages <= pages
    
    def is_size_gt(self, size: Decimal = Decimal(10)):
        return self.document_size and self.document_size >= size
    
    def is_size_lt(self, size: Decimal = Decimal(10)):
        return self.document_size and self.document_size <= size

    def __eq__(self, other: 'DocumentProcessing') -> bool:
        if not other:
            return False

        return (
            self.digest == other.digest
            and self.status == other.status
            and self.file_path == other.file_path
            and self.file_auxiliar_path == other.file_auxiliar_path
            and self.issued_at == other.issued_at
            and self.uploaded_at == other.uploaded_at
            and self.enqueued_at == other.enqueued_at
            and self.started_at == other.started_at
            and self.failed_at == other.failed_at
            and self.completed_at == other.completed_at
        )

    @property
    def to_dict(self) -> dict:
        return {
            'digest': self.digest,
            'status': str(self.status),
            'file_path': self.file_path,
            'file_auxiliar_path': self.file_auxiliar_path,
            'category': (
                str(self.category)
                if self.category else None
            ),
            'sub_category': (
                str(self.sub_category)
                if self.sub_category else None
            ),
            'uploaded_from': (
                str(self.uploaded_from)
                if self.uploaded_from else None
            ),
            'locked_by_admin': self.locked_by_admin,
            'processed_csv_path': self.processed_csv_path,
            'processed_xlsx_path': self.processed_xlsx_path,
            'processed_json_path': self.processed_json_path,
            'processed_metadata_path': self.processed_metadata_path,
            'processing_time': (
                normalize_number(self.processing_time)
                if self.processing_time else None
            ),
            'processing_accuracy': (
                normalize_number(self.processing_accuracy)
                if self.processing_accuracy else None
            ),
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'enqueued_at': self.enqueued_at.isoformat() if self.enqueued_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'failed_at': self.failed_at.isoformat() if self.failed_at else None,
            'failed_reason': self.failed_reason,
            'feedback': self.feedback,
            'metadata': self.metadata,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata_items': [metadata.to_dict for metadata in self.metadata_items],
            'document_size': (
                normalize_number(self.document_size)
                if self.document_size else None
            ),
            'document_pages': self.document_pages,
        }

    @property
    def to_simple_dict(self) -> dict:
        simple_dict = self.to_dict.copy()
        simple_dict.pop('metadata_items')
        return simple_dict

    @property
    def to_queue_dict(self) -> dict:
        return self.to_dict


    def overload(
        self,
        new_instance: 'DocumentProcessing',
        properties: List[str] = None,
    ):
        instance_properties = properties or [
            'status',
            'metadata',
            'file_path',
            'file_auxiliar_path',
            'file_bytes',
            'category',
            'sub_category',
            'uploaded_from',
            'locked_by_admin',
            'processed_csv_path',
            'processed_csv_bytes',
            'processed_xlsx_path',
            'processed_xlsx_bytes',
            'processed_json_path',
            'processed_json_bytes',
            'processed_metadata_path',
            'processed_metadata_bytes',
            'processing_time',
            'processing_accuracy',
            'issued_at',
            'uploaded_at',
            'enqueued_at',
            'started_at',
            'failed_at',
            'failed_reason',
            'feedback',
            'metadata',
            'document_size',
            'document_pages'
            'completed_at',
        ]
        for _property in instance_properties:
            property_value = getattr(new_instance, _property)
            if not hasattr(self, _property):
                continue
            setattr(self, _property, property_value)
        return self

    @classmethod
    def from_dict(cls, data: dict) -> 'DocumentProcessing':
        return cls(
            digest=data.get('digest'),
            status=DocumentProcessingStatus.from_value(data.get('status')),
            file_path=data.get('file_path'),
            file_auxiliar_path=data.get('file_auxiliar_path'),
            category=(
                DocumentProcessingCategory.from_value(data.get('category'))
                if data.get('category') else None
            ),
            sub_category=(
                DocumentProcessingSubCategory.from_value(data.get('sub_category'))
                if data.get('sub_category') else None
            ),
            uploaded_from=(
                DocumentProcessingSource.from_value(data.get('uploaded_from'))
                if data.get('uploaded_from') else None
            ),
            locked_by_admin=data.get('locked_by_admin'),
            processed_csv_path=data.get('processed_csv_path'),
            processed_xlsx_path=data.get('processed_xlsx_path'),
            processed_json_path=data.get('processed_json_path'),
            processed_metadata_path=data.get('processed_metadata_path'),
            processing_time=(
                Decimal(data.get('processing_time'))
                if data.get('processing_time') else None
            ),
            processing_accuracy=(
                Decimal(data.get('processing_accuracy'))
                if data.get('processing_accuracy') else None
            ),
            issued_at=get_datetime_from_data(input_datetime=data.get('issued_at')),
            uploaded_at=get_datetime_from_data(input_datetime=data.get('uploaded_at')),
            enqueued_at=get_datetime_from_data(input_datetime=data.get('enqueued_at')),
            started_at=get_datetime_from_data(input_datetime=data.get('started_at')),
            failed_at=get_datetime_from_data(input_datetime=data.get('failed_at')),
            failed_reason=data.get('failed_reason'),
            feedback=data.get('feedback'),
            metadata=data.get('metadata', {}),
            completed_at=get_datetime_from_data(input_datetime=data.get('completed_at')),
            metadata_items=[
                DocumentProcessingMetadata.from_dict(metadata)
                for metadata in data.get('metadata_items', [])
            ],
            document_size=(
                Decimal(data.get('document_size'))
                if data.get('document_size') else None
            ),
            document_pages=data.get('document_pages')
        )

