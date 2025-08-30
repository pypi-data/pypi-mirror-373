
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.admissoespreliminares",
    pk_field="admissaopreliminar",
    default_order_fields=["cpf","dataadmissao","empresa"],
)
class AdmissoespreliminareEntity(EntityBase):
    admissaopreliminar: uuid.UUID = None
    tenant: int = None
    nome: str = None
    codigo: str = None
    cpf: str = None
    dataadmissao: datetime.datetime = None
    datanascimento: datetime.datetime = None
    empresa: uuid.UUID = None
    lastupdate: datetime.datetime = None
    trabalhador: uuid.UUID = None
    nivelcargo: uuid.UUID = None
    horario: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    origem: int = None
    salariofixo: float = None
    cargo: uuid.UUID = None
    created_at: datetime.datetime = None
    numero: int = None
    departamento: uuid.UUID = None
    created_by: dict = None
    updated_by: dict = None
    updated_at: datetime.datetime = None
    solicitante: uuid.UUID = None
    observacao: str = None
    solicitacao: uuid.UUID = None
