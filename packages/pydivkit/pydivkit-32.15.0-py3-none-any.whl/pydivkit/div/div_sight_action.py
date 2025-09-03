# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_action_typed, div_download_callbacks


class DivSightAction(BaseDiv):

    def __init__(
        self, *,
        download_callbacks: typing.Optional[div_download_callbacks.DivDownloadCallbacks] = None,
        is_enabled: typing.Optional[typing.Union[Expr, bool]] = None,
        log_id: typing.Optional[typing.Union[Expr, str]] = None,
        log_limit: typing.Optional[typing.Union[Expr, int]] = None,
        payload: typing.Optional[typing.Dict[str, typing.Any]] = None,
        referer: typing.Optional[typing.Union[Expr, str]] = None,
        scope_id: typing.Optional[typing.Union[Expr, str]] = None,
        typed: typing.Optional[div_action_typed.DivActionTyped] = None,
        url: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            download_callbacks=download_callbacks,
            is_enabled=is_enabled,
            log_id=log_id,
            log_limit=log_limit,
            payload=payload,
            referer=referer,
            scope_id=scope_id,
            typed=typed,
            url=url,
            **kwargs,
        )

    download_callbacks: typing.Optional[div_download_callbacks.DivDownloadCallbacks] = Field(
        description=(
            "Callbacks that are called after [data "
            "loading](../../interaction#loading-data)."
        ),
    )
    is_enabled: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "The parameter disables the action. Disabled actions stop "
            "listening to theirassociated event (clicks, changes in "
            "visibility, and so on)."
        ),
    )
    log_id: typing.Union[Expr, str] = Field(
        description="Logging ID.",
    )
    log_limit: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Limit on the number of loggings. If `0`, the limit is "
            "removed."
        ),
    )
    payload: typing.Optional[typing.Dict[str, typing.Any]] = Field(
        description="Additional parameters, passed to the host application.",
    )
    referer: typing.Optional[typing.Union[Expr, str]] = Field(
        format="uri", 
        description="Referer URL for logging.",
    )
    scope_id: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "The ID of the element within which the specified action "
            "will be performed."
        ),
    )
    typed: typing.Optional[div_action_typed.DivActionTyped] = Field(
    )
    url: typing.Optional[typing.Union[Expr, str]] = Field(
        format="uri", 
        description=(
            "URL. Possible values: `url` or `div-action://`. To learn "
            "more, see [Interactionwith elements](../../interaction)."
        ),
    )


DivSightAction.update_forward_refs()
