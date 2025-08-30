
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.regrasdepagamento",
    pk_field="regradepagamento",
    default_order_fields=["regradepagamento"],
)
class RegrasdepagamentoEntity(EntityBase):
    regradepagamento: uuid.UUID = None
    tenant: int = None
    descricao: str = None
    codigo: str = None
    classificacao: str = None
    desconto: float = None
    empresa: uuid.UUID = None
    grupoempresarial: uuid.UUID = None
    lastupdate: datetime.datetime = None
