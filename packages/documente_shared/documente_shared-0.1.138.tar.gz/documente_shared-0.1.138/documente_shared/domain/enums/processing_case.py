from documente_shared.domain.base_enum import BaseEnum


class ProcessingCaseType(BaseEnum):
    BCP_MICROCREDITO = 'BCP_MICROCREDITO'
    UNIVIDA_SOAT = 'UNIVIDA_SOAT'
    AGNOSTIC = 'AGNOSTIC'

    @property
    def is_bcp_microcredito(self):
        return self == ProcessingCaseType.BCP_MICROCREDITO

    @property
    def is_univida_soat(self):
        return self == ProcessingCaseType.UNIVIDA_SOAT

    @property
    def is_agnostic(self):
        return self == ProcessingCaseType.AGNOSTIC




class ProcessingDocumentType(BaseEnum):
    REVIEW_CHECKLIST = 'REVISION_CHECKLIST'
    SOLICITUD_DE_CREDITO = 'SOLICITUD_DE_CREDITO'
    RESOLUCION_DE_CREDITO = 'RESOLUCION_DE_CREDITO'
    CEDULA_DE_IDENTIDAD = 'CEDULA_DE_IDENTIDAD'
    NIT = 'NIT'
    FICHA_VERIFICACION = 'FICHA_VERIFICACION'
    FACTURA_ELECTRICIDAD = 'FACTURA_ELECTRICIDAD'
    CARTA_CLIENTE = 'CARTA_CLIENTE'

    @property
    def is_review_checklist(self):
        return self == ProcessingDocumentType.REVIEW_CHECKLIST

    @property
    def is_solicitud_de_credito(self):
        return self == ProcessingDocumentType.SOLICITUD_DE_CREDITO

    @property
    def is_resolucion_de_credito(self):
        return self == ProcessingDocumentType.RESOLUCION_DE_CREDITO

    @property
    def is_cedula_de_identidad(self):
        return self == ProcessingDocumentType.CEDULA_DE_IDENTIDAD

    @property
    def is_nit(self):
        return self == ProcessingDocumentType.NIT

    @property
    def is_ficha_verificacion(self):
        return self == ProcessingDocumentType.FICHA_VERIFICACION

    @property
    def is_factura_electricidad(self):
        return self == ProcessingDocumentType.FACTURA_ELECTRICIDAD

    @property
    def is_carta_cliente(self):
        return self == ProcessingDocumentType.CARTA_CLIENTE


