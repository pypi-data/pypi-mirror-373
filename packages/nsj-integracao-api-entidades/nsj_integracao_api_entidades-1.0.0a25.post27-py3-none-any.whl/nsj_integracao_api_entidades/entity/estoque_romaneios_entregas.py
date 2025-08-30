
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.romaneios_entregas",
    pk_field="romaneio_entrega",
    default_order_fields=["romaneio_entrega"],
)
class RomaneioEntregaEntity(EntityBase):
    romaneio_entrega: uuid.UUID = None
    tenant: int = None
    situacao: int = None
    observacoes: str = None
    receptor_nome: str = None
    receptor_documento: str = None
    url_assinatura: str = None
    geo_localizacao_checkin: dict = None
    geo_localizacao_checkout: dict = None
    checkin: datetime.datetime = None
    checkout: datetime.datetime = None
    lastupdate: datetime.datetime = None
    id_pessoa: uuid.UUID = None
    id_endereco: uuid.UUID = None
    romaneio: uuid.UUID = None
    ordem: int = None
