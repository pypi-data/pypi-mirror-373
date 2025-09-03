# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Specifies the element with the given index as the scrolling end position.
class IndexDestination(BaseDiv):

    def __init__(
        self, *,
        type: str = "index",
        value: typing.Optional[typing.Union[Expr, int]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            value=value,
            **kwargs,
        )

    type: str = Field(default="index")
    value: typing.Union[Expr, int] = Field(
        description="Container element index.",
    )


IndexDestination.update_forward_refs()
