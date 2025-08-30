
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.df_linhas",
    pk_field="df_linha",
    default_order_fields=["df_linha"],
)
class DfLinhaEntity(EntityBase):
    df_linha: uuid.UUID = None
    tenant: int = None
    df_linha_origem: uuid.UUID = None
    id_item: uuid.UUID = None
    id_cfop: uuid.UUID = None
    id_docfis: uuid.UUID = None
    id_docfis_origem: uuid.UUID = None
    produto: uuid.UUID = None
    tipolinha: int = None
    marcado: bool = None
    quantidadecomercial: float = None
    valorunitariocomercial: float = None
    valortotal: float = None
    valordesconto: float = None
    codigobarratributavel: str = None
    quantidadetributavel: float = None
    valorunitariotributacao: float = None
    valorfrete: float = None
    valorseguro: float = None
    valoroutrasdespesas: float = None
    extipi: float = None
    razaoconversao: float = None
    alteratotalnfe: bool = None
    ordem: int = None
    id_localdeestoque: uuid.UUID = None
    localdeestoquedescricao: str = None
    codigoitemfornecedor: str = None
    lastupdate: datetime.datetime = None
    id_unidade_comercial: uuid.UUID = None
    unidade_comercial: str = None
    id_unidade_tributada: uuid.UUID = None
    unidade_tributada: str = None
    valorbasemarkup: float = None
    formulabasemarkup: str = None
    observacao: str = None
    id_linha_docfis_origem: uuid.UUID = None
    ipienquadramento_id: uuid.UUID = None
    ipienquadramento_codigo: str = None
    ibptbase: float = None
    ibptaliquotafederal: float = None
    ibptaliquotaestadual: float = None
    ibptaliquotamunicipal: float = None
    ibptvalor: float = None
    id_di: uuid.UUID = None
    id_adicao: uuid.UUID = None
    id_adicao_item: uuid.UUID = None
    tipo_documento_origem: int = None
    di_numero: str = None
    di_registro: datetime.datetime = None
    di_adicao_numero: str = None
    cest: str = None
    id_comentario: uuid.UUID = None
    comentario: str = None
    id_composicao_instancia: uuid.UUID = None
    id_instancia: uuid.UUID = None
    situacaogerencial: int = None
    codigoitemdocfis: str = None
    descricaoitemdocfis: str = None
    custo: float = None
    dataprevisaoentrega: datetime.datetime = None
    fci: str = None
    numeropedidocompra: str = None
    itempedidocompra: str = None
    comb_cprodanp: str = None
    comb_ufcons: str = None
    peso_bruto: float = None
    peso_liquido: float = None
    especie: str = None
    marca: str = None
    aprovado: bool = None
    ratfrete: float = None
    ratseguro: float = None
    ratdespaduaneira: float = None
    ratdespacessorias: float = None
    ratsiscomex: float = None
    rataframm: float = None
    ratoutrasdesp: float = None
    custo_dif_cofins: float = None
    cfop_original: str = None
    codigo_beneficio_fiscal: str = None
    destinacao: int = None
    fabricante: str = None
    id_beneficio_fiscal: uuid.UUID = None
    id_cfop_previsto: uuid.UUID = None
    id_tabeladepreco: uuid.UUID = None
    idorigemlinha: uuid.UUID = None
    indicador_escala_relevante: int = None
    observacao_automatico: str = None
    observacao_manual: str = None
    volume_razao: float = None
    qtd_entregue_romaneio: float = None
    percentualcomissao: float = None
    valorcomissao: float = None
