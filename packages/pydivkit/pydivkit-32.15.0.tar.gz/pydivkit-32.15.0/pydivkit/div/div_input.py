# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    div_accessibility, div_action, div_alignment_horizontal,
    div_alignment_vertical, div_animator, div_appearance_transition,
    div_background, div_border, div_change_transition, div_disappear_action,
    div_edge_insets, div_extension, div_focus, div_font_weight, div_function,
    div_input_filter, div_input_mask, div_input_validator, div_layout_provider,
    div_size, div_size_unit, div_tooltip, div_transform, div_transition_trigger,
    div_trigger, div_variable, div_visibility, div_visibility_action,
)


# Text input element.
class DivInput(BaseDiv):

    def __init__(
        self, *,
        type: str = "input",
        accessibility: typing.Optional[div_accessibility.DivAccessibility] = None,
        alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = None,
        alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = None,
        alpha: typing.Optional[typing.Union[Expr, float]] = None,
        animators: typing.Optional[typing.Sequence[div_animator.DivAnimator]] = None,
        autocapitalization: typing.Optional[typing.Union[Expr, DivInputAutocapitalization]] = None,
        background: typing.Optional[typing.Sequence[div_background.DivBackground]] = None,
        border: typing.Optional[div_border.DivBorder] = None,
        column_span: typing.Optional[typing.Union[Expr, int]] = None,
        disappear_actions: typing.Optional[typing.Sequence[div_disappear_action.DivDisappearAction]] = None,
        enter_key_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        enter_key_type: typing.Optional[typing.Union[Expr, DivInputEnterKeyType]] = None,
        extensions: typing.Optional[typing.Sequence[div_extension.DivExtension]] = None,
        filters: typing.Optional[typing.Sequence[div_input_filter.DivInputFilter]] = None,
        focus: typing.Optional[div_focus.DivFocus] = None,
        font_family: typing.Optional[typing.Union[Expr, str]] = None,
        font_size: typing.Optional[typing.Union[Expr, int]] = None,
        font_size_unit: typing.Optional[typing.Union[Expr, div_size_unit.DivSizeUnit]] = None,
        font_variation_settings: typing.Optional[typing.Dict[str, typing.Any]] = None,
        font_weight: typing.Optional[typing.Union[Expr, div_font_weight.DivFontWeight]] = None,
        font_weight_value: typing.Optional[typing.Union[Expr, int]] = None,
        functions: typing.Optional[typing.Sequence[div_function.DivFunction]] = None,
        height: typing.Optional[div_size.DivSize] = None,
        highlight_color: typing.Optional[typing.Union[Expr, str]] = None,
        hint_color: typing.Optional[typing.Union[Expr, str]] = None,
        hint_text: typing.Optional[typing.Union[Expr, str]] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        is_enabled: typing.Optional[typing.Union[Expr, bool]] = None,
        keyboard_type: typing.Optional[typing.Union[Expr, DivInputKeyboardType]] = None,
        layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = None,
        letter_spacing: typing.Optional[typing.Union[Expr, float]] = None,
        line_height: typing.Optional[typing.Union[Expr, int]] = None,
        margins: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        mask: typing.Optional[div_input_mask.DivInputMask] = None,
        max_length: typing.Optional[typing.Union[Expr, int]] = None,
        max_visible_lines: typing.Optional[typing.Union[Expr, int]] = None,
        native_interface: typing.Optional[DivInputNativeInterface] = None,
        paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        reuse_id: typing.Optional[typing.Union[Expr, str]] = None,
        row_span: typing.Optional[typing.Union[Expr, int]] = None,
        select_all_on_focus: typing.Optional[typing.Union[Expr, bool]] = None,
        selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        text_alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = None,
        text_alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = None,
        text_color: typing.Optional[typing.Union[Expr, str]] = None,
        text_variable: typing.Optional[typing.Union[Expr, str]] = None,
        tooltips: typing.Optional[typing.Sequence[div_tooltip.DivTooltip]] = None,
        transform: typing.Optional[div_transform.DivTransform] = None,
        transition_change: typing.Optional[div_change_transition.DivChangeTransition] = None,
        transition_in: typing.Optional[div_appearance_transition.DivAppearanceTransition] = None,
        transition_out: typing.Optional[div_appearance_transition.DivAppearanceTransition] = None,
        transition_triggers: typing.Optional[typing.Sequence[typing.Union[Expr, div_transition_trigger.DivTransitionTrigger]]] = None,
        validators: typing.Optional[typing.Sequence[div_input_validator.DivInputValidator]] = None,
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
            alignment_horizontal=alignment_horizontal,
            alignment_vertical=alignment_vertical,
            alpha=alpha,
            animators=animators,
            autocapitalization=autocapitalization,
            background=background,
            border=border,
            column_span=column_span,
            disappear_actions=disappear_actions,
            enter_key_actions=enter_key_actions,
            enter_key_type=enter_key_type,
            extensions=extensions,
            filters=filters,
            focus=focus,
            font_family=font_family,
            font_size=font_size,
            font_size_unit=font_size_unit,
            font_variation_settings=font_variation_settings,
            font_weight=font_weight,
            font_weight_value=font_weight_value,
            functions=functions,
            height=height,
            highlight_color=highlight_color,
            hint_color=hint_color,
            hint_text=hint_text,
            id=id,
            is_enabled=is_enabled,
            keyboard_type=keyboard_type,
            layout_provider=layout_provider,
            letter_spacing=letter_spacing,
            line_height=line_height,
            margins=margins,
            mask=mask,
            max_length=max_length,
            max_visible_lines=max_visible_lines,
            native_interface=native_interface,
            paddings=paddings,
            reuse_id=reuse_id,
            row_span=row_span,
            select_all_on_focus=select_all_on_focus,
            selected_actions=selected_actions,
            text_alignment_horizontal=text_alignment_horizontal,
            text_alignment_vertical=text_alignment_vertical,
            text_color=text_color,
            text_variable=text_variable,
            tooltips=tooltips,
            transform=transform,
            transition_change=transition_change,
            transition_in=transition_in,
            transition_out=transition_out,
            transition_triggers=transition_triggers,
            validators=validators,
            variable_triggers=variable_triggers,
            variables=variables,
            visibility=visibility,
            visibility_action=visibility_action,
            visibility_actions=visibility_actions,
            width=width,
            **kwargs,
        )

    type: str = Field(default="input")
    accessibility: typing.Optional[div_accessibility.DivAccessibility] = Field(
        description="Accessibility settings.",
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
    autocapitalization: typing.Optional[typing.Union[Expr, DivInputAutocapitalization]] = Field(
        description=(
            "Text auto-capitalization type. By default: `auto` — default "
            "behavior of theplatform;`none\' — automatic capitalization "
            "is not applied;`words` —capitalization of each "
            "word;`sentences` — capitalization at the beginning of "
            "asentence;`all_characters\' — capitalization of each "
            "character."
        ),
    )
    background: typing.Optional[typing.Sequence[div_background.DivBackground]] = Field(
        description="Element background. It can contain multiple layers.",
    )
    border: typing.Optional[div_border.DivBorder] = Field(
        description="Element stroke.",
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
    enter_key_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "Actions when pressing the \'Enter\' key. Actions (if any) "
            "override the defaultbehavior."
        ),
    )
    enter_key_type: typing.Optional[typing.Union[Expr, DivInputEnterKeyType]] = Field(
        description="\'Enter\' key type.",
    )
    extensions: typing.Optional[typing.Sequence[div_extension.DivExtension]] = Field(
        description=(
            "Extensions for additional processing of an element. The "
            "list of extensions isgiven in "
            "[DivExtension](../../extensions)."
        ),
    )
    filters: typing.Optional[typing.Sequence[div_input_filter.DivInputFilter]] = Field(
        description=(
            "Filter that prevents users from entering text that doesn\'t "
            "satisfy the specifiedconditions."
        ),
    )
    focus: typing.Optional[div_focus.DivFocus] = Field(
        description="Parameters when focusing on an element or losing focus.",
    )
    font_family: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Font family:`text` — a standard text font;`display` — a "
            "family of fonts with alarge font size."
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
    highlight_color: typing.Optional[typing.Union[Expr, str]] = Field(
        format="color", 
        description=(
            "Text highlight color. If the value isn\'t set, the color "
            "set in the client will beused instead."
        ),
    )
    hint_color: typing.Optional[typing.Union[Expr, str]] = Field(
        format="color", 
        description="Text color.",
    )
    hint_text: typing.Optional[typing.Union[Expr, str]] = Field(
        description="Tooltip text.",
    )
    id: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Element ID. It must be unique within the root element. It "
            "is used as`accessibilityIdentifier` on iOS."
        ),
    )
    is_enabled: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Enables or disables text editing.",
    )
    keyboard_type: typing.Optional[typing.Union[Expr, DivInputKeyboardType]] = Field(
        description="Keyboard type.",
    )
    layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = Field(
        description="Provides data on the actual size of the element.",
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
    margins: typing.Optional[div_edge_insets.DivEdgeInsets] = Field(
        description="External margins from the element stroke.",
    )
    mask: typing.Optional[div_input_mask.DivInputMask] = Field(
        description="Mask for entering text based on the specified template.",
    )
    max_length: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Maximum number of characters that can be entered in the "
            "input field."
        ),
    )
    max_visible_lines: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Maximum number of lines to be displayed in the input field."
        ),
    )
    native_interface: typing.Optional[DivInputNativeInterface] = Field(
        description="Text input line used in the native interface.",
    )
    paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = Field(
        description="Internal margins from the element stroke.",
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
    select_all_on_focus: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Highlighting input text when focused.",
    )
    selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "List of [actions](div-action.md) to be executed when "
            "selecting an element in[pager](div-pager.md)."
        ),
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
    text_variable: typing.Union[Expr, str] = Field(
        description="Name of text storage variable.",
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
    validators: typing.Optional[typing.Sequence[div_input_validator.DivInputValidator]] = Field(
        description=(
            "Validator that checks that the field value meets the "
            "specified conditions."
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


class DivInputAutocapitalization(str, enum.Enum):
    AUTO = "auto"
    NONE = "none"
    WORDS = "words"
    SENTENCES = "sentences"
    ALL_CHARACTERS = "all_characters"


class DivInputEnterKeyType(str, enum.Enum):
    DEFAULT = "default"
    GO = "go"
    SEARCH = "search"
    SEND = "send"
    DONE = "done"


class DivInputKeyboardType(str, enum.Enum):
    SINGLE_LINE_TEXT = "single_line_text"
    MULTI_LINE_TEXT = "multi_line_text"
    PHONE = "phone"
    NUMBER = "number"
    EMAIL = "email"
    URI = "uri"
    PASSWORD = "password"


# Text input line used in the native interface.
class DivInputNativeInterface(BaseDiv):

    def __init__(
        self, *,
        color: typing.Optional[typing.Union[Expr, str]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            color=color,
            **kwargs,
        )

    color: typing.Union[Expr, str] = Field(
        format="color", 
        description="Text input line color.",
    )


DivInputNativeInterface.update_forward_refs()


DivInput.update_forward_refs()
