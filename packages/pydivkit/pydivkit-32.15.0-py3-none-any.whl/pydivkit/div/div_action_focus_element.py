# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Requests focus for an element. May require a user action on the web.
class DivActionFocusElement(BaseDiv):

    def __init__(
        self, *,
        type: str = "focus_element",
        element_id: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            element_id=element_id,
            **kwargs,
        )

    type: str = Field(default="focus_element")
    element_id: typing.Union[Expr, str] = Field(
    )


DivActionFocusElement.update_forward_refs()
