# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


class UrlValue(BaseDiv):

    def __init__(
        self, *,
        type: str = "url",
        value: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            value=value,
            **kwargs,
        )

    type: str = Field(default="url")
    value: typing.Union[Expr, str] = Field(
        format="uri",
    )


UrlValue.update_forward_refs()
