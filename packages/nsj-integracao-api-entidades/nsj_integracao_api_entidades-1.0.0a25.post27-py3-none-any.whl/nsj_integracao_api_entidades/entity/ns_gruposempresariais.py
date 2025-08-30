
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.gruposempresariais",
    pk_field="grupoempresarial",
    default_order_fields=["codigo"],
)
class GruposempresariaiEntity(EntityBase):
    grupoempresarial: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    usagrade: int = None
    lastupdate: datetime.datetime = None
    modogestaopatrimonial: bool = None
    escopoworkflow: int = None
    importacao_hash: str = None
    modo_calculo_pmc: int = None
    modocomissoes: int = None
