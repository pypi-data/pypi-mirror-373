
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.gestorestrabalhadores",
    pk_field="gestortrabalhador",
    default_order_fields=["gestortrabalhador"],
)
class GestorestrabalhadoreEntity(EntityBase):
    gestortrabalhador: uuid.UUID = None
    tenant: int = None
    trabalhador: uuid.UUID = None
    gestor: uuid.UUID = None
    percentualengajamento: float = None
    lastupdate: datetime.datetime = None
    identificacaonasajongestor: str = None
    datainicio: datetime.datetime = None
    datafim: datetime.datetime = None
