
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.produtos",
    pk_field="produto",
    default_order_fields=["codigo"],
)
class ProdutoEntity(EntityBase):
    produto: uuid.UUID = None
    tenant: int = None
    id_grupo: uuid.UUID = None
    codigo: str = None
    especificacao: str = None
    tipoproduto: int = None
    bloqueado: bool = None
    foto: bytes = None
    origemmercadoria: int = None
    codigodebarras: str = None
    codigogtin: str = None
    volume_marca: str = None
    dnf_dif: str = None
    volume_pesobruto: float = None
    volume_pesoliquido: float = None
    grupodeinventario: int = None
    capacidadevolume: float = None
    estoqueminimo: float = None
    estoquemaximo: float = None
    grade: uuid.UUID = None
    controlanumerodeserie: bool = None
    controlalote: bool = None
    unidadedemedida: uuid.UUID = None
    tipodemedicamento: int = None
    tipodemedicamento_ggrem: str = None
    tipodemedicamento_maxaoconsumidor: float = None
    codigoanpdecombustivel: str = None
    bebidas_tabeladeincidencia: int = None
    bebidas_grupo: str = None
    bebidas_marca: str = None
    energia_comunicacao_telecomunicacao_st_icms: str = None
    id_fabricante: uuid.UUID = None
    tipi: str = None
    familia: uuid.UUID = None
    consignado: int = None
    figuratributaria: uuid.UUID = None
    precovenda: float = None
    volume_especie: str = None
    autovolumedocfis: bool = None
    categoriadeproduto: uuid.UUID = None
    observacao: str = None
    observacao_naofiscal: str = None
    invisivel: bool = None
    codigo_antigo: str = None
    especificacaotecnica: str = None
    estoquereposicao: float = None
    cest: str = None
    tipo: int = None
    epi_certificado_aprovacao: str = None
    epi_periodicidade: int = None
    epi_tipo_uso: str = None
    controlaativos: bool = None
    codigo_fabricante: str = None
    observacao_etiqueta: str = None
    tipo_periodo_validade: int = None
    periodo_validade: int = None
    etiquetalayoutpadrao: uuid.UUID = None
    lastupdate: datetime.datetime = None
    setores: str = None
    descontomaximo: float = None
    percentualcomissao: float = None
    classificacaofinanceiracompra: uuid.UUID = None
    classificacaofinanceiravenda: uuid.UUID = None
    id_fornecedor_principal: uuid.UUID = None
    lead_time: int = None
    estoque_de_seguranca: float = None
    multiplo_de_compra: int = None
    valorultimacompra: float = None
    custoultimacompra: float = None
    margemlucro: float = None
    markup: uuid.UUID = None
    unidadetributada: str = None
    razaounidade: float = None
    importacao_hash: str = None
    gtin_trib: str = None
    indicador_escala_relevante: int = None
    enviarlote: bool = None
    tipodemedicamento_codigoanvisa: str = None
    markupprecovenda: uuid.UUID = None
    centrocustovenda: uuid.UUID = None
    volume_razao: float = None
    id_codigobeneficio: uuid.UUID = None
    codigobeneficio: str = None
    id_conjunto: uuid.UUID = None
    precosugeridorevenda: float = None
    tipolote: int = None
    validadelote: int = None
    quantidadelote: int = None
    codigolote: int = None
    item_seguranca: bool = None
    planodeinspecao: uuid.UUID = None
    classificacaofragilidade: uuid.UUID = None
