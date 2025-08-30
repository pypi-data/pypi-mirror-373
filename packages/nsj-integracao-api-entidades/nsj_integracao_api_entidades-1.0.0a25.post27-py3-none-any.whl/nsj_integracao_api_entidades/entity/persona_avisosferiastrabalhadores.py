
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.avisosferiastrabalhadores",
    pk_field="avisoferiastrabalhador",
    default_order_fields=["avisoferiastrabalhador"],
)
class AvisosferiastrabalhadoreEntity(EntityBase):
    avisoferiastrabalhador: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    datainiciogozo: datetime.datetime = None
    datafimgozo: datetime.datetime = None
    datainicioperiodoaquisitivo: datetime.datetime = None
    datafimperiodoaquisitivo: datetime.datetime = None
    temabonopecuniario: bool = None
    observacao: str = None
    tipo: int = None
    trabalhador: uuid.UUID = None
    diasvendidos: int = None
    diasferiascoletivas: int = None
    lastupdate: datetime.datetime = None
    faltas: int = None
    adto13nasferias: bool = None
    consideraravisoparacalculovt: bool = None
    situacao: int = None
    origem: int = None
    created_at: datetime.datetime = None
    consideraravisoparacalculoben: bool = None
    solicitacao: uuid.UUID = None
