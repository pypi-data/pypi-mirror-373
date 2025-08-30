
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.calculostrabalhadores",
    pk_field="calculotrabalhador",
    default_order_fields=["calculotrabalhador"],
)
class CalculostrabalhadoreEntity(EntityBase):
    calculotrabalhador: uuid.UUID = None
    tenant: int = None
    ordem: int = None
    ano: int = None
    mes: int = None
    semana: int = None
    datapagamento: datetime.datetime = None
    referencia: str = None
    valor: float = None
    invisivel: bool = None
    anogerador: int = None
    mesgerador: int = None
    semanageradora: int = None
    calculogerador: str = None
    tipo: str = None
    tipoperiodo: int = None
    mesperiodo: int = None
    semanaperiodo: int = None
    datainicialperiodo: datetime.datetime = None
    datafinalperiodo: datetime.datetime = None
    mesinicialperiodo: int = None
    mesfinalperiodo: int = None
    anoinicialperiodo: int = None
    anofinalperiodo: int = None
    calculanofim: bool = None
    conteudo: float = None
    tipoprocedencia: int = None
    tipomovimento: int = None
    valorbruto: float = None
    estabelecimentomovimento: uuid.UUID = None
    departamentomovimento: uuid.UUID = None
    dependentetrabalhador: uuid.UUID = None
    evento: uuid.UUID = None
    trabalhador: uuid.UUID = None
    lotacao: uuid.UUID = None
    sindicatomovimento: uuid.UUID = None
    avisoferiastrabalhador: uuid.UUID = None
    avisopreviotrabalhador: uuid.UUID = None
    afastamentotrabalhador: uuid.UUID = None
    sindicato: uuid.UUID = None
    lastupdate: datetime.datetime = None
    cargomovimento: uuid.UUID = None
    origemcalculo: int = None
    reajustesindicato: uuid.UUID = None
    calculotrabalhadororigem: uuid.UUID = None
    lancamentoponto: uuid.UUID = None
    origem: int = None
    apontamentotrabalhador: uuid.UUID = None
    solicitacaorescisao: uuid.UUID = None
    solicitacaorescisaomeurh: uuid.UUID = None
    mesreferencia: int = None
    anoreferencia: int = None
