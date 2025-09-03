# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# The page size is equal to the size of its content.
class DivPageContentSize(BaseDiv):

    def __init__(
        self, *,
        type: str = "wrap_content",
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            **kwargs,
        )

    type: str = Field(default="wrap_content")


DivPageContentSize.update_forward_refs()
