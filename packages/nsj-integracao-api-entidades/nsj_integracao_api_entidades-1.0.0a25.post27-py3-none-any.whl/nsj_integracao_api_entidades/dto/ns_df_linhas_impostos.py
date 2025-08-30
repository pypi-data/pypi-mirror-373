
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class DfLinhaImpostoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='df_linha_imposto',
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
    df_linha: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    valorsituacaotributariaicms: float = DTOField()
    valororigemmercadoriaicms: float = DTOField()
    valoraliquotacreditoicms: float = DTOField()
    valorcreditoicms: float = DTOField()
    valorpercentualreducaoicms: float = DTOField()
    valorbaseicms: float = DTOField()
    valoraliquotaicms: float = DTOField()
    valoricms: float = DTOField()
    valorformacobrancaicmsst: float = DTOField()
    valorbaseretidaicmsst: float = DTOField()
    valorretidoicmsst: float = DTOField()
    valorpercentualmvaicmsst: float = DTOField()
    valorpercentualreducaoicmsst: float = DTOField()
    valorbaseicmsst: float = DTOField()
    valoraliquotaicmsst: float = DTOField()
    valoricmsst: float = DTOField()
    valortipotributacaoipi: float = DTOField()
    valorbaseipi: float = DTOField()
    valoraliquotaipi: float = DTOField()
    valoripi: float = DTOField()
    valortipotributacaopis: float = DTOField()
    valorbasepis: float = DTOField()
    valoraliquotapis: float = DTOField()
    valorpis: float = DTOField()
    valortipotributacaocofins: float = DTOField()
    valorbasecofins: float = DTOField()
    valoraliquotacofins: float = DTOField()
    valorcofins: float = DTOField()
    lastupdate: datetime.datetime = DTOField()
    valorbaseii: float = DTOField()
    valoraliquotaii: float = DTOField()
    valorii: float = DTOField()
    valorpercentualfcpicmsdestino: float = DTOField()
    valoraliquotainternaicmsdestino: float = DTOField()
    valorpercentualpartilhaicmsdestino: float = DTOField()
    valorfcpicmsdestino: float = DTOField()
    valoricmsdestino: float = DTOField()
    valoricmsinterestadualorigem: float = DTOField()
    valoraliquotainterestadualicmsdestino: float = DTOField()
    incidencia_ipi: int = DTOField()
    motivodesoneracao: int = DTOField()
    percentual_diferimento: float = DTOField()
    pfcp: float = DTOField()
    pfcpst: float = DTOField()
    pfcpstret: float = DTOField()
    picmsefet: float = DTOField()
    predbcefet: float = DTOField()
    pst: float = DTOField()
    valor_diferimento: float = DTOField()
    valoraduaneiro: float = DTOField()
    valorbaseicmsdestino: float = DTOField()
    valordesoneracao: float = DTOField()
    valoricms_sem_diferimento: float = DTOField()
    valornaoretidoicmsst: float = DTOField()
    vbcefet: float = DTOField()
    vbcfcp: float = DTOField()
    vbcfcpst: float = DTOField()
    vbcfcpstret: float = DTOField()
    vbcfcpufdest: float = DTOField()
    vfcp: float = DTOField()
    vfcpst: float = DTOField()
    vfcpstret: float = DTOField()
    vicmsefet: float = DTOField()

