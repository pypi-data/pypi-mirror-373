# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_action_scroll_destination


# Scrolls to a position or switches to the container element specified by the
# `destination` parameter.
class DivActionScrollTo(BaseDiv):

    def __init__(
        self, *,
        type: str = "scroll_to",
        animated: typing.Optional[typing.Union[Expr, bool]] = None,
        destination: typing.Optional[div_action_scroll_destination.DivActionScrollDestination] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            animated=animated,
            destination=destination,
            id=id,
            **kwargs,
        )

    type: str = Field(default="scroll_to")
    animated: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Enables scrolling animation.",
    )
    destination: div_action_scroll_destination.DivActionScrollDestination = Field(
        description=(
            "Defines the scrolling end position:`index`: Scroll to the "
            "element with the indexprovided in `value``offset`: Scroll "
            "to the position specified in `value` andmeasured in `dp` "
            "from the start of the container. Applies only "
            "in`gallery`;`start`: Scroll to the container start;`end`: "
            "Scroll to the containerend."
        ),
    )
    id: typing.Union[Expr, str] = Field(
        description="ID of the element where the action should be performed.",
    )


DivActionScrollTo.update_forward_refs()
