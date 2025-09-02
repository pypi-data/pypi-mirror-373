from copy import deepcopy
from typing import Any, Optional, Tuple, Type

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo


def partial_model(model: Type[BaseModel]) -> Type[BaseModel]:
    """Marks all fields of a model as optional. Useful for updating models.
    Inherits all fields, docstrings, and the model name.

    >>> @partial_model
    >>> class Model(BaseModel):
    >>>     i: int
    >>>     f: float
    >>>     s: str

    >>> Model(i=1)
    """

    def make_field_optional(
        field: FieldInfo, default: Any = None
    ) -> Tuple[Any, FieldInfo]:
        new = deepcopy(field)
        new.default = default
        new.annotation = Optional[field.annotation]  # type: ignore
        return new.annotation, new

    return create_model(
        model.__name__,
        __base__=model,
        __module__=model.__module__,
        __doc__=model.__doc__,
        **{
            field_name: make_field_optional(field_info)
            for field_name, field_info in model.model_fields.items()
        },
    )
