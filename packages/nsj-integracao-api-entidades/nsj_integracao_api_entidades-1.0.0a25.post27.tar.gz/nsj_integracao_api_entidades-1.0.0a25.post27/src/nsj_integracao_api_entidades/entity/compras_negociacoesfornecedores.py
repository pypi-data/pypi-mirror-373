
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="compras.negociacoesfornecedores",
    pk_field="negociacaofornecedor",
    default_order_fields=["negociacaofornecedor"],
)
class NegociacoesfornecedoreEntity(EntityBase):
    negociacaofornecedor: uuid.UUID = None
    tenant: int = None
    fornecedor: uuid.UUID = None
    negociacao: uuid.UUID = None
    valorfrete: float = None
    valoroutrasdespesas: float = None
    ordem: int = None
    fretemarcado: bool = None
    outrasdespesasmarcado: bool = None
    lastupdate: datetime.datetime = None
    cotacaofornecedor: uuid.UUID = None
    prazoentrega: int = None
    pis: float = None
    cofins: float = None
    icms: float = None
    icmsst: float = None
    ipi: float = None
    tributosmarcado: bool = None
