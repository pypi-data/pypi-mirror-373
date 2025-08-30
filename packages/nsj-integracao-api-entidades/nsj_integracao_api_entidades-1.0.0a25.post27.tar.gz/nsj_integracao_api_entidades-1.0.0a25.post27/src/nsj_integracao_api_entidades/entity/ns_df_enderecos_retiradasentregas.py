
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.df_enderecos_retiradasentregas",
    pk_field="df_endereco_retiradaentrega",
    default_order_fields=["df_endereco_retiradaentrega"],
)
class DfEnderecoRetiradasentregaEntity(EntityBase):
    df_endereco_retiradaentrega: uuid.UUID = None
    tenant: int = None
    estabelecimento: uuid.UUID = None
    id_pessoa: uuid.UUID = None
    tipopessoa: int = None
    pais: str = None
    ibge: str = None
    municipio: str = None
    retiradaentrega: int = None
    tipologradouro: str = None
    logradouro: str = None
    numero: str = None
    complemento: str = None
    cep: str = None
    bairro: str = None
    tipo: int = None
    ufexterior: str = None
    uf: str = None
    cidade: str = None
    referencia: str = None
    lastupdate: datetime.datetime = None
    geo_localizacao: dict = None
