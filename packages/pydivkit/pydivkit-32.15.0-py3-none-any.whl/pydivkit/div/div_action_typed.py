# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing
from typing import Union

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    div_action_animator_start, div_action_animator_stop,
    div_action_array_insert_value, div_action_array_remove_value,
    div_action_array_set_value, div_action_clear_focus,
    div_action_copy_to_clipboard, div_action_dict_set_value,
    div_action_download, div_action_focus_element, div_action_hide_tooltip,
    div_action_scroll_by, div_action_scroll_to, div_action_set_state,
    div_action_set_stored_value, div_action_set_variable,
    div_action_show_tooltip, div_action_submit, div_action_timer,
    div_action_update_structure, div_action_video,
)


DivActionTyped = Union[
    div_action_animator_start.DivActionAnimatorStart,
    div_action_animator_stop.DivActionAnimatorStop,
    div_action_array_insert_value.DivActionArrayInsertValue,
    div_action_array_remove_value.DivActionArrayRemoveValue,
    div_action_array_set_value.DivActionArraySetValue,
    div_action_clear_focus.DivActionClearFocus,
    div_action_copy_to_clipboard.DivActionCopyToClipboard,
    div_action_dict_set_value.DivActionDictSetValue,
    div_action_download.DivActionDownload,
    div_action_focus_element.DivActionFocusElement,
    div_action_hide_tooltip.DivActionHideTooltip,
    div_action_scroll_by.DivActionScrollBy,
    div_action_scroll_to.DivActionScrollTo,
    div_action_set_state.DivActionSetState,
    div_action_set_stored_value.DivActionSetStoredValue,
    div_action_set_variable.DivActionSetVariable,
    div_action_show_tooltip.DivActionShowTooltip,
    div_action_submit.DivActionSubmit,
    div_action_timer.DivActionTimer,
    div_action_update_structure.DivActionUpdateStructure,
    div_action_video.DivActionVideo,
]
