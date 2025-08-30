
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.romaneios_notas",
    pk_field="romaneio_nota",
    default_order_fields=["romaneio_nota"],
)
class RomaneioNotaEntity(EntityBase):
    romaneio_nota: uuid.UUID = None
    tenant: int = None
    id_romaneio: uuid.UUID = None
    id_pessoa: uuid.UUID = None
    id_endereco: uuid.UUID = None
    id_docfis: uuid.UUID = None
    valor: float = None
    peso_bruto: float = None
    peso_liquido: float = None
    observacaoes_entrega_parcial: str = None
    id_romaneio_entrega: uuid.UUID = None
    lastupdate: datetime.datetime = None
