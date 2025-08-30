
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ItenDTO(DTOBase):
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
    reduzido: str = DTOField()
    especificacao: str = DTOField()
    codigobarra: str = DTOField()
    gtin: str = DTOField()
    ggrem: str = DTOField()
    tipi: str = DTOField()
    dacon: str = DTOField()
    sped_pc: str = DTOField()
    anp_sped: str = DTOField()
    anp_scanc: str = DTOField()
    codigorefri: str = DTOField()
    classeserv: str = DTOField()
    grupo: str = DTOField()
    localizacao: str = DTOField()
    cst_icms_a: str = DTOField()
    cst_icms_b: str = DTOField()
    csosn: str = DTOField()
    especie: str = DTOField()
    marca: str = DTOField()
    marcacomercial: str = DTOField()
    especievolume: str = DTOField()
    marcavolume: str = DTOField()
    trib_dia_am: str = DTOField()
    tipocalctrib: int = DTOField()
    tipopis: int = DTOField()
    tipocofins: int = DTOField()
    tipomedicamento: int = DTOField()
    tabelarefri: int = DTOField()
    grupoinventario: int = DTOField()
    tiposubstituicao: int = DTOField()
    decimaisinventario: int = DTOField()
    tipoipi: int = DTOField()
    tipomargem: int = DTOField()
    ultimacompra: datetime.datetime = DTOField()
    bloqueado: bool = DTOField()
    imuneicms: bool = DTOField()
    icms: float = DTOField()
    ipi: float = DTOField()
    ii: float = DTOField()
    pis: float = DTOField()
    cofins: float = DTOField()
    reducaoicms: float = DTOField()
    reducaoipi: float = DTOField()
    reducaost: float = DTOField()
    lucrosubstituicao: float = DTOField()
    diferimentoicms: float = DTOField()
    ipiporquantidade: float = DTOField()
    quantunitrib: float = DTOField()
    margemvenda: float = DTOField()
    precovenda: float = DTOField()
    precocusto: float = DTOField()
    precomediocusto: float = DTOField()
    precomedioanterior: float = DTOField()
    precomaxconsumidor: float = DTOField()
    pesobruto: float = DTOField()
    pesoliquido: float = DTOField()
    capacidade: float = DTOField()
    basesubstituicao: float = DTOField()
    baseicmsminima: float = DTOField()
    fatordia_am: float = DTOField()
    item: str = DTOField(
      candidate_key=True,
      strip=False,
      resume=True,
      not_null=True,)
    id_prodacabado: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    unidade: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    unidadetrib: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_grupo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_fabricante: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    id_ultimofornecedor: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    produto: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    gradetemplate: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    consignado: int = DTOField()
    estoqueminimo: float = DTOField()
    estoquemaximo: float = DTOField()
    subapuracao: int = DTOField()
    observacao: str = DTOField()
    invisivel: bool = DTOField()
    tipo_utilizacao: int = DTOField()
    convenio_115_03: bool = DTOField()
    conta_credito_inventario: str = DTOField()
    conta_debito_inventario: str = DTOField()
    empresacontroller: str = DTOField()
    itemcompra: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lastupdate: datetime.datetime = DTOField()
    id_fornecedor_principal: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    lead_time: int = DTOField()
    estoque_de_seguranca: float = DTOField()
    multiplo_de_compra: int = DTOField()
    cest: str = DTOField()
    gtin_trib: str = DTOField()

