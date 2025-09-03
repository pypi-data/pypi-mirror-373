# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_evaluable_type


# Function argument.
class DivFunctionArgument(BaseDiv):

    def __init__(
        self, *,
        name: typing.Optional[typing.Union[Expr, str]] = None,
        type: typing.Optional[typing.Union[Expr, div_evaluable_type.DivEvaluableType]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            name=name,
            type=type,
            **kwargs,
        )

    name: typing.Union[Expr, str] = Field(
        description="Function argument name.",
    )
    type: typing.Union[Expr, div_evaluable_type.DivEvaluableType] = Field(
        description="Function argument type.",
    )


DivFunctionArgument.update_forward_refs()
