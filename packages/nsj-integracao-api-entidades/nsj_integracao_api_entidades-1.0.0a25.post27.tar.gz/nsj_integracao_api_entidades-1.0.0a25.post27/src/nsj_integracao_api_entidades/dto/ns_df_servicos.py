
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class DfServicoDTO(DTOBase):
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
    id_ano: int = DTOField()
    cfop: str = DTOField()
    descricao: str = DTOField()
    incideirrf: bool = DTOField()
    incideinss: bool = DTOField()
    tipo: int = DTOField()
    rapis: int = DTOField()
    remas: int = DTOField()
    deducao: float = DTOField()
    unitario: float = DTOField()
    quantidade: float = DTOField()
    valordesc: float = DTOField()
    valor: float = DTOField()
    vlrservicos15: float = DTOField()
    vlrservicos20: float = DTOField()
    vlrservicos25: float = DTOField()
    valorinssadicional: float = DTOField()
    valorinssnaoretido: float = DTOField()
    ordem: int = DTOField(
      not_null=True,)
    id_docfis: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_notadeducao: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_obra: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_servico: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    vencimento: datetime.datetime = DTOField()
    inicioreferencia: datetime.datetime = DTOField()
    fimreferencia: datetime.datetime = DTOField()
    diasvencimento: int = DTOField()
    titulo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    itemcontrato: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    pessoa: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    contrato: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    processamentocontrato: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tipocobranca: int = DTOField()
    lastupdate: datetime.datetime = DTOField()
    parcela: int = DTOField(
      not_null=True,)
    totalparcelas: int = DTOField(
      not_null=True,)
    objetoservico_id: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tiposervico: int = DTOField()
    base_iss: float = DTOField()
    valor_iss: float = DTOField()
    base_inss: float = DTOField()
    valor_inss: float = DTOField()
    base_irrf: float = DTOField()
    valor_irrf: float = DTOField()
    base_cofins: float = DTOField()
    valor_cofins: float = DTOField()
    base_pis: float = DTOField()
    valor_pis: float = DTOField()
    base_csll: float = DTOField()
    valor_csll: float = DTOField()
    retem_iss: bool = DTOField()
    retem_inss: bool = DTOField()
    retem_irrf: bool = DTOField()
    retem_cofins: bool = DTOField()
    retem_pis: bool = DTOField()
    retem_csll: bool = DTOField()
    emissao: datetime.datetime = DTOField()
    valorcontabilpis: float = DTOField()
    valorcontabilcofins: float = DTOField()
    id_origem: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    desconto: float = DTOField()
    datareajusteitemcontrato: datetime.datetime = DTOField()
    valortotalocorrenciasitemcontrato: float = DTOField()
    valordebitopis: float = DTOField(
      not_null=True,)
    valordebitocofins: float = DTOField(
      not_null=True,)

