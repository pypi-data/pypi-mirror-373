
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.enderecos",
    pk_field="endereco",
    default_order_fields=["endereco"],
)
class EnderecoEntity(EntityBase):
    endereco: uuid.UUID = None
    tenant: int = None
    tipologradouro: str = None
    logradouro: str = None
    numero: str = None
    complemento: str = None
    cep: str = None
    bairro: str = None
    tipoendereco: int = None
    ufexterior: str = None
    enderecopadrao: int = None
    uf: str = None
    pais: str = None
    ibge: str = None
    cidade: str = None
    referencia: str = None
    id_pessoa: uuid.UUID = None
    lastupdate: datetime.datetime = None
