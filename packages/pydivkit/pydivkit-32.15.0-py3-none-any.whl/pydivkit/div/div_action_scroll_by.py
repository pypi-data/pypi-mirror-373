# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Scrolls the container by `item_count` or `offset` starting from the current
# position. If both values are specified, the action will be combined. For
# scrolling back, use negative values.
class DivActionScrollBy(BaseDiv):

    def __init__(
        self, *,
        type: str = "scroll_by",
        animated: typing.Optional[typing.Union[Expr, bool]] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        item_count: typing.Optional[typing.Union[Expr, int]] = None,
        offset: typing.Optional[typing.Union[Expr, int]] = None,
        overflow: typing.Optional[typing.Union[Expr, DivActionScrollByOverflow]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            animated=animated,
            id=id,
            item_count=item_count,
            offset=offset,
            overflow=overflow,
            **kwargs,
        )

    type: str = Field(default="scroll_by")
    animated: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Enables scrolling animation.",
    )
    id: typing.Union[Expr, str] = Field(
        description="ID of the element where the action should be performed.",
    )
    item_count: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Number of container elements to scroll through. For "
            "scrolling back, use negativevalues."
        ),
    )
    offset: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Scrolling distance measured in `dp` from the current "
            "position. For scrollingback, use negative values. Only "
            "applies in `gallery`."
        ),
    )
    overflow: typing.Optional[typing.Union[Expr, DivActionScrollByOverflow]] = Field(
        description=(
            "Defines navigation behavior at boundary elements:`clamp`: "
            "Stop navigation at theboundary element (default)`ring`: "
            "Navigate to the start or end, depending on thecurrent "
            "element."
        ),
    )


class DivActionScrollByOverflow(str, enum.Enum):
    CLAMP = "clamp"
    RING = "ring"


DivActionScrollBy.update_forward_refs()
