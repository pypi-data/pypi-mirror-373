
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.avisospreviostrabalhadores",
    pk_field="avisopreviotrabalhador",
    default_order_fields=["avisopreviotrabalhador"],
)
class AvisospreviostrabalhadoreEntity(EntityBase):
    avisopreviotrabalhador: uuid.UUID = None
    tenant: int = None
    dataconcessao: datetime.datetime = None
    dataprojetada: datetime.datetime = None
    cancelado: bool = None
    observacaoconcessao: str = None
    observacaocancelamento: str = None
    tipoconcessao: int = None
    tipocancelamento: int = None
    datacancelamento: datetime.datetime = None
    interrompido: bool = None
    trabalhador: uuid.UUID = None
    lastupdate: datetime.datetime = None
    created_by: dict = None
    created_at: datetime.datetime = None
    updated_by: dict = None
    updated_at: datetime.datetime = None
    situacao: int = None
