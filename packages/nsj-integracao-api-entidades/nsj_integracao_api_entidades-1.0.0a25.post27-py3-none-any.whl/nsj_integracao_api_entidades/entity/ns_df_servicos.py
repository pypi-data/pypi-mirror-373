
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.df_servicos",
    pk_field="id",
    default_order_fields=["id"],
)
class DfServicoEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    id_ano: int = None
    cfop: str = None
    descricao: str = None
    incideirrf: bool = None
    incideinss: bool = None
    tipo: int = None
    rapis: int = None
    remas: int = None
    deducao: float = None
    unitario: float = None
    quantidade: float = None
    valordesc: float = None
    valor: float = None
    vlrservicos15: float = None
    vlrservicos20: float = None
    vlrservicos25: float = None
    valorinssadicional: float = None
    valorinssnaoretido: float = None
    ordem: int = None
    id_docfis: uuid.UUID = None
    id_notadeducao: uuid.UUID = None
    id_obra: uuid.UUID = None
    id_servico: uuid.UUID = None
    vencimento: datetime.datetime = None
    inicioreferencia: datetime.datetime = None
    fimreferencia: datetime.datetime = None
    diasvencimento: int = None
    titulo: uuid.UUID = None
    itemcontrato: uuid.UUID = None
    pessoa: uuid.UUID = None
    contrato: uuid.UUID = None
    processamentocontrato: uuid.UUID = None
    tipocobranca: int = None
    lastupdate: datetime.datetime = None
    parcela: int = None
    totalparcelas: int = None
    objetoservico_id: uuid.UUID = None
    tiposervico: int = None
    base_iss: float = None
    valor_iss: float = None
    base_inss: float = None
    valor_inss: float = None
    base_irrf: float = None
    valor_irrf: float = None
    base_cofins: float = None
    valor_cofins: float = None
    base_pis: float = None
    valor_pis: float = None
    base_csll: float = None
    valor_csll: float = None
    retem_iss: bool = None
    retem_inss: bool = None
    retem_irrf: bool = None
    retem_cofins: bool = None
    retem_pis: bool = None
    retem_csll: bool = None
    emissao: datetime.datetime = None
    valorcontabilpis: float = None
    valorcontabilcofins: float = None
    id_origem: uuid.UUID = None
    desconto: float = None
    datareajusteitemcontrato: datetime.datetime = None
    valortotalocorrenciasitemcontrato: float = None
    valordebitopis: float = None
    valordebitocofins: float = None
