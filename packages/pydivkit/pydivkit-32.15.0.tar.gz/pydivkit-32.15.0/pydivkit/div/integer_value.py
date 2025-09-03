# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


class IntegerValue(BaseDiv):

    def __init__(
        self, *,
        type: str = "integer",
        value: typing.Optional[typing.Union[Expr, int]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            value=value,
            **kwargs,
        )

    type: str = Field(default="integer")
    value: typing.Union[Expr, int] = Field(
    )


IntegerValue.update_forward_refs()
