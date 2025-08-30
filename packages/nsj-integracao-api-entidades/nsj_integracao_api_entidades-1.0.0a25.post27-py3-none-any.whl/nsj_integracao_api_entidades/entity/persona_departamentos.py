
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.departamentos",
    pk_field="departamento",
    default_order_fields=["codigo"],
)
class DepartamentoEntity(EntityBase):
    departamento: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    centrocustonasajon: int = None
    ccustopersona: str = None
    classefinpersona: str = None
    classefinnasajon: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    lastupdate: datetime.datetime = None
    gestor: uuid.UUID = None
    identificacaonasajongestor: str = None
