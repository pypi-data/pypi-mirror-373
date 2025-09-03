# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_size_unit_value


# Element size adjusts to a parent element.
class DivMatchParentSize(BaseDiv):

    def __init__(
        self, *,
        type: str = "match_parent",
        max_size: typing.Optional[div_size_unit_value.DivSizeUnitValue] = None,
        min_size: typing.Optional[div_size_unit_value.DivSizeUnitValue] = None,
        weight: typing.Optional[typing.Union[Expr, float]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            max_size=max_size,
            min_size=min_size,
            weight=weight,
            **kwargs,
        )

    type: str = Field(default="match_parent")
    max_size: typing.Optional[div_size_unit_value.DivSizeUnitValue] = Field(
        description="Maximum size of an element.",
    )
    min_size: typing.Optional[div_size_unit_value.DivSizeUnitValue] = Field(
        description="Minimum size of an element.",
    )
    weight: typing.Optional[typing.Union[Expr, float]] = Field(
        description=(
            "Weight when distributing free space between elements with "
            "the size type`match_parent` inside an element. If the "
            "weight isn\'t specified, the elementswill divide the place "
            "equally."
        ),
    )


DivMatchParentSize.update_forward_refs()
