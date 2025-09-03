# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Specifies the end of the container as the scrolling end position.
class EndDestination(BaseDiv):

    def __init__(
        self, *,
        type: str = "end",
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            **kwargs,
        )

    type: str = Field(default="end")


EndDestination.update_forward_refs()
