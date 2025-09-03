# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_size_unit_value


# The size of an element adjusts to its contents.
class DivWrapContentSize(BaseDiv):

    def __init__(
        self, *,
        type: str = "wrap_content",
        constrained: typing.Optional[typing.Union[Expr, bool]] = None,
        max_size: typing.Optional[div_size_unit_value.DivSizeUnitValue] = None,
        min_size: typing.Optional[div_size_unit_value.DivSizeUnitValue] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            constrained=constrained,
            max_size=max_size,
            min_size=min_size,
            **kwargs,
        )

    type: str = Field(default="wrap_content")
    constrained: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "The final size mustn\'t exceed the parent one. On iOS and "
            "in a default browser`false`. On Android always `true`."
        ),
    )
    max_size: typing.Optional[div_size_unit_value.DivSizeUnitValue] = Field(
        description="Maximum size of an element.",
    )
    min_size: typing.Optional[div_size_unit_value.DivSizeUnitValue] = Field(
        description="Minimum size of an element.",
    )


DivWrapContentSize.update_forward_refs()
