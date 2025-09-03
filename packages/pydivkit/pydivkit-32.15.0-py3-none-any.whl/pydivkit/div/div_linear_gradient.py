# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Linear gradient.
class DivLinearGradient(BaseDiv):

    def __init__(
        self, *,
        type: str = "gradient",
        angle: typing.Optional[typing.Union[Expr, int]] = None,
        color_map: typing.Optional[typing.Sequence[DivLinearGradientColorPoint]] = None,
        colors: typing.Optional[typing.Sequence[typing.Union[Expr, str]]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            angle=angle,
            color_map=color_map,
            colors=colors,
            **kwargs,
        )

    type: str = Field(default="gradient")
    angle: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Angle of gradient direction.",
    )
    color_map: typing.Optional[typing.Sequence[DivLinearGradientColorPoint]] = Field(
        min_items=2, 
        description=(
            "Colors and positions of gradient points. When using this "
            "parameter, the `colors`parameter is ignored."
        ),
    )
    colors: typing.Optional[typing.Sequence[typing.Union[Expr, str]]] = Field(
        min_items=2, 
        description=(
            "Colors. Gradient points are located at an equal distance "
            "from each other."
        ),
    )


# Describes color at particular gradient position.
class DivLinearGradientColorPoint(BaseDiv):

    def __init__(
        self, *,
        color: typing.Optional[typing.Union[Expr, str]] = None,
        position: typing.Optional[typing.Union[Expr, float]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            color=color,
            position=position,
            **kwargs,
        )

    color: typing.Union[Expr, str] = Field(
        format="color", 
        description="Gradient color corresponding to gradient point.",
    )
    position: typing.Union[Expr, float] = Field(
        description="The position of the gradient point.",
    )


DivLinearGradientColorPoint.update_forward_refs()


DivLinearGradient.update_forward_refs()
