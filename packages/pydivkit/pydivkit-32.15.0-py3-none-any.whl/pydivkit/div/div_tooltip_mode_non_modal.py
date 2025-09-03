# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Non-modal mode. Clicks outside pass through to underlying elements. Does not
# restrict focus to the tooltip. Back button on Android and back gesture on iOS do
# not close the tooltip.
class DivTooltipModeNonModal(BaseDiv):

    def __init__(
        self, *,
        type: str = "non_modal",
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            **kwargs,
        )

    type: str = Field(default="non_modal")


DivTooltipModeNonModal.update_forward_refs()
