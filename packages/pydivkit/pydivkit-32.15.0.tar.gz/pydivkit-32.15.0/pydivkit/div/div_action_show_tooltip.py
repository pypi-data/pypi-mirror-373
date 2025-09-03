# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Shows the tooltip.
class DivActionShowTooltip(BaseDiv):

    def __init__(
        self, *,
        type: str = "show_tooltip",
        id: typing.Optional[typing.Union[Expr, str]] = None,
        multiple: typing.Optional[typing.Union[Expr, bool]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            id=id,
            multiple=multiple,
            **kwargs,
        )

    type: str = Field(default="show_tooltip")
    id: typing.Union[Expr, str] = Field(
        description="Tooltip ID.",
    )
    multiple: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "Sets whether the tooltip can be shown again after it’s "
            "closed."
        ),
    )


DivActionShowTooltip.update_forward_refs()
