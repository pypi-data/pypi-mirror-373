from typing import Generic, TypeVar
from typing import List

from strawberry.types import Info

from edat_utils.query_builder import EdatQueryBuilder
from edat_utils.query_runner import EdatQueriyRunner
from edat_utils.schema import (
    EdatFilter,
    EdatOrder,
    EdatPagination,
    EdatPaginationWindow,
)
from edat_utils.utils import EdatUtils


T = TypeVar("T")


class GenericController(Generic[T]):

    def get(self, info: Info, filter: EdatFilter, pagination: EdatPagination = None, orders: List[EdatOrder] = None) -> EdatPaginationWindow[T]:
        table = EdatUtils.get_table_name(info)
        grouped = EdatUtils.is_grouped(info)
        fields = EdatUtils.get_fields(info)
        user = EdatUtils.get_user(info)
        query = EdatQueryBuilder.build_query(
            table, filter, fields, pagination, orders, grouped)

        print(f'query={query}')

        rows = EdatQueriyRunner.list(query, user)
        obj_list = EdatUtils.get_list(info, rows)
        return EdatPaginationWindow(items=obj_list, total_items_count=len(obj_list))
