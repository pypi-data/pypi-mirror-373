
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="servicos.ordensservicosvisitas",
    pk_field="ordemservicovisita",
    default_order_fields=["ordemservicovisita"],
)
class OrdensservicosvisitaEntity(EntityBase):
    ordemservicovisita: uuid.UUID = None
    tenant: int = None
    ordemservico: uuid.UUID = None
    descricao: str = None
    datavisita: datetime.datetime = None
    agendado: int = None
    executado: int = None
    enderecoparticipante: uuid.UUID = None
    atendimento_consecutivo: bool = None
    deslocamento: bool = None
    hora_chegada_cliente: datetime.time = None
    hora_inicio_manutencao: datetime.time = None
    hora_termino_manutencao: datetime.time = None
    parada_para_almoco: bool = None
    lastupdate: datetime.datetime = None
    hora_inicio_almoco: datetime.time = None
    hora_termino_almoco: datetime.time = None
    origem_saida: str = None
    hora_saida: datetime.time = None
    km_saida: float = None
    km_chegada_cliente: float = None
    deslocamento_extra: bool = None
    motivo_deslocamento: str = None
    hora_saida_deslocamento: datetime.time = None
    hora_chegada_deslocamento: datetime.time = None
    km_chegada_deslocamento: float = None
    hora_saida_cliente: datetime.time = None
    veiculo_id: uuid.UUID = None
    horasexecutadas: datetime.time = None
    horasestimadas: datetime.time = None
    hora_estimada_inicio: datetime.time = None
    hora_estimada_fim: datetime.time = None
