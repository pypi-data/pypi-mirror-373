# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    div_action, div_animation_direction, div_animation_interpolator, div_count,
)


# Numeric value animator.
class DivNumberAnimator(BaseDiv):

    def __init__(
        self, *,
        type: str = "number_animator",
        cancel_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        direction: typing.Optional[typing.Union[Expr, div_animation_direction.DivAnimationDirection]] = None,
        duration: typing.Optional[typing.Union[Expr, int]] = None,
        end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        end_value: typing.Optional[typing.Union[Expr, float]] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        interpolator: typing.Optional[typing.Union[Expr, div_animation_interpolator.DivAnimationInterpolator]] = None,
        repeat_count: typing.Optional[div_count.DivCount] = None,
        start_delay: typing.Optional[typing.Union[Expr, int]] = None,
        start_value: typing.Optional[typing.Union[Expr, float]] = None,
        variable_name: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            cancel_actions=cancel_actions,
            direction=direction,
            duration=duration,
            end_actions=end_actions,
            end_value=end_value,
            id=id,
            interpolator=interpolator,
            repeat_count=repeat_count,
            start_delay=start_delay,
            start_value=start_value,
            variable_name=variable_name,
            **kwargs,
        )

    type: str = Field(default="number_animator")
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
    end_value: typing.Union[Expr, float] = Field(
        description="The value the variable will have when the animation ends.",
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
    start_value: typing.Optional[typing.Union[Expr, float]] = Field(
        description=(
            "The value the variable will have when the animation starts. "
            "If the property isn\'tspecified, the current value of the "
            "variable will be used."
        ),
    )
    variable_name: typing.Union[Expr, str] = Field(
        description="Name of the variable being animated.",
    )


DivNumberAnimator.update_forward_refs()
