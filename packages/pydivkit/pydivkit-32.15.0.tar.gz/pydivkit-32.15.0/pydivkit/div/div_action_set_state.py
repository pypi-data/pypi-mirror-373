# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Applies a new appearance to the content in `div-state'.
class DivActionSetState(BaseDiv):

    def __init__(
        self, *,
        type: str = "set_state",
        state_id: typing.Optional[typing.Union[Expr, str]] = None,
        temporary: typing.Optional[typing.Union[Expr, bool]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            state_id=state_id,
            temporary=temporary,
            **kwargs,
        )

    type: str = Field(default="set_state")
    state_id: typing.Union[Expr, str] = Field(
        description=(
            "The path of the state inside `state` that needs to be "
            "activated. Set in theformat "
            "`div_data_state_id/id/state_id\'. Can be "
            "hierarchical:`div_data_state_id/id_1/state_id_1/../id_n/sta"
            "te_id_n`. Consistsof:`div_data_state_id` — the numeric "
            "value of the `state_id` of the `state`object in `data`\'id` "
            "— the `id` value of the `state` object`state_id` — "
            "the`state_id` value of the `state` object in `state`"
        ),
    )
    temporary: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "Indicates a state change:`true` — the change is temporary "
            "and will switch to theoriginal one (default value) when the "
            "element is recreated`false` — the change ispermanent"
        ),
    )


DivActionSetState.update_forward_refs()
