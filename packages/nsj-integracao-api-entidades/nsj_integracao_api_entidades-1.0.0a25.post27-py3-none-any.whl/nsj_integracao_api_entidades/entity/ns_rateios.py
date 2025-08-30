
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.rateios",
    pk_field="rateio",
    default_order_fields=["rateio"],
)
class RateioEntity(EntityBase):
    rateio: uuid.UUID = None
    tenant: int = None
    classificacaofinanceira: uuid.UUID = None
    centrocusto: uuid.UUID = None
    projeto: uuid.UUID = None
    bempatrimonial: uuid.UUID = None
    tipo: int = None
    valor: float = None
    percentual: float = None
    quantidade: float = None
    observacao: str = None
    ordem: int = None
    id_documento_associado: uuid.UUID = None
    tipo_documento_associado: int = None
    id_linha_doc_associado: uuid.UUID = None
    modo: int = None
    conta: uuid.UUID = None
    rateiopadrao: uuid.UUID = None
    id_origem: uuid.UUID = None
