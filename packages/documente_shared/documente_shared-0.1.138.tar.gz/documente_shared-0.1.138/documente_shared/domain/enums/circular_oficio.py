from documente_shared.domain.base_enum import BaseEnum


class CircularOficioType(BaseEnum):
    RETENCION = "RETENCION"
    SUSPENSION = "SUSPENSION"
    REMISION = "REMISION"
    INFORMATIVA = "INFORMATIVA"
    NORMATIVA = "NORMATIVA"

    @property
    def is_normativa(self) -> bool:
        return self == CircularOficioType.NORMATIVA

    @property
    def is_retencion(self):
        return self == CircularOficioType.RETENCION

    @property
    def is_remision(self):
        return self == CircularOficioType.REMISION

    @property
    def is_informativa(self):
        return self == CircularOficioType.INFORMATIVA

    @property
    def is_suspension(self) -> bool:
        return self == CircularOficioType.SUSPENSION
