
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.documentoscolaboradores",
    pk_field="documentocolaborador",
    default_order_fields=["documentocolaborador"],
)
class DocumentoscolaboradoreEntity(EntityBase):
    documentocolaborador: uuid.UUID = None
    tenant: int = None
    tipodocumentocolaborador: uuid.UUID = None
    urldocumento: str = None
    lastupdate: datetime.datetime = None
    trabalhador: uuid.UUID = None
    origem: int = None
    solicitacao: uuid.UUID = None
