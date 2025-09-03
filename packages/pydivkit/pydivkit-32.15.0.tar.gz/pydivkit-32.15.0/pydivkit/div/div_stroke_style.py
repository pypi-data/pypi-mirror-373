# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing
from typing import Union

from pydivkit.core import BaseDiv, Expr, Field

from . import div_stroke_style_dashed, div_stroke_style_solid


DivStrokeStyle = Union[
    div_stroke_style_solid.DivStrokeStyleSolid,
    div_stroke_style_dashed.DivStrokeStyleDashed,
]
