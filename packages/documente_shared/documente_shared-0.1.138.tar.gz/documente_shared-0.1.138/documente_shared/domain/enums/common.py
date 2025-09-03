from typing import List

from documente_shared.domain.base_enum import BaseEnum


class ProcessingSource(BaseEnum):
    AGENT_UI = 'AGENT_UI'
    AGENT_CRAWLER = 'AGENT_CRAWLER'
    PLATFORM_UI = 'PLATFORM_UI'
    PLATFORM_API = 'PLATFORM_API'
    AWS_CONSOLE = 'AWS_CONSOLE'
    LOCAL_MANUAL = 'LOCAL_MANUAL'

    @property
    def is_agent_ui(self):
        return self == ProcessingSource.AGENT_UI

    @property
    def is_agent_crawler(self):
        return self == ProcessingSource.AGENT_CRAWLER

    @property
    def is_platform_ui(self):
        return self == ProcessingSource.PLATFORM_UI

    @property
    def is_platform_api(self):
        return self == ProcessingSource.PLATFORM_API

    @property
    def is_aws_console(self):
        return self == ProcessingSource.AWS_CONSOLE

    @property
    def is_local_manual(self):
        return self == ProcessingSource.LOCAL_MANUAL


class ProcessingStatus(BaseEnum):
    PENDING = 'PENDING'
    ENQUEUED = 'ENQUEUED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    INCOMPLETE = 'INCOMPLETE'
    FAILED = 'FAILED'
    DELETED = 'DELETED'
    CANCELLED = 'CANCELLED'
    IN_REVIEW = 'IN_REVIEW'

    @property
    def procesable_statuses(self) -> List['ProcessingStatus']:
        return [
            ProcessingStatus.PENDING,
            ProcessingStatus.ENQUEUED,
            ProcessingStatus.PROCESSING,
        ]

    @property
    def final_statuses(self) -> List['ProcessingStatus']:
        return [
            ProcessingStatus.COMPLETED,
            ProcessingStatus.FAILED,
        ]

    @property
    def is_pending(self):
        return self == ProcessingStatus.PENDING

    @property
    def is_enqueued(self):
        return self == ProcessingStatus.ENQUEUED

    @property
    def is_processing(self):
        return self == ProcessingStatus.PROCESSING

    @property
    def is_completed(self):
        return self == ProcessingStatus.COMPLETED

    @property
    def is_incomplete(self):
        return self == ProcessingStatus.INCOMPLETE

    @property
    def is_failed(self):
        return self == ProcessingStatus.FAILED

    @property
    def is_deleted(self):
        return self == ProcessingStatus.DELETED

    @property
    def is_cancelled(self):
        return self == ProcessingStatus.CANCELLED

    @property
    def is_in_review(self):
        return self == ProcessingStatus.IN_REVIEW


class ProcessingType(BaseEnum):
    DOCUMENT = 'DOCUMENT'
    PROCESSING_CASE = 'PROCESSING_CASE'

    @property
    def is_document(self):
        return self == ProcessingType.DOCUMENT

    @property
    def is_processing_case(self):
        return self == ProcessingType.PROCESSING_CASE


class TaskResultStatus(BaseEnum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    IN_PROGRESS = "IN_PROGRESS"
    FAILURE = "FAILURE"


class DocumentViewFormat(BaseEnum):
    PUBLIC_URL = 'PUBLIC_URL'
    STORAGE_KEY = 'STORAGE_KEY'

    @property
    def is_public_url(self):
        return self == DocumentViewFormat.PUBLIC_URL

    @property
    def is_object_storage(self):
        return self == DocumentViewFormat.STORAGE_KEY

