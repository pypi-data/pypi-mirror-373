# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Manages video playback.
class DivActionVideo(BaseDiv):

    def __init__(
        self, *,
        type: str = "video",
        action: typing.Optional[typing.Union[Expr, DivActionVideoAction]] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            action=action,
            id=id,
            **kwargs,
        )

    type: str = Field(default="video")
    action: typing.Union[Expr, DivActionVideoAction] = Field(
        description=(
            "Defines the action for the video: `start` — starts playing "
            "the video if the videois ready to be played, or schedules "
            "playback`pause\' — stops the video playback"
        ),
    )
    id: typing.Union[Expr, str] = Field(
        description="Video ID.",
    )


class DivActionVideoAction(str, enum.Enum):
    START = "start"
    PAUSE = "pause"


DivActionVideo.update_forward_refs()
