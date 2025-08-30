
from nsj_rest_lib.controller.get_route import GetRoute
from nsj_rest_lib.controller.list_route import ListRoute
from nsj_rest_lib.controller.post_route import PostRoute
from nsj_rest_lib.controller.put_route import PutRoute
from nsj_rest_lib.controller.delete_route import DeleteRoute
from nsj_integracao_api_entidades.nsj_rest_lib_extensions.controller.post_blob_filter_hash_route import PostBlobFilterHashRoute
from nsj_integracao_api_entidades.nsj_rest_lib_extensions.controller.put_blob_route import PutBlobRoute
from nsj_integracao_api_entidades.nsj_rest_lib_extensions.controller.integrity_check_route import IntegrityCheckRoute

from nsj_integracao_api_entidades.auth import auth
from nsj_integracao_api_entidades.injector_factory import InjectorFactory
from nsj_integracao_api_entidades.settings import application, APP_NAME, MOPE_CODE

from nsj_integracao_api_entidades.dto.persona_documentoscolaboradores import DocumentoscolaboradoreDTO as DTO
from nsj_integracao_api_entidades.entity.persona_documentoscolaboradores import DocumentoscolaboradoreEntity as Entity

from nsj_integracao_api_entidades.dto.persona_documentoscolaboradores_documento import DocumentoColaboradorDocumentoDTO as DocumentoDTO
from nsj_integracao_api_entidades.entity.persona_documentoscolaboradores_documento import DocumentoColaboradorDocumentoEntity as DocumentoEntity

ROUTE = f"/{APP_NAME}/{MOPE_CODE}/persona/documentoscolaboradores"
ID_ROUTE = f"/{APP_NAME}/{MOPE_CODE}/persona/documentoscolaboradores/<id>"
INTEGRITY_ROUTE = f"/{APP_NAME}/{MOPE_CODE}/persona/documentoscolaboradores/verificacao-integridade"
BLOB_FILTER_HASH_ROUTE = f"/{APP_NAME}/{MOPE_CODE}/blobs-documentoscolaboradores-hashes/filtros"
BLOB_ROUTE = f"/{APP_NAME}/{MOPE_CODE}/blobs-documentoscolaboradores"


@application.route(ROUTE, methods=["GET"])
@auth.requires_api_key_or_access_token()
@ListRoute(
    url=ROUTE,
    http_method="GET",
    dto_class=DTO,
    entity_class=Entity,
    injector_factory=InjectorFactory,
)
def persona_documentoscolaboradores_list_action(_, response):
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
def persona_documentoscolaboradores_get_action(_, response):
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
def persona_documentoscolaboradores_post_action(_, response):
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
def persona_documentoscolaboradores_put_action(_, response):
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
def persona_documentoscolaboradores_put_list_action(_, response):
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
def persona_documentoscolaboradores_delete_action(_, response):
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
def persona_documentoscolaboradores_delete_list_action(_, response):
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
def persona_documentoscolaboradores_integrity_check_action(_, response):
    return response


@application.route(BLOB_FILTER_HASH_ROUTE, methods=["POST"])
@auth.requires_api_key_or_access_token()
@PostBlobFilterHashRoute(
    url=BLOB_FILTER_HASH_ROUTE,
    http_method="POST",
    dto_class=DocumentoDTO,
    entity_class=DocumentoEntity,
    injector_factory=InjectorFactory,
)
def blobs_documentoscolaboradores_hashes_post_action(_, response):
    return response


@application.route(BLOB_ROUTE, methods=["PUT"])
@auth.requires_api_key_or_access_token()
@PutBlobRoute(
    url=ROUTE,
    http_method="PUT",
    dto_class=DocumentoDTO,
    entity_class=DocumentoEntity,
    injector_factory=InjectorFactory,
)
def blobs_documentoscolaboradores_post_action(_, response):
    return response
