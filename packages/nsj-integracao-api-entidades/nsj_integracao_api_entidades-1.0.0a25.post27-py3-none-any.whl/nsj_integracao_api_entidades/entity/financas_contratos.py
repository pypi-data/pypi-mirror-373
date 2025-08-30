
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.contratos",
    pk_field="contrato",
    default_order_fields=["codigo"],
)
class ContratoEntity(EntityBase):
    contrato: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    tipocontrato: int = None
    definicaocontratante: str = None
    definicaobeneficiario: str = None
    datainicial: datetime.datetime = None
    administradorlegal: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    participante: uuid.UUID = None
    fiador: uuid.UUID = None
    conta: uuid.UUID = None
    bempatrimonial: uuid.UUID = None
    qtddiasdesconto: int = None
    qtddiasmulta: int = None
    qtddiasjurosdiarios: int = None
    percentualcomissao: float = None
    valorcomissao: float = None
    percentualretencaoimposto: float = None
    valorretencaoimposto: float = None
    familia: uuid.UUID = None
    processado: int = None
    cancelado: bool = None
    datahoracancelamento: datetime.datetime = None
    origem: int = None
    emitirnotafiscal: bool = None
    tipocontabilizacao: int = None
    formula_id: uuid.UUID = None
    lastupdate: datetime.datetime = None
    unidadenatureza: int = None
    unidadeintervalonatureza: int = None
    quantidadeintervalonatureza: int = None
    tipovencimento: int = None
    diavencimento: int = None
    adicaomesesvencimento: int = None
    tipocobranca: int = None
    qtddiasparainicio: int = None
    qtddiasparafim: int = None
    qtdmesesparareajuste: int = None
    percentualdesconto: float = None
    percentualmulta: float = None
    percentualjurosdiarios: float = None
    indice: uuid.UUID = None
    dataproximoreajuste: datetime.datetime = None
    considerardatainicio: bool = None
    parcelainicial: int = None
    parcelafinal: int = None
    parcelaatual: int = None
    participantecomissao: uuid.UUID = None
    numero: int = None
    processaperiodoanterior: bool = None
    debitoautomatico: bool = None
    perfilcontrato: str = None
    classfinanceiracomissao: uuid.UUID = None
    tipoemissao: int = None
    qtddiasemissaotitulo: int = None
    id_tipo_outras_recdesp: uuid.UUID = None
    gerartitulos: bool = None
    diaparafaturamento: int = None
    id_formapagamento: uuid.UUID = None
    diainicioreferencia: int = None
    encerramentoprevisaofinanceira: int = None
    datahoraencerramento: datetime.datetime = None
    pessoamunicipio: uuid.UUID = None
    id_documento_vinculado: uuid.UUID = None
    observacao: str = None
    templateordemservico: uuid.UUID = None
    grupofaturamento: int = None
    datacontrolesistema: datetime.datetime = None
    previsaofinanceirapersona: bool = None
    tipoordempagamentopersona: int = None
    reajusteautomatico: bool = None
    id_proposta: uuid.UUID = None
    created_at: datetime.datetime = None
    created_by: dict = None
    anteciparvencimentodiautil: bool = None
    contratoemrenegociacao: bool = None
    layoutcobranca: uuid.UUID = None
    detentor_id: uuid.UUID = None
    titulosprovisorios: bool = None
    usarindicevariavel: bool = None
    pisretido: float = None
    cofinsretido: float = None
    csllretido: float = None
    irretido: float = None
    issretido: float = None
    inssretido: float = None
    outrasretencoes: float = None
    descricaooutrasretencoes: str = None
    id_tipo_outras_recdesplocacao: uuid.UUID = None
    contabilizar: bool = None
    contabilizar_baixa: bool = None
    projeto: uuid.UUID = None
    competencia_vencimento: bool = None
    observacao_titulo: str = None
    template_observacao: uuid.UUID = None
    numerorps: int = None
    descontoglobalitensnaofaturados: float = None
