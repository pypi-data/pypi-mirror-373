import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.documentoscolaboradores",
    pk_field="documentocolaborador",
    default_order_fields=["documentocolaborador"],
)
class DocumentoColaboradorDocumentoEntity(EntityBase):
    documentocolaborador: uuid.UUID = None
    tenant: int = None
    bindocumento: bytes = None
