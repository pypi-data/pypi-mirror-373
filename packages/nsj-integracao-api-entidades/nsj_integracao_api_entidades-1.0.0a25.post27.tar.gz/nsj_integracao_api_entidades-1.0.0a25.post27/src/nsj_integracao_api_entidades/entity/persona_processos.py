
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.processos",
    pk_field="processo",
    default_order_fields=["codigo"],
)
class ProcessoEntity(EntityBase):
    processo: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    tipo: int = None
    descricao: str = None
    tipodecisao: int = None
    extensaodecisao: int = None
    datadecisao: datetime.datetime = None
    depositointegral: bool = None
    tipoautor: int = None
    ibge: str = None
    codigovara: str = None
    motivo: int = None
    empresa: uuid.UUID = None
    dataabertura: datetime.datetime = None
    lastupdate: datetime.datetime = None
