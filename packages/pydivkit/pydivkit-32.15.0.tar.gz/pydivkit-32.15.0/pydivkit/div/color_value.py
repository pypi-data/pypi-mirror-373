# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


class ColorValue(BaseDiv):

    def __init__(
        self, *,
        type: str = "color",
        value: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            value=value,
            **kwargs,
        )

    type: str = Field(default="color")
    value: typing.Union[Expr, str] = Field(
        format="color",
    )


ColorValue.update_forward_refs()
