# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


class ArrayValue(BaseDiv):

    def __init__(
        self, *,
        type: str = "array",
        value: typing.Optional[typing.Sequence[typing.Any]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            value=value,
            **kwargs,
        )

    type: str = Field(default="array")
    value: typing.Sequence[typing.Any] = Field(
    )


ArrayValue.update_forward_refs()
