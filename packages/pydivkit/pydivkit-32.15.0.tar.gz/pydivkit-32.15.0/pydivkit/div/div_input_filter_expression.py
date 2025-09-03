# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Filter based on [calculated expressions](../../expressions).
class DivInputFilterExpression(BaseDiv):

    def __init__(
        self, *,
        type: str = "expression",
        condition: typing.Optional[typing.Union[Expr, bool]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            condition=condition,
            **kwargs,
        )

    type: str = Field(default="expression")
    condition: typing.Union[Expr, bool] = Field(
        description=(
            "[Calculated expression](../../expressions) used to verify "
            "the validity of thevalue."
        ),
    )


DivInputFilterExpression.update_forward_refs()
