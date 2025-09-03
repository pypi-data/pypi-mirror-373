# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_typed_value


# Assigns a value to the variable
class DivActionSetVariable(BaseDiv):

    def __init__(
        self, *,
        type: str = "set_variable",
        value: typing.Optional[div_typed_value.DivTypedValue] = None,
        variable_name: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            value=value,
            variable_name=variable_name,
            **kwargs,
        )

    type: str = Field(default="set_variable")
    value: div_typed_value.DivTypedValue = Field(
    )
    variable_name: typing.Union[Expr, str] = Field(
    )


DivActionSetVariable.update_forward_refs()
