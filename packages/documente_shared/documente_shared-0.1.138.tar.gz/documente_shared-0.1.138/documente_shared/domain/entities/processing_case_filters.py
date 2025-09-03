from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from documente_shared.domain.enums.common import ProcessingStatus
from documente_shared.domain.enums.processing_case import ProcessingCaseType
from documente_shared.application.query_params import QueryParams


@dataclass
class ProcessingCaseFilters(object):
    case_ids: Optional[List[str]] = None
    sort_order: Optional[str] = None
    search: Optional[str] = None
    init_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    statuses: List[ProcessingStatus] = None
    case_types: List[ProcessingCaseType] = None
    include_archived: bool = False
    tenant_slug: Optional[str] = None

    def __post_init__(self):
        self.case_ids = self.case_ids or []
        self.statuses = self.statuses or []
        self.case_types = self.case_types or []
        self.sort_order = self.sort_order or "desc"

    @classmethod
    def from_params(cls, params: QueryParams) -> "ProcessingCaseFilters":
        search_term = params.get_str(key="search", default=None)
        return ProcessingCaseFilters(
            case_ids=params.get_uuid_list(key="case_ids", default=None),
            sort_order=params.get(key="sort", default="desc"),
            search=search_term.strip() if search_term else None,
            init_date=params.get_datetime(key="init_date", default=None),
            end_date=params.get_datetime(key="end_date", default=None),
            statuses=params.get_enum_list(
                key="statuses",
                enum_class=ProcessingStatus,
                default=None,
            ),
            case_types=params.get_enum_list(
                key="case_types",
                enum_class=ProcessingCaseType,
                default=None,
            ),
            include_archived=params.get_bool(
                key="include_archived",
                default=False,
            ),
        )
