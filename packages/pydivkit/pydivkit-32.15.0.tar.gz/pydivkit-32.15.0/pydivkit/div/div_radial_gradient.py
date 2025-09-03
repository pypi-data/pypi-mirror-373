# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_radial_gradient_center, div_radial_gradient_radius


# Radial gradient.
class DivRadialGradient(BaseDiv):

    def __init__(
        self, *,
        type: str = "radial_gradient",
        center_x: typing.Optional[div_radial_gradient_center.DivRadialGradientCenter] = None,
        center_y: typing.Optional[div_radial_gradient_center.DivRadialGradientCenter] = None,
        color_map: typing.Optional[typing.Sequence[DivRadialGradientColorPoint]] = None,
        colors: typing.Optional[typing.Sequence[typing.Union[Expr, str]]] = None,
        radius: typing.Optional[div_radial_gradient_radius.DivRadialGradientRadius] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            center_x=center_x,
            center_y=center_y,
            color_map=color_map,
            colors=colors,
            radius=radius,
            **kwargs,
        )

    type: str = Field(default="radial_gradient")
    center_x: typing.Optional[div_radial_gradient_center.DivRadialGradientCenter] = Field(
        description=(
            "Shift of the central point of the gradient relative to the "
            "left edge along the Xaxis."
        ),
    )
    center_y: typing.Optional[div_radial_gradient_center.DivRadialGradientCenter] = Field(
        description=(
            "Shift of the central point of the gradient relative to the "
            "top edge along the Yaxis."
        ),
    )
    color_map: typing.Optional[typing.Sequence[DivRadialGradientColorPoint]] = Field(
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
    radius: typing.Optional[div_radial_gradient_radius.DivRadialGradientRadius] = Field(
        description="Radius of the gradient transition.",
    )


# Describes color at particular gradient position.
class DivRadialGradientColorPoint(BaseDiv):

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


DivRadialGradientColorPoint.update_forward_refs()


DivRadialGradient.update_forward_refs()
