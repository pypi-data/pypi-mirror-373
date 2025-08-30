
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.formaspagamentos",
    pk_field="formapagamento",
    default_order_fields=["formapagamento"],
)
class FormaspagamentoEntity(EntityBase):
    formapagamento: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    tipo: int = None
    padrao: bool = None
    lastupdate: datetime.datetime = None
    bloqueada: bool = None
    diasprevisaopagar: int = None
    diasprevisaoreceber: int = None
    grupoempresarial: uuid.UUID = None
    sinaldiaspagar: int = None
    sinaldiasreceber: int = None
    tipodiaspagar: int = None
    tipodiasreceber: int = None
    uf: str = None
