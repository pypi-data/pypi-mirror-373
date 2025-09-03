# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_evaluable_type, div_function_argument


# User-defined function.
class DivFunction(BaseDiv):

    def __init__(
        self, *,
        arguments: typing.Optional[typing.Sequence[div_function_argument.DivFunctionArgument]] = None,
        body: typing.Optional[typing.Union[Expr, str]] = None,
        name: typing.Optional[typing.Union[Expr, str]] = None,
        return_type: typing.Optional[typing.Union[Expr, div_evaluable_type.DivEvaluableType]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            arguments=arguments,
            body=body,
            name=name,
            return_type=return_type,
            **kwargs,
        )

    arguments: typing.Sequence[div_function_argument.DivFunctionArgument] = Field(
        description="Function argument.",
    )
    body: typing.Union[Expr, str] = Field(
        description=(
            "Function body. Evaluated as an expression using the passed "
            "arguments. Doesn\'tcapture external variables."
        ),
    )
    name: typing.Union[Expr, str] = Field(
        description="Function name.",
    )
    return_type: typing.Union[Expr, div_evaluable_type.DivEvaluableType] = Field(
        description="Return value type.",
    )


DivFunction.update_forward_refs()
