# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# Controls the timer.
class DivActionTimer(BaseDiv):

    def __init__(
        self, *,
        type: str = "timer",
        action: typing.Optional[typing.Union[Expr, DivActionTimerAction]] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            action=action,
            id=id,
            **kwargs,
        )

    type: str = Field(default="timer")
    action: typing.Union[Expr, DivActionTimerAction] = Field(
        description=(
            "Timer actions:`start` — starts the timer from a stopped "
            "state`stop`— stops thetimer and performs the `onEnd` "
            "action`pause` — pauses the timer, saves thecurrent "
            "time`resume` — restarts the timer after a pause`cancel` — "
            "interrupts thetimer, resets the time`reset` — cancels the "
            "timer, then starts it again"
        ),
    )
    id: typing.Union[Expr, str] = Field(
        description="Timer ID.",
    )


class DivActionTimerAction(str, enum.Enum):
    START = "start"
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    RESET = "reset"


DivActionTimer.update_forward_refs()
