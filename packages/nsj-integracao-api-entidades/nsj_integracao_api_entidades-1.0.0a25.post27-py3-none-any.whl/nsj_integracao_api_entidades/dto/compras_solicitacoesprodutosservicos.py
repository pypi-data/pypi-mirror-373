
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class SolicitacoesprodutosservicoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='solicitacaoprodutoservico',
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
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    solicitante: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    numero: str = DTOField(
      not_null=True,)
    datalimite: datetime.datetime = DTOField()
    motivo: str = DTOField()
    rateio: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    data_cadastro: datetime.datetime = DTOField(
      not_null=True,)
    cadastrado_por: str = DTOField(
      not_null=True,)
    situacao: int = DTOField(
      not_null=True,)
    localdeuso_padrao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    wkf_data: datetime.datetime = DTOField()
    wkf_estado: str = DTOField()
    uso_consumo: bool = DTOField()
    cliente: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    localdeuso_modelo: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    origem: int = DTOField(
      not_null=True,)
    id_documento_origem: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    rascunho: bool = DTOField(
      not_null=True,)
    lastupdate: datetime.datetime = DTOField()

