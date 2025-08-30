
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.centroscustos",
    pk_field="centrocusto",
    default_order_fields=["codigo"],
)
class CentroscustoEntity(EntityBase):
    centrocusto: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    codigocontabil: str = None
    resumo: str = None
    situacao: int = None
    paiid: uuid.UUID = None
    grupoempresarial: uuid.UUID = None
    lastupdate: datetime.datetime = None
    natureza: int = None
    resumoexplicativo: str = None
    importacao_hash: str = None
    usuario_responsavel: uuid.UUID = None
