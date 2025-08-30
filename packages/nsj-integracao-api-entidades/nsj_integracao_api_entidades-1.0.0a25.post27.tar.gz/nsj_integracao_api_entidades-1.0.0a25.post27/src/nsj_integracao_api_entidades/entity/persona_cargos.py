
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.cargos",
    pk_field="cargo",
    default_order_fields=["codigo"],
)
class CargoEntity(EntityBase):
    cargo: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    descricao: str = None
    cbo: str = None
    experiencia: str = None
    grauinstrucao: str = None
    maiorsalmercado: float = None
    menorsalmercado: float = None
    requisitos: str = None
    diasexperienciacontrato: int = None
    diasprorrogacaocontrato: int = None
    empresa: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    departamento: uuid.UUID = None
    horario: uuid.UUID = None
    lotacao: uuid.UUID = None
    sindicato: uuid.UUID = None
    lastupdate: datetime.datetime = None
    pontuacao: float = None
    contagemespecial: int = None
    dedicacaoexclusiva: bool = None
    dataleicargo: datetime.datetime = None
    numeroleicargo: str = None
    situacaoleicargo: int = None
    pisominimo: float = None
    cargopublico: bool = None
    acumulacaocargos: int = None
    desabilitado: bool = None
    importacao_hash: str = None
    condicaoambientetrabalho: uuid.UUID = None
