
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.locaisdeestoques",
    pk_field="localdeestoque",
    default_order_fields=["codigo"],
)
class LocaisdeestoqueEntity(EntityBase):
    localdeestoque: uuid.UUID = None
    tenant: int = None
    estabelecimento: uuid.UUID = None
    codigo: str = None
    nome: str = None
    tipo: int = None
    tipologradouro: str = None
    logradouro: str = None
    numero: str = None
    complemento: str = None
    cep: str = None
    bairro: str = None
    referencia: str = None
    ibge: str = None
    cidade: str = None
    uf: str = None
    cnpj: str = None
    enderecodiferente: bool = None
    lastupdate: datetime.datetime = None
    expedicao: bool = None
    aplicarlocalestoquepoderterceiros: bool = None
    desabilitado: bool = None
    localdeestoquedeterceiro: bool = None
    tipoterceiro: int = None
    id_terceiro: uuid.UUID = None
    bloqueado: bool = None
