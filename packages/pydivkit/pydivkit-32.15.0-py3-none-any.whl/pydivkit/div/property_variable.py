# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_action, div_evaluable_type


# A property that is handeled with `get` and `set` methods.
class PropertyVariable(BaseDiv):

    def __init__(
        self, *,
        type: str = "property",
        get: typing.Optional[typing.Union[Expr, str]] = None,
        name: typing.Optional[typing.Union[Expr, str]] = None,
        new_value_variable_name: typing.Optional[typing.Union[Expr, str]] = None,
        set: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        value_type: typing.Optional[typing.Union[Expr, div_evaluable_type.DivEvaluableType]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            get=get,
            name=name,
            new_value_variable_name=new_value_variable_name,
            set=set,
            value_type=value_type,
            **kwargs,
        )

    type: str = Field(default="property")
    get: typing.Union[Expr, str] = Field(
        description="Value. Supports expressions for property initialization.",
    )
    name: typing.Union[Expr, str] = Field(
        description="Property name.",
    )
    new_value_variable_name: typing.Optional[typing.Union[Expr, str]] = Field(
        description="Name for accessing the data passed to the setter.",
    )
    set: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Action when setting a property.",
    )
    value_type: typing.Union[Expr, div_evaluable_type.DivEvaluableType] = Field(
    )


PropertyVariable.update_forward_refs()
