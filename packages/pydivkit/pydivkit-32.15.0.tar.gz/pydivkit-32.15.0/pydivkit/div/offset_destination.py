# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Specifies the position measured in `dp` from the container start as the scrolling
# end position. Only applies in `gallery`.
class OffsetDestination(BaseDiv):

    def __init__(
        self, *,
        type: str = "offset",
        value: typing.Optional[typing.Union[Expr, int]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            value=value,
            **kwargs,
        )

    type: str = Field(default="offset")
    value: typing.Union[Expr, int] = Field(
        description="Position measured in `dp`.",
    )


OffsetDestination.update_forward_refs()
