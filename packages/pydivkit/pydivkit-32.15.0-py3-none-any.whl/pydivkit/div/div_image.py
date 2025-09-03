# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    div_accessibility, div_action, div_alignment_horizontal,
    div_alignment_vertical, div_animation, div_animator,
    div_appearance_transition, div_aspect, div_background, div_blend_mode,
    div_border, div_change_transition, div_disappear_action, div_edge_insets,
    div_extension, div_fade_transition, div_filter, div_focus, div_function,
    div_image_scale, div_layout_provider, div_size, div_tooltip, div_transform,
    div_transition_trigger, div_trigger, div_variable, div_visibility,
    div_visibility_action,
)


# Image.
class DivImage(BaseDiv):

    def __init__(
        self, *,
        type: str = "image",
        accessibility: typing.Optional[div_accessibility.DivAccessibility] = None,
        action: typing.Optional[div_action.DivAction] = None,
        action_animation: typing.Optional[div_animation.DivAnimation] = None,
        actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = None,
        alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = None,
        alpha: typing.Optional[typing.Union[Expr, float]] = None,
        animators: typing.Optional[typing.Sequence[div_animator.DivAnimator]] = None,
        appearance_animation: typing.Optional[div_fade_transition.DivFadeTransition] = None,
        aspect: typing.Optional[div_aspect.DivAspect] = None,
        background: typing.Optional[typing.Sequence[div_background.DivBackground]] = None,
        border: typing.Optional[div_border.DivBorder] = None,
        capture_focus_on_action: typing.Optional[typing.Union[Expr, bool]] = None,
        column_span: typing.Optional[typing.Union[Expr, int]] = None,
        content_alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = None,
        content_alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = None,
        disappear_actions: typing.Optional[typing.Sequence[div_disappear_action.DivDisappearAction]] = None,
        doubletap_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        extensions: typing.Optional[typing.Sequence[div_extension.DivExtension]] = None,
        filters: typing.Optional[typing.Sequence[div_filter.DivFilter]] = None,
        focus: typing.Optional[div_focus.DivFocus] = None,
        functions: typing.Optional[typing.Sequence[div_function.DivFunction]] = None,
        height: typing.Optional[div_size.DivSize] = None,
        high_priority_preview_show: typing.Optional[typing.Union[Expr, bool]] = None,
        hover_end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        hover_start_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        image_url: typing.Optional[typing.Union[Expr, str]] = None,
        layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = None,
        longtap_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        margins: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        placeholder_color: typing.Optional[typing.Union[Expr, str]] = None,
        preload_required: typing.Optional[typing.Union[Expr, bool]] = None,
        press_end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        press_start_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        preview: typing.Optional[typing.Union[Expr, str]] = None,
        reuse_id: typing.Optional[typing.Union[Expr, str]] = None,
        row_span: typing.Optional[typing.Union[Expr, int]] = None,
        scale: typing.Optional[typing.Union[Expr, div_image_scale.DivImageScale]] = None,
        selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        tint_color: typing.Optional[typing.Union[Expr, str]] = None,
        tint_mode: typing.Optional[typing.Union[Expr, div_blend_mode.DivBlendMode]] = None,
        tooltips: typing.Optional[typing.Sequence[div_tooltip.DivTooltip]] = None,
        transform: typing.Optional[div_transform.DivTransform] = None,
        transition_change: typing.Optional[div_change_transition.DivChangeTransition] = None,
        transition_in: typing.Optional[div_appearance_transition.DivAppearanceTransition] = None,
        transition_out: typing.Optional[div_appearance_transition.DivAppearanceTransition] = None,
        transition_triggers: typing.Optional[typing.Sequence[typing.Union[Expr, div_transition_trigger.DivTransitionTrigger]]] = None,
        variable_triggers: typing.Optional[typing.Sequence[div_trigger.DivTrigger]] = None,
        variables: typing.Optional[typing.Sequence[div_variable.DivVariable]] = None,
        visibility: typing.Optional[typing.Union[Expr, div_visibility.DivVisibility]] = None,
        visibility_action: typing.Optional[div_visibility_action.DivVisibilityAction] = None,
        visibility_actions: typing.Optional[typing.Sequence[div_visibility_action.DivVisibilityAction]] = None,
        width: typing.Optional[div_size.DivSize] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            accessibility=accessibility,
            action=action,
            action_animation=action_animation,
            actions=actions,
            alignment_horizontal=alignment_horizontal,
            alignment_vertical=alignment_vertical,
            alpha=alpha,
            animators=animators,
            appearance_animation=appearance_animation,
            aspect=aspect,
            background=background,
            border=border,
            capture_focus_on_action=capture_focus_on_action,
            column_span=column_span,
            content_alignment_horizontal=content_alignment_horizontal,
            content_alignment_vertical=content_alignment_vertical,
            disappear_actions=disappear_actions,
            doubletap_actions=doubletap_actions,
            extensions=extensions,
            filters=filters,
            focus=focus,
            functions=functions,
            height=height,
            high_priority_preview_show=high_priority_preview_show,
            hover_end_actions=hover_end_actions,
            hover_start_actions=hover_start_actions,
            id=id,
            image_url=image_url,
            layout_provider=layout_provider,
            longtap_actions=longtap_actions,
            margins=margins,
            paddings=paddings,
            placeholder_color=placeholder_color,
            preload_required=preload_required,
            press_end_actions=press_end_actions,
            press_start_actions=press_start_actions,
            preview=preview,
            reuse_id=reuse_id,
            row_span=row_span,
            scale=scale,
            selected_actions=selected_actions,
            tint_color=tint_color,
            tint_mode=tint_mode,
            tooltips=tooltips,
            transform=transform,
            transition_change=transition_change,
            transition_in=transition_in,
            transition_out=transition_out,
            transition_triggers=transition_triggers,
            variable_triggers=variable_triggers,
            variables=variables,
            visibility=visibility,
            visibility_action=visibility_action,
            visibility_actions=visibility_actions,
            width=width,
            **kwargs,
        )

    type: str = Field(default="image")
    accessibility: typing.Optional[div_accessibility.DivAccessibility] = Field(
        description="Accessibility settings.",
    )
    action: typing.Optional[div_action.DivAction] = Field(
        description=(
            "One action when clicking on an element. Not used if the "
            "`actions` parameter isset."
        ),
    )
    action_animation: typing.Optional[div_animation.DivAnimation] = Field(
        description=(
            "Click animation. The web only supports the following "
            "values: `fade`, `scale`,`native`, `no_animation` and `set`."
        ),
    )
    actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Multiple actions when clicking on an element.",
    )
    alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = Field(
        description=(
            "Horizontal alignment of an element inside the parent "
            "element."
        ),
    )
    alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = Field(
        description=(
            "Vertical alignment of an element inside the parent element."
        ),
    )
    alpha: typing.Optional[typing.Union[Expr, float]] = Field(
        description=(
            "Sets transparency of the entire element: `0` — completely "
            "transparent, `1` —opaque."
        ),
    )
    animators: typing.Optional[typing.Sequence[div_animator.DivAnimator]] = Field(
        description=(
            "Declaration of animators that change variable values over "
            "time."
        ),
    )
    appearance_animation: typing.Optional[div_fade_transition.DivFadeTransition] = Field(
        description="Transparency animation when loading an image.",
    )
    aspect: typing.Optional[div_aspect.DivAspect] = Field(
        description=(
            "Fixed aspect ratio. The element\'s height is calculated "
            "based on the width,ignoring the `height` value."
        ),
    )
    background: typing.Optional[typing.Sequence[div_background.DivBackground]] = Field(
        description="Element background. It can contain multiple layers.",
    )
    border: typing.Optional[div_border.DivBorder] = Field(
        description="Element stroke.",
    )
    capture_focus_on_action: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "If the value is:`true` - when the element action is "
            "activated, the focus will bemoved to that element. That "
            "means that the accessibility focus will be moved andthe "
            "virtual keyboard will be hidden, unless the target element "
            "implies itspresence (e.g. `input`).`false` - when you click "
            "on an element, the focus willremain on the currently "
            "focused element."
        ),
    )
    column_span: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Merges cells in a column of the [grid](div-grid.md) "
            "element."
        ),
    )
    content_alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = Field(
        description="Horizontal image alignment.",
    )
    content_alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = Field(
        description="Vertical image alignment.",
    )
    disappear_actions: typing.Optional[typing.Sequence[div_disappear_action.DivDisappearAction]] = Field(
        description="Actions when an element disappears from the screen.",
    )
    doubletap_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Action when double-clicking on an element.",
    )
    extensions: typing.Optional[typing.Sequence[div_extension.DivExtension]] = Field(
        description=(
            "Extensions for additional processing of an element. The "
            "list of extensions isgiven in "
            "[DivExtension](../../extensions)."
        ),
    )
    filters: typing.Optional[typing.Sequence[div_filter.DivFilter]] = Field(
        description="Image filters.",
    )
    focus: typing.Optional[div_focus.DivFocus] = Field(
        description="Parameters when focusing on an element or losing focus.",
    )
    functions: typing.Optional[typing.Sequence[div_function.DivFunction]] = Field(
        description="User functions.",
    )
    height: typing.Optional[div_size.DivSize] = Field(
        description=(
            "Element height. For Android: if there is text in this or in "
            "a child element,specify height in `sp` to scale the element "
            "together with the text. To learn moreabout units of size "
            "measurement, see [Layout inside the card](../../layout)."
        ),
    )
    high_priority_preview_show: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "It sets the priority of displaying the preview — the "
            "preview is decoded in themain stream and displayed as the "
            "first frame. Use the parameter carefully — itwill worsen "
            "the preview display time and can worsen the application "
            "launch time."
        ),
    )
    hover_end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "Actions performed after hovering over an element. Available "
            "on platforms thatsupport pointing devices (such as a mouse "
            "or stylus)."
        ),
    )
    hover_start_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "Actions performed when hovering over an element. Available "
            "on platforms thatsupport pointing devices (such as a mouse "
            "or stylus)."
        ),
    )
    id: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Element ID. It must be unique within the root element. It "
            "is used as`accessibilityIdentifier` on iOS."
        ),
    )
    image_url: typing.Union[Expr, str] = Field(
        format="uri", 
        description="Direct URL to an image.",
    )
    layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = Field(
        description="Provides data on the actual size of the element.",
    )
    longtap_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "Action when long-clicking an element. Doesn\'t work on "
            "devices that don\'t supporttouch gestures."
        ),
    )
    margins: typing.Optional[div_edge_insets.DivEdgeInsets] = Field(
        description="External margins from the element stroke.",
    )
    paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = Field(
        description="Internal margins from the element stroke.",
    )
    placeholder_color: typing.Optional[typing.Union[Expr, str]] = Field(
        format="color", 
        description="Placeholder background before the image is loaded.",
    )
    preload_required: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Background image must be loaded before the display.",
    )
    press_end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions performed after clicking/tapping an element.",
    )
    press_start_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "Actions performed at the start of a click/tap on an "
            "element."
        ),
    )
    preview: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Image preview encoded in `base64`. It will be shown instead "
            "of`placeholder_color` before the image is loaded. Format "
            "`data url`:`data:[;base64],<data>`"
        ),
    )
    reuse_id: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "ID for the div object structure. Used to optimize block "
            "reuse. See [blockreuse](../../reuse/reuse.md)."
        ),
    )
    row_span: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Merges cells in a string of the [grid](div-grid.md) "
            "element."
        ),
    )
    scale: typing.Optional[typing.Union[Expr, div_image_scale.DivImageScale]] = Field(
        description=(
            "Image scaling:`fit` places the entire image into the "
            "element (free space isfilled with background);`fill` scales "
            "the image to the element size and cuts offthe excess."
        ),
    )
    selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "List of [actions](div-action.md) to be executed when "
            "selecting an element in[pager](div-pager.md)."
        ),
    )
    tint_color: typing.Optional[typing.Union[Expr, str]] = Field(
        format="color", 
        description="New color of a contour image.",
    )
    tint_mode: typing.Optional[typing.Union[Expr, div_blend_mode.DivBlendMode]] = Field(
        description="Blend mode of the color specified in `tint_color`.",
    )
    tooltips: typing.Optional[typing.Sequence[div_tooltip.DivTooltip]] = Field(
        description=(
            "Tooltips linked to an element. A tooltip can be shown "
            "by`div-action://show_tooltip?id=`, hidden by "
            "`div-action://hide_tooltip?id=` where`id` — tooltip id."
        ),
    )
    transform: typing.Optional[div_transform.DivTransform] = Field(
        description=(
            "Applies the passed transformation to the element. Content "
            "that doesn\'t fit intothe original view area is cut off."
        ),
    )
    transition_change: typing.Optional[div_change_transition.DivChangeTransition] = Field(
        description=(
            "Change animation. It is played when the position or size of "
            "an element changes inthe new layout."
        ),
    )
    transition_in: typing.Optional[div_appearance_transition.DivAppearanceTransition] = Field(
        description=(
            "Appearance animation. It is played when an element with a "
            "new ID appears. Tolearn more about the concept of "
            "transitions, see "
            "[Animatedtransitions](../../interaction#animation/transitio"
            "n-animation)."
        ),
    )
    transition_out: typing.Optional[div_appearance_transition.DivAppearanceTransition] = Field(
        description=(
            "Disappearance animation. It is played when an element "
            "disappears in the newlayout."
        ),
    )
    transition_triggers: typing.Optional[typing.Sequence[typing.Union[Expr, div_transition_trigger.DivTransitionTrigger]]] = Field(
        min_items=1, 
        description=(
            "Animation starting triggers. Default value: `[state_change, "
            "visibility_change]`."
        ),
    )
    variable_triggers: typing.Optional[typing.Sequence[div_trigger.DivTrigger]] = Field(
        description="Triggers for changing variables within an element.",
    )
    variables: typing.Optional[typing.Sequence[div_variable.DivVariable]] = Field(
        description=(
            "Declaration of variables that can be used within an "
            "element. Variables declaredin this array can only be used "
            "within the element and its child elements."
        ),
    )
    visibility: typing.Optional[typing.Union[Expr, div_visibility.DivVisibility]] = Field(
        description="Element visibility.",
    )
    visibility_action: typing.Optional[div_visibility_action.DivVisibilityAction] = Field(
        description=(
            "Tracking visibility of a single element. Not used if the "
            "`visibility_actions`parameter is set."
        ),
    )
    visibility_actions: typing.Optional[typing.Sequence[div_visibility_action.DivVisibilityAction]] = Field(
        description="Actions when an element appears on the screen.",
    )
    width: typing.Optional[div_size.DivSize] = Field(
        description="Element width.",
    )


DivImage.update_forward_refs()
