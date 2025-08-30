
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="servicos.servicos",
    pk_field="id",
    default_order_fields=["servico"],
)
class ServicoEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    servico: str = None
    descricao: str = None
    codigosped: str = None
    atividade: str = None
    lcp: str = None
    codserv: str = None
    nbs: str = None
    codigocontabil: str = None
    contrapartida: str = None
    centrocusto: str = None
    cpsrb: str = None
    incideirrf: bool = None
    incideinss: bool = None
    tipoiss: int = None
    regimepc: int = None
    tributacaopc: int = None
    bloqueado: int = None
    tipoatividade: int = None
    sped_outro: str = None
    sped_detalhe: str = None
    tipo_esocial: str = None
    valor: float = None
    unidade: uuid.UUID = None
    insspercentualincidencia: float = None
    descontocobranca: int = None
    anotacao: str = None
    incidecomissao: int = None
    detalhes: bytes = None
    aliquotainss: float = None
    classificacaofinanceira: uuid.UUID = None
    id_grupo: uuid.UUID = None
    cfop: uuid.UUID = None
    vinculado: uuid.UUID = None
    tiposervico: uuid.UUID = None
    tributacaoservico: uuid.UUID = None
    geracobranca: int = None
    tipoperiodocobranca: int = None
    quantidadeperiodocobranca: int = None
    lastupdate: datetime.datetime = None
    visivel: bool = None
    id_grupodeservico: uuid.UUID = None
    sped_pc: uuid.UUID = None
    valor_contrato: float = None
    pode_alterar_valor_contrato_na_proposta: bool = None
    id_conjunto: uuid.UUID = None
