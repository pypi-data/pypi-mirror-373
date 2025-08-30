
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.outrosrecebimentostrabalhadores",
    pk_field="outrorecebimentotrabalhador",
    default_order_fields=["outrorecebimentotrabalhador"],
)
class OutrosrecebimentostrabalhadoreEntity(EntityBase):
    outrorecebimentotrabalhador: uuid.UUID = None
    tenant: int = None
    tipo: int = None
    mes: int = None
    ano: int = None
    valor: float = None
    tipoidentificacao: int = None
    identificacao: str = None
    valorinss: float = None
    trabalhador: uuid.UUID = None
    lastupdate: datetime.datetime = None
    anofinal: int = None
    mesfinal: int = None
    categoriatrabalhador: str = None
