from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from documente_shared.application.query_params import QueryParams
from documente_shared.domain.enums.common import ProcessingStatus
from documente_shared.domain.enums.document import (
    DocumentProcessingStatus,
)
from documente_shared.domain.enums.processing_case import ProcessingDocumentType


@dataclass
class ProcessingCaseItemFilters(object):
    sort_order: Optional[str] = None
    search: Optional[str] = None
    init_date: Optional[datetime] = None
    end_date: Optional[datetime]= None
    case_id: Optional[str] = None
    statuses: List[ProcessingStatus] = None
    document_types: List[ProcessingDocumentType] = None
    include_archived: bool = False
    tenant_slug: Optional[str] = None

    def __post_init__(self):
        self.statuses = self.statuses or []
        self.document_types = self.document_types or []
        self.sort_order = self.sort_order or "desc"


    @classmethod
    def from_params(cls, params: QueryParams) -> "ProcessingCaseItemFilters":
        search_term = params.get_str(key="search", default=None)
        return cls(
            sort_order=params.get(key="sort", default="desc"),
            search=search_term.strip() if search_term else None,
            init_date=params.get_datetime(key="init_date", default=None),
            end_date=params.get_datetime(key="end_date", default=None),
            case_id=params.get_str(key="case_id", default=None),
            statuses=params.get_enum_list(
                key="statuses",
                enum_class=DocumentProcessingStatus,
                default=None,
            ),
            document_types=params.get_enum_list(
                key="document_types",
                enum_class=ProcessingDocumentType,
                default=None,
            ),
            include_archived=params.get_bool(
                key="include_archived",
                default=False,
            ),
        )
