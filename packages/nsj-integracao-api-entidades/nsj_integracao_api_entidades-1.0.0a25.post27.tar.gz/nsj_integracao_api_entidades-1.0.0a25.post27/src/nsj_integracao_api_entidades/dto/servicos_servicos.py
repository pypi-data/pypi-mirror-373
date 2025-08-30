
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ServicoDTO(DTOBase):
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
    servico: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    descricao: str = DTOField()
    codigosped: str = DTOField()
    atividade: str = DTOField()
    lcp: str = DTOField()
    codserv: str = DTOField()
    nbs: str = DTOField()
    codigocontabil: str = DTOField()
    contrapartida: str = DTOField()
    centrocusto: str = DTOField()
    cpsrb: str = DTOField()
    incideirrf: bool = DTOField()
    incideinss: bool = DTOField()
    tipoiss: int = DTOField()
    regimepc: int = DTOField()
    tributacaopc: int = DTOField()
    bloqueado: int = DTOField()
    tipoatividade: int = DTOField()
    sped_outro: str = DTOField()
    sped_detalhe: str = DTOField()
    tipo_esocial: str = DTOField()
    valor: float = DTOField()
    unidade: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    insspercentualincidencia: float = DTOField()
    descontocobranca: int = DTOField()
    anotacao: str = DTOField()
    incidecomissao: int = DTOField()
    aliquotainss: float = DTOField()
    classificacaofinanceira: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_grupo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    cfop: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    vinculado: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tiposervico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tributacaoservico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    geracobranca: int = DTOField()
    tipoperiodocobranca: int = DTOField()
    quantidadeperiodocobranca: int = DTOField()
    lastupdate: datetime.datetime = DTOField()
    visivel: bool = DTOField()
    id_grupodeservico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    sped_pc: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    valor_contrato: float = DTOField()
    pode_alterar_valor_contrato_na_proposta: bool = DTOField()
    id_conjunto: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)

