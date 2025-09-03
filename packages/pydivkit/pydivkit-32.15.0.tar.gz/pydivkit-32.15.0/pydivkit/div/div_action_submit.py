# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_action


# Sends variables from the container by link. Data sending configuration can be
# defined by the host app. By default, variables are sent as JSON in the request
# body using the POST method.
class DivActionSubmit(BaseDiv):

    def __init__(
        self, *,
        type: str = "submit",
        container_id: typing.Optional[typing.Union[Expr, str]] = None,
        on_fail_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        on_success_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        request: typing.Optional[DivActionSubmitRequest] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            container_id=container_id,
            on_fail_actions=on_fail_actions,
            on_success_actions=on_success_actions,
            request=request,
            **kwargs,
        )

    type: str = Field(default="submit")
    container_id: typing.Union[Expr, str] = Field(
        description="ID of the container with the variables to be sent.",
    )
    on_fail_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions when sending data is unsuccessful.",
    )
    on_success_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions when sending data is successful.",
    )
    request: DivActionSubmitRequest = Field(
        description=(
            "HTTP request parameters for configuring the sending of "
            "data."
        ),
    )


# HTTP request parameters for configuring the sending of data.
class DivActionSubmitRequest(BaseDiv):

    def __init__(
        self, *,
        headers: typing.Optional[typing.Sequence[RequestHeader]] = None,
        method: typing.Optional[typing.Union[Expr, RequestMethod]] = None,
        url: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            headers=headers,
            method=method,
            url=url,
            **kwargs,
        )

    headers: typing.Optional[typing.Sequence[RequestHeader]] = Field(
        description=(
            "HTTP request headers. Please note that DivKit does not "
            "clean duplicate headers,which can lead to errors in request "
            "processing. Keep this in mind when assemblingactions with "
            "complex JSON-builders."
        ),
    )
    method: typing.Optional[typing.Union[Expr, RequestMethod]] = Field(
        description="HTTP request method.",
    )
    url: typing.Union[Expr, str] = Field(
        format="uri", 
        description="Link for sending data from the container.",
    )


class RequestMethod(str, enum.Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    HEAD = "head"
    OPTIONS = "options"


class RequestHeader(BaseDiv):

    def __init__(
        self, *,
        name: typing.Optional[typing.Union[Expr, str]] = None,
        value: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            name=name,
            value=value,
            **kwargs,
        )

    name: typing.Union[Expr, str] = Field(
    )
    value: typing.Union[Expr, str] = Field(
    )


RequestHeader.update_forward_refs()


DivActionSubmitRequest.update_forward_refs()


DivActionSubmit.update_forward_refs()
