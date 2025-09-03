# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Deletes a value from the array
class DivActionArrayRemoveValue(BaseDiv):

    def __init__(
        self, *,
        type: str = "array_remove_value",
        index: typing.Optional[typing.Union[Expr, int]] = None,
        variable_name: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            index=index,
            variable_name=variable_name,
            **kwargs,
        )

    type: str = Field(default="array_remove_value")
    index: typing.Union[Expr, int] = Field(
    )
    variable_name: typing.Union[Expr, str] = Field(
    )


DivActionArrayRemoveValue.update_forward_refs()
