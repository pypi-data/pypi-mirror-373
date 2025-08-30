
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.estabelecimentosconjuntos",
    pk_field="estabelecimentoconjunto",
    default_order_fields=["estabelecimentoconjunto"],
)
class EstabelecimentosconjuntoEntity(EntityBase):
    estabelecimentoconjunto: uuid.UUID = None
    tenant: int = None
    estabelecimento: uuid.UUID = None
    conjunto: uuid.UUID = None
    cadastro: int = None
    permissao: bool = None
    lastupdate: datetime.datetime = None
