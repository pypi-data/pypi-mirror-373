# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Dashed stroke style.
class DivStrokeStyleDashed(BaseDiv):

    def __init__(
        self, *,
        type: str = "dashed",
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            **kwargs,
        )

    type: str = Field(default="dashed")


DivStrokeStyleDashed.update_forward_refs()
