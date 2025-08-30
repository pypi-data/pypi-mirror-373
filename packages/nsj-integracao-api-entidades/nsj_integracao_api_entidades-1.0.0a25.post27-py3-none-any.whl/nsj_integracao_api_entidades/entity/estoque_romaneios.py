
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.romaneios",
    pk_field="romaneio",
    default_order_fields=["numero"],
)
class RomaneioEntity(EntityBase):
    romaneio: uuid.UUID = None
    tenant: int = None
    id_rota: uuid.UUID = None
    id_veiculo: uuid.UUID = None
    id_motorista: uuid.UUID = None
    id_empresa: uuid.UUID = None
    id_usuario_criacao: uuid.UUID = None
    numero: str = None
    situacao: int = None
    data_envio: datetime.datetime = None
    data_entrega: datetime.datetime = None
    data_retorno: datetime.datetime = None
    observacao: str = None
    peso_bruto: float = None
    peso_liquido: float = None
    volumes: float = None
    valor: float = None
    id_entregador: uuid.UUID = None
    geo_localizacao_checkin: dict = None
    geo_localizacao_checkout: dict = None
    checkin: datetime.datetime = None
    checkout: datetime.datetime = None
    data_criacao: datetime.datetime = None
    lastupdate: datetime.datetime = None
