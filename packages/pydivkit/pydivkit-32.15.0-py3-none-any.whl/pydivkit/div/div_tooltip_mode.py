# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing
from typing import Union

from pydivkit.core import BaseDiv, Expr, Field

from . import div_tooltip_mode_modal, div_tooltip_mode_non_modal


DivTooltipMode = Union[
    div_tooltip_mode_non_modal.DivTooltipModeNonModal,
    div_tooltip_mode_modal.DivTooltipModeModal,
]
