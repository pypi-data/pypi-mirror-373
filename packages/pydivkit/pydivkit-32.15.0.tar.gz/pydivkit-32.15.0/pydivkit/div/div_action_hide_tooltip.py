# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Hides the tooltip.
class DivActionHideTooltip(BaseDiv):

    def __init__(
        self, *,
        type: str = "hide_tooltip",
        id: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            id=id,
            **kwargs,
        )

    type: str = Field(default="hide_tooltip")
    id: typing.Union[Expr, str] = Field(
        description="Tooltip ID.",
    )


DivActionHideTooltip.update_forward_refs()
