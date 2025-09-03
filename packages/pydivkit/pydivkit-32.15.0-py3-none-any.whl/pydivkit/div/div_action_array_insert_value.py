# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_typed_value


# Adds a value to the array
class DivActionArrayInsertValue(BaseDiv):

    def __init__(
        self, *,
        type: str = "array_insert_value",
        index: typing.Optional[typing.Union[Expr, int]] = None,
        value: typing.Optional[div_typed_value.DivTypedValue] = None,
        variable_name: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            index=index,
            value=value,
            variable_name=variable_name,
            **kwargs,
        )

    type: str = Field(default="array_insert_value")
    index: typing.Optional[typing.Union[Expr, int]] = Field(
    )
    value: div_typed_value.DivTypedValue = Field(
    )
    variable_name: typing.Union[Expr, str] = Field(
    )


DivActionArrayInsertValue.update_forward_refs()
