
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.locaisdeuso",
    pk_field="localdeuso",
    default_order_fields=["codigo"],
)
class LocaisdeusoEntity(EntityBase):
    localdeuso: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    grupoempresarial: uuid.UUID = None
    centrocusto: uuid.UUID = None
    projeto: uuid.UUID = None
    lastupdate: datetime.datetime = None
    localdeestoque: uuid.UUID = None
    classificacaofinanceira: uuid.UUID = None
    agrega_solicitacoes: bool = None
    uso_consumo: bool = None
    estabelecimento: uuid.UUID = None
    modelo: bool = None
    localdeuso_modelo: uuid.UUID = None
