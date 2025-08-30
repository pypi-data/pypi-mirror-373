
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="servicos.operacoesordensservicos",
    pk_field="operacaoordemservico",
    default_order_fields=["operacaoordemservico"],
)
class OperacoesordensservicoEntity(EntityBase):
    operacaoordemservico: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    ativo: bool = None
    referenciaexterna: bool = None
    ordemservicoretorno: bool = None
    chamadotecnico: bool = None
    campodetalheinstancia: str = None
    horimetro: bool = None
    contrato: bool = None
    sintoma: bool = None
    causa: bool = None
    intervencao: bool = None
    orcamento: bool = None
    assinadopor: bool = None
    materiais: bool = None
    gerarequisicao: bool = None
    documentorequisicao_id: uuid.UUID = None
    geranotafiscal: bool = None
    documentonotafiscal_id: uuid.UUID = None
    estimativadehoras: bool = None
    saidaparacliente: bool = None
    chegadanocliente: bool = None
    saidadocliente: bool = None
    deslocamentoextra: bool = None
    veiculo: bool = None
    faturamento: bool = None
    faturaservico: bool = None
    faturavisita: bool = None
    tipoordemservico: uuid.UUID = None
    tipomanutencao: uuid.UUID = None
    lastupdate: datetime.datetime = None
    utilizadevolviveis: bool = None
    documentodevolvivelsaida_id: uuid.UUID = None
    participante_id: uuid.UUID = None
    tiporeajuste: int = None
    valorpercentualreajuste: float = None
    documentodevolvivelentrada_id: uuid.UUID = None
    gerarentradadevolvivel: bool = None
    sinaldocumentovalordevolvivel: int = None
    validade: str = None
    tempoaviso: str = None
    projeto: bool = None
    utiliza_tipo_manutencao: bool = None
    visita: bool = None
    encerrar_ao_executar_visita: bool = None
    utiliza_centrocusto_os: bool = None
    created_at: datetime.datetime = None
    created_by: dict = None
    updated_at: datetime.datetime = None
    updated_by: dict = None
    objetoservico: bool = None
    textoconformativo: str = None
    rateiopadrao: str = None
