
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class PerfiltribEstValidadeImpostoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='perfiltrib_est_validade_imposto',
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
    perfiltrib_est_validade: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    uf_destino: str = DTOField()
    icms_cst: int = DTOField()
    icms_reducao: float = DTOField()
    mva: float = DTOField()
    icms_reducao_st: float = DTOField()
    icms_reducao_st_simples: float = DTOField()
    icms_formadecobranca_st: int = DTOField()
    icms_baseminima: float = DTOField()
    icms_entrada: float = DTOField()
    icms_saida: float = DTOField()
    icms_csosn: int = DTOField()
    lastupdate: datetime.datetime = DTOField()
    icms_csosn_contribuinte: int = DTOField()
    fcp: float = DTOField()
    diferimento: float = DTOField()
    modalidade_bc_icmsst: int = DTOField()
    modalidade_bc_icms: int = DTOField()
    icms_cst_contribuinte: int = DTOField()

