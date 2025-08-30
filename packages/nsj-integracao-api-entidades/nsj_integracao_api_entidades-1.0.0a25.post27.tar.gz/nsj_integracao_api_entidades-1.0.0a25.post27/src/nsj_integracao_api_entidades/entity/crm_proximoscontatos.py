
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="crm.proximoscontatos",
    pk_field="proximocontato",
    default_order_fields=["proximocontato"],
)
class ProximoscontatoEntity(EntityBase):
    proximocontato: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    assunto: uuid.UUID = None
    participante: uuid.UUID = None
    usuario: uuid.UUID = None
    lastupdate: datetime.datetime = None
    observacao: str = None
    situacao: int = None
    hora: datetime.time = None
