# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    div, div_accessibility, div_action, div_alignment_horizontal,
    div_alignment_vertical, div_animation, div_animator,
    div_appearance_transition, div_background, div_border,
    div_change_transition, div_disappear_action, div_edge_insets, div_extension,
    div_focus, div_function, div_layout_provider, div_size, div_tooltip,
    div_transform, div_transition_selector, div_transition_trigger, div_trigger,
    div_variable, div_visibility, div_visibility_action,
)


# It contains sets of states for visual elements and switches between them.
class DivState(BaseDiv):

    def __init__(
        self, *,
        type: str = "state",
        accessibility: typing.Optional[div_accessibility.DivAccessibility] = None,
        action: typing.Optional[div_action.DivAction] = None,
        action_animation: typing.Optional[div_animation.DivAnimation] = None,
        actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = None,
        alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = None,
        alpha: typing.Optional[typing.Union[Expr, float]] = None,
        animators: typing.Optional[typing.Sequence[div_animator.DivAnimator]] = None,
        background: typing.Optional[typing.Sequence[div_background.DivBackground]] = None,
        border: typing.Optional[div_border.DivBorder] = None,
        capture_focus_on_action: typing.Optional[typing.Union[Expr, bool]] = None,
        clip_to_bounds: typing.Optional[typing.Union[Expr, bool]] = None,
        column_span: typing.Optional[typing.Union[Expr, int]] = None,
        default_state_id: typing.Optional[typing.Union[Expr, str]] = None,
        disappear_actions: typing.Optional[typing.Sequence[div_disappear_action.DivDisappearAction]] = None,
        div_id: typing.Optional[typing.Union[Expr, str]] = None,
        doubletap_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        extensions: typing.Optional[typing.Sequence[div_extension.DivExtension]] = None,
        focus: typing.Optional[div_focus.DivFocus] = None,
        functions: typing.Optional[typing.Sequence[div_function.DivFunction]] = None,
        height: typing.Optional[div_size.DivSize] = None,
        hover_end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        hover_start_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = None,
        longtap_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        margins: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        press_end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        press_start_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        reuse_id: typing.Optional[typing.Union[Expr, str]] = None,
        row_span: typing.Optional[typing.Union[Expr, int]] = None,
        selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        state_id_variable: typing.Optional[typing.Union[Expr, str]] = None,
        states: typing.Optional[typing.Sequence[DivStateState]] = None,
        tooltips: typing.Optional[typing.Sequence[div_tooltip.DivTooltip]] = None,
        transform: typing.Optional[div_transform.DivTransform] = None,
        transition_animation_selector: typing.Optional[typing.Union[Expr, div_transition_selector.DivTransitionSelector]] = None,
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
            background=background,
            border=border,
            capture_focus_on_action=capture_focus_on_action,
            clip_to_bounds=clip_to_bounds,
            column_span=column_span,
            default_state_id=default_state_id,
            disappear_actions=disappear_actions,
            div_id=div_id,
            doubletap_actions=doubletap_actions,
            extensions=extensions,
            focus=focus,
            functions=functions,
            height=height,
            hover_end_actions=hover_end_actions,
            hover_start_actions=hover_start_actions,
            id=id,
            layout_provider=layout_provider,
            longtap_actions=longtap_actions,
            margins=margins,
            paddings=paddings,
            press_end_actions=press_end_actions,
            press_start_actions=press_start_actions,
            reuse_id=reuse_id,
            row_span=row_span,
            selected_actions=selected_actions,
            state_id_variable=state_id_variable,
            states=states,
            tooltips=tooltips,
            transform=transform,
            transition_animation_selector=transition_animation_selector,
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

    type: str = Field(default="state")
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
    clip_to_bounds: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "Enables the bounding of child elements by the parent\'s "
            "borders."
        ),
    )
    column_span: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Merges cells in a column of the [grid](div-grid.md) "
            "element."
        ),
    )
    default_state_id: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "ID of the status that will be set by default. If the "
            "parameter isnt set, thefirst state of the `states` will be "
            "set."
        ),
    )
    disappear_actions: typing.Optional[typing.Sequence[div_disappear_action.DivDisappearAction]] = Field(
        description="Actions when an element disappears from the screen.",
    )
    div_id: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "ID of an element to search in the hierarchy. The ID must be "
            "unique at onehierarchy level. @deprecated"
        ),
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
    press_end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions performed after clicking/tapping an element.",
    )
    press_start_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "Actions performed at the start of a click/tap on an "
            "element."
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
    selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "List of [actions](div-action.md) to be executed when "
            "selecting an element in[pager](div-pager.md)."
        ),
    )
    state_id_variable: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "The name of the variable that stores the ID for the current "
            "state. If thevariable changes, the active state will also "
            "change. The variable is prioritizedover the "
            "default_state_id parameter."
        ),
    )
    states: typing.Sequence[DivStateState] = Field(
        min_items=1, 
        description=(
            "States. Each element can have a few states with a different "
            "layout. Transitionbetween states is performed using "
            "[special scheme](../../interaction) of "
            "the[action](div-action.md) element."
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
    transition_animation_selector: typing.Optional[typing.Union[Expr, div_transition_selector.DivTransitionSelector]] = Field(
        description=(
            "It determines which events trigger transition animations. "
            "@deprecated"
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


class DivStateState(BaseDiv):

    def __init__(
        self, *,
        animation_in: typing.Optional[div_animation.DivAnimation] = None,
        animation_out: typing.Optional[div_animation.DivAnimation] = None,
        div: typing.Optional[div.Div] = None,
        state_id: typing.Optional[typing.Union[Expr, str]] = None,
        swipe_out_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            animation_in=animation_in,
            animation_out=animation_out,
            div=div,
            state_id=state_id,
            swipe_out_actions=swipe_out_actions,
            **kwargs,
        )

    animation_in: typing.Optional[div_animation.DivAnimation] = Field(
        description=(
            "State appearance animation. Use `transition_in` instead. "
            "@deprecated"
        ),
    )
    animation_out: typing.Optional[div_animation.DivAnimation] = Field(
        description=(
            "State disappearance animation. Use `transition_out` "
            "instead. @deprecated"
        ),
    )
    div: typing.Optional[div.Div] = Field(
        description=(
            "Contents. If the parameter is missing, the state won\'t be "
            "displayed."
        ),
    )
    state_id: typing.Union[Expr, str] = Field(
        description="State ID. It must be unique at one hierarchy level.",
    )
    swipe_out_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions when swiping the state horizontally. @deprecated",
    )


DivStateState.update_forward_refs()


DivState.update_forward_refs()
