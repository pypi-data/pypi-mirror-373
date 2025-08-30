
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.configuracoes",
    pk_field="configuracao",
    default_order_fields=["configuracao"],
)
class ConfiguracoEntity(EntityBase):
    configuracao: uuid.UUID = None
    tenant: int = None
    campo: int = None
    valor: str = None
    grupo: int = None
    sessao: int = None
    camadasistema: int = None
    maquina: str = None
    aplicacao: int = None
    ano: int = None
    ano_ini: int = None
    tipo_ini: int = None
    nome_ini: str = None
    grupo_ini: str = None
    campo_ini: str = None
    date_ini: datetime.datetime = None
    boolean_ini: bool = None
    integer_ini: int = None
    largeint_ini: int = None
    currency_ini: float = None
    float_ini: float = None
    guid_ini: uuid.UUID = None
    string_ini: str = None
    empresa: uuid.UUID = None
    chave_ini: uuid.UUID = None
    estabelecimento: uuid.UUID = None
    usuario: uuid.UUID = None
    identificacao: uuid.UUID = None
    lastupdate: datetime.datetime = None
