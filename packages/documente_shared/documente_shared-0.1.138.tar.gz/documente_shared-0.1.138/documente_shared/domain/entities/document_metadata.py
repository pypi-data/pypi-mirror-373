from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DocumentProcessingMetadata(object):
    publication_date: Optional[datetime] = None
    num_circular: Optional[str] = None
    asfi_identifier: Optional[str] = None
    contains_tables: Optional[bool] = None
    text_content: Optional[str] = None
    case_name: Optional[str] = None
    starting_office: Optional[str] = None
    output_json: Optional[dict] = None
    processing_time: Optional[float] = None
    llm_model: Optional[str] = None
    num_pages: Optional[float] = None
    num_tokens: Optional[float] = None
    citcular_type: Optional[str] = None

    @property
    def to_dict(self):
        return {
            'publication_date': (
                self.publication_date.isoformat()
                if self.publication_date
                else None
            ),
            'num_circular': self.num_circular,
            'asfi_identifier': self.asfi_identifier,
            'contains_tables': self.contains_tables,
            'text_content': self.text_content,
            'case_name': self.case_name,
            'starting_office': self.starting_office,
            'output_json': self.output_json,
            'processing_time': self.processing_time,
            'llm_model': self.llm_model,
            'num_pages': self.num_pages,
            'num_tokens': self.num_tokens,
            'citcular_type': self.citcular_type
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            publication_date=(
                datetime.fromisoformat(data.get('publication_date'))
                if data.get('publication_date')
                else None
            ),
            num_circular=data.get('num_circular'),
            asfi_identifier=data.get('asfi_identifier'),
            contains_tables=data.get('contains_tables'),
            text_content=data.get('text_content'),
            case_name=data.get('case_name'),
            starting_office=data.get('starting_office'),
            output_json=data.get('output_json'),
            processing_time=data.get('processing_time'),
            llm_model=data.get('llm_model'),
            num_pages=data.get('num_pages'),
            num_tokens=data.get('num_tokens'),
            citcular_type=data.get('citcular_type')
        )