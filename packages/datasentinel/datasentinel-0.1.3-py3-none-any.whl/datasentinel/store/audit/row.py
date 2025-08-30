from dataclasses import dataclass
from datetime import date, datetime
from types import NoneType, UnionType
from typing import Any, Union, get_args, get_origin

from pydantic import BaseModel, model_validator
from typing_extensions import Self


_VALID_SCALAR_TYPES = {str, int, float, bool, datetime, date}
_VALID_COLLECTION_TYPES = {list, tuple, set}
_VALID_OPTIONAL_TYPES = {Union, UnionType}
_VALID_TYPES = {*_VALID_SCALAR_TYPES, *_VALID_COLLECTION_TYPES, *_VALID_OPTIONAL_TYPES, dict}
_VALID_TYPES_STR = ",".join([t.__name__ for t in _VALID_TYPES])


@dataclass
class FieldInfo:
    """Information about a field in a row.

    Attributes:
        annotation: The annotation/type of the field.
        type: The normalized type of the field.
        args: The arguments of the type of the field.
        required: Whether the field is required.
        complex: Whether the field is complex.
    """

    annotation: type
    type: type
    args: tuple | None
    required: bool
    complex: bool


class BaseAuditRow(BaseModel):
    @model_validator(mode="after")
    def validate_fields(self) -> Self:
        self._validate_fields()
        return self

    def to_dict(self) -> dict[str, Any]:
        """Returns the row as a dictionary."""
        return self.model_dump()

    @property
    def columns(self) -> list[str]:
        """Returns the columns of the row."""
        return list(self.model_fields.keys())

    @property
    def row_fields(self) -> dict[str, FieldInfo]:
        """Returns the schema of the row."""
        row_fields = {}

        for name, pydantic_field_info in self.model_fields.items():
            field_type, args = self._field_type(pydantic_field_info.annotation)
            row_fields[name] = FieldInfo(
                annotation=pydantic_field_info.annotation,
                type=field_type,
                args=args,
                required=pydantic_field_info.is_required(),
                complex=self._is_complex(pydantic_field_info.annotation),
            )

        return row_fields

    def _validate_fields(self) -> None:
        for name, pydantic_field_info in self.model_fields.items():
            if self._is_multi_type(pydantic_field_info.annotation):
                raise ValueError(f"Multi-type fields are not supported '{name}'.")

    def _is_multi_type(self, annotation: type) -> bool:  # noqa PLR0911
        field_type = get_origin(annotation) or annotation
        if field_type is Any:
            return True
        if field_type not in _VALID_TYPES:
            raise ValueError(
                f"Unsupported field type '{annotation}'. Supported types: {_VALID_TYPES_STR}"
            )

        args = get_args(annotation)

        if field_type in _VALID_SCALAR_TYPES:
            return False
        if field_type is dict:
            return False
        if field_type in _VALID_COLLECTION_TYPES:
            return self._is_multi_typed_collection(field_type=field_type, args=args)
        if self._is_optional_field(field_type, args):
            if args[0] in _VALID_OPTIONAL_TYPES:
                return True
            return self._is_multi_type(args[0])
        return True

    @staticmethod
    def _is_optional_field(field_type: type, args: tuple | None) -> bool:
        if field_type not in _VALID_OPTIONAL_TYPES:
            return False

        if len(args) != 2 or args[1] is not NoneType:  # noqa PLR2004
            return False

        return True

    @staticmethod
    def _is_multi_typed_collection(field_type: type, args: tuple | None) -> bool:
        if not args:
            return True

        if (
            field_type is list
            and args[0] in _VALID_SCALAR_TYPES
            and all(arg == args[0] for arg in args)
        ):
            return False

        if (
            field_type is tuple
            and args[0] in _VALID_SCALAR_TYPES
            and all(arg == args[0] or arg is Ellipsis for arg in args)
        ):
            return False

        if (
            field_type is set
            and args[0] in _VALID_SCALAR_TYPES
            and all(arg == args[0] for arg in args)
        ):
            return False

        return True

    def _is_complex(self, annotation: type) -> bool:
        field_type = get_origin(annotation) or annotation
        args = get_args(annotation)
        if field_type in _VALID_SCALAR_TYPES:
            return False

        if self._is_optional_field(field_type=field_type, args=args):
            return self._is_complex(args[0])

        return True

    def _field_type(self, annotation: type) -> tuple[type, tuple[type, ...] | None]:
        field_type = get_origin(annotation) or annotation

        if field_type in _VALID_SCALAR_TYPES:
            return field_type, None

        args = get_args(annotation)

        if field_type in _VALID_OPTIONAL_TYPES:
            return self._field_type(args[0])

        if field_type is tuple:
            return field_type, (args[0],)

        return field_type, args
