
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.horarios",
    pk_field="horario",
    default_order_fields=["codigo"],
)
class HorarioEntity(EntityBase):
    horario: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    nome: str = None
    numerofolgasfixas: int = None
    diafolgaextra: int = None
    diasemanafolgaextra: int = None
    tipo: int = None
    diasemanatolerancia: int = None
    atrasosegunda: bool = None
    atrasoterca: bool = None
    atrasoquarta: bool = None
    atrasoquinta: bool = None
    atrasosexta: bool = None
    atrasosabado: bool = None
    atrasodomingo: bool = None
    repousosegunda: bool = None
    repousoterca: bool = None
    repousoquarta: bool = None
    repousoquinta: bool = None
    repousosexta: bool = None
    repousosabado: bool = None
    repousodomingo: bool = None
    empresa: uuid.UUID = None
    jornadaquinta: uuid.UUID = None
    jornadadomingo: uuid.UUID = None
    jornadasabado: uuid.UUID = None
    jornadasegunda: uuid.UUID = None
    jornadaoutros: uuid.UUID = None
    jornadaquarta: uuid.UUID = None
    jornadasexta: uuid.UUID = None
    jornadaterca: uuid.UUID = None
    lastupdate: datetime.datetime = None
    desconsiderardsrsegunda: bool = None
    desconsiderardsrterca: bool = None
    desconsiderardsrquarta: bool = None
    desconsiderardsrquinta: bool = None
    desconsiderardsrsexta: bool = None
    desconsiderardsrsabado: bool = None
    desconsiderardsrdomingo: bool = None
    dsrsobredomingoseferiados: bool = None
    descricaoescala: str = None
    desconsiderardsrfolgasfixas: bool = None
    desabilitado: bool = None
    pagahoraextranormalemferiado: bool = None
