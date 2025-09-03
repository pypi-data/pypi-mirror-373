# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


class DivLayoutProvider(BaseDiv):

    def __init__(
        self, *,
        height_variable_name: typing.Optional[typing.Union[Expr, str]] = None,
        width_variable_name: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            height_variable_name=height_variable_name,
            width_variable_name=width_variable_name,
            **kwargs,
        )

    height_variable_name: typing.Optional[typing.Union[Expr, str]] = Field(
        description="Name of the variable that stores the element’s height.",
    )
    width_variable_name: typing.Optional[typing.Union[Expr, str]] = Field(
        description="Name of the variable that stores the element’s width.",
    )


DivLayoutProvider.update_forward_refs()
