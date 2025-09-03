# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


class DivContentAlignmentVertical(str, enum.Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"
    BASELINE = "baseline"
    SPACE_BETWEEN = "space-between"
    SPACE_AROUND = "space-around"
    SPACE_EVENLY = "space-evenly"
