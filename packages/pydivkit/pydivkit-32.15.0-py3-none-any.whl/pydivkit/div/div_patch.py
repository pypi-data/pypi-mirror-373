# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div, div_action


# Edits the element.
class DivPatch(BaseDiv):

    def __init__(
        self, *,
        changes: typing.Optional[typing.Sequence[DivPatchChange]] = None,
        mode: typing.Optional[typing.Union[Expr, DivPatchMode]] = None,
        on_applied_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        on_failed_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            changes=changes,
            mode=mode,
            on_applied_actions=on_applied_actions,
            on_failed_actions=on_failed_actions,
            **kwargs,
        )

    changes: typing.Sequence[DivPatchChange] = Field(
        min_items=1, 
        description="Element changes.",
    )
    mode: typing.Optional[typing.Union[Expr, DivPatchMode]] = Field(
        description=(
            "Procedure for applying changes:`transactional` — if an "
            "error occurs duringapplication of at least one element, the "
            "changes aren\'t applied.`partial` — allpossible changes are "
            "applied. If there are errors, they are reported."
        ),
    )
    on_applied_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions to perform after changes are applied.",
    )
    on_failed_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "Actions to perform if there’s an error when applying "
            "changes in transaction mode."
        ),
    )


class DivPatchMode(str, enum.Enum):
    TRANSACTIONAL = "transactional"
    PARTIAL = "partial"


class DivPatchChange(BaseDiv):

    def __init__(
        self, *,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        items: typing.Optional[typing.Sequence[div.Div]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            id=id,
            items=items,
            **kwargs,
        )

    id: typing.Union[Expr, str] = Field(
        description="ID of an element to be replaced or removed.",
    )
    items: typing.Optional[typing.Sequence[div.Div]] = Field(
        description=(
            "Elements to be inserted. If the parameter isn\'t specified, "
            "the element will beremoved."
        ),
    )


DivPatchChange.update_forward_refs()


DivPatch.update_forward_refs()
