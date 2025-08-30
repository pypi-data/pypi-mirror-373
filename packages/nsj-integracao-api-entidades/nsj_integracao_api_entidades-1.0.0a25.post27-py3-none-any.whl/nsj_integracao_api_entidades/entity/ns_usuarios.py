
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="ns.usuarios",
    pk_field="usuario",
    default_order_fields=["usuario"],
)
class UsuarioEntity(EntityBase):
    usuario: uuid.UUID = None
    tenant: int = None
    nome: str = None
    situacao: int = None
    email: str = None
    login: str = None
    senha: str = None
    temresponsabilidadeatendimento: bool = None
    moduloinicialpersona: int = None
    moduloinicialscritta: int = None
    moduloinicialcontabil: int = None
    ultimoanocontabil: int = None
    representante: uuid.UUID = None
    departamento: uuid.UUID = None
    ultimaempresapersona: uuid.UUID = None
    ultimoestabelecimentocontabil: uuid.UUID = None
    ultimaempresascritta: uuid.UUID = None
    ultimogrupo: uuid.UUID = None
    perfilusuario: uuid.UUID = None
    grupodeusuario: uuid.UUID = None
    ultimaentidadeempresarial_estoque: uuid.UUID = None
    lastupdate: datetime.datetime = None
    bloqueado_ate: datetime.datetime = None
    representante_pessoa: uuid.UUID = None
    telefone: str = None
    ultimoestabelecimentopersonaweb: uuid.UUID = None
    vendedor: uuid.UUID = None
    id_entregador: uuid.UUID = None
