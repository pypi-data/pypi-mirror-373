from typing import Any, TypeVar, Union

from pydantic import BaseModel, ConfigDict, GetCoreSchemaHandler, model_serializer
from pydantic_core import core_schema

_T = TypeVar("_T")


class NotGivenType:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "NOT_GIVEN"

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        # If we're dealing with NotGivenType directly
        if source is cls:
            return core_schema.is_instance_schema(cls)

        # Otherwise, it's a NotGivenOr[T] situation
        # Create a union schema: either it's an instance of NotGivenType or the underlying type
        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(cls),
                handler(source),
            ]
        )


NOT_GIVEN = NotGivenType()
NotGivenOr = Union[_T, NotGivenType]


class BaseModelWithOptionalFields(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    @model_serializer(mode="wrap")
    def filter_values(self, handler, info):
        if info.mode != "python":
            data = self.model_dump()
        else:
            data = handler(self)
        filtered = {k: v for k, v in data.items() if v is not NOT_GIVEN}
        return filtered
