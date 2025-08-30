
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class DfPagamentoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='pagamento',
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
    id_formapagamento: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_docfis: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_conta: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_rateiopadrao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_meioeletronico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_layoutcobranca: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_operadora: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_bandeira: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_parcelamento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    nomeformadepagamento: str = DTOField()
    nomemeioeletronico: str = DTOField()
    nomebandeira: str = DTOField()
    nomeoperadora: str = DTOField()
    nomeconta: str = DTOField()
    valor: float = DTOField()
    numeroparcelas: int = DTOField()
    datafatura: datetime.datetime = DTOField()
    tipooperacao: int = DTOField()
    autorizacaocartao: str = DTOField()
    dataautorizacaocartao: datetime.datetime = DTOField()
    documentocartao: str = DTOField()
    irretido: float = DTOField()
    pisretido: float = DTOField()
    cofinsretido: float = DTOField()
    csllretido: float = DTOField()
    tipo: int = DTOField()
    lastupdate: datetime.datetime = DTOField()
    isdefault: bool = DTOField(
      not_null=True,)
    cnpj_operadora: str = DTOField()
    id_contratocartao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_documentorateado: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    inssretido: float = DTOField()
    issretido: float = DTOField()
    percentual: float = DTOField()

