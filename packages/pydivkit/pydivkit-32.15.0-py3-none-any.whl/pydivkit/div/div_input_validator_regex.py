# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Regex validator.
class DivInputValidatorRegex(BaseDiv):

    def __init__(
        self, *,
        type: str = "regex",
        allow_empty: typing.Optional[typing.Union[Expr, bool]] = None,
        label_id: typing.Optional[typing.Union[Expr, str]] = None,
        pattern: typing.Optional[typing.Union[Expr, str]] = None,
        variable: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            allow_empty=allow_empty,
            label_id=label_id,
            pattern=pattern,
            variable=variable,
            **kwargs,
        )

    type: str = Field(default="regex")
    allow_empty: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Determines whether the empty field value is valid.",
    )
    label_id: typing.Union[Expr, str] = Field(
        description=(
            "ID of the text element containing the error message. The "
            "message will also beused for providing access."
        ),
    )
    pattern: typing.Union[Expr, str] = Field(
        description=(
            "A regular expression (pattern) that the field value must "
            "match."
        ),
    )
    variable: typing.Union[Expr, str] = Field(
        description=(
            "The name of the variable that stores the calculation "
            "results."
        ),
    )


DivInputValidatorRegex.update_forward_refs()
