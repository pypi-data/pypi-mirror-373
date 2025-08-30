
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="pedidos.configuracoes_aprovacoes",
    pk_field="configuracao_aprovacao",
    default_order_fields=["configuracao_aprovacao"],
)
class ConfiguracoAprovacoEntity(EntityBase):
    configuracao_aprovacao: uuid.UUID = None
    tenant: int = None
    bloquear_clientes_negativados: bool = None
    formas_pagamentos_negativados_excessao: dict = None
    bloquear_clientes_sem_limite_credito: bool = None
    formas_pagamentos_limite_credito_excessao: dict = None
    campos_obrigatorios_cliente: dict = None
    bloquear_clientes_titulos_vencidos: bool = None
    bloquear_criacao_pedido: bool = None
    estabelecimento: uuid.UUID = None
