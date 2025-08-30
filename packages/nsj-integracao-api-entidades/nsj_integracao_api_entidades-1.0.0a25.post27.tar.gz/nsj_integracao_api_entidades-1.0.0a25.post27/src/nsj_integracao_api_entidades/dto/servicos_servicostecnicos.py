
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ServicostecnicoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='servicotecnico',
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
    codigo: str = DTOField()
    descricao: str = DTOField()
    bloqueado: int = DTOField()
    codigocontabil: str = DTOField()
    insspercentualincidencia: float = DTOField()
    aliquotainss: float = DTOField()
    descontocobranca: int = DTOField()
    valor: float = DTOField()
    incidecomissao: int = DTOField()
    cfop: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    classificacaofinanceira: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tiposervico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    unidademedida: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    servicocatalogo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    cor: str = DTOField()
    incluinopedidovenda: int = DTOField()
    minimohorascontratadas: int = DTOField()
    lastupdate: datetime.datetime = DTOField()
    id_grupoempresarial: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    servicovinculado: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    faturar: bool = DTOField(
      not_null=True,)
    gerarordemdeservico: bool = DTOField(
      not_null=True,)
    created_at: datetime.datetime = DTOField()
    created_by: dict = DTOField()
    updated_at: datetime.datetime = DTOField()
    updated_by: dict = DTOField()
    tipo: int = DTOField()

