# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_fixed_size


# A mask to hide text (spoiler). Looks like randomly distributed particles, same as
# in Telegram.
class DivTextRangeMaskParticles(BaseDiv):

    def __init__(
        self, *,
        type: str = "particles",
        color: typing.Optional[typing.Union[Expr, str]] = None,
        density: typing.Optional[typing.Union[Expr, float]] = None,
        is_animated: typing.Optional[typing.Union[Expr, bool]] = None,
        is_enabled: typing.Optional[typing.Union[Expr, bool]] = None,
        particle_size: typing.Optional[div_fixed_size.DivFixedSize] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            color=color,
            density=density,
            is_animated=is_animated,
            is_enabled=is_enabled,
            particle_size=particle_size,
            **kwargs,
        )

    type: str = Field(default="particles")
    color: typing.Union[Expr, str] = Field(
        format="color", 
        description="The color of particles on the mask.",
    )
    density: typing.Optional[typing.Union[Expr, float]] = Field(
        description=(
            "The density of particles on the mask. Interpreted as the "
            "probability of aparticle to appear in a given point on the "
            "mask."
        ),
    )
    is_animated: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "Enables animation for particles on the mask. The animation "
            "looks like a smoothmovement of particles across the mask, "
            "same as in Telegram."
        ),
    )
    is_enabled: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "Controls the mask state. If set to `true`, the mask will "
            "hide the specified partof text. Otherwise, the text will be "
            "shown."
        ),
    )
    particle_size: typing.Optional[div_fixed_size.DivFixedSize] = Field(
        description="The size of a single particle on the mask.",
    )


DivTextRangeMaskParticles.update_forward_refs()
