
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.romaneios_notas_itens",
    pk_field="romaneio_nota_item",
    default_order_fields=["romaneio_nota_item"],
)
class RomaneioNotaItenEntity(EntityBase):
    romaneio_nota_item: uuid.UUID = None
    tenant: int = None
    id_docfis: uuid.UUID = None
    id_linha: uuid.UUID = None
    id_item: uuid.UUID = None
    id_romaneio_nota: uuid.UUID = None
    quantidade_enviada: float = None
    quantidade_entregue: float = None
    quantidade_naoentregue: float = None
    peso_bruto: float = None
    peso_liquido: float = None
    situacao: int = None
    data_nova_entrega: datetime.datetime = None
    motivo_retorno: str = None
    lastupdate: datetime.datetime = None
