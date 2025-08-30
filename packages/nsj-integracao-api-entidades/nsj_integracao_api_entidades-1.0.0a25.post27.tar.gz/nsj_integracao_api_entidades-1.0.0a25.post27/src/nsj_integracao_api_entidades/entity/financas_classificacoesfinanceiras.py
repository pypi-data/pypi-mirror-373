
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="financas.classificacoesfinanceiras",
    pk_field="classificacaofinanceira",
    default_order_fields=["codigo"],
)
class ClassificacoesfinanceiraEntity(EntityBase):
    classificacaofinanceira: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    codigocontabil: str = None
    resumo: str = None
    situacao: int = None
    natureza: int = None
    paiid: uuid.UUID = None
    grupoempresarial: uuid.UUID = None
    lastupdate: datetime.datetime = None
    resumoexplicativo: str = None
    importacao_hash: str = None
    iniciogrupo: bool = None
    apenasagrupador: bool = None
