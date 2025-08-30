
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.tiposdocumentoscolaboradores",
    pk_field="tipodocumentocolaborador",
    default_order_fields=["tipodocumentocolaborador"],
)
class TiposdocumentoscolaboradoreEntity(EntityBase):
    tipodocumentocolaborador: uuid.UUID = None
    tenant: int = None
    descricao: str = None
    lastupdate: datetime.datetime = None
    tipocategoria: int = None
