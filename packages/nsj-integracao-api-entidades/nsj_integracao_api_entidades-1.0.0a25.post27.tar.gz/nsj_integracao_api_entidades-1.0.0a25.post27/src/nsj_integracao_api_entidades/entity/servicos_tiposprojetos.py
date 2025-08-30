
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="servicos.tiposprojetos",
    pk_field="tipoprojeto",
    default_order_fields=["codigo"],
)
class TiposprojetoEntity(EntityBase):
    tipoprojeto: uuid.UUID = None
    tenant: int = None
    grupoempresarial_id: uuid.UUID = None
    codigo: str = None
    descricao: str = None
    cor: str = None
    gerasolicitacaocompras: int = None
    utilizahorasvendidas: int = None
    nivelcontrolehorasvendidas: int = None
    alocartarefasaoresponsavel: int = None
    contabilizarhorasimprodutivas: int = None
    controlasaldohoras: int = None
    todosostiposdehoras: bool = None
    nivelcontrolesaldohoras: int = None
    gerarexecucoes: int = None
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None
    created_by: dict = None
    updated_by: dict = None
