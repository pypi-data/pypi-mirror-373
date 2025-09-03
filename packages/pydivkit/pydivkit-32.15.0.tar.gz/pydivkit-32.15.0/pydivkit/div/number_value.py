# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


class NumberValue(BaseDiv):

    def __init__(
        self, *,
        type: str = "number",
        value: typing.Optional[typing.Union[Expr, float]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            value=value,
            **kwargs,
        )

    type: str = Field(default="number")
    value: typing.Union[Expr, float] = Field(
    )


NumberValue.update_forward_refs()
