
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.df_pagamentos",
    pk_field="pagamento",
    default_order_fields=["pagamento"],
)
class DfPagamentoEntity(EntityBase):
    pagamento: uuid.UUID = None
    tenant: int = None
    id_formapagamento: uuid.UUID = None
    id_docfis: uuid.UUID = None
    id_conta: uuid.UUID = None
    id_rateiopadrao: uuid.UUID = None
    id_meioeletronico: uuid.UUID = None
    id_layoutcobranca: uuid.UUID = None
    id_operadora: uuid.UUID = None
    id_bandeira: uuid.UUID = None
    id_parcelamento: uuid.UUID = None
    nomeformadepagamento: str = None
    nomemeioeletronico: str = None
    nomebandeira: str = None
    nomeoperadora: str = None
    nomeconta: str = None
    valor: float = None
    numeroparcelas: int = None
    datafatura: datetime.datetime = None
    tipooperacao: int = None
    autorizacaocartao: str = None
    dataautorizacaocartao: datetime.datetime = None
    documentocartao: str = None
    irretido: float = None
    pisretido: float = None
    cofinsretido: float = None
    csllretido: float = None
    tipo: int = None
    lastupdate: datetime.datetime = None
    isdefault: bool = None
    cnpj_operadora: str = None
    id_contratocartao: uuid.UUID = None
    id_documentorateado: uuid.UUID = None
    inssretido: float = None
    issretido: float = None
    percentual: float = None
