
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class DfEnderecoRetiradasentregaDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='df_endereco_retiradaentrega',
      resume=True,
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tenant: int = DTOField(
      partition_data=tenant_is_partition_data,
      resume=True,
      not_null=True,)
    estabelecimento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_pessoa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tipopessoa: int = DTOField()
    pais: str = DTOField()
    ibge: str = DTOField()
    municipio: str = DTOField()
    retiradaentrega: int = DTOField(
      not_null=True,)
    tipologradouro: str = DTOField()
    logradouro: str = DTOField()
    numero: str = DTOField()
    complemento: str = DTOField()
    cep: str = DTOField()
    bairro: str = DTOField()
    tipo: int = DTOField()
    ufexterior: str = DTOField()
    uf: str = DTOField()
    cidade: str = DTOField()
    referencia: str = DTOField()
    lastupdate: datetime.datetime = DTOField()
    geo_localizacao: dict = DTOField()

