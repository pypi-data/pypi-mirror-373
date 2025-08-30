
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ConfiguracoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='configuracao',
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
    campo: int = DTOField()
    valor: str = DTOField()
    grupo: int = DTOField()
    sessao: int = DTOField()
    camadasistema: int = DTOField()
    maquina: str = DTOField()
    aplicacao: int = DTOField()
    ano: int = DTOField()
    ano_ini: int = DTOField()
    tipo_ini: int = DTOField()
    nome_ini: str = DTOField()
    grupo_ini: str = DTOField()
    campo_ini: str = DTOField()
    date_ini: datetime.datetime = DTOField()
    boolean_ini: bool = DTOField()
    integer_ini: int = DTOField()
    largeint_ini: int = DTOField()
    currency_ini: float = DTOField()
    float_ini: float = DTOField()
    guid_ini: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    string_ini: str = DTOField()
    empresa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    chave_ini: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    estabelecimento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    usuario: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    identificacao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()

