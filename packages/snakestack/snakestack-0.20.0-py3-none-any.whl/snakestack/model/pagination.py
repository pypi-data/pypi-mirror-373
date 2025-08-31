from math import ceil
from typing import Generic, Self, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from snakestack import constants

T = TypeVar("T")


class PaginatedModel(BaseModel, Generic[T]):
    model_config = ConfigDict(
        extra='forbid'
    )

    items: list[T] = Field(
        ..., description=constants.PAGINATE_ITEMS_SCHEMA_DESCRIPTION
    )
    total: int = Field(
        ..., description=constants.PAGINATE_TOTAL_SCHEMA_DESCRIPTION
    )
    page: int = Field(
        default=1, description=constants.PAGINATE_PAGE_SCHEMA_DESCRIPTION
    )
    size: int = Field(
        ..., description=constants.PAGINATE_SIZE_SCHEMA_DESCRIPTION
    )
    has_next: bool = Field(
        default=False, description=constants.PAGINATE_HAS_NEXT_SCHEMA_DESCRIPTION
    )
    has_prev: bool = Field(
        default=False, description=constants.PAGINATE_HAS_PREV_SCHEMA_DESCRIPTION
    )
    total_pages: int = Field(
        default=0,
        description=constants.PAGINATE_TOTAL_PAGES_SCHEMA_DESCRIPTION
    )
    offset: int = Field(
        default=0,
        description=constants.PAGINATE_OFFSET_SCHEMA_DESCRIPTION
    )

    @model_validator(mode="after")
    def validate_page(self: Self) -> Self:
        self.page = (self.offset // self.size) + 1
        return self

    @model_validator(mode="after")
    def calculate_pagination_metadata(
        self: Self
    ) -> Self:
        self.total_pages = ceil(self.total / self.size)
        self.has_next = self.page < self.total_pages
        self.has_prev = self.page > 1
        return self
