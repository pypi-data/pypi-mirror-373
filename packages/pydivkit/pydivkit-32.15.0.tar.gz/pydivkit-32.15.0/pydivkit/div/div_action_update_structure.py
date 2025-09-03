# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_typed_value


# Set values ​​in a variable of type array or dictionary with different nesting.
class DivActionUpdateStructure(BaseDiv):

    def __init__(
        self, *,
        type: str = "update_structure",
        path: typing.Optional[typing.Union[Expr, str]] = None,
        value: typing.Optional[div_typed_value.DivTypedValue] = None,
        variable_name: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            path=path,
            value=value,
            variable_name=variable_name,
            **kwargs,
        )

    type: str = Field(default="update_structure")
    path: typing.Union[Expr, str] = Field(
        description=(
            "Path within an array/dictionary where a value needs to be "
            "set. Path format: Eachpath element is separated by a \'/\' "
            "symbol.Path elements can be of two types: anindex of an "
            "element in an array, starting from 0 or dictionary keys in "
            "the formof arbitrary strings.The path is read from left to "
            "right, each element determinesthe transition to the next "
            "level of nesting.Example path: `key/0/inner_key/1`."
        ),
    )
    value: div_typed_value.DivTypedValue = Field(
        description="Value set into dictionary/array.",
    )
    variable_name: typing.Union[Expr, str] = Field(
        description="Variable name of array or dictionary type.",
    )


DivActionUpdateStructure.update_forward_refs()
