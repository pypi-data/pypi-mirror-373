
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class MovimentoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='movimento',
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
    ordem: int = DTOField(
      not_null=True,)
    tipo: int = DTOField(
      not_null=True,)
    tipoperiodo: int = DTOField(
      not_null=True,)
    mesperiodo: int = DTOField()
    semanaperiodo: int = DTOField()
    datainicialperiodo: datetime.datetime = DTOField()
    datafinalperiodo: datetime.datetime = DTOField()
    mesinicialperiodo: int = DTOField()
    mesfinalperiodo: int = DTOField()
    anoinicialperiodo: int = DTOField()
    anofinalperiodo: int = DTOField()
    calculanofim: bool = DTOField()
    conteudo: float = DTOField()
    tipoprocedencia: int = DTOField()
    invisivel: bool = DTOField()
    folha: bool = DTOField()
    adiantamentofolha: bool = DTOField()
    decimoterceiro: bool = DTOField()
    adiantamentodecimoterceiro: bool = DTOField()
    ferias: bool = DTOField()
    rescisao: bool = DTOField()
    pplr: bool = DTOField()
    folhacorretiva: bool = DTOField()
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
    evento: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lotacaofuncionario: uuid.UUID = DTOField(
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
    complementodecimoterceiro: bool = DTOField()
    lastupdate: datetime.datetime = DTOField()
    trabalhador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    complementoferias: bool = DTOField()
    cargo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lancamentoponto: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    mesreferencia: int = DTOField()
    anoreferencia: int = DTOField()
    origem: int = DTOField()
    situacao: int = DTOField()
    apontamentotrabalhador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    updated_by: dict = DTOField()
    updated_at: datetime.datetime = DTOField()
    solicitacaorescisao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    solicitacaorescisaomeurh: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    convocacaotrabalhador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    dependentetrabalhador: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    instituicao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    medico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    referencia: str = DTOField()
    desabilitado: bool = DTOField()

