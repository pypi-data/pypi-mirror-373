
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="estoque.veiculos",
    pk_field="veiculo",
    default_order_fields=["codigo"],
)
class VeiculoEntity(EntityBase):
    veiculo: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    placa: str = None
    renavam: str = None
    tarakg: int = None
    capacidadekg: int = None
    capacidadem3: int = None
    tipoveiculo: int = None
    tiporodado: int = None
    tipocarroceria: int = None
    uflicenciamento: str = None
    proprietario: uuid.UUID = None
    motorista: uuid.UUID = None
    empresa: uuid.UUID = None
    ano: int = None
    modelo: str = None
    rntc: str = None
    tipo: int = None
    lastupdate: datetime.datetime = None
