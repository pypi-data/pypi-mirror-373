
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class RomaneioDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='romaneio',
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
    id_rota: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_veiculo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_motorista: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_empresa: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_usuario_criacao: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    numero: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    situacao: int = DTOField(
      not_null=True,)
    data_envio: datetime.datetime = DTOField()
    data_entrega: datetime.datetime = DTOField()
    data_retorno: datetime.datetime = DTOField()
    observacao: str = DTOField()
    peso_bruto: float = DTOField()
    peso_liquido: float = DTOField()
    volumes: float = DTOField()
    valor: float = DTOField()
    id_entregador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    geo_localizacao_checkin: dict = DTOField()
    geo_localizacao_checkout: dict = DTOField()
    checkin: datetime.datetime = DTOField()
    checkout: datetime.datetime = DTOField()
    data_criacao: datetime.datetime = DTOField()
    lastupdate: datetime.datetime = DTOField()

