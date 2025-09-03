# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    div_accessibility, div_action, div_alignment_horizontal,
    div_alignment_vertical, div_animation, div_animator,
    div_appearance_transition, div_background, div_blend_mode, div_border,
    div_change_transition, div_disappear_action, div_edge_insets, div_extension,
    div_fixed_size, div_focus, div_font_weight, div_function,
    div_layout_provider, div_line_style, div_shadow, div_size, div_size_unit,
    div_text_alignment_vertical, div_text_gradient, div_text_range_background,
    div_text_range_border, div_text_range_mask, div_tooltip, div_transform,
    div_transition_trigger, div_trigger, div_variable, div_visibility,
    div_visibility_action,
)


# Text.
class DivText(BaseDiv):

    def __init__(
        self, *,
        type: str = "text",
        accessibility: typing.Optional[div_accessibility.DivAccessibility] = None,
        action: typing.Optional[div_action.DivAction] = None,
        action_animation: typing.Optional[div_animation.DivAnimation] = None,
        actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = None,
        alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = None,
        alpha: typing.Optional[typing.Union[Expr, float]] = None,
        animators: typing.Optional[typing.Sequence[div_animator.DivAnimator]] = None,
        auto_ellipsize: typing.Optional[typing.Union[Expr, bool]] = None,
        background: typing.Optional[typing.Sequence[div_background.DivBackground]] = None,
        border: typing.Optional[div_border.DivBorder] = None,
        capture_focus_on_action: typing.Optional[typing.Union[Expr, bool]] = None,
        column_span: typing.Optional[typing.Union[Expr, int]] = None,
        disappear_actions: typing.Optional[typing.Sequence[div_disappear_action.DivDisappearAction]] = None,
        doubletap_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        ellipsis: typing.Optional[DivTextEllipsis] = None,
        extensions: typing.Optional[typing.Sequence[div_extension.DivExtension]] = None,
        focus: typing.Optional[div_focus.DivFocus] = None,
        focused_text_color: typing.Optional[typing.Union[Expr, str]] = None,
        font_family: typing.Optional[typing.Union[Expr, str]] = None,
        font_feature_settings: typing.Optional[typing.Union[Expr, str]] = None,
        font_size: typing.Optional[typing.Union[Expr, int]] = None,
        font_size_unit: typing.Optional[typing.Union[Expr, div_size_unit.DivSizeUnit]] = None,
        font_variation_settings: typing.Optional[typing.Dict[str, typing.Any]] = None,
        font_weight: typing.Optional[typing.Union[Expr, div_font_weight.DivFontWeight]] = None,
        font_weight_value: typing.Optional[typing.Union[Expr, int]] = None,
        functions: typing.Optional[typing.Sequence[div_function.DivFunction]] = None,
        height: typing.Optional[div_size.DivSize] = None,
        hover_end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        hover_start_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        images: typing.Optional[typing.Sequence[DivTextImage]] = None,
        layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = None,
        letter_spacing: typing.Optional[typing.Union[Expr, float]] = None,
        line_height: typing.Optional[typing.Union[Expr, int]] = None,
        longtap_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        margins: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        max_lines: typing.Optional[typing.Union[Expr, int]] = None,
        min_hidden_lines: typing.Optional[typing.Union[Expr, int]] = None,
        paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        press_end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        press_start_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        ranges: typing.Optional[typing.Sequence[DivTextRange]] = None,
        reuse_id: typing.Optional[typing.Union[Expr, str]] = None,
        row_span: typing.Optional[typing.Union[Expr, int]] = None,
        selectable: typing.Optional[typing.Union[Expr, bool]] = None,
        selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        strike: typing.Optional[typing.Union[Expr, div_line_style.DivLineStyle]] = None,
        text: typing.Optional[typing.Union[Expr, str]] = None,
        text_alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = None,
        text_alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = None,
        text_color: typing.Optional[typing.Union[Expr, str]] = None,
        text_gradient: typing.Optional[div_text_gradient.DivTextGradient] = None,
        text_shadow: typing.Optional[div_shadow.DivShadow] = None,
        tighten_width: typing.Optional[typing.Union[Expr, bool]] = None,
        tooltips: typing.Optional[typing.Sequence[div_tooltip.DivTooltip]] = None,
        transform: typing.Optional[div_transform.DivTransform] = None,
        transition_change: typing.Optional[div_change_transition.DivChangeTransition] = None,
        transition_in: typing.Optional[div_appearance_transition.DivAppearanceTransition] = None,
        transition_out: typing.Optional[div_appearance_transition.DivAppearanceTransition] = None,
        transition_triggers: typing.Optional[typing.Sequence[typing.Union[Expr, div_transition_trigger.DivTransitionTrigger]]] = None,
        truncate: typing.Optional[typing.Union[Expr, DivTextTruncate]] = None,
        underline: typing.Optional[typing.Union[Expr, div_line_style.DivLineStyle]] = None,
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
            auto_ellipsize=auto_ellipsize,
            background=background,
            border=border,
            capture_focus_on_action=capture_focus_on_action,
            column_span=column_span,
            disappear_actions=disappear_actions,
            doubletap_actions=doubletap_actions,
            ellipsis=ellipsis,
            extensions=extensions,
            focus=focus,
            focused_text_color=focused_text_color,
            font_family=font_family,
            font_feature_settings=font_feature_settings,
            font_size=font_size,
            font_size_unit=font_size_unit,
            font_variation_settings=font_variation_settings,
            font_weight=font_weight,
            font_weight_value=font_weight_value,
            functions=functions,
            height=height,
            hover_end_actions=hover_end_actions,
            hover_start_actions=hover_start_actions,
            id=id,
            images=images,
            layout_provider=layout_provider,
            letter_spacing=letter_spacing,
            line_height=line_height,
            longtap_actions=longtap_actions,
            margins=margins,
            max_lines=max_lines,
            min_hidden_lines=min_hidden_lines,
            paddings=paddings,
            press_end_actions=press_end_actions,
            press_start_actions=press_start_actions,
            ranges=ranges,
            reuse_id=reuse_id,
            row_span=row_span,
            selectable=selectable,
            selected_actions=selected_actions,
            strike=strike,
            text=text,
            text_alignment_horizontal=text_alignment_horizontal,
            text_alignment_vertical=text_alignment_vertical,
            text_color=text_color,
            text_gradient=text_gradient,
            text_shadow=text_shadow,
            tighten_width=tighten_width,
            tooltips=tooltips,
            transform=transform,
            transition_change=transition_change,
            transition_in=transition_in,
            transition_out=transition_out,
            transition_triggers=transition_triggers,
            truncate=truncate,
            underline=underline,
            variable_triggers=variable_triggers,
            variables=variables,
            visibility=visibility,
            visibility_action=visibility_action,
            visibility_actions=visibility_actions,
            width=width,
            **kwargs,
        )

    type: str = Field(default="text")
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
    auto_ellipsize: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Automatic text cropping to fit the container size.",
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
    disappear_actions: typing.Optional[typing.Sequence[div_disappear_action.DivDisappearAction]] = Field(
        description="Actions when an element disappears from the screen.",
    )
    doubletap_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Action when double-clicking on an element.",
    )
    ellipsis: typing.Optional[DivTextEllipsis] = Field(
        description=(
            "Text cropping marker. It is displayed when text size "
            "exceeds the limit on thenumber of lines."
        ),
    )
    extensions: typing.Optional[typing.Sequence[div_extension.DivExtension]] = Field(
        description=(
            "Extensions for additional processing of an element. The "
            "list of extensions isgiven in "
            "[DivExtension](../../extensions)."
        ),
    )
    focus: typing.Optional[div_focus.DivFocus] = Field(
        description="Parameters when focusing on an element or losing focus.",
    )
    focused_text_color: typing.Optional[typing.Union[Expr, str]] = Field(
        format="color", 
        description="Text color when focusing on the element.",
    )
    font_family: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Font family:`text` — a standard text font;`display` — a "
            "family of fonts with alarge font size."
        ),
    )
    font_feature_settings: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "List of OpenType font features. The format matches the CSS "
            "attribute\"font-feature-settings\". Learn "
            "more:https://www.w3.org/TR/css-fonts-3/#font-feature-settin"
            "gs-prop"
        ),
    )
    font_size: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Font size.",
    )
    font_size_unit: typing.Optional[typing.Union[Expr, div_size_unit.DivSizeUnit]] = Field(
        description=(
            "Unit of measurement:`px` — a physical pixel.`dp` — a "
            "logical pixel that doesn\'tdepend on screen density.`sp` — "
            "a logical pixel that depends on the font size ona device. "
            "Specify height in `sp`. Only available on Android."
        ),
    )
    font_variation_settings: typing.Optional[typing.Dict[str, typing.Any]] = Field(
        description=(
            "List of TrueType/OpenType font features. The object is "
            "constructed from pairs ofaxis tag and style values. The "
            "axis tag must contain four ASCII characters."
        ),
    )
    font_weight: typing.Optional[typing.Union[Expr, div_font_weight.DivFontWeight]] = Field(
        description="Style.",
    )
    font_weight_value: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Style. Numeric value.",
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
    images: typing.Optional[typing.Sequence[DivTextImage]] = Field(
        description="Images embedded in text.",
    )
    layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = Field(
        description="Provides data on the actual size of the element.",
    )
    letter_spacing: typing.Optional[typing.Union[Expr, float]] = Field(
        description="Spacing between characters.",
    )
    line_height: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Line spacing of the text.",
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
    max_lines: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Maximum number of lines not to be cropped when breaking the "
            "limits."
        ),
    )
    min_hidden_lines: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Minimum number of cropped lines when breaking the limits.",
    )
    paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = Field(
        description="Internal margins from the element stroke.",
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
    ranges: typing.Optional[typing.Sequence[DivTextRange]] = Field(
        description=(
            "A character range in which additional style parameters can "
            "be set. Defined bymandatory `start` and `end` fields."
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
    selectable: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Ability to select and copy text.",
    )
    selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "List of [actions](div-action.md) to be executed when "
            "selecting an element in[pager](div-pager.md)."
        ),
    )
    strike: typing.Optional[typing.Union[Expr, div_line_style.DivLineStyle]] = Field(
        description="Strikethrough.",
    )
    text: typing.Union[Expr, str] = Field(
        description="Text.",
    )
    text_alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = Field(
        description="Horizontal text alignment.",
    )
    text_alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = Field(
        description="Vertical text alignment.",
    )
    text_color: typing.Optional[typing.Union[Expr, str]] = Field(
        format="color", 
        description="Text color.",
    )
    text_gradient: typing.Optional[div_text_gradient.DivTextGradient] = Field(
        description="Gradient text color.",
    )
    text_shadow: typing.Optional[div_shadow.DivShadow] = Field(
        description="Parameters of the shadow applied to the text.",
    )
    tighten_width: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "Limit the text width to the maximum line width. Applies "
            "only when the width isset to `wrap_content`, "
            "`constrained=true`, and `max_size` is specified."
        ),
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
    truncate: typing.Optional[typing.Union[Expr, DivTextTruncate]] = Field(
        description="Location of text cropping marker.",
    )
    underline: typing.Optional[typing.Union[Expr, div_line_style.DivLineStyle]] = Field(
        description="Underline.",
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


class DivTextTruncate(str, enum.Enum):
    NONE = "none"
    START = "start"
    END = "end"
    MIDDLE = "middle"


# Text cropping marker. It is displayed when text size exceeds the limit on the
# number of lines.
class DivTextEllipsis(BaseDiv):

    def __init__(
        self, *,
        actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        images: typing.Optional[typing.Sequence[DivTextImage]] = None,
        ranges: typing.Optional[typing.Sequence[DivTextRange]] = None,
        text: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            actions=actions,
            images=images,
            ranges=ranges,
            text=text,
            **kwargs,
        )

    actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions when clicking on a crop marker.",
    )
    images: typing.Optional[typing.Sequence[DivTextImage]] = Field(
        description="Images embedded in a crop marker.",
    )
    ranges: typing.Optional[typing.Sequence[DivTextRange]] = Field(
        description=(
            "Character ranges inside a crop marker with different text "
            "styles."
        ),
    )
    text: typing.Union[Expr, str] = Field(
        description="Marker text.",
    )


DivTextEllipsis.update_forward_refs()


# Image.
class DivTextImage(BaseDiv):

    def __init__(
        self, *,
        accessibility: typing.Optional[ImageAccessibility] = None,
        alignment_vertical: typing.Optional[typing.Union[Expr, div_text_alignment_vertical.DivTextAlignmentVertical]] = None,
        height: typing.Optional[div_fixed_size.DivFixedSize] = None,
        indexing_direction: typing.Optional[typing.Union[Expr, ImageIndexingDirection]] = None,
        preload_required: typing.Optional[typing.Union[Expr, bool]] = None,
        start: typing.Optional[typing.Union[Expr, int]] = None,
        tint_color: typing.Optional[typing.Union[Expr, str]] = None,
        tint_mode: typing.Optional[typing.Union[Expr, div_blend_mode.DivBlendMode]] = None,
        url: typing.Optional[typing.Union[Expr, str]] = None,
        width: typing.Optional[div_fixed_size.DivFixedSize] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            accessibility=accessibility,
            alignment_vertical=alignment_vertical,
            height=height,
            indexing_direction=indexing_direction,
            preload_required=preload_required,
            start=start,
            tint_color=tint_color,
            tint_mode=tint_mode,
            url=url,
            width=width,
            **kwargs,
        )

    accessibility: typing.Optional[ImageAccessibility] = Field(
    )
    alignment_vertical: typing.Optional[typing.Union[Expr, div_text_alignment_vertical.DivTextAlignmentVertical]] = Field(
        description="Vertical image alignment within the row.",
    )
    height: typing.Optional[div_fixed_size.DivFixedSize] = Field(
        description="Image height.",
    )
    indexing_direction: typing.Optional[typing.Union[Expr, ImageIndexingDirection]] = Field(
        description=(
            "Defines the direction in the `start` parameter:– `normal` "
            "is for regular stringindexing ([0, 1, 2, ..., N]). Use it "
            "if you need to insert an image by indexrelative to the "
            "beginning of a string.– `reversed` is for indexing a string "
            "fromthe end to the beginning ([N, ..., 2, 1, 0]). Use it if "
            "you need to insert animage by index relative to the end of "
            "a string."
        ),
    )
    preload_required: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Background image must be loaded before the display.",
    )
    start: typing.Union[Expr, int] = Field(
        description=(
            "A symbol to insert prior to an image. To insert an image at "
            "the end of the text,specify the number of the last "
            "character plus one."
        ),
    )
    tint_color: typing.Optional[typing.Union[Expr, str]] = Field(
        format="color", 
        description="New color of a contour image.",
    )
    tint_mode: typing.Optional[typing.Union[Expr, div_blend_mode.DivBlendMode]] = Field(
        description="Blend mode of the color specified in `tint_color`.",
    )
    url: typing.Union[Expr, str] = Field(
        format="uri", 
        description="Image URL.",
    )
    width: typing.Optional[div_fixed_size.DivFixedSize] = Field(
        description="Image width.",
    )


class ImageIndexingDirection(str, enum.Enum):
    NORMAL = "normal"
    REVERSED = "reversed"


class ImageAccessibility(BaseDiv):

    def __init__(
        self, *,
        description: typing.Optional[typing.Union[Expr, str]] = None,
        type: typing.Optional[typing.Union[Expr, AccessibilityType]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            description=description,
            type=type,
            **kwargs,
        )

    description: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Element description. It is used as the main description for "
            "screen readingapplications."
        ),
    )
    type: typing.Optional[typing.Union[Expr, AccessibilityType]] = Field(
        description=(
            "Element role. Used to correctly identify an element by the "
            "accessibility service.For example, the `list` element is "
            "used to group list elements into one element."
        ),
    )


class AccessibilityType(str, enum.Enum):
    NONE = "none"
    BUTTON = "button"
    IMAGE = "image"
    TEXT = "text"
    AUTO = "auto"


ImageAccessibility.update_forward_refs()


DivTextImage.update_forward_refs()


# Additional parameters of the character range.
class DivTextRange(BaseDiv):

    def __init__(
        self, *,
        actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        alignment_vertical: typing.Optional[typing.Union[Expr, div_text_alignment_vertical.DivTextAlignmentVertical]] = None,
        background: typing.Optional[div_text_range_background.DivTextRangeBackground] = None,
        baseline_offset: typing.Optional[typing.Union[Expr, float]] = None,
        border: typing.Optional[div_text_range_border.DivTextRangeBorder] = None,
        end: typing.Optional[typing.Union[Expr, int]] = None,
        font_family: typing.Optional[typing.Union[Expr, str]] = None,
        font_feature_settings: typing.Optional[typing.Union[Expr, str]] = None,
        font_size: typing.Optional[typing.Union[Expr, int]] = None,
        font_size_unit: typing.Optional[typing.Union[Expr, div_size_unit.DivSizeUnit]] = None,
        font_variation_settings: typing.Optional[typing.Dict[str, typing.Any]] = None,
        font_weight: typing.Optional[typing.Union[Expr, div_font_weight.DivFontWeight]] = None,
        font_weight_value: typing.Optional[typing.Union[Expr, int]] = None,
        letter_spacing: typing.Optional[typing.Union[Expr, float]] = None,
        line_height: typing.Optional[typing.Union[Expr, int]] = None,
        mask: typing.Optional[div_text_range_mask.DivTextRangeMask] = None,
        start: typing.Optional[typing.Union[Expr, int]] = None,
        strike: typing.Optional[typing.Union[Expr, div_line_style.DivLineStyle]] = None,
        text_color: typing.Optional[typing.Union[Expr, str]] = None,
        text_shadow: typing.Optional[div_shadow.DivShadow] = None,
        top_offset: typing.Optional[typing.Union[Expr, int]] = None,
        underline: typing.Optional[typing.Union[Expr, div_line_style.DivLineStyle]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            actions=actions,
            alignment_vertical=alignment_vertical,
            background=background,
            baseline_offset=baseline_offset,
            border=border,
            end=end,
            font_family=font_family,
            font_feature_settings=font_feature_settings,
            font_size=font_size,
            font_size_unit=font_size_unit,
            font_variation_settings=font_variation_settings,
            font_weight=font_weight,
            font_weight_value=font_weight_value,
            letter_spacing=letter_spacing,
            line_height=line_height,
            mask=mask,
            start=start,
            strike=strike,
            text_color=text_color,
            text_shadow=text_shadow,
            top_offset=top_offset,
            underline=underline,
            **kwargs,
        )

    actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Action when clicking on text.",
    )
    alignment_vertical: typing.Optional[typing.Union[Expr, div_text_alignment_vertical.DivTextAlignmentVertical]] = Field(
        description=(
            "Vertical text alignment within the row. Ignored when a "
            "baseline offset isspecified."
        ),
    )
    background: typing.Optional[div_text_range_background.DivTextRangeBackground] = Field(
        description="Character range background.",
    )
    baseline_offset: typing.Optional[typing.Union[Expr, float]] = Field(
        description=(
            "Vertical baseline offset in a character range. If set, "
            "vertical alignment isignored."
        ),
    )
    border: typing.Optional[div_text_range_border.DivTextRangeBorder] = Field(
        description="Character range border.",
    )
    end: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Ordinal number of the last character to be included in the "
            "range. If the propertyis omitted, the range ends at the "
            "last character of the text."
        ),
    )
    font_family: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Font family:`text` — a standard text font;`display` — a "
            "family of fonts with alarge font size."
        ),
    )
    font_feature_settings: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "List of OpenType font features. The format matches the CSS "
            "attribute\"font-feature-settings\". Learn "
            "more:https://www.w3.org/TR/css-fonts-3/#font-feature-settin"
            "gs-prop"
        ),
    )
    font_size: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Font size.",
    )
    font_size_unit: typing.Optional[typing.Union[Expr, div_size_unit.DivSizeUnit]] = Field(
        description=(
            "Unit of measurement:`px` — a physical pixel.`dp` — a "
            "logical pixel that doesn\'tdepend on screen density.`sp` — "
            "a logical pixel that depends on the font size ona device. "
            "Specify height in `sp`. Only available on Android."
        ),
    )
    font_variation_settings: typing.Optional[typing.Dict[str, typing.Any]] = Field(
        description=(
            "List of TrueType/OpenType font features. The object is "
            "constructed from pairs ofaxis tag and style values. The "
            "axis tag must contain four ASCII characters."
        ),
    )
    font_weight: typing.Optional[typing.Union[Expr, div_font_weight.DivFontWeight]] = Field(
        description="Style.",
    )
    font_weight_value: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Style. Numeric value.",
    )
    letter_spacing: typing.Optional[typing.Union[Expr, float]] = Field(
        description="Spacing between characters.",
    )
    line_height: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Line spacing of the text. Units specified in "
            "`font_size_unit`."
        ),
    )
    mask: typing.Optional[div_text_range_mask.DivTextRangeMask] = Field(
        description=(
            "A mask that hides a part of text. To show the hidden text, "
            "disable the mask usingthe `is_enabled` property."
        ),
    )
    start: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Ordinal number of a character which the range begins from. "
            "The first characterhas a number `0`."
        ),
    )
    strike: typing.Optional[typing.Union[Expr, div_line_style.DivLineStyle]] = Field(
        description="Strikethrough.",
    )
    text_color: typing.Optional[typing.Union[Expr, str]] = Field(
        format="color", 
        description=(
            "Text color for a specific range. Priority: has the highest "
            "priority over`text_gradient` and `text_color`."
        ),
    )
    text_shadow: typing.Optional[div_shadow.DivShadow] = Field(
        description="Parameters of the shadow applied to the character range.",
    )
    top_offset: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Top margin of the character range. Units specified in "
            "`font_size_unit`."
        ),
    )
    underline: typing.Optional[typing.Union[Expr, div_line_style.DivLineStyle]] = Field(
        description="Underline.",
    )


DivTextRange.update_forward_refs()


DivText.update_forward_refs()
