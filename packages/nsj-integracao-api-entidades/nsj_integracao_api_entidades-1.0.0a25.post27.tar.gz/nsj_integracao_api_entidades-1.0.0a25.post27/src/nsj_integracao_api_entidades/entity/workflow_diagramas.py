
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="workflow.diagramas",
    pk_field="diagrama",
    default_order_fields=["diagrama"],
)
class DiagramaEntity(EntityBase):
    diagrama: uuid.UUID = None
    tenant: int = None
    processo: uuid.UUID = None
    codigo: str = None
    titulo: str = None
    descricao: str = None
    ativo: bool = None
    fechado: bool = None
    iniciovigencia: datetime.datetime = None
    fimvigencia: datetime.datetime = None
    lastupdate: datetime.datetime = None
    escopoworkflow: int = None
    exigircomentario: bool = None
