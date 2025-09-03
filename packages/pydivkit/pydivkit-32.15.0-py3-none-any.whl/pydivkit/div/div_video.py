# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    div_accessibility, div_action, div_alignment_horizontal,
    div_alignment_vertical, div_animator, div_appearance_transition, div_aspect,
    div_background, div_border, div_change_transition, div_disappear_action,
    div_edge_insets, div_extension, div_focus, div_function,
    div_layout_provider, div_size, div_tooltip, div_transform,
    div_transition_trigger, div_trigger, div_variable, div_video_scale,
    div_video_source, div_visibility, div_visibility_action,
)


# Video.
class DivVideo(BaseDiv):

    def __init__(
        self, *,
        type: str = "video",
        accessibility: typing.Optional[div_accessibility.DivAccessibility] = None,
        alignment_horizontal: typing.Optional[typing.Union[Expr, div_alignment_horizontal.DivAlignmentHorizontal]] = None,
        alignment_vertical: typing.Optional[typing.Union[Expr, div_alignment_vertical.DivAlignmentVertical]] = None,
        alpha: typing.Optional[typing.Union[Expr, float]] = None,
        animators: typing.Optional[typing.Sequence[div_animator.DivAnimator]] = None,
        aspect: typing.Optional[div_aspect.DivAspect] = None,
        autostart: typing.Optional[typing.Union[Expr, bool]] = None,
        background: typing.Optional[typing.Sequence[div_background.DivBackground]] = None,
        border: typing.Optional[div_border.DivBorder] = None,
        buffering_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        column_span: typing.Optional[typing.Union[Expr, int]] = None,
        disappear_actions: typing.Optional[typing.Sequence[div_disappear_action.DivDisappearAction]] = None,
        elapsed_time_variable: typing.Optional[typing.Union[Expr, str]] = None,
        end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        extensions: typing.Optional[typing.Sequence[div_extension.DivExtension]] = None,
        fatal_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        focus: typing.Optional[div_focus.DivFocus] = None,
        functions: typing.Optional[typing.Sequence[div_function.DivFunction]] = None,
        height: typing.Optional[div_size.DivSize] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = None,
        margins: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        muted: typing.Optional[typing.Union[Expr, bool]] = None,
        paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = None,
        pause_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        player_settings_payload: typing.Optional[typing.Dict[str, typing.Any]] = None,
        preload_required: typing.Optional[typing.Union[Expr, bool]] = None,
        preview: typing.Optional[typing.Union[Expr, str]] = None,
        repeatable: typing.Optional[typing.Union[Expr, bool]] = None,
        resume_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        reuse_id: typing.Optional[typing.Union[Expr, str]] = None,
        row_span: typing.Optional[typing.Union[Expr, int]] = None,
        scale: typing.Optional[typing.Union[Expr, div_video_scale.DivVideoScale]] = None,
        selected_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        tooltips: typing.Optional[typing.Sequence[div_tooltip.DivTooltip]] = None,
        transform: typing.Optional[div_transform.DivTransform] = None,
        transition_change: typing.Optional[div_change_transition.DivChangeTransition] = None,
        transition_in: typing.Optional[div_appearance_transition.DivAppearanceTransition] = None,
        transition_out: typing.Optional[div_appearance_transition.DivAppearanceTransition] = None,
        transition_triggers: typing.Optional[typing.Sequence[typing.Union[Expr, div_transition_trigger.DivTransitionTrigger]]] = None,
        variable_triggers: typing.Optional[typing.Sequence[div_trigger.DivTrigger]] = None,
        variables: typing.Optional[typing.Sequence[div_variable.DivVariable]] = None,
        video_sources: typing.Optional[typing.Sequence[div_video_source.DivVideoSource]] = None,
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
            aspect=aspect,
            autostart=autostart,
            background=background,
            border=border,
            buffering_actions=buffering_actions,
            column_span=column_span,
            disappear_actions=disappear_actions,
            elapsed_time_variable=elapsed_time_variable,
            end_actions=end_actions,
            extensions=extensions,
            fatal_actions=fatal_actions,
            focus=focus,
            functions=functions,
            height=height,
            id=id,
            layout_provider=layout_provider,
            margins=margins,
            muted=muted,
            paddings=paddings,
            pause_actions=pause_actions,
            player_settings_payload=player_settings_payload,
            preload_required=preload_required,
            preview=preview,
            repeatable=repeatable,
            resume_actions=resume_actions,
            reuse_id=reuse_id,
            row_span=row_span,
            scale=scale,
            selected_actions=selected_actions,
            tooltips=tooltips,
            transform=transform,
            transition_change=transition_change,
            transition_in=transition_in,
            transition_out=transition_out,
            transition_triggers=transition_triggers,
            variable_triggers=variable_triggers,
            variables=variables,
            video_sources=video_sources,
            visibility=visibility,
            visibility_action=visibility_action,
            visibility_actions=visibility_actions,
            width=width,
            **kwargs,
        )

    type: str = Field(default="video")
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
    aspect: typing.Optional[div_aspect.DivAspect] = Field(
        description=(
            "Fixed aspect ratio. The element\'s height is calculated "
            "based on the width,ignoring the `height` value."
        ),
    )
    autostart: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "This option turns on automatic video playback. On the web, "
            "the video starts ifmuted playback is turned on."
        ),
    )
    background: typing.Optional[typing.Sequence[div_background.DivBackground]] = Field(
        description="Element background. It can contain multiple layers.",
    )
    border: typing.Optional[div_border.DivBorder] = Field(
        description="Element stroke.",
    )
    buffering_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions performed during video loading.",
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
    elapsed_time_variable: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Time interval from the video beginning to the current "
            "position in milliseconds."
        ),
    )
    end_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions performed after the video ends.",
    )
    extensions: typing.Optional[typing.Sequence[div_extension.DivExtension]] = Field(
        description=(
            "Extensions for additional processing of an element. The "
            "list of extensions isgiven in "
            "[DivExtension](../../extensions)."
        ),
    )
    fatal_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "Actions performed when playback can\'t be continued due to "
            "a player error."
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
    layout_provider: typing.Optional[div_layout_provider.DivLayoutProvider] = Field(
        description="Provides data on the actual size of the element.",
    )
    margins: typing.Optional[div_edge_insets.DivEdgeInsets] = Field(
        description="External margins from the element stroke.",
    )
    muted: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="This option mutes video.",
    )
    paddings: typing.Optional[div_edge_insets.DivEdgeInsets] = Field(
        description="Internal margins from the element stroke.",
    )
    pause_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions performed when playback is paused.",
    )
    player_settings_payload: typing.Optional[typing.Dict[str, typing.Any]] = Field(
        description="Additional information that can be used in the player.",
    )
    preload_required: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Enables video preloading.",
    )
    preview: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Video preview encoded in `base64`. Will be shown until the "
            "video is ready toplay. `Data url` format: "
            "`data:[;base64],<data>`"
        ),
    )
    repeatable: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="This option turns on video repeat.",
    )
    resume_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description="Actions performed when video playback resumes.",
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
    scale: typing.Optional[typing.Union[Expr, div_video_scale.DivVideoScale]] = Field(
        description=(
            "Video scaling:`fit` places the entire video into the "
            "element (free space isfilled with background);`fill` scales "
            "the video to the element size and cuts offanything that\'s "
            "extra."
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
    video_sources: typing.Sequence[div_video_source.DivVideoSource] = Field(
        min_items=1,
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


DivVideo.update_forward_refs()
