
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class HorarioDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='horario',
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
    numerofolgasfixas: int = DTOField()
    diafolgaextra: int = DTOField()
    diasemanafolgaextra: int = DTOField()
    tipo: int = DTOField()
    diasemanatolerancia: int = DTOField()
    atrasosegunda: bool = DTOField()
    atrasoterca: bool = DTOField()
    atrasoquarta: bool = DTOField()
    atrasoquinta: bool = DTOField()
    atrasosexta: bool = DTOField()
    atrasosabado: bool = DTOField()
    atrasodomingo: bool = DTOField()
    repousosegunda: bool = DTOField()
    repousoterca: bool = DTOField()
    repousoquarta: bool = DTOField()
    repousoquinta: bool = DTOField()
    repousosexta: bool = DTOField()
    repousosabado: bool = DTOField()
    repousodomingo: bool = DTOField()
    empresa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    jornadaquinta: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    jornadadomingo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    jornadasabado: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    jornadasegunda: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    jornadaoutros: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    jornadaquarta: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    jornadasexta: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    jornadaterca: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    desconsiderardsrsegunda: bool = DTOField()
    desconsiderardsrterca: bool = DTOField()
    desconsiderardsrquarta: bool = DTOField()
    desconsiderardsrquinta: bool = DTOField()
    desconsiderardsrsexta: bool = DTOField()
    desconsiderardsrsabado: bool = DTOField()
    desconsiderardsrdomingo: bool = DTOField()
    dsrsobredomingoseferiados: bool = DTOField()
    descricaoescala: str = DTOField()
    desconsiderardsrfolgasfixas: bool = DTOField()
    desabilitado: bool = DTOField(
      not_null=True,)
    pagahoraextranormalemferiado: bool = DTOField()

