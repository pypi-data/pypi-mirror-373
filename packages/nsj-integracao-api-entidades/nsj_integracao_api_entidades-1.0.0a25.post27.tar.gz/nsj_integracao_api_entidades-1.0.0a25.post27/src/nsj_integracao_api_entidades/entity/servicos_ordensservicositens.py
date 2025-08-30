
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="servicos.ordensservicositens",
    pk_field="ordemservicoitem",
    default_order_fields=["ordemservicoitem"],
)
class OrdensservicositenEntity(EntityBase):
    ordemservicoitem: uuid.UUID = None
    tenant: int = None
    ordemservico: uuid.UUID = None
    servicotecnico: uuid.UUID = None
    objetoservico: uuid.UUID = None
    horascontratadas: int = None
    horasexecutadas: int = None
    horasfaturar: int = None
    servicoexecutado: int = None
    descontopercentual: float = None
    valortotal: float = None
    lastupdate: datetime.datetime = None
    valorunitario: float = None
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None
    created_by: dict = None
    updated_by: dict = None
    diastrabalhados: int = None
    quantidadeutilizada: int = None
    horasutilizadas: float = None
    projetoitemescopo: uuid.UUID = None
    horas_prevista_execucao: int = None
    datainiciomanutencao: datetime.datetime = None
    dataterminomanutencao: datetime.datetime = None
