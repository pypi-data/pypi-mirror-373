from typing import List, Dict, Any
import uuid
from nsj_rest_lib.dto.dto_base import DTOBase
from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.service.service_base import ServiceBase
from nsj_rest_lib.injector_factory_base import NsjInjectorFactoryBase

from nsj_integracao_api_entidades.nsj_rest_lib_extensions.dao.integridade_dao import IntegridadeDAO


class IntegridadeService(ServiceBase):
    _dao: IntegridadeDAO

    def __init__(
        self,
        injector_factory: NsjInjectorFactoryBase,
        dao: IntegridadeDAO,
        dto_class: DTOBase,
        entity_class: EntityBase,
        dto_post_response_class: DTOBase = None,
    ):
        super().__init__(
            injector_factory, dao, dto_class, entity_class, dto_post_response_class
        )
        self._dao = dao

    def list_ids_integridade(
        self,
        after: uuid.UUID,
        limit: int,
        order_fields: List[str],
        filters: Dict[str, Any]
    )-> List[uuid.UUID]:
        """
        Lista os IDs encontrados, de acordo com os filtros recebidos.
        """

        # Handling order fields
        order_fields = self._convert_to_entity_fields(order_fields)

        # Tratando dos filtros
        all_filters = {}
        if self._dto_class.fixed_filters is not None:
            all_filters.update(self._dto_class.fixed_filters)
        if filters is not None:
            all_filters.update(filters)

        entity_filters = self._create_entity_filters(all_filters)

        # Resolve o campo de chave sendo utilizado
        _entity_key_field, _entity_id_value = (None, None)
        if after is not None:
            _entity_key_field, _entity_id_value = self._resolve_field_key(
                after,
                filters,
            )

        # Retrieving from DAO
        id_list = self._dao.list_ids_integridade(
            after=after,
            limit=limit,
            order_fields=order_fields,
            filters=entity_filters,
        )

        # Returning
        return id_list
