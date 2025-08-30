
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.dependentestrabalhadores",
    pk_field="dependentetrabalhador",
    default_order_fields=["codigo"],
)
class DependentestrabalhadoreEntity(EntityBase):
    dependentetrabalhador: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    datainclusao: datetime.datetime = None
    tipoparentesco: int = None
    impostorenda: bool = None
    salariofamilia: bool = None
    pensaoalimenticia: bool = None
    percentualpensaoalimenticia: float = None
    percentualpensaoalimenticiafgts: float = None
    cpf: str = None
    datanascimento: datetime.datetime = None
    ufnascimento: str = None
    cidadenascimento: str = None
    cartoriocertidao: str = None
    numeroregistrocertidao: str = None
    numerolivrocertidao: str = None
    numerofolhacertidao: str = None
    dataentregacertidao: datetime.datetime = None
    databaixacertidao: datetime.datetime = None
    tiporecebimento: int = None
    numerocontarecebimento: str = None
    numerocontadvrecebimento: str = None
    datavencimentodeclaracaoescolar: datetime.datetime = None
    datavencimentovacinacao: datetime.datetime = None
    sexo: int = None
    databaixaimpostorenda: datetime.datetime = None
    planosaude: bool = None
    agencia: uuid.UUID = None
    dependentetrabalhadorpensao: uuid.UUID = None
    eventopensaofolha: uuid.UUID = None
    eventopensaoferias: uuid.UUID = None
    eventopensaopplr: uuid.UUID = None
    eventopensao13: uuid.UUID = None
    trabalhador: uuid.UUID = None
    lastupdate: datetime.datetime = None
    incapacidadefisicamental: bool = None
    possuiatestadoparanaofrequentarescola: bool = None
