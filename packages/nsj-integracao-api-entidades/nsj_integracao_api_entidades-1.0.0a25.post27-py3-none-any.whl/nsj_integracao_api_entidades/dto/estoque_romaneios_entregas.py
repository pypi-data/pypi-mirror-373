
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class RomaneioEntregaDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='romaneio_entrega',
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
    situacao: int = DTOField(
      not_null=True,)
    observacoes: str = DTOField()
    receptor_nome: str = DTOField()
    receptor_documento: str = DTOField()
    url_assinatura: str = DTOField()
    geo_localizacao_checkin: dict = DTOField()
    geo_localizacao_checkout: dict = DTOField()
    checkin: datetime.datetime = DTOField()
    checkout: datetime.datetime = DTOField()
    lastupdate: datetime.datetime = DTOField()
    id_pessoa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_endereco: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    romaneio: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    ordem: int = DTOField()

