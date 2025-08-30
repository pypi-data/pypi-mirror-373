
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.configuracaoacessoapi",
    pk_field="id",
    default_order_fields=["username"],
)
class ConfiguracaoacessoapiEntity(EntityBase):
    id: uuid.UUID = None
    tenant: int = None
    idusuario: uuid.UUID = None
    username: str = None
    password: str = None
    acesstoken: str = None
    refreshtoken: str = None
    proxy: str = None
    codigo_organizacao: str = None
    nome_organizacao: str = None
    temposessao: str = None
    configuracaovalida: bool = None
    lastupdate: datetime.datetime = None
    datahoraacesstoken: datetime.datetime = None
