
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.configuracoes",
    pk_field="configuracao",
    default_order_fields=["configuracao"],
)
class ConfiguracoEntity(EntityBase):
    configuracao: uuid.UUID = None
    tenant: int = None
    vendedor: uuid.UUID = None
    created_at: datetime.datetime = None
    created_by: dict = None
    updated_at: datetime.datetime = None
    updated_by: dict = None
    permitir_cliente_sem_documento: bool = None
    permitir_pedido_com_cliente_inadimplente: bool = None
    obrigatorio_pedido_com_local_de_estoque: bool = None
    permitir_alterar_preco_com_tabela: bool = None
    obrigatorio_pedido_com_parcelamento: bool = None
    obrigatorio_pedido_com_tabela_de_preco: bool = None
    permitir_cadastrar_cliente: bool = None
    permitir_alterar_data_emissao: bool = None
    usar_data_entrega_calculo_vencimento: bool = None
    obrigatorio_pedido_com_forma_pagamento: bool = None
    bloquear_produtos_nao_vinculados_a_tabela_de_precos: bool = None
    alertar_saldo_estoque_insuficiente: bool = None
    bloquear_saldo_estoque_insuficiente: bool = None
    exibir_markup: bool = None
    permitir_incluir_item_duplicado: bool = None
    utilizar_preco_pedido_sugerido: bool = None
    permitir_aplicar_desconto: bool = None
    bloquear_pedido_cliente_sem_limite_credito: bool = None
    bloquear_preco_abaixo_da_tabela: bool = None
    utilizar_saldos_produtos: bool = None
    alertar_pedido_cliente_sem_limite_credito: bool = None
    aprovacao_automatica: bool = None
    utilizar_somente_familias_cliente_produtos_consumidos: bool = None
    campos_obrigatorios_cliente: dict = None
    cadastrar_clientes_com_pendencia_aprovacao: bool = None
    desconto_maximo: float = None
    opcao_desconto: int = None
