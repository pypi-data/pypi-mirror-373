# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Stops the specified animator.
class DivActionAnimatorStop(BaseDiv):

    def __init__(
        self, *,
        type: str = "animator_stop",
        animator_id: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            animator_id=animator_id,
            **kwargs,
        )

    type: str = Field(default="animator_stop")
    animator_id: typing.Union[Expr, str] = Field(
        description="ID of the animator to be stopped.",
    )


DivActionAnimatorStop.update_forward_refs()
