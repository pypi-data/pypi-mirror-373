
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.emprestimostrabalhadores",
    pk_field="emprestimotrabalhador",
    default_order_fields=["trabalhador"],
)
class EmprestimostrabalhadoreEntity(EntityBase):
    emprestimotrabalhador: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    descricao: str = None
    percentualiof: float = None
    percentualjuros: float = None
    parcelas: int = None
    valor: float = None
    observacao: str = None
    trabalhador: uuid.UUID = None
    lastupdate: datetime.datetime = None
    evento: uuid.UUID = None
