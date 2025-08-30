
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.feriados",
    pk_field="feriado",
    default_order_fields=["feriado"],
)
class FeriadoEntity(EntityBase):
    feriado: uuid.UUID = None
    tenant: int = None
    descricao: str = None
    fixo: int = None
    tipo: int = None
    uf: str = None
    municipio: str = None
    data: datetime.datetime = None
    estabelecimento: uuid.UUID = None
    pessoa: uuid.UUID = None
    sindicato: uuid.UUID = None
    obra: uuid.UUID = None
    lastupdate: datetime.datetime = None
    lotacao: uuid.UUID = None
