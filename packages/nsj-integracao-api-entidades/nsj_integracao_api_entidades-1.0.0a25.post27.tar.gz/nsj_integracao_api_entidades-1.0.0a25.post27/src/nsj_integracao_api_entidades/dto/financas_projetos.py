
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ProjetoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='projeto',
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
    nome: str = DTOField(
      not_null=True,)
    finalizado: bool = DTOField()
    datainicio: datetime.datetime = DTOField()
    datafim: datetime.datetime = DTOField()
    grupoempresarial: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    cliente_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    importacao_hash: str = DTOField()
    estabelecimento_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tipoprojeto_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    observacao: str = DTOField()
    situacao: int = DTOField()
    data_criacao: datetime.datetime = DTOField()
    criado_por: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    updated_at: datetime.datetime = DTOField()
    # created_by: dict = DTOField()
    # updated_by: dict = DTOField()
    valor: float = DTOField(
      not_null=True,)
    documentovinculado: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    origem: str = DTOField(
      not_null=True,)
    tipodocumentovinculado: int = DTOField()
    sincronizaescopo: bool = DTOField(
      not_null=True,)
    localdeuso: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    sincronizasolicitacao: bool = DTOField(
      not_null=True,)
    pcp: bool = DTOField(
      not_null=True,)
    dataentrega: datetime.datetime = DTOField()
    tipoprojeto: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tempoadquirido: int = DTOField(
      not_null=True,)
    responsavel: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tempoprevisto: int = DTOField(
      not_null=True,)
    projetopai: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    codigopai: str = DTOField()
    usuario_responsavel: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    anotacao: str = DTOField()
    producao_processo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    producao_modelo_processo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    created_at: datetime.datetime = DTOField(
      not_null=True,)
    responsavel_conta_nasajon: dict = DTOField()
    endereco_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    localdeestoque_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    projeto_adm_debito: bool = DTOField()
    bloqueado: bool = DTOField()

