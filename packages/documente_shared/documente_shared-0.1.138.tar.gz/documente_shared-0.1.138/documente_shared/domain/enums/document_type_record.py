from src.common.domain.base_enum import BaseEnum

class DocumentTypeRecord(BaseEnum):
    DOCUMENT_PROCESSING = 'DOCUMENT_PROCESSING'
    PROCESSING_CASE_ITEM = 'PROCESSING_CASE_ITEM'
    
    @property
    def is_document_processing(self):
        return self == DocumentTypeRecord.DOCUMENT_PROCESSING
    
    @property
    def is_processing_case_item(self):
        return self == DocumentTypeRecord.PROCESSING_CASE_ITEM
