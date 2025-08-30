
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.eventos",
    pk_field="evento",
    default_order_fields=["codigo"],
)
class EventoEntity(EntityBase):
    evento: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    tipovalor: int = None
    unidade: int = None
    percentual: float = None
    incideinss: bool = None
    incideirrf: bool = None
    incidefgts: bool = None
    categoria: int = None
    totalizarais: bool = None
    totalizainforme: bool = None
    acumulahoraextra: bool = None
    valorminimo: float = None
    valormaximo: float = None
    basefaixa: int = None
    incidepis: bool = None
    incideencargos: bool = None
    pagobancohoras: bool = None
    fazproporcaopiso: bool = None
    valorpiso: float = None
    codigohomolognet: str = None
    tipomedia: int = None
    valorintegralbasevh: bool = None
    incidedsr: bool = None
    periodoanuenio: int = None
    qtdemaximaanuenio: int = None
    rubricaesocial: str = None
    incidesindical: bool = None
    somamediaferias: bool = None
    somamedia13: bool = None
    somamediarescisao: bool = None
    somamaiorremuneracao: bool = None
    tipocalculo: int = None
    acumulavalordia: bool = None
    valorintegralbasevalordia: bool = None
    incidesalariofamilia: bool = None
    fazproporcaocalculo: bool = None
    comparacomtarifas: bool = None
    valorintegralbasesindical: bool = None
    valorintegralbasesalariofamilia: bool = None
    incidepensaoalimenticia: bool = None
    somamediamaternidade: bool = None
    empresa: uuid.UUID = None
    eventofaixa: uuid.UUID = None
    faixa: uuid.UUID = None
    instituicao: uuid.UUID = None
    tipoformula: int = None
    formulabasicacondicao: str = None
    formulabasicavalor: str = None
    formulabasicareferencia: str = None
    formulaavancada: str = None
    lastupdate: datetime.datetime = None
    somentecompoemaiorremuneracao: bool = None
    valorconteudolimitealerta: float = None
    valorconteudolimiteerro: float = None
    explicacao: str = None
    informativa: bool = None
    calcularpelopercentualdoreajustesindical: bool = None
    somarbasevalorhoramaiorremuneracaorescisao: bool = None
    considerarsomentevalordocalculoatualemformulas: bool = None
    ignorarnocalculosindical: bool = None
    desabilitado: bool = None
    id_conjunto: uuid.UUID = None
