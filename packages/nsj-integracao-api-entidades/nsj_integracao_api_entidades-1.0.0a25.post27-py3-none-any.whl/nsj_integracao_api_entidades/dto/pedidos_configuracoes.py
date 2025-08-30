
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class ConfiguracoDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='configuracao',
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
    vendedor: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    created_at: datetime.datetime = DTOField()
    created_by: dict = DTOField()
    updated_at: datetime.datetime = DTOField()
    updated_by: dict = DTOField()
    permitir_cliente_sem_documento: bool = DTOField()
    permitir_pedido_com_cliente_inadimplente: bool = DTOField()
    obrigatorio_pedido_com_local_de_estoque: bool = DTOField()
    permitir_alterar_preco_com_tabela: bool = DTOField()
    obrigatorio_pedido_com_parcelamento: bool = DTOField()
    obrigatorio_pedido_com_tabela_de_preco: bool = DTOField()
    permitir_cadastrar_cliente: bool = DTOField()
    permitir_alterar_data_emissao: bool = DTOField()
    usar_data_entrega_calculo_vencimento: bool = DTOField()
    obrigatorio_pedido_com_forma_pagamento: bool = DTOField()
    bloquear_produtos_nao_vinculados_a_tabela_de_precos: bool = DTOField()
    alertar_saldo_estoque_insuficiente: bool = DTOField()
    bloquear_saldo_estoque_insuficiente: bool = DTOField()
    exibir_markup: bool = DTOField()
    permitir_incluir_item_duplicado: bool = DTOField()
    utilizar_preco_pedido_sugerido: bool = DTOField()
    permitir_aplicar_desconto: bool = DTOField()
    bloquear_pedido_cliente_sem_limite_credito: bool = DTOField()
    bloquear_preco_abaixo_da_tabela: bool = DTOField()
    utilizar_saldos_produtos: bool = DTOField()
    alertar_pedido_cliente_sem_limite_credito: bool = DTOField()
    aprovacao_automatica: bool = DTOField()
    utilizar_somente_familias_cliente_produtos_consumidos: bool = DTOField()
    campos_obrigatorios_cliente: dict = DTOField()
    cadastrar_clientes_com_pendencia_aprovacao: bool = DTOField()
    desconto_maximo: float = DTOField()
    opcao_desconto: int = DTOField()

