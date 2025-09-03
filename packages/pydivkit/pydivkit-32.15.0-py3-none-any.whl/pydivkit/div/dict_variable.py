# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# An arbitrary object in JSON format.
class DictVariable(BaseDiv):

    def __init__(
        self, *,
        type: str = "dict",
        name: typing.Optional[typing.Union[Expr, str]] = None,
        value: typing.Optional[typing.Dict[str, typing.Any]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            name=name,
            value=value,
            **kwargs,
        )

    type: str = Field(default="dict")
    name: typing.Union[Expr, str] = Field(
        description="Variable name.",
    )
    value: typing.Dict[str, typing.Any] = Field(
        description="Value. Supports expressions for variable initialization.",
    )


DictVariable.update_forward_refs()
