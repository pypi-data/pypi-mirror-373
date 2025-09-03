# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


class DictValue(BaseDiv):

    def __init__(
        self, *,
        type: str = "dict",
        value: typing.Optional[typing.Dict[str, typing.Any]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            value=value,
            **kwargs,
        )

    type: str = Field(default="dict")
    value: typing.Dict[str, typing.Any] = Field(
    )


DictValue.update_forward_refs()
