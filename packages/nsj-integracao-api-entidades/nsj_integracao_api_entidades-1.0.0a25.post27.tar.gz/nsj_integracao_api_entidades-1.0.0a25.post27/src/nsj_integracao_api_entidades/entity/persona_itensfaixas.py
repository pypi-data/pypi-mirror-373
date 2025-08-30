
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.itensfaixas",
    pk_field="itemfaixa",
    default_order_fields=["itemfaixa"],
)
class ItensfaixaEntity(EntityBase):
    itemfaixa: uuid.UUID = None
    tenant: int = None
    datacriacao: datetime.datetime = None
    valorfinal: float = None
    perccalculo: float = None
    valorconstante: float = None
    faixa: uuid.UUID = None
    lastupdate: datetime.datetime = None
