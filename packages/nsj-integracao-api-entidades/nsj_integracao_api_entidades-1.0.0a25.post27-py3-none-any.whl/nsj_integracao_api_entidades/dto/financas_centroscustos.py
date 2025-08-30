
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class CentroscustoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='centrocusto',
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
    codigo: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    descricao: str = DTOField()
    codigocontabil: str = DTOField()
    resumo: str = DTOField()
    situacao: int = DTOField(
      not_null=True,)
    paiid: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    grupoempresarial: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    natureza: int = DTOField(
      not_null=True,)
    resumoexplicativo: str = DTOField()
    importacao_hash: str = DTOField()
    usuario_responsavel: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)

