
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.itenscontratos",
    pk_field="itemcontrato",
    default_order_fields=["itemcontrato"],
)
class ItenscontratoEntity(EntityBase):
    itemcontrato: uuid.UUID = None
    tenant: int = None
    contrato: uuid.UUID = None
    servico: uuid.UUID = None
    codigo: str = None
    observacao: str = None
    valor: float = None
    rateio: uuid.UUID = None
    processado: bool = None
    cancelado: bool = None
    datahoracancelamento: datetime.datetime = None
    quantidade: float = None
    objetoservicoitem: uuid.UUID = None
    descontosnopedido: float = None
    unidadenatureza: int = None
    unidadeintervalonatureza: int = None
    quantidadeintervalonatureza: int = None
    tipovencimento: int = None
    diavencimento: int = None
    adicaomesesvencimento: int = None
    qtddiasparainicio: int = None
    qtddiasparafim: int = None
    qtdmesesparareajuste: int = None
    percentualdesconto: float = None
    percentualmulta: float = None
    percentualjurosdiarios: float = None
    tipocobranca: int = None
    ultimadataprocessamento: datetime.datetime = None
    ultimadataprocessamentotemp: datetime.datetime = None
    recorrente: bool = None
    indice: uuid.UUID = None
    dataproximoreajuste: datetime.datetime = None
    diaultimadataprocessamento: int = None
    considerardatainicio: bool = None
    lastupdate: datetime.datetime = None
    recorrenciapropria: bool = None
    parcelainicial: int = None
    parcelafinal: int = None
    parcelaatual: int = None
    possuicomissao: bool = None
    retemimposto: bool = None
    tipovalor: int = None
    objetoservico_id: uuid.UUID = None
    processaperiodoanterior: bool = None
    dataproximaprevisao: datetime.datetime = None
    dataproximaprevisaosugerida: datetime.datetime = None
    tipoemissao: int = None
    qtddiasemissaotitulo: int = None
    usadiscriminacao: bool = None
    qtdtitulosagerar: int = None
    qtdtitulosgerados: int = None
    diaparafaturamento: int = None
    id_item_faturamento: uuid.UUID = None
    codigoitem: str = None
    grupofaturamento: int = None
    reajusteautomatico: bool = None
    created_at: datetime.datetime = None
    created_by: dict = None
    tiposuspensao: int = None
    tipocomissao: int = None
    itemcontratoorigem: uuid.UUID = None
    transferido: bool = None
    datafaturamento: datetime.datetime = None
    numerodiasparavencimento: int = None
    previsaovencimento: datetime.datetime = None
    evento: bool = None
    usarindicevariavel: bool = None
    motivocancelamento: uuid.UUID = None
    tipocancelamento: int = None
    origemnaorecorrente: int = None
    situacaofaturamento: int = None
