# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


class StringValue(BaseDiv):

    def __init__(
        self, *,
        type: str = "string",
        value: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            value=value,
            **kwargs,
        )

    type: str = Field(default="string")
    value: typing.Union[Expr, str] = Field(
    )


StringValue.update_forward_refs()
