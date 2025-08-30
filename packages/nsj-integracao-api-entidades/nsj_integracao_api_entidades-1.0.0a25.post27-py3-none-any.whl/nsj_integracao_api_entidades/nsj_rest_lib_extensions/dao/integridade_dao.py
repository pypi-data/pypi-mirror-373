import uuid
import re

from typing import List, Dict

from nsj_rest_lib.dao.dao_base import DAOBase
from nsj_rest_lib.entity.filter import Filter
from nsj_rest_lib.exception import (
    NotFoundException,
    AfterRecordNotFoundException,
)


class IntegridadeDAO(DAOBase):

    def list_ids_integridade(
        self,
        filters: Dict[str, List[Filter]],
        after: uuid.UUID,
        limit: int,
        order_fields: List[str]
    ):
        """
        Lista os IDs encontrados, de acordo com os filtros recebidos.
        """

        # Retorna None, se não receber filtros
        # if filters is None or len(filters) <= 0:
        #     return None

        # Montando uma entity fake
        entity = self._entity_class()

        # Recuperando o campo de chave primária
        entity_key_field = entity.get_pk_field()

        # Cheking should use default entity order
        if order_fields is None:
            order_fields = entity.get_default_order_fields()

        # Making order fields with alias list
        order_fields_alias = [f"t0.{i}" for i in order_fields]

        # Resolving data to pagination
        order_map = {
            re.sub(r"\basc\b", "", re.sub(r"\bdesc\b", "", field)).strip(): None
            for field in order_fields
        }

        if after is not None:
            try:
                after_obj = self.get(entity_key_field, after, [entity_key_field], filters)
            except NotFoundException:
                raise AfterRecordNotFoundException(
                    f"Identificador recebido no parâmetro after {id}, não encontrado para a entidade {self._entity_class.__name__}."
                )

            if after_obj is not None:
                for field in order_fields:
                    order_map[
                        re.sub(r"\basc\b", "", re.sub(r"\bdesc\b", "", field)).strip()
                    ] = getattr(
                        after_obj,
                        re.sub(r"\basc\b", "", re.sub(r"\bdesc\b", "", field)).strip(),
                        None,
                    )

        # Making default order by clause
        order_by = f"""
            {', '.join(order_fields_alias)}
        """

        # Organizando o where da paginação
        pagination_where = ""
        if after is not None:
            # Making a list of pagination condictions
            list_page_where = []
            old_fields = []
            for field in order_fields:
                # Making equals condictions
                buffer_old_fields = "true"
                for of in old_fields:
                    buffer_old_fields += f" and t0.{of} = :{of}"

                field_adjusted = re.sub(
                    r"\basc\b", "", re.sub(r"\bdesc\b", "", field)
                ).strip()

                # Making current more than condiction
                list_page_where.append(
                    f"({buffer_old_fields} and t0.{field_adjusted} {'<' if 'desc' in field else '>'} :{field_adjusted})"
                )

                # Storing current field as old
                old_fields.append(field_adjusted)

            # Making SQL page condiction
            pagination_where = f"""
                and (
                    false
                    or {' or '.join(list_page_where)}
                )
            """

        # Organizando o where dos filtros
        filters_where, filter_values_map = self._make_filters_sql(filters)

        # Montando a query
        sql = f"""
        select {entity_key_field}
        from {entity.get_table_name()} as t0
        where
            true
            {pagination_where}
            {filters_where}

        order by
            {order_by}
        """

        # Adding limit if received
        if limit is not None:
            sql += f"        limit {limit}"

        # Making the values dict
        kwargs = {**order_map, **filter_values_map}

        # Executando a query
        resp = self._db.execute_query(sql, **kwargs)

        # Retornando em formato de lista de IDs
        if resp is None:
            return []
        else:
            return [item[entity_key_field] for item in resp]
