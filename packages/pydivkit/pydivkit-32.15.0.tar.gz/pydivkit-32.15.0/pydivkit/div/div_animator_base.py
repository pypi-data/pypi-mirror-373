# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    div_action, div_animation_direction, div_animation_interpolator, div_count,
)


class DivAnimatorBase(BaseDiv):

    def __init__(
        self, *,
        cancel_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        direction: typing.Optional[typing.Union[Expr, div_animation_direction.DivAnimationDirection]] = None,
        duration: typing.Optional[typing.Union[Expr, int]] = None,
        end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        interpolator: typing.Optional[typing.Union[Expr, div_animation_interpolator.DivAnimationInterpolator]] = None,
        repeat_count: typing.Optional[div_count.DivCount] = None,
        start_delay: typing.Optional[typing.Union[Expr, int]] = None,
        variable_name: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            cancel_actions=cancel_actions,
            direction=direction,
            duration=duration,
            end_actions=end_actions,
            id=id,
            interpolator=interpolator,
            repeat_count=repeat_count,
            start_delay=start_delay,
            variable_name=variable_name,
            **kwargs,
        )

    cancel_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "Actions performed when the animation is canceled. For "
            "example, when a commandwith the \'animator_stop\' type is "
            "received."
        ),
    )
    direction: typing.Optional[typing.Union[Expr, div_animation_direction.DivAnimationDirection]] = Field(
        description=(
            "Animation direction. Determines whether the animation "
            "should be played forward,backward, or alternate between "
            "forward and backward."
        ),
    )
    duration: typing.Union[Expr, int] = Field(
        description="Animation duration in milliseconds.",
    )
    end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions when the animation is completed.",
    )
    id: typing.Union[Expr, str] = Field(
        description="Animator ID.",
    )
    interpolator: typing.Optional[typing.Union[Expr, div_animation_interpolator.DivAnimationInterpolator]] = Field(
        description="Animated value interpolation function.",
    )
    repeat_count: typing.Optional[div_count.DivCount] = Field(
        description=(
            "Number of times the animation will repeat before stopping. "
            "A value of `0` enablesinfinite looping."
        ),
    )
    start_delay: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Delay before the animation is launched in milliseconds.",
    )
    variable_name: typing.Union[Expr, str] = Field(
        description="Name of the variable being animated.",
    )


DivAnimatorBase.update_forward_refs()
