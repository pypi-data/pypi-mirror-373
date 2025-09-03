# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    div, div_accessibility, div_action, div_alignment_horizontal,
    div_alignment_vertical, div_animator, div_appearance_transition,
    div_background, div_border, div_change_transition,
    div_collection_item_builder, div_disappear_action, div_edge_insets,
    div_extension, div_fixed_size, div_focus, div_function, div_layout_provider,
    div_page_transformation, div_pager_layout_mode, div_size, div_tooltip,
    div_transform, div_transition_trigger, div_trigger, div_variable,
    div_visibility, div_visibility_action,
)


# Pager. It contains a horizontal set of cards that can be scrolled page by page.
# It shows the main page and the beginning of the next one.
class DivPager(BaseDiv):

    def __init__(
        self, *,
        type: str = "pager",
        accessibility: typing.Optional[div_accessibility.DivAccessibility] = None,
        alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = None,
        alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = None,
        alpha: typing.Optional[typing.Union[Expr, float]] = None,
        animators: typing.Optional[typing.Sequence[div_animator.DivAnimator]] = None,
        background: typing.Optional[typing.Sequence[div_background.DivBackground]] = None,
        border: typing.Optional[div_border.DivBorder] = None,
        column_span: typing.Optional[typing.Union[Expr, int]] = None,
        cross_axis_alignment: typing.Optional[typing.Union[Expr, DivPagerItemAlignment]] = None,
        default_item: typing.Optional[typing.Union[Expr, int]] = None,
        disappear_actions: typing.Optional[typing.Sequence[div_disappear_action.DivDisappearAction]] = None,
        extensions: typing.Optional[typing.Sequence[div_extension.DivExtension]] = None,
        focus: typing.Optional[div_focus.DivFocus] = None,
        functions: typing.Optional[typing.Sequence[div_function.DivFunction]] = None,
        height: typing.Optional[div_size.DivSize] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        infinite_scroll: typing.Optional[typing.Union[Expr, bool]] = None,
        item_builder: typing.Optional[div_collection_item_builder.DivCollectionItemBuilder] = None,
        item_spacing: typing.Optional[div_fixed_size.DivFixedSize] = None,
        items: typing.Optional[typing.Sequence[div.Div]] = None,
        layout_mode: typing.Optional[div_pager_layout_mode.DivPagerLayoutMode] = None,
        layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = None,
        margins: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        orientation: typing.Optional[typing.Union[Expr, DivPagerOrientation]] = None,
        paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        page_transformation: typing.Optional[div_page_transformation.DivPageTransformation] = None,
        restrict_parent_scroll: typing.Optional[typing.Union[Expr, bool]] = None,
        reuse_id: typing.Optional[typing.Union[Expr, str]] = None,
        row_span: typing.Optional[typing.Union[Expr, int]] = None,
        scroll_axis_alignment: typing.Optional[typing.Union[Expr, DivPagerItemAlignment]] = None,
        selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
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
            alignment_horizontal=alignment_horizontal,
            alignment_vertical=alignment_vertical,
            alpha=alpha,
            animators=animators,
            background=background,
            border=border,
            column_span=column_span,
            cross_axis_alignment=cross_axis_alignment,
            default_item=default_item,
            disappear_actions=disappear_actions,
            extensions=extensions,
            focus=focus,
            functions=functions,
            height=height,
            id=id,
            infinite_scroll=infinite_scroll,
            item_builder=item_builder,
            item_spacing=item_spacing,
            items=items,
            layout_mode=layout_mode,
            layout_provider=layout_provider,
            margins=margins,
            orientation=orientation,
            paddings=paddings,
            page_transformation=page_transformation,
            restrict_parent_scroll=restrict_parent_scroll,
            reuse_id=reuse_id,
            row_span=row_span,
            scroll_axis_alignment=scroll_axis_alignment,
            selected_actions=selected_actions,
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

    type: str = Field(default="pager")
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
    cross_axis_alignment: typing.Optional[typing.Union[Expr, DivPagerItemAlignment]] = Field(
        description=(
            "Aligning elements in the direction perpendicular to the "
            "scroll direction. Inhorizontal pager:`start` — alignment to "
            "the top of the card;`center` — to thecenter;`end` — to the "
            "bottom.</p><p>In vertical pager:`start` — alignment to "
            "theleft of the card;`center` — to the center;`end` — to the "
            "right."
        ),
    )
    default_item: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Ordinal number of the pager element that will be opened by "
            "default."
        ),
    )
    disappear_actions: typing.Optional[typing.Sequence[div_disappear_action.DivDisappearAction]] = Field(
        description="Actions when an element disappears from the screen.",
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
    id: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Element ID. It must be unique within the root element. It "
            "is used as`accessibilityIdentifier` on iOS."
        ),
    )
    infinite_scroll: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "Enables infinite scrolling of cards. Scrolling is looped: "
            "after the last card isdisplayed, it starts over again."
        ),
    )
    item_builder: typing.Optional[div_collection_item_builder.DivCollectionItemBuilder] = Field(
        description=(
            "Sets collection elements dynamically using `data` and "
            "`prototypes`."
        ),
    )
    item_spacing: typing.Optional[div_fixed_size.DivFixedSize] = Field(
        description="Spacing between elements.",
    )
    items: typing.Optional[typing.Sequence[div.Div]] = Field(
        description=(
            "Pager elements. Page-by-page transition options can be "
            "implementedusing:`div-action://set_current_item?id=&item=` "
            "— set the current page with anordinal number `item` inside "
            "an element, with the "
            "specified`id`;`div-action://set_next_item?id=[&overflow={cl"
            "amp\|ring}]` — go to the nextpage inside an element, with "
            "the "
            "specified`id`;`div-action://set_previous_item?id=[&overflow"
            "={clamp\|ring}]` — go to theprevious page inside an "
            "element, with the specified `id`.</p><p>The "
            "optional`overflow` parameter is used to set navigation when "
            "the first or last element isreached:`clamp` — transition "
            "will stop at the border element;`ring` — go to thebeginning "
            "or end, depending on the current element.</p><p>By default, "
            "`clamp`."
        ),
    )
    layout_mode: div_pager_layout_mode.DivPagerLayoutMode = Field(
        description=(
            "Type of calculation of the main page width:`fixed` — from "
            "the fixed width of thenext page "
            "`neighbour_page_width`;`percentage` — from the percentage "
            "value`page_width`."
        ),
    )
    layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = Field(
        description="Provides data on the actual size of the element.",
    )
    margins: typing.Optional[div_edge_insets.DivEdgeInsets] = Field(
        description="External margins from the element stroke.",
    )
    orientation: typing.Optional[typing.Union[Expr, DivPagerOrientation]] = Field(
        description="Pager orientation.",
    )
    paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = Field(
        description="Internal margins from the element stroke.",
    )
    page_transformation: typing.Optional[div_page_transformation.DivPageTransformation] = Field(
        description="Page transformation during pager scrolling.",
    )
    restrict_parent_scroll: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "If the parameter is enabled, the pager won\'t transmit the "
            "scroll gesture to theparent element."
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
    scroll_axis_alignment: typing.Optional[typing.Union[Expr, DivPagerItemAlignment]] = Field(
        description=(
            "Alignment of pager pages along the scroll direction. In "
            "horizontal pager:`start`— alignment to the left of the "
            "card;`center` — to the center;`end` — to theright.</p><p>In "
            "vertical pager:`start` — alignment to the top of "
            "thecard;`center` — to the center;`end` — to the bottom.. "
            "For edge alignment, themargin from the edge of the parent "
            "equals the value of the corresponding padding."
        ),
    )
    selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "List of [actions](div-action.md) to be executed when "
            "selecting an element in[pager](div-pager.md)."
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


class DivPagerItemAlignment(str, enum.Enum):
    START = "start"
    CENTER = "center"
    END = "end"


class DivPagerOrientation(str, enum.Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


DivPager.update_forward_refs()
