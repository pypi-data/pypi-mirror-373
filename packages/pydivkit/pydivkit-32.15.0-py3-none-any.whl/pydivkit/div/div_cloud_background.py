# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_edge_insets


# Cloud-style text background. Rows have a rectangular background in the specified
# color with rounded corners.
class DivCloudBackground(BaseDiv):

    def __init__(
        self, *,
        type: str = "cloud",
        color: typing.Optional[typing.Union[Expr, str]] = None,
        corner_radius: typing.Optional[typing.Union[Expr, int]] = None,
        paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            color=color,
            corner_radius=corner_radius,
            paddings=paddings,
            **kwargs,
        )

    type: str = Field(default="cloud")
    color: typing.Union[Expr, str] = Field(
        format="color", 
        description="Fill color.",
    )
    corner_radius: typing.Union[Expr, int] = Field(
        description="Corner rounding radius.",
    )
    paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = Field(
        description="Margins between the row border and background border.",
    )


DivCloudBackground.update_forward_refs()
