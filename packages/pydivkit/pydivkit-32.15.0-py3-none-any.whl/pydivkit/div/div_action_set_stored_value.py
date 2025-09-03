# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_typed_value


# Temporarily saves the variable in storage.
class DivActionSetStoredValue(BaseDiv):

    def __init__(
        self, *,
        type: str = "set_stored_value",
        lifetime: typing.Optional[typing.Union[Expr, int]] = None,
        name: typing.Optional[typing.Union[Expr, str]] = None,
        value: typing.Optional[div_typed_value.DivTypedValue] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            lifetime=lifetime,
            name=name,
            value=value,
            **kwargs,
        )

    type: str = Field(default="set_stored_value")
    lifetime: typing.Union[Expr, int] = Field(
        description="Duration of storage in seconds.",
    )
    name: typing.Union[Expr, str] = Field(
        description="Name of the saved variable.",
    )
    value: div_typed_value.DivTypedValue = Field(
        description="Saved value.",
    )


DivActionSetStoredValue.update_forward_refs()
