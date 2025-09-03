# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Mask for entering phone numbers with dynamic regional format identification.
class DivPhoneInputMask(BaseDiv):

    def __init__(
        self, *,
        type: str = "phone",
        raw_text_variable: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            raw_text_variable=raw_text_variable,
            **kwargs,
        )

    type: str = Field(default="phone")
    raw_text_variable: typing.Union[Expr, str] = Field(
        description="Name of the variable to store the unprocessed value.",
    )


DivPhoneInputMask.update_forward_refs()
