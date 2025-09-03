# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


class DivVideoSource(BaseDiv):

    def __init__(
        self, *,
        type: str = "video_source",
        bitrate: typing.Optional[typing.Union[Expr, int]] = None,
        mime_type: typing.Optional[typing.Union[Expr, str]] = None,
        resolution: typing.Optional[DivVideoSourceResolution] = None,
        url: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            bitrate=bitrate,
            mime_type=mime_type,
            resolution=resolution,
            url=url,
            **kwargs,
        )

    type: str = Field(default="video_source")
    bitrate: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Media file bitrate: Data transfer rate in a video stream, "
            "measured in kilobitsper second (kbps)."
        ),
    )
    mime_type: typing.Union[Expr, str] = Field(
        description=(
            "MIME type (Multipurpose Internet Mail Extensions): A string "
            "that defines the filetype and helps process it correctly."
        ),
    )
    resolution: typing.Optional[DivVideoSourceResolution] = Field(
        description="Media file resolution.",
    )
    url: typing.Union[Expr, str] = Field(
        format="uri", 
        description="Link to the media file available for playback or download.",
    )


# Media file resolution.
class DivVideoSourceResolution(BaseDiv):

    def __init__(
        self, *,
        type: str = "resolution",
        height: typing.Optional[typing.Union[Expr, int]] = None,
        width: typing.Optional[typing.Union[Expr, int]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            height=height,
            width=width,
            **kwargs,
        )

    type: str = Field(default="resolution")
    height: typing.Union[Expr, int] = Field(
        description="Media file frame height.",
    )
    width: typing.Union[Expr, int] = Field(
        description="Media file frame width.",
    )


DivVideoSourceResolution.update_forward_refs()


DivVideoSource.update_forward_refs()
