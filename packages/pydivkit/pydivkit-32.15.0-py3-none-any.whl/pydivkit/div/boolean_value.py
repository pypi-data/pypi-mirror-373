# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


class BooleanValue(BaseDiv):

    def __init__(
        self, *,
        type: str = "boolean",
        value: typing.Optional[typing.Union[Expr, bool]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            value=value,
            **kwargs,
        )

    type: str = Field(default="boolean")
    value: typing.Union[Expr, bool] = Field(
    )


BooleanValue.update_forward_refs()
