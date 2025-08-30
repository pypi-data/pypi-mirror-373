
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.tipi",
    pk_field="id",
    default_order_fields=["ncm"],
)
class TipiEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    ncm: str = None
    texto: str = None
    unidade: str = None
    tipoipi: int = None
    ipi: float = None
    ipivalor: float = None
    ii: float = None
    taxadepreciacao: float = None
    descricao: str = None
    lastupdate: datetime.datetime = None
    perfil_importacao: uuid.UUID = None
    fimvigencia: datetime.datetime = None
    unidadetributada: str = None
