# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Removes focus from an element.
class DivActionClearFocus(BaseDiv):

    def __init__(
        self, *,
        type: str = "clear_focus",
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            **kwargs,
        )

    type: str = Field(default="clear_focus")


DivActionClearFocus.update_forward_refs()
