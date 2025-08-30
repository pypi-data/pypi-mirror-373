
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.tarifasconcessionariasvts",
    pk_field="tarifaconcessionariavt",
    default_order_fields=["codigo"],
)
class TarifasconcessionariasvtEntity(EntityBase):
    tarifaconcessionariavt: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    valor: float = None
    tipo: int = None
    codigoexterno: str = None
    concessionariavt: uuid.UUID = None
    lastupdate: datetime.datetime = None
    rederecarga: str = None
    importacao_hash: str = None
