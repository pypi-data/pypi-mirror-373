
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class DependentestrabalhadoreDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='dependentetrabalhador',
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
    nome: str = DTOField()
    datainclusao: datetime.datetime = DTOField()
    tipoparentesco: int = DTOField()
    impostorenda: bool = DTOField()
    salariofamilia: bool = DTOField()
    pensaoalimenticia: bool = DTOField()
    percentualpensaoalimenticia: float = DTOField()
    percentualpensaoalimenticiafgts: float = DTOField()
    cpf: str = DTOField()
    datanascimento: datetime.datetime = DTOField()
    ufnascimento: str = DTOField()
    cidadenascimento: str = DTOField()
    cartoriocertidao: str = DTOField()
    numeroregistrocertidao: str = DTOField()
    numerolivrocertidao: str = DTOField()
    numerofolhacertidao: str = DTOField()
    dataentregacertidao: datetime.datetime = DTOField()
    databaixacertidao: datetime.datetime = DTOField()
    tiporecebimento: int = DTOField()
    numerocontarecebimento: str = DTOField()
    numerocontadvrecebimento: str = DTOField()
    datavencimentodeclaracaoescolar: datetime.datetime = DTOField()
    datavencimentovacinacao: datetime.datetime = DTOField()
    sexo: int = DTOField()
    databaixaimpostorenda: datetime.datetime = DTOField()
    planosaude: bool = DTOField()
    agencia: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    dependentetrabalhadorpensao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    eventopensaofolha: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    eventopensaoferias: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    eventopensaopplr: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    eventopensao13: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    trabalhador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    incapacidadefisicamental: bool = DTOField()
    possuiatestadoparanaofrequentarescola: bool = DTOField()

