# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# A mask to hide text (spoiler). Looks like a rectangle filled with the color
# specified in the `color` parameter, same as in Telegram.
class DivTextRangeMaskSolid(BaseDiv):

    def __init__(
        self, *,
        type: str = "solid",
        color: typing.Optional[typing.Union[Expr, str]] = None,
        is_enabled: typing.Optional[typing.Union[Expr, bool]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            color=color,
            is_enabled=is_enabled,
            **kwargs,
        )

    type: str = Field(default="solid")
    color: typing.Union[Expr, str] = Field(
        format="color", 
        description="Color.",
    )
    is_enabled: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "Controls the mask state. If set to `true`, the mask will "
            "hide the specified partof text. Otherwise, the text will be "
            "shown."
        ),
    )


DivTextRangeMaskSolid.update_forward_refs()
