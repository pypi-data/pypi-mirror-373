import strawberry

from typing import List, NewType, TypeVar
from enum import Enum    

EdatFilter = strawberry.scalar(
    NewType("Filter", object),
    description="Json utilizado para efeturar filtros no GrahpQL",
    serialize=lambda v: v,
    parse_value=lambda v: v,
)

EdatGenericType = TypeVar("EdatGenericType")

@strawberry.interface
class EdatGrouped:
    contador: int

@strawberry.type
class EdatPaginationWindow(List[EdatGenericType]):
    items: List[EdatGenericType] = strawberry.field(
        description="The list of items in this pagination window."
    )

    total_items_count: int = strawberry.field(
        description="Total number of items in the filtered dataset."
    )

@strawberry.input
class EdatPagination:
    limit: int
    offset: int = 0

@strawberry.enum
class EdatOrderType(Enum):
    ASC = 'asc'
    DESC = 'desc'

@strawberry.input
class EdatOrder:
    field: str
    type: EdatOrderType