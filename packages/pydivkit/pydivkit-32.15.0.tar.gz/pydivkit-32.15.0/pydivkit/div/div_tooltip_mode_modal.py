# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Modal mode. Clicks outside do not pass through to underlying elements. Restricts
# focus to the tooltip. Back button on Android and back gesture on iOS close the
# tooltip.
class DivTooltipModeModal(BaseDiv):

    def __init__(
        self, *,
        type: str = "modal",
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            **kwargs,
        )

    type: str = Field(default="modal")


DivTooltipModeModal.update_forward_refs()
