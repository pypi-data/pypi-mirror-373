# nsj_integracao_entidades

O nsj-integracao-entidades é uma biblioteca que fornece modelos e estruturas padronizadas para facilitar a integração entre sistemas via APIs RESTful. O objetivo é oferecer uma base consistente para gerenciar dados e entidades compartilhadas entre diferentes aplicações.

## Criando entidades

A biblioteca segue o modelo estabelecido no [rest lib](https://github.com/Nasajon/nsj_rest_lib) onde são necessárias três contruções: DTO, Entity e Controller, podendo caso haja necessidade de customização de fluxo, sobrescrever Sevice e DAO, que geralmente são usados internamente.

A maioria das contruções é feita por decorators, que ajudam a definir as regras de negócio e validações.

### DTO, Entity e Controller

- **Entity:** Representa a estrutura de dados persistida no banco de dados, incluindo regras de negócio e validações específicas.

- **DTO (Data Transfer Object):** Responsável por transportar dados entre diferentes camadas da aplicação, geralmente utilizado para entrada e saída de informações em APIs.

- **Controller:** Atua como intermediário entre a API e as camadas de serviço, gerenciando as requisições e respostas, além de orquestrar a lógica necessária para atender às operações solicitadas.

Para adicionar uma entidade ao projeto, é necessário as três construções anteriores. Abaixo um exemplo de implementação simplificado para a entidade de **faixas**:

**Entidade:** @Entity
```python
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.faixas",
    pk_field="faixa",
    default_order_fields=["codigo"],
)
class FaixaEntity(EntityBase):
    faixa: uuid.UUID = None
    tenant: int = None
    codigo: str = None
    descricao: str = None
    lastupdate: datetime.datetime = None
```
> Essa classe criar uma entidade de faixas com o nome `FaixaEntity` e as propriedades correspondentes, definindo o nome da tabela, chave primária e campos de ordenação padrão.
>

---

**DTO:** @DTO
```python

import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase

# Imports Lista
from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from nsj_integracao_api_entidades.dto.persona_itensfaixas import ItensfaixaDTO
from nsj_integracao_api_entidades.entity.persona_itensfaixas import ItensfaixaEntity

# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class FaixaDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='faixa',
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
    codigo: str = DTOField(
      candidate_key=True,
      strip=True,
      resume=True,
      not_null=True,)
    descricao: str = DTOField()
    lastupdate: datetime.datetime = DTOField()
    # Atributos de lista
    itensfaixas: list = DTOListField(
      dto_type=ItensfaixaDTO,
      entity_type=ItensfaixaEntity,
      related_entity_field='faixa'
    )
```
> Essa classe cria um DTO de faixas com o nome `FaixaDTO` e as propriedades correspondentes, definindo o nome da tabela, chave primária e campos de ordenação padrão. A classe **DTOField** e **DTOListField** ajudam a definir as regras de negócio e validações das propriedades da entidade. Em especial o **DTOListField** permite construir listas de DTOs relacionados a uma entidade (agregações).

---

**Controller:**


Nesse arquivo são declaradas as rotas e os mapeamentos para as entidades. Cada rota possui um decorator correspondente, que define as regras de negócio e validações das requisições.



```python

from nsj_rest_lib.controller.get_route import GetRoute
from nsj_rest_lib.controller.list_route import ListRoute
from nsj_rest_lib.controller.post_route import PostRoute
from nsj_rest_lib.controller.put_route import PutRoute
from nsj_rest_lib.controller.delete_route import DeleteRoute
from nsj_integracao_api_entidades.nsj_rest_lib_extensions.controller.integrity_check_route import IntegrityCheckRoute

from nsj_integracao_api_entidades.auth import auth
from nsj_integracao_api_entidades.injector_factory import InjectorFactory
from nsj_integracao_api_entidades.settings import application, APP_NAME, MOPE_CODE

from nsj_integracao_api_entidades.dto.persona_faixas import FaixaDTO as DTO
from nsj_integracao_api_entidades.entity.persona_faixas import FaixaEntity as Entity

ROUTE = f"/{APP_NAME}/{MOPE_CODE}/faixas"
ID_ROUTE = f"/{APP_NAME}/{MOPE_CODE}/faixas/<id>"
INTEGRITY_ROUTE = f"/{APP_NAME}/{MOPE_CODE}/faixas/verificacao-integridade"


@application.route(ROUTE, methods=["GET"])
@auth.requires_api_key_or_access_token()
@ListRoute(
    url=ROUTE,
    http_method="GET",
    dto_class=DTO,
    entity_class=Entity,
    injector_factory=InjectorFactory,
)
def persona_faixas_list_action(_, response):
    return response


@application.route(f"{ROUTE}/<id>", methods=["GET"])
@auth.requires_api_key_or_access_token()
@GetRoute(
    url=f"{ROUTE}/<id>",
    http_method="GET",
    dto_class=DTO,
    entity_class=Entity,
    injector_factory=InjectorFactory,
)
def persona_faixas_get_action(_, response):
    return response


@application.route(ROUTE, methods=["POST"])
@auth.requires_api_key_or_access_token()
@PostRoute(
    url=ROUTE,
    http_method="POST",
    dto_class=DTO,
    entity_class=Entity,
    injector_factory=InjectorFactory,
)
def persona_faixas_post_action(_, response):
    return response


@application.route(ID_ROUTE, methods=["PUT"])
@auth.requires_api_key_or_access_token()
@PutRoute(
    url=ID_ROUTE,
    http_method="PUT",
    dto_class=DTO,
    entity_class=Entity,
    injector_factory=InjectorFactory,
)
def persona_faixas_put_action(_, response):
    return response


@application.route(ROUTE, methods=["PUT"])
@auth.requires_api_key_or_access_token()
@PutRoute(
    url=ROUTE,
    http_method="PUT",
    dto_class=DTO,
    entity_class=Entity,
    injector_factory=InjectorFactory,
)
def persona_faixas_put_list_action(_, response):
    return response


@application.route(ID_ROUTE, methods=["DELETE"])
@auth.requires_api_key_or_access_token()
@DeleteRoute(
    url=ID_ROUTE,
    http_method="DELETE",
    dto_class=DTO,
    entity_class=Entity,
    injector_factory=InjectorFactory,
)
def persona_faixas_delete_action(_, response):
    return response


@application.route(ROUTE, methods=["DELETE"])
@auth.requires_api_key_or_access_token()
@DeleteRoute(
    url=ROUTE,
    http_method="DELETE",
    dto_class=DTO,
    entity_class=Entity,
    injector_factory=InjectorFactory,
)
def persona_faixas_delete_list_action(_, response):
    return response


@application.route(INTEGRITY_ROUTE, methods=["GET"])
@auth.requires_api_key_or_access_token()
@IntegrityCheckRoute(
    url=INTEGRITY_ROUTE,
    http_method="GET",
    dto_class=DTO,
    entity_class=Entity,
    injector_factory=InjectorFactory,
)
def persona_faixas_integrity_check_action(_, response):
    return response

```

Todas as entidades deverão ter as rotas conforme declaradas nestes arquivo, considerando o padrão de rotas que se espera para cada entidade.

As rotas definidas por cada decorator são as seguintes:

- `@ListRoute`: Define uma rota para listagem de entidades.
- `@GetRoute` : Define uma rota para obter uma entidade.
- `@PostRoute`: Define uma rota para criar uma nova entidade ou uma nova lista de entidades.
- `@PutRoute`: Define uma rota para atualizar uma entidade ou uma lista de entidades.
- `@DeleteRoute`: Define uma rota para excluir uma entidade ou uma lista de entidades.
- `@IntegrityCheckRoute`:  Define uma rota para verificar integridade das entidades.

---

> Para maiores detalhes sobre mapeamentos e outras convenções, consulte a documentação oficial do [rest lib](https://github.com/Nasajon/nsj_rest_lib).


## Publicando novas versões da biblioteca

1. Atualize o arquivo `setup.cfg` com a nova versão da biblioteca e ajsutes de dependências.

1. Rode o comando make publicar_pkg para publicar a nova versão na pypi. Certifique-se de instalar as dependências de dev antes (requirements-dev.txt).
