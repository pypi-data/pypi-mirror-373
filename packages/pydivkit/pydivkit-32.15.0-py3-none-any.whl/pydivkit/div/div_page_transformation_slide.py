# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_animation_interpolator


# Pages move without overlapping during pager scrolling.
class DivPageTransformationSlide(BaseDiv):

    def __init__(
        self, *,
        type: str = "slide",
        interpolator: typing.Optional[typing.Union[Expr, div_animation_interpolator.DivAnimationInterpolator]] = None,
        next_page_alpha: typing.Optional[typing.Union[Expr, float]] = None,
        next_page_scale: typing.Optional[typing.Union[Expr, float]] = None,
        previous_page_alpha: typing.Optional[typing.Union[Expr, float]] = None,
        previous_page_scale: typing.Optional[typing.Union[Expr, float]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            interpolator=interpolator,
            next_page_alpha=next_page_alpha,
            next_page_scale=next_page_scale,
            previous_page_alpha=previous_page_alpha,
            previous_page_scale=previous_page_scale,
            **kwargs,
        )

    type: str = Field(default="slide")
    interpolator: typing.Optional[typing.Union[Expr, div_animation_interpolator.DivAnimationInterpolator]] = Field(
        description=(
            "Animation speed adjustment. When the value is set to "
            "`spring`, it’s a dampedoscillation animation truncated to "
            "0.7, with the `damping=1` parameter. Othervalues correspond "
            "to the Bezier curve:`linear` — cubic-bezier(0, 0, 1, "
            "1)`ease` —cubic-bezier(0.25, 0.1, 0.25, 1)`ease_in` — "
            "cubic-bezier(0.42, 0, 1, 1)`ease_out`— cubic-bezier(0, 0, "
            "0.58, 1)`ease_in_out` — cubic-bezier(0.42, 0, 0.58, 1)"
        ),
    )
    next_page_alpha: typing.Optional[typing.Union[Expr, float]] = Field(
        description=(
            "Minimum transparency of the next page, within the range [0, "
            "1], when scrollingthrough the pager. The following page is "
            "always the page with a larger ordinalnumber in the `items` "
            "list, regardless of the scrolling direction."
        ),
    )
    next_page_scale: typing.Optional[typing.Union[Expr, float]] = Field(
        description=(
            "Scaling the next page during pager scrolling. The following "
            "page is always thepage with a larger ordinal number in the "
            "`items` list, regardless of thescrolling direction."
        ),
    )
    previous_page_alpha: typing.Optional[typing.Union[Expr, float]] = Field(
        description=(
            "Minimum transparency of the previous page, in the range [0, "
            "1], during pagerscrolling. The previous page is always the "
            "page with a lower ordinal number inthe `items` list, "
            "regardless of the scrolling direction."
        ),
    )
    previous_page_scale: typing.Optional[typing.Union[Expr, float]] = Field(
        description=(
            "Scaling the previous page during pager scrolling. The "
            "previous page is always thepage with a lower ordinal number "
            "in the `items` list, regardless of the scrollingdirection."
        ),
    )


DivPageTransformationSlide.update_forward_refs()
