
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ContatosemailDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='id',
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
    pessoa_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    contato_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    email: str = DTOField()
    recebe_nfse: bool = DTOField()
    envia_nfse_prefeitura: bool = DTOField()
    recebe_nfe: bool = DTOField()
    envia_nfe_receita: bool = DTOField()
    recebe_boleto: bool = DTOField()
    recebe_pedido: bool = DTOField()
    recebe_cotacao_compra: bool = DTOField()
    lastupdate: datetime.datetime = DTOField()
    recebe_mala_direta: bool = DTOField()
    recebe_fatura_locacao: bool = DTOField()
    principal: bool = DTOField(
      not_null=True,)

