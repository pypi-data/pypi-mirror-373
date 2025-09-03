# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Specifies the start of the container as the scrolling end position.
class StartDestination(BaseDiv):

    def __init__(
        self, *,
        type: str = "start",
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            **kwargs,
        )

    type: str = Field(default="start")


StartDestination.update_forward_refs()
