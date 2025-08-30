
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="crm.negociosoperacoes",
    pk_field="proposta_operacao",
    default_order_fields=["proposta_operacao"],
)
class NegociosoperacoEntity(EntityBase):
    proposta_operacao: uuid.UUID = None
    tenant: int = None
    id_grupoempresarial: uuid.UUID = None
    codigo: str = None
    descricao: str = None
    created_by: dict = None
    updated_by: dict = None
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None
