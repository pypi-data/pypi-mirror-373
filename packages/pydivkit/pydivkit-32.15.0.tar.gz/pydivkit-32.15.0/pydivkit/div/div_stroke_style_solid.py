# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Solid stroke style.
class DivStrokeStyleSolid(BaseDiv):

    def __init__(
        self, *,
        type: str = "solid",
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            **kwargs,
        )

    type: str = Field(default="solid")


DivStrokeStyleSolid.update_forward_refs()
