
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.itens",
    pk_field="id",
    default_order_fields=["item"],
)
class ItenEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    reduzido: str = None
    especificacao: str = None
    codigobarra: str = None
    gtin: str = None
    ggrem: str = None
    tipi: str = None
    dacon: str = None
    sped_pc: str = None
    anp_sped: str = None
    anp_scanc: str = None
    codigorefri: str = None
    classeserv: str = None
    grupo: str = None
    localizacao: str = None
    cst_icms_a: str = None
    cst_icms_b: str = None
    csosn: str = None
    especie: str = None
    marca: str = None
    marcacomercial: str = None
    especievolume: str = None
    marcavolume: str = None
    trib_dia_am: str = None
    tipocalctrib: int = None
    tipopis: int = None
    tipocofins: int = None
    tipomedicamento: int = None
    tabelarefri: int = None
    grupoinventario: int = None
    tiposubstituicao: int = None
    decimaisinventario: int = None
    tipoipi: int = None
    tipomargem: int = None
    ultimacompra: datetime.datetime = None
    bloqueado: bool = None
    imuneicms: bool = None
    icms: float = None
    ipi: float = None
    ii: float = None
    pis: float = None
    cofins: float = None
    reducaoicms: float = None
    reducaoipi: float = None
    reducaost: float = None
    lucrosubstituicao: float = None
    diferimentoicms: float = None
    ipiporquantidade: float = None
    quantunitrib: float = None
    margemvenda: float = None
    precovenda: float = None
    precocusto: float = None
    precomediocusto: float = None
    precomedioanterior: float = None
    precomaxconsumidor: float = None
    pesobruto: float = None
    pesoliquido: float = None
    capacidade: float = None
    basesubstituicao: float = None
    baseicmsminima: float = None
    fatordia_am: float = None
    item: str = None
    id_prodacabado: uuid.UUID = None
    unidade: uuid.UUID = None
    unidadetrib: uuid.UUID = None
    id_grupo: uuid.UUID = None
    id_fabricante: uuid.UUID = None
    id_ultimofornecedor: uuid.UUID = None
    produto: uuid.UUID = None
    gradetemplate: uuid.UUID = None
    consignado: int = None
    estoqueminimo: float = None
    estoquemaximo: float = None
    subapuracao: int = None
    observacao: str = None
    invisivel: bool = None
    tipo_utilizacao: int = None
    convenio_115_03: bool = None
    conta_credito_inventario: str = None
    conta_debito_inventario: str = None
    empresacontroller: str = None
    itemcompra: uuid.UUID = None
    lastupdate: datetime.datetime = None
    id_fornecedor_principal: uuid.UUID = None
    lead_time: int = None
    estoque_de_seguranca: float = None
    multiplo_de_compra: int = None
    cest: str = None
    gtin_trib: str = None
