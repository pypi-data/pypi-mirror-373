# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


class DivInputValidatorBase(BaseDiv):

    def __init__(
        self, *,
        allow_empty: typing.Optional[typing.Union[Expr, bool]] = None,
        label_id: typing.Optional[typing.Union[Expr, str]] = None,
        variable: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            allow_empty=allow_empty,
            label_id=label_id,
            variable=variable,
            **kwargs,
        )

    allow_empty: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Determines whether the empty field value is valid.",
    )
    label_id: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "ID of the text element containing the error message. The "
            "message will also beused for providing access."
        ),
    )
    variable: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "The name of the variable that stores the calculation "
            "results."
        ),
    )


DivInputValidatorBase.update_forward_refs()
