# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# An arbitrary array in JSON format.
class ArrayVariable(BaseDiv):

    def __init__(
        self, *,
        type: str = "array",
        name: typing.Optional[typing.Union[Expr, str]] = None,
        value: typing.Optional[typing.Sequence[typing.Any]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            name=name,
            value=value,
            **kwargs,
        )

    type: str = Field(default="array")
    name: typing.Union[Expr, str] = Field(
        description="Variable name.",
    )
    value: typing.Sequence[typing.Any] = Field(
        description="Value. Supports expressions for variable initialization.",
    )


ArrayVariable.update_forward_refs()
