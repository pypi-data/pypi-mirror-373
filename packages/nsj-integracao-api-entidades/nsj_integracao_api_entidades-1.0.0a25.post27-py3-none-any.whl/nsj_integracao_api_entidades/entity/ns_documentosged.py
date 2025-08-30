
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.documentosged",
    pk_field="documentoged",
    default_order_fields=["nome"],
)
class DocumentosgedEntity(EntityBase):
    documentoged: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    nome: str = None
    uuidarquivo: str = None
    cpfcnpj: str = None
    nomefantasiaempresa: str = None
    documento: bytes = None
    lastupdate: datetime.datetime = None
    created_at: datetime.datetime = None
    mimetype: str = None
    created_by: dict = None
    id_erp: int = None
    tamanho: int = None
    uploadid: uuid.UUID = None
    hash: str = None
