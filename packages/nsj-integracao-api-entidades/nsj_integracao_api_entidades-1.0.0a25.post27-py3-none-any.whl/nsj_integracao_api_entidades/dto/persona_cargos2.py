
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase

from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from  nsj_integracao_api_entidades.dto.persona_niveiscargos import NiveiscargoDTO
from  nsj_integracao_api_entidades.entity.persona_niveiscargos import NiveiscargoEntity

# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class CargoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='cargo',
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
      strip=True,
      resume=True,
      not_null=True,)
    nome: str = DTOField()
    descricao: str = DTOField()
    cbo: str = DTOField()
    experiencia: str = DTOField()
    grauinstrucao: str = DTOField()
    maiorsalmercado: int = DTOField()
    menorsalmercado: int = DTOField()
    requisitos: str = DTOField()
    diasexperienciacontrato: int = DTOField()
    diasprorrogacaocontrato: int = DTOField()
    empresa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    estabelecimento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    departamento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    horario: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lotacao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    sindicato: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    pontuacao: int = DTOField()
    contagemespecial: int = DTOField()
    dedicacaoexclusiva: bool = DTOField()
    numeroleicargo: str = DTOField()
    dataleicargo: datetime.datetime = DTOField()
    situacaoleicargo: int = DTOField()
    pisominimo: int = DTOField()
    cargopublico: bool = DTOField()
    acumulacaocargos: int = DTOField()
    desabilitado: bool = DTOField(
      not_null=True,)
    importacao_hash: str = DTOField()
    condicaoambientetrabalho: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    niveis : list = DTOListField(
      dto_type=NiveiscargoDTO,
      entity_type=NiveiscargoEntity,
      related_entity_field='cargo'
    )
