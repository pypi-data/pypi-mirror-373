# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# [Calculated expression](../../expressions) validator.
class DivInputValidatorExpression(BaseDiv):

    def __init__(
        self, *,
        type: str = "expression",
        allow_empty: typing.Optional[typing.Union[Expr, bool]] = None,
        condition: typing.Optional[typing.Union[Expr, bool]] = None,
        label_id: typing.Optional[typing.Union[Expr, str]] = None,
        variable: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            allow_empty=allow_empty,
            condition=condition,
            label_id=label_id,
            variable=variable,
            **kwargs,
        )

    type: str = Field(default="expression")
    allow_empty: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Determines whether the empty field value is valid.",
    )
    condition: typing.Union[Expr, bool] = Field(
        description=(
            "[Calculated expression](../../expressions) used as a value "
            "validity condition."
        ),
    )
    label_id: typing.Union[Expr, str] = Field(
        description=(
            "ID of the text element containing the error message. The "
            "message will also beused for providing access."
        ),
    )
    variable: typing.Union[Expr, str] = Field(
        description=(
            "The name of the variable that stores the calculation "
            "results."
        ),
    )


DivInputValidatorExpression.update_forward_refs()
