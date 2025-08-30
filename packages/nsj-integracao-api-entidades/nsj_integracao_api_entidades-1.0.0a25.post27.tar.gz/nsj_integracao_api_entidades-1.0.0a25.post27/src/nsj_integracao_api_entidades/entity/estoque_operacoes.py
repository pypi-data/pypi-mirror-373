
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.operacoes",
    pk_field="operacao",
    default_order_fields=["codigo"],
)
class OperacoEntity(EntityBase):
    operacao: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    sinal: int = None
    afetacustodosprodutos: bool = None
    grupodeoperacao: uuid.UUID = None
    usatabeladepreco: bool = None
    associardocumento: bool = None
    id_documento: uuid.UUID = None
    associarproduto: bool = None
    finalidade: int = None
    ativa: bool = None
    tipooperacao: int = None
    requisicao: bool = None
    simularimpostos: bool = None
    simularfrete: bool = None
    objetivodaoperacao: int = None
    emitirnfe: bool = None
    nropedidoexterno: bool = None
    gerafinanceiro: bool = None
    formagerafinanceiro: int = None
    cfoppadrao_estadual: uuid.UUID = None
    cfoppadrao_interestadual: uuid.UUID = None
    cfoppadrao_exterior: uuid.UUID = None
    modalidadefrete: int = None
    id_markup: uuid.UUID = None
    gerar_ra: bool = None
    usamodulocompras: bool = None
    processarautomaticamente: bool = None
    layoutdanfe: int = None
    layoutvisualizacao: int = None
    semfatura_semtitulo: bool = None
    exibeqtdassociadarestante: bool = None
    modoexibicaoproduto: int = None
    exibenumseriedescproddanfe: bool = None
    aprovaitens: bool = None
    parcelabaseadaemissaodoc: bool = None
    comportamentooperacao: int = None
    idoperacaopadraofaturamento: uuid.UUID = None
    idoperacaopadraoremessa: uuid.UUID = None
    cfoppadrao_interestadualst: uuid.UUID = None
    cfoppadrao_estadualst: uuid.UUID = None
    associacaoobrigatoriadocumentos: bool = None
    diretoriocopiaxmlemitido: str = None
    lastupdate: datetime.datetime = None
    usatabeladeprecoporitem: bool = None
    codigonumericochaveacesso: str = None
    id_grupo_empresarial: uuid.UUID = None
    id_empresa: uuid.UUID = None
    gerar_ordem_producao: bool = None
    usaultimoprecopraticado: bool = None
    calcular_ibpt: bool = None
    exigirchavereferencia: bool = None
    validarchavereferencia: bool = None
    textoobsnumeroexterno: str = None
    naturezabehavior: float = None
    natureza: str = None
    permitireditarnatureza: bool = None
    interno: bool = None
    situacaonumerosdeseries: int = None
    gerarnumeroautomaticamentepedido: bool = None
    diversos_participantes: bool = None
    controla_triangulacao: bool = None
    faturarapenasimpostos: bool = None
    geraprojetopcp: bool = None
    habilitarrateioentrega: bool = None
    faturartotaldocumento: bool = None
    permitir_grupo_inventario_mercadoria: bool = None
    permitir_grupo_inventario_materia_prima: bool = None
    permitir_grupo_inventario_produto_intermediario: bool = None
    permitir_grupo_inventario_material_embalagem: bool = None
    permitir_grupo_inventario_prod_acabado_manufaturado: bool = None
    permitir_grupo_inventario_prod_fase_fabricacao: bool = None
    permitir_grupo_inventario_bens_terceiros: bool = None
    permitir_grupo_inventario_ativo_permanente: bool = None
    permitir_grupo_inventario_uso_e_consumo: bool = None
    permitir_grupo_inventario_outros_sem_inv: bool = None
    cfoppadrao_estadual_producao: uuid.UUID = None
    cfoppadrao_estadualst_producao: uuid.UUID = None
    cfoppadrao_interestadual_producao: uuid.UUID = None
    cfoppadrao_interestadualst_producao: uuid.UUID = None
    validarfaixascomissao: bool = None
