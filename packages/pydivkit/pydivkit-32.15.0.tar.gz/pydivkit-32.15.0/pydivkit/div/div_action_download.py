# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_action


# Loads additional data in `div-patch` format and updates the current element.
class DivActionDownload(BaseDiv):

    def __init__(
        self, *,
        type: str = "download",
        on_fail_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        on_success_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        url: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            on_fail_actions=on_fail_actions,
            on_success_actions=on_success_actions,
            url=url,
            **kwargs,
        )

    type: str = Field(default="download")
    on_fail_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "Actions in case of unsuccessful loading if the host "
            "reported it or the waitingtime expired."
        ),
    )
    on_success_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions in case of successful loading.",
    )
    url: typing.Union[Expr, str] = Field(
        format="uri", 
        description="Link for receiving changes.",
    )


DivActionDownload.update_forward_refs()
