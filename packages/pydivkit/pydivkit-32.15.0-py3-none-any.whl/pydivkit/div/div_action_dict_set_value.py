# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_typed_value


# Sets the value in the dictionary by the specified key. Deletes the key if the
# value is not set.
class DivActionDictSetValue(BaseDiv):

    def __init__(
        self, *,
        type: str = "dict_set_value",
        key: typing.Optional[typing.Union[Expr, str]] = None,
        value: typing.Optional[div_typed_value.DivTypedValue] = None,
        variable_name: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            key=key,
            value=value,
            variable_name=variable_name,
            **kwargs,
        )

    type: str = Field(default="dict_set_value")
    key: typing.Union[Expr, str] = Field(
    )
    value: typing.Optional[div_typed_value.DivTypedValue] = Field(
    )
    variable_name: typing.Union[Expr, str] = Field(
    )


DivActionDictSetValue.update_forward_refs()
