
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.movimentos",
    pk_field="movimento",
    default_order_fields=["movimento"],
)
class MovimentoEntity(EntityBase):
    movimento: uuid.UUID = None
    tenant: int = None
    ordem: int = None
    tipo: int = None
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
    invisivel: bool = None
    folha: bool = None
    adiantamentofolha: bool = None
    decimoterceiro: bool = None
    adiantamentodecimoterceiro: bool = None
    ferias: bool = None
    rescisao: bool = None
    pplr: bool = None
    folhacorretiva: bool = None
    empresa: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    departamento: uuid.UUID = None
    evento: uuid.UUID = None
    lotacaofuncionario: uuid.UUID = None
    lotacao: uuid.UUID = None
    sindicato: uuid.UUID = None
    complementodecimoterceiro: bool = None
    lastupdate: datetime.datetime = None
    trabalhador: uuid.UUID = None
    complementoferias: bool = None
    cargo: uuid.UUID = None
    lancamentoponto: uuid.UUID = None
    mesreferencia: int = None
    anoreferencia: int = None
    origem: int = None
    situacao: int = None
    apontamentotrabalhador: uuid.UUID = None
    updated_by: dict = None
    updated_at: datetime.datetime = None
    solicitacaorescisao: uuid.UUID = None
    solicitacaorescisaomeurh: uuid.UUID = None
    convocacaotrabalhador: uuid.UUID = None
    dependentetrabalhador: uuid.UUID = None
    instituicao: uuid.UUID = None
    medico: uuid.UUID = None
    referencia: str = None
    desabilitado: bool = None
